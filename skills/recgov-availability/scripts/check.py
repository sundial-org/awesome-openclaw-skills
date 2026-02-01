#!/usr/bin/env python3
"""
Check campsite availability on recreation.gov for given campground(s) and dates.

Usage:
    python check.py --campground 232448 --start 2026-07-10 --nights 2
    python check.py -c 232448 232450 --start 2026-07-10 --nights 2 --type tent
    python check.py -c 232448 --start 2026-07-10 --nights 2 --electric --pets
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

BASE_URL = "https://www.recreation.gov"
AVAILABILITY_URL = BASE_URL + "/api/camps/availability/campground/{campground_id}/month"
CAMPGROUND_URL = BASE_URL + "/api/camps/campgrounds/{campground_id}"
CAMPSITE_URL = BASE_URL + "/api/camps/campsites/{campsite_id}"

# Campsite type keywords for filtering
TYPE_KEYWORDS = {
    "tent": ["TENT"],
    "rv": ["RV", "TRAILER"],
    "standard": ["STANDARD"],
    "cabin": ["CABIN"],
    "group": ["GROUP"],
    "electric": ["ELECTRIC"],
    "nonelectric": ["NONELECTRIC"],
}

# Availability statuses
STATUS_AVAILABLE = "Available"
STATUS_RESERVED = "Reserved"
STATUS_NYR = "NYR"  # Not Yet Released
STATUS_OPEN = "Open"  # First-come-first-served, not reservable
STATUS_NOT_RESERVABLE = "Not Reservable"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) recgov-checker/1.0"
}


def fetch_json(url: str, params: dict = None) -> dict:
    """Fetch JSON from URL with optional query params."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_campground_name(campground_id: str) -> str:
    """Get campground name from ID."""
    try:
        data = fetch_json(CAMPGROUND_URL.format(campground_id=campground_id))
        return data.get("campground", {}).get("facility_name", f"Campground {campground_id}")
    except Exception:
        return f"Campground {campground_id}"


def get_availability(campground_id: str, start_date: datetime, end_date: datetime) -> dict:
    """
    Get campsite availability for a campground.
    Returns dict of campsite_id -> campsite data with availability.
    """
    # Get each month's data
    all_campsites = {}
    current = datetime(start_date.year, start_date.month, 1)
    
    while current <= end_date:
        month_str = current.strftime("%Y-%m-01T00:00:00.000Z")
        url = AVAILABILITY_URL.format(campground_id=campground_id)
        
        try:
            data = fetch_json(url, {"start_date": month_str})
            for site_id, site_data in data.get("campsites", {}).items():
                if site_id not in all_campsites:
                    all_campsites[site_id] = site_data
                else:
                    # Merge availabilities
                    all_campsites[site_id]["availabilities"].update(
                        site_data.get("availabilities", {})
                    )
        except Exception as e:
            print(f"Warning: Failed to fetch month {current.strftime('%Y-%m')}: {e}", file=sys.stderr)
        
        # Move to next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    
    return all_campsites


def get_campsite_details(campsite_id: str) -> dict:
    """Get detailed campsite info including amenities."""
    try:
        data = fetch_json(CAMPSITE_URL.format(campsite_id=campsite_id))
        return data.get("campsite", {})
    except Exception:
        return {}


def check_consecutive_availability(
    availabilities: dict,
    start_date: datetime,
    nights: int,
) -> list[tuple[str, str]]:
    """
    Check for consecutive available nights.
    Returns list of (start_date, end_date) tuples for valid ranges.
    """
    valid_ranges = []
    end_date = start_date + timedelta(days=nights)
    
    # Check each possible start date in the range
    check_date = start_date
    while check_date + timedelta(days=nights) <= end_date + timedelta(days=30):  # Look ahead
        dates_to_check = [
            (check_date + timedelta(days=i)).strftime("%Y-%m-%dT00:00:00Z")
            for i in range(nights)
        ]
        
        all_available = all(
            availabilities.get(d) == STATUS_AVAILABLE
            for d in dates_to_check
        )
        
        if all_available:
            range_start = check_date.strftime("%Y-%m-%d")
            range_end = (check_date + timedelta(days=nights)).strftime("%Y-%m-%d")
            valid_ranges.append((range_start, range_end))
        
        check_date += timedelta(days=1)
        
        # Don't look too far ahead
        if check_date > start_date + timedelta(days=60):
            break
    
    return valid_ranges


