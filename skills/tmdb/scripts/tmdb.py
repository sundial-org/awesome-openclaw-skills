# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "click"]
# ///
"""TMDb movie/TV database with streaming info and personalized recommendations."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
import httpx

TMDB_BASE = "https://api.themoviedb.org/3"
API_KEY = os.environ.get("TMDB_API_KEY", "")
DATA_DIR = Path(__file__).parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
PREFS_FILE = DATA_DIR / "preferences.json"

# Genre name to ID mapping
GENRES = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
    "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
    "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
    "mystery": 9648, "romance": 10749, "sci-fi": 878, "science fiction": 878,
    "thriller": 53, "tv movie": 10770, "war": 10752, "western": 37,
}

GENRE_NAMES = {v: k for k, v in GENRES.items()}


def api_get(endpoint: str, params: dict = None) -> dict:
    """Make TMDb API request."""
    if not API_KEY:
        click.echo("❌ TMDB_API_KEY not set", err=True)
        sys.exit(1)
    
    params = params or {}
    params["api_key"] = API_KEY
    
    resp = httpx.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def load_json(path: Path) -> dict:
    """Load JSON file."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_json(path: Path, data: dict) -> None:
    """Save JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def format_movie(m: dict, detailed: bool = False) -> str:
    """Format movie info for display."""
    year = m.get("release_date", "")[:4] or "TBD"
    rating = m.get("vote_average", 0)
    stars = "⭐" * round(rating / 2)
    
    lines = [f"🎬 **{m.get('title', 'Unknown')}** ({year})"]
    lines.append(f"   Rating: {rating}/10 {stars}")
    
    if detailed:
        if m.get("tagline"):
            lines.append(f"   \"{m['tagline']}\"")
        if m.get("runtime"):
            hrs, mins = divmod(m["runtime"], 60)
            lines.append(f"   Runtime: {hrs}h {mins}m")
        if m.get("genres"):
            genres = ", ".join(g["name"] for g in m["genres"])
            lines.append(f"   Genres: {genres}")
        if m.get("overview"):
            overview = m["overview"][:200] + "..." if len(m.get("overview", "")) > 200 else m.get("overview", "")
            lines.append(f"   {overview}")
    
    return "\n".join(lines)


def format_tv(t: dict, detailed: bool = False) -> str:
    """Format TV show info for display."""
    year = t.get("first_air_date", "")[:4] or "TBD"
    rating = t.get("vote_average", 0)
    stars = "⭐" * round(rating / 2)
    
    lines = [f"📺 **{t.get('name', 'Unknown')}** ({year})"]
    lines.append(f"   Rating: {rating}/10 {stars}")
    
    if detailed:
        if t.get("tagline"):
            lines.append(f"   \"{t['tagline']}\"")
        if t.get("number_of_seasons"):
            lines.append(f"   Seasons: {t['number_of_seasons']}, Episodes: {t.get('number_of_episodes', '?')}")
        if t.get("genres"):
            genres = ", ".join(g["name"] for g in t["genres"])
            lines.append(f"   Genres: {genres}")
        if t.get("overview"):
            overview = t["overview"][:200] + "..." if len(t.get("overview", "")) > 200 else t.get("overview", "")
            lines.append(f"   {overview}")
    
    return "\n".join(lines)


@click.group()
def cli():
    """TMDb - Movie and TV Database."""
    pass


@cli.command()
@click.argument("query")
@click.option("--tv", is_flag=True, help="Search TV shows instead of movies")
@click.option("--limit", "-l", default=5, help="Max results")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def search(query: str, tv: bool, limit: int, json_output: bool):
    """Search for movies or TV shows."""
    endpoint = "/search/tv" if tv else "/search/movie"
    data = api_get(endpoint, {"query": query})
    
    results = data.get("results", [])[:limit]
    
    if json_output:
        click.echo(json.dumps(results, indent=2))
        return
    
    if not results:
        click.echo(f"No results for '{query}'")
        return
    
    media_type = "TV shows" if tv else "movies"
    click.echo(f"Found {len(results)} {media_type}:\n")
    
    for item in results:
        if tv:
            year = item.get("first_air_date", "")[:4] or "?"
            click.echo(f"  [{item['id']}] {item.get('name', '?')} ({year}) ⭐{item.get('vote_average', 0):.1f}")
        else:
            year = item.get("release_date", "")[:4] or "?"
            click.echo(f"  [{item['id']}] {item.get('title', '?')} ({year}) ⭐{item.get('vote_average', 0):.1f}")


@cli.command()
@click.argument("movie_id")
@click.option("--cast", is_flag=True, help="Include cast information")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def movie(movie_id: str, cast: bool, json_output: bool):
    """Get movie details by ID."""
    # Try to search if not numeric
    if not movie_id.isdigit():
        data = api_get("/search/movie", {"query": movie_id})
        results = data.get("results", [])
        if not results:
            click.echo(f"❌ Movie '{movie_id}' not found")
            return
        movie_id = str(results[0]["id"])
    
    data = api_get(f"/movie/{movie_id}")
    
    if cast:
        credits = api_get(f"/movie/{movie_id}/credits")
        data["cast"] = credits.get("cast", [])[:10]
        data["crew"] = [c for c in credits.get("crew", []) if c.get("job") in ("Director", "Writer", "Screenplay")]
    
    if json_output:
        click.echo(json.dumps(data, indent=2))
        return
    
    click.echo(format_movie(data, detailed=True))
    
    if cast and data.get("cast"):
        click.echo("\n   Cast:")
        for c in data["cast"]:
            click.echo(f"     • {c['name']} as {c.get('character', '?')}")
    
    if cast and data.get("crew"):
        click.echo("\n   Crew:")
        for c in data["crew"]:
            click.echo(f"     • {c['name']} ({c['job']})")


@cli.command()
@click.argument("tv_id")
@click.option("--cast", is_flag=True, help="Include cast information")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def tv(tv_id: str, cast: bool, json_output: bool):
    """Get TV show details by ID."""
    # Try to search if not numeric
    if not tv_id.isdigit():
        data = api_get("/search/tv", {"query": tv_id})
        results = data.get("results", [])
        if not results:
            click.echo(f"❌ TV show '{tv_id}' not found")
            return
        tv_id = str(results[0]["id"])
    
    data = api_get(f"/tv/{tv_id}")
    
    if cast:
        credits = api_get(f"/tv/{tv_id}/credits")
        data["cast"] = credits.get("cast", [])[:10]
    
    if json_output:
        click.echo(json.dumps(data, indent=2))
        return
    
    click.echo(format_tv(data, detailed=True))
    
    if cast and data.get("cast"):
        click.echo("\n   Cast:")
        for c in data["cast"]:
            click.echo(f"     • {c['name']} as {c.get('character', '?')}")


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=5, help="Max results")
def person(query: str, limit: int):
    """Search for actors, directors, etc."""
    data = api_get("/search/person", {"query": query})
    results = data.get("results", [])[:limit]
    
    if not results:
        click.echo(f"No people found matching '{query}'")
        return
    
    for p in results:
        known_for = p.get("known_for", [])[:3]
        titles = ", ".join(
            m.get("title") or m.get("name", "?") for m in known_for
        )
        click.echo(f"👤 **{p['name']}** ({p.get('known_for_department', '?')})")
        if titles:
            click.echo(f"   Known for: {titles}")
        click.echo()


@cli.command()
@click.argument("query")
@click.option("--region", "-r", default="US", help="Region code (US, GB, etc)")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def where(query: str, region: str, json_output: bool):
    """Find where to stream a movie or TV show."""
    # Search for the movie/TV first
    movie_data = api_get("/search/movie", {"query": query})
    tv_data = api_get("/search/tv", {"query": query})
    
    movie_results = movie_data.get("results", [])
    tv_results = tv_data.get("results", [])
    
    # Use movie if found, otherwise TV
    if movie_results:
        item = movie_results[0]
        media_type = "movie"
        title = item.get("title", "Unknown")
        item_id = item["id"]
    elif tv_results:
        item = tv_results[0]
        media_type = "tv"
        title = item.get("name", "Unknown")
        item_id = item["id"]
    else:
        click.echo(f"❌ '{query}' not found")
        return
    
    # Get watch providers
    providers = api_get(f"/{media_type}/{item_id}/watch/providers")
    region_data = providers.get("results", {}).get(region, {})
    
    if json_output:
        click.echo(json.dumps({"title": title, "id": item_id, "type": media_type, "providers": region_data}, indent=2))
        return
    
    click.echo(f"🎬 **{title}** - Streaming in {region}:\n")
    
    if not region_data:
        click.echo(f"   No streaming info available for {region}")
        return
    
    if region_data.get("flatrate"):
        click.echo("   📺 Streaming:")
        for p in region_data["flatrate"]:
            click.echo(f"      • {p['provider_name']}")
    
    if region_data.get("rent"):
        click.echo("   💵 Rent:")
        for p in region_data["rent"][:5]:
            click.echo(f"      • {p['provider_name']}")
    
    if region_data.get("buy"):
        click.echo("   🛒 Buy:")
        for p in region_data["buy"][:5]:
            click.echo(f"      • {p['provider_name']}")
    
    if region_data.get("link"):
        click.echo(f"\n   More info: {region_data['link']}")


@cli.command()
@click.option("--tv", is_flag=True, help="Trending TV instead of movies")
@click.option("--limit", "-l", default=10, help="Max results")
def trending(tv: bool, limit: int):
    """Show trending movies or TV shows."""
    media_type = "tv" if tv else "movie"
    data = api_get(f"/trending/{media_type}/week")
    results = data.get("results", [])[:limit]
    
    click.echo(f"🔥 Trending {'TV Shows' if tv else 'Movies'} This Week:\n")
    
    for i, item in enumerate(results, 1):
        if tv:
            year = item.get("first_air_date", "")[:4] or "?"
            click.echo(f"  {i}. {item.get('name', '?')} ({year}) ⭐{item.get('vote_average', 0):.1f}")
        else:
            year = item.get("release_date", "")[:4] or "?"
            click.echo(f"  {i}. {item.get('title', '?')} ({year}) ⭐{item.get('vote_average', 0):.1f}")


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Max results")
def recommend(query: str, limit: int):
    """Get recommendations based on a movie."""
    # Search for the movie first
    search_data = api_get("/search/movie", {"query": query})
    results = search_data.get("results", [])
    
    if not results:
        click.echo(f"❌ Movie '{query}' not found")
        return
    
    movie_id = results[0]["id"]
    title = results[0].get("title", "Unknown")
    
    # Get recommendations
    rec_data = api_get(f"/movie/{movie_id}/recommendations")
    recs = rec_data.get("results", [])[:limit]
    
    if not recs:
        click.echo(f"No recommendations found for '{title}'")
        return
    
    click.echo(f"🎯 If you liked **{title}**, try:\n")
    
    for r in recs:
        year = r.get("release_date", "")[:4] or "?"
        click.echo(f"  • {r.get('title', '?')} ({year}) ⭐{r.get('vote_average', 0):.1f}")


@cli.command()
@click.option("--genre", "-g", help="Genre name (action, comedy, sci-fi, etc)")
@click.option("--year", "-y", type=int, help="Release year")
@click.option("--rating", "-r", type=float, help="Minimum rating")
@click.option("--limit", "-l", default=10, help="Max results")
def discover(genre: str, year: int, rating: float, limit: int):
    """Discover movies with filters."""
    params = {"sort_by": "popularity.desc"}
    
    if genre:
        genre_id = GENRES.get(genre.lower())
        if not genre_id:
            click.echo(f"❌ Unknown genre '{genre}'. Try: {', '.join(GENRES.keys())}")
            return
        params["with_genres"] = genre_id
    
    if year:
        params["primary_release_year"] = year
    
    if rating:
        params["vote_average.gte"] = rating
        params["vote_count.gte"] = 100  # Ensure enough votes
    
    data = api_get("/discover/movie", params)
    results = data.get("results", [])[:limit]
    
    filters = []
    if genre:
        filters.append(genre.title())
    if year:
        filters.append(str(year))
    if rating:
        filters.append(f"≥{rating}⭐")
    
    click.echo(f"🔍 Discover: {' | '.join(filters) or 'Popular'}\n")
    
    for r in results:
        year_str = r.get("release_date", "")[:4] or "?"
        click.echo(f"  • {r.get('title', '?')} ({year_str}) ⭐{r.get('vote_average', 0):.1f}")


@cli.command()
@click.argument("user_id")
@click.option("--genres", help="Comma-separated favorite genres")
@click.option("--directors", help="Comma-separated favorite directors")
@click.option("--avoid", help="Comma-separated genres to avoid")
@click.option("--show", is_flag=True, help="Show current preferences")
def pref(user_id: str, genres: str, directors: str, avoid: str, show: bool):
    """Set or view user preferences."""
    prefs = load_json(PREFS_FILE)
    
    if user_id not in prefs:
        prefs[user_id] = {"genres": [], "directors": [], "avoid": [], "updated": None}
    
    if show:
        user_prefs = prefs.get(user_id, {})
        click.echo(f"Preferences for {user_id}:")
        click.echo(f"  Favorite genres: {', '.join(user_prefs.get('genres', [])) or 'None'}")
        click.echo(f"  Favorite directors: {', '.join(user_prefs.get('directors', [])) or 'None'}")
        click.echo(f"  Avoid genres: {', '.join(user_prefs.get('avoid', [])) or 'None'}")
        return
    
    if genres:
        prefs[user_id]["genres"] = [g.strip().lower() for g in genres.split(",")]
    if directors:
        prefs[user_id]["directors"] = [d.strip() for d in directors.split(",")]
    if avoid:
        prefs[user_id]["avoid"] = [a.strip().lower() for a in avoid.split(",")]
    
    prefs[user_id]["updated"] = datetime.now(timezone.utc).isoformat()
    save_json(PREFS_FILE, prefs)
    
    click.echo(f"✅ Preferences updated for {user_id}")
    
    # Try to save to ppl.gift if available
    try:
        ppl_note = f"🎬 MOVIE PREFS: genres={','.join(prefs[user_id].get('genres', []))}, avoid={','.join(prefs[user_id].get('avoid', []))}"
        # This would integrate with ppl skill if present
    except Exception:
        pass


@cli.command()
@click.argument("user_id")
@click.argument("action", required=False)
@click.argument("movie_ref", required=False)
def watchlist(user_id: str, action: str, movie_ref: str):
    """Manage user watchlist."""
    data = load_json(WATCHLIST_FILE)
    
    if user_id not in data:
        data[user_id] = []
    
    # View watchlist
    if not action:
        items = data.get(user_id, [])
        if not items:
            click.echo(f"Watchlist for {user_id} is empty")
            return
        
        click.echo(f"📋 Watchlist for {user_id} ({len(items)} items):\n")
        for item in items:
            click.echo(f"  [{item['id']}] {item['title']} ({item.get('year', '?')})")
        return
    
    # Add to watchlist
    if action == "add" and movie_ref:
        # Search if not numeric
        if not movie_ref.isdigit():
            search_data = api_get("/search/movie", {"query": movie_ref})
            results = search_data.get("results", [])
            if not results:
                click.echo(f"❌ Movie '{movie_ref}' not found")
                return
            movie_info = results[0]
        else:
            movie_info = api_get(f"/movie/{movie_ref}")
        
        movie_id = movie_info["id"]
        
        # Check if already in watchlist
        if any(m["id"] == movie_id for m in data[user_id]):
            click.echo(f"'{movie_info.get('title', '?')}' is already in your watchlist")
            return
        
        data[user_id].append({
            "id": movie_id,
            "title": movie_info.get("title", "Unknown"),
            "year": movie_info.get("release_date", "")[:4],
            "added": datetime.now(timezone.utc).isoformat(),
        })
        save_json(WATCHLIST_FILE, data)
        click.echo(f"✅ Added '{movie_info.get('title', '?')}' to watchlist")
        return
    
    # Remove from watchlist
    if action == "rm" and movie_ref:
        movie_id = int(movie_ref) if movie_ref.isdigit() else None
        original_len = len(data[user_id])
        
        if movie_id:
            data[user_id] = [m for m in data[user_id] if m["id"] != movie_id]
        else:
            data[user_id] = [m for m in data[user_id] if movie_ref.lower() not in m["title"].lower()]
        
        if len(data[user_id]) < original_len:
            save_json(WATCHLIST_FILE, data)
            click.echo(f"✅ Removed from watchlist")
        else:
            click.echo(f"❌ '{movie_ref}' not found in watchlist")
        return
    
    click.echo("Usage: watchlist <user> [add|rm] [movie]")


@cli.command()
@click.argument("user_id")
@click.option("--limit", "-l", default=10, help="Max suggestions")
def suggest(user_id: str, limit: int):
    """Get personalized movie suggestions."""
    prefs = load_json(PREFS_FILE).get(user_id, {})
    
    liked_genres = prefs.get("genres", [])
    avoid_genres = prefs.get("avoid", [])
    
    # Build discover params based on preferences
    params = {"sort_by": "popularity.desc", "vote_count.gte": 500}
    
    if liked_genres:
        genre_ids = [GENRES.get(g) for g in liked_genres if g in GENRES]
        if genre_ids:
            params["with_genres"] = ",".join(str(g) for g in genre_ids[:3])
    
    if avoid_genres:
        avoid_ids = [GENRES.get(g) for g in avoid_genres if g in GENRES]
        if avoid_ids:
            params["without_genres"] = ",".join(str(g) for g in avoid_ids)
    
    # Try to get Plex watch history for better recommendations
    plex_watched = []
    try:
        # Check if plex skill exists
        plex_skill = Path(__file__).parent.parent.parent / "plex"
        if plex_skill.exists():
            # Could integrate with Plex here for watch history
            pass
    except Exception:
        pass
    
    data = api_get("/discover/movie", params)
    results = data.get("results", [])[:limit]
    
    pref_desc = f" (based on: {', '.join(liked_genres)})" if liked_genres else ""
    click.echo(f"🎯 Suggestions for {user_id}{pref_desc}:\n")
    
    for r in results:
        year = r.get("release_date", "")[:4] or "?"
        genre_names = []
        for gid in r.get("genre_ids", [])[:2]:
            if gid in GENRE_NAMES:
                genre_names.append(GENRE_NAMES[gid].title())
        genres_str = f" [{', '.join(genre_names)}]" if genre_names else ""
        click.echo(f"  • {r.get('title', '?')} ({year}) ⭐{r.get('vote_average', 0):.1f}{genres_str}")


@cli.command()
@click.argument("query")
@click.option("--cast", is_flag=True, help="Include cast")
def info(query: str, cast: bool):
    """Search and show details for a movie or TV show."""
    # Try movie first
    movie_data = api_get("/search/movie", {"query": query})
    if movie_data.get("results"):
        movie_id = movie_data["results"][0]["id"]
        ctx = click.Context(movie)
        ctx.invoke(movie, movie_id=str(movie_id), cast=cast, json_output=False)
        return
    
    # Try TV
    tv_data = api_get("/search/tv", {"query": query})
    if tv_data.get("results"):
        tv_id = tv_data["results"][0]["id"]
        ctx = click.Context(tv)
        ctx.invoke(tv, tv_id=str(tv_id), cast=cast, json_output=False)
        return
    
    click.echo(f"❌ No movie or TV show found for '{query}'")


if __name__ == "__main__":
    cli()