def analyze_campground_status(campsites: dict, start_date: datetime, nights: int) -> dict:
    """
    Analyze why sites might not be available.
    Returns dict with counts of different statuses for the requested dates.
    
    Key insight: recreation.gov uses a rolling booking window (typically 6 months).
    - Dates outside the window show as "Open" (near-term) or "NYR" (far-term)
    - If a campground has ANY "NYR" or "Reserved" dates, it's reservable (not FCFS)
    - True FCFS campgrounds show "Open" or "Not Reservable" for ALL dates
    """
    dates_to_check = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%dT00:00:00Z")
        for i in range(nights)
    ]
    
    status_counts = {
        "available": 0,
        "reserved": 0,
        "nyr": 0,  # Not Yet Released
        "fcfs": 0,  # First-come-first-served (Open/Not Reservable)
        "not_yet_bookable": 0,  # Reservable campground, but dates not open yet
        "other": 0,
    }
    
    # First pass: check if this is a reservable campground (has ANY NYR or Reserved dates)
    campground_has_nyr_or_reserved = False
    for site_data in campsites.values():
        avails = site_data.get("availabilities", {})
        all_statuses = set(avails.values())
        if STATUS_NYR in all_statuses or STATUS_RESERVED in all_statuses or STATUS_AVAILABLE in all_statuses:
            campground_has_nyr_or_reserved = True
            break
    
    for site_data in campsites.values():
        avails = site_data.get("availabilities", {})
        site_statuses = [avails.get(d, "Unknown") for d in dates_to_check]
        
        # Check status for all requested nights
        if all(s == STATUS_AVAILABLE for s in site_statuses):
            status_counts["available"] += 1
        elif all(s == STATUS_NYR for s in site_statuses):
            status_counts["nyr"] += 1
        elif all(s in (STATUS_OPEN, STATUS_NOT_RESERVABLE) for s in site_statuses):
            # Is this true FCFS or just outside the booking window?
            if campground_has_nyr_or_reserved:
                status_counts["not_yet_bookable"] += 1
            else:
                status_counts["fcfs"] += 1
        elif any(s == STATUS_RESERVED for s in site_statuses):
            status_counts["reserved"] += 1
        else:
            status_counts["other"] += 1
    
    return status_counts


def is_group_site(site_data: dict) -> bool:
    """Check if a campsite is a group site."""
    site_type = site_data.get("campsite_type", "").upper()
    site_name = site_data.get("site", "").upper()
    
    return "GROUP" in site_type or site_name in ("GRP", "GROUP")


def matches_type_filter(campsite_type: str, type_filter: str) -> bool:
    """Check if campsite type matches the filter."""
    if not type_filter:
        return True
    
    type_filter = type_filter.lower()
    campsite_type = campsite_type.upper()
    
    # Handle combined filters like "tent-electric" or "rv-nonelectric"
    filters = type_filter.replace("-", " ").replace("_", " ").split()
    
    for f in filters:
        keywords = TYPE_KEYWORDS.get(f, [f.upper()])
        if not any(kw in campsite_type for kw in keywords):
            return False
    
    return True


def matches_amenity_filters(details: dict, filters: dict) -> bool:
    """Check if campsite details match amenity filters."""
    if not filters:
        return True
    
    site_details = details.get("site_details_map", {})
    amenities = {a.get("attribute_code"): a.get("attribute_value") for a in details.get("amenities", [])}
    attributes = {a.get("attribute_code"): a.get("attribute_value") for a in details.get("attributes", [])}
    equipment = details.get("equipment_details_map", {})
    
    # Merge all attributes
    all_attrs = {**amenities, **attributes}
    for k, v in site_details.items():
        if isinstance(v, dict):
            all_attrs[k] = v.get("attribute_value")
        else:
            all_attrs[k] = v
    for k, v in equipment.items():
        if isinstance(v, dict):
            all_attrs[k] = v.get("attribute_value")
    
    # Check each filter
    if filters.get("pets") and all_attrs.get("pets_allowed", "").lower() not in ["yes", "y", "true"]:
        return False
    
    if filters.get("shade") and all_attrs.get("shade", "").lower() not in ["full", "partial"]:
        return False
    
    if filters.get("fire_pit") and all_attrs.get("fire_pit", "").upper() != "Y":
        return False
    
    if filters.get("campfire") and all_attrs.get("campfire_allowed", "").lower() not in ["yes", "y", "true"]:
        return False
    
    # Vehicle length filter
    max_len = filters.get("min_vehicle_length")
    if max_len:
        site_max = int(all_attrs.get("max_vehicle_length", 0) or 0)
        if site_max < max_len:
            return False
    
    return True


def format_results(results: list, json_output: bool = False) -> str:
    """Format availability results for output."""
    if json_output:
        return json.dumps(results, indent=2)
    
    if not results:
        return "❌ No campsites found matching your criteria."
    
    lines = []
    for cg in results:
        status = cg.get("status", {})
        available = cg['available_count']
        total = cg['total_count']
        
        lines.append(f"\n🏕️  {cg['campground_name']} ({cg['campground_id']})")
        
        # Determine the primary status message
        nyr = status.get("nyr", 0)
        fcfs = status.get("fcfs", 0)
        not_yet_bookable = status.get("not_yet_bookable", 0)
        reserved = status.get("reserved", 0)
        
        if status.get("nyr", 0) == total and total > 0:
            # All sites are Not Yet Released
            lines.append(f"   ⏳ NOT YET RELEASED — Reservations not open for these dates")
        elif (nyr + not_yet_bookable) == total and total > 0:
            # Reservable campground but dates not open yet
            lines.append(f"   ⏳ NOT YET BOOKABLE — Check back when 6-month window opens")
        elif status.get("fcfs", 0) == total and total > 0:
            # All sites are first-come-first-served
            lines.append(f"   🚗 FIRST-COME-FIRST-SERVED — No reservations, show up early")
        elif available > 0:
            lines.append(f"   ✅ {available} site(s) available out of {total}")
        else:
            # Break down why nothing is available
            if reserved > 0 and (nyr + not_yet_bookable) > 0:
                lines.append(f"   ❌ SOLD OUT — {reserved} reserved, {nyr + not_yet_bookable} not yet bookable")
            elif (nyr + not_yet_bookable) > 0:
                lines.append(f"   ⏳ {nyr + not_yet_bookable}/{total} sites not yet bookable for these dates")
            elif fcfs > 0:
                lines.append(f"   🚗 {fcfs}/{total} sites are first-come-first-served (not reservable)")
            elif reserved > 0:
                lines.append(f"   ❌ SOLD OUT — All {reserved} reservable sites are booked")
            else:
                lines.append(f"   ❌ 0 site(s) available out of {total}")
        
        lines.append(f"   🔗 {cg['url']}")
        
        if cg.get("sites"):
            for site in cg["sites"][:10]:  # Limit to first 10
                site_name = site.get("name", site.get("id"))
                site_type = site.get("type", "Unknown")
                lines.append(f"\n   📍 Site {site_name} ({site_type})")
                for start, end in site.get("available_ranges", [])[:3]:
                    lines.append(f"      ✅ {start} → {end}")
            
            if len(cg["sites"]) > 10:
                lines.append(f"\n   ... and {len(cg['sites']) - 10} more sites")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check campsite availability on recreation.gov"
    )
    parser.add_argument(
        "--campground", "-c",
        nargs="+",
        required=True,
        help="Campground ID(s) to check"
    )
    parser.add_argument(
        "--start", "-s",
        required=True,
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--nights", "-n",
        type=int,
        default=1,
        help="Number of consecutive nights needed (default: 1)"
    )
    parser.add_argument(
        "--type", "-t",
        help="Filter by site type (tent, rv, standard, electric, nonelectric, cabin, group)"
    )
    parser.add_argument(
        "--electric",
        action="store_true",
        help="Filter to electric sites only"
    )
    parser.add_argument(
        "--nonelectric",
        action="store_true",
        help="Filter to non-electric sites only"
    )
    parser.add_argument(
        "--include-group",
        action="store_true",
        help="Include group sites (excluded by default)"
    )
    parser.add_argument(
        "--pets",
        action="store_true",
        help="Filter to pet-friendly sites (requires detail lookup)"
    )
    parser.add_argument(
        "--shade",
        action="store_true",
        help="Filter to shaded sites (requires detail lookup)"
    )
    parser.add_argument(
        "--fire-pit",
        action="store_true",
        help="Filter to sites with fire pits (requires detail lookup)"
    )
    parser.add_argument(
        "--vehicle-length",
        type=int,
        help="Minimum vehicle length in feet (requires detail lookup)"
    )
    parser.add_argument(
        "--show-sites",
        action="store_true",
        help="Show individual site details"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Parse start date
    try:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
    
    end_date = start_date + timedelta(days=args.nights)
    
    # Build type filter
    type_filter = args.type or ""
    if args.electric:
        type_filter = (type_filter + " electric").strip()
    if args.nonelectric:
        type_filter = (type_filter + " nonelectric").strip()
    
    # Build amenity filters
    amenity_filters = {}
    if args.pets:
        amenity_filters["pets"] = True
    if args.shade:
        amenity_filters["shade"] = True
    if args.fire_pit:
        amenity_filters["fire_pit"] = True
    if args.vehicle_length:
        amenity_filters["min_vehicle_length"] = args.vehicle_length
    
    need_details = bool(amenity_filters)
    
    results = []
    
    for campground_id in args.campground:
        campground_name = get_campground_name(campground_id)
        
        if not args.json:
            print(f"Checking {campground_name}...", file=sys.stderr)
        
        campsites = get_availability(campground_id, start_date, end_date)
        
        # Filter out group sites unless requested
        if not args.include_group:
            campsites = {
                site_id: site_data 
                for site_id, site_data in campsites.items() 
                if not is_group_site(site_data)
            }
        
        # Analyze campground status (NYR, FCFS, etc.)
        status_analysis = analyze_campground_status(campsites, start_date, args.nights)
        
        available_sites = []
        
        for site_id, site_data in campsites.items():
            site_type = site_data.get("campsite_type", "")
            
            # Fast filter by type
            if not matches_type_filter(site_type, type_filter):
                continue
            
            # Check availability
            avail_ranges = check_consecutive_availability(
                site_data.get("availabilities", {}),
                start_date,
                args.nights,
            )
            
            if not avail_ranges:
                continue
            
            # If we need detailed amenity filtering
            if need_details:
                details = get_campsite_details(site_id)
                if not matches_amenity_filters(details, amenity_filters):
                    continue
            
            available_sites.append({
                "id": site_id,
                "name": site_data.get("site", site_id),
                "type": site_type,
                "loop": site_data.get("loop", ""),
                "available_ranges": avail_ranges,
            })
        
        result = {
            "campground_id": campground_id,
            "campground_name": campground_name,
            "url": f"https://www.recreation.gov/camping/campgrounds/{campground_id}",
            "total_count": len(campsites),
            "available_count": len(available_sites),
            "status": status_analysis,
        }
        
        if args.show_sites or args.json:
            result["sites"] = available_sites
        
        results.append(result)
    
    print(format_results(results, args.json))


if __name__ == "__main__":
    main()
