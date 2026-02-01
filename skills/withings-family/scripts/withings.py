#!/usr/bin/env python3
"""
Withings Health Data CLI
Supports multiple users with per-user token files.
"""

import os
import sys
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path.home() / '.clawdbot' / 'withings-family'

# Load .env if present
env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip().strip('"\'')

CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID')
CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:18081'


def get_token_file(user_id='default'):
    """Get token file path for a user."""
    return BASE_DIR / f'tokens-{user_id}.json'


def save_tokens(data, user_id='default'):
    """Save tokens with expiry calculation."""
    expiry = time.time() + data['expires_in']
    payload = {**data, 'expiry_date': expiry}
    get_token_file(user_id).write_text(json.dumps(payload, indent=2))
    return payload


def post_request(endpoint, params):
    """Make a POST request to Withings API."""
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        f'https://wbsapi.withings.net{endpoint}',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        if result['status'] != 0:
            raise Exception(f"API Error: {result['status']} - {result}")
        return result.get('body', result)


def get_valid_token(user_id='default'):
    """Get a valid access token, refreshing if needed."""
    token_file = get_token_file(user_id)
    
    if not token_file.exists():
        raise Exception(f"No token found for '{user_id}'. Run: python3 withings.py {user_id} auth")
    
    tokens = json.loads(token_file.read_text())
    
    # Fix expiry if it's in milliseconds instead of seconds
    if tokens['expiry_date'] > time.time() * 1000:
        tokens['expiry_date'] = tokens['expiry_date'] / 1000
        token_file.write_text(json.dumps(tokens, indent=2))
    
    # Refresh if expiring in less than 60 seconds
    if time.time() > (tokens['expiry_date'] - 60):
        print("Token expired, refreshing...", file=sys.stderr)
        new_tokens = post_request('/v2/oauth2', {
            'action': 'requesttoken',
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': tokens['refresh_token']
        })
        tokens = save_tokens(new_tokens, user_id)
    
    return tokens['access_token']


def auth(user_id, code=None):
    """Handle OAuth flow."""
    if not code:
        params = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': 'user.metrics,user.activity',
            'state': 'init'
        }
        url = f"https://account.withings.com/oauth2_user/authorize2?{urllib.parse.urlencode(params)}"
        
        print("\n=== AUTHENTICATION REQUIRED ===")
        print(f"User: {user_id}")
        print("1. Open this link in your browser:")
        print(url)
        print("\n2. After login, you'll be redirected to an error page (this is normal).")
        print("3. Copy the code from the URL (e.g., ?code=my_code&...)")
        print(f"4. Run: python3 withings.py {user_id} auth YOUR_CODE_HERE\n")
        return
    
    tokens = post_request('/v2/oauth2', {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    })
    
    save_tokens(tokens, user_id)
    print(f"Authentication successful for '{user_id}'! Tokens saved.")


def get_weight(user_id='default'):
    """Fetch recent weight measurements."""
    token = get_valid_token(user_id)
    data = post_request('/measure', {
        'action': 'getmeas',
        'access_token': token,
        'meastype': 1,  # Weight
        'category': 1
    })
    
    measures = []
    for grp in data['measuregrps']:
        date = datetime.fromtimestamp(grp['date']).isoformat()
        meas = next((m for m in grp['measures'] if m['type'] == 1), None)
        if meas:
            weight = meas['value'] * (10 ** meas['unit'])
            measures.append({
                'date': date,
                'weight': f"{weight:.2f} kg"
            })
    
    print(json.dumps(measures[:5], indent=2))


def get_body(user_id='default', limit=None):
    """Fetch body composition data."""
    token = get_valid_token(user_id)
    data = post_request('/measure', {
        'action': 'getmeas',
        'access_token': token,
        'category': 1
    })
    
    measure_types = {
        1: ('weight', 'kg', 2),
        4: ('height', 'm', 2),
        6: ('fat_percent', '%', 1),
        8: ('fat_mass', 'kg', 2),
        76: ('muscle_mass', 'kg', 2),
        77: ('hydration', '%', 1),
        88: ('bone_mass', 'kg', 2)
    }
    
    measures = []
    for grp in data['measuregrps']:
        date = datetime.fromtimestamp(grp['date']).isoformat()
        result = {'date': date}
        
        for meas in grp['measures']:
            if meas['type'] in measure_types:
                name, unit, decimals = measure_types[meas['type']]
                value = meas['value'] * (10 ** meas['unit'])
                result[name] = f"{value:.{decimals}f} {unit}"
        
        if len(result) > 1:
            measures.append(result)
    
    # Apply limit if specified (default None = all)
    if limit:
        measures = measures[:limit]
    
    print(json.dumps(measures, indent=2))


def get_activity(user_id='default', days=7):
    """Fetch activity data."""
    token = get_valid_token(user_id)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = post_request('/v2/measure', {
        'action': 'getactivity',
        'access_token': token,
        'startdateymd': start_date.strftime('%Y-%m-%d'),
        'enddateymd': end_date.strftime('%Y-%m-%d')
    })
    
    if not data.get('activities'):
        print("[]")
        return
    
    activities = []
    for a in data['activities']:
        activities.append({
            'date': a['date'],
            'steps': a.get('steps', 0),
            'distance': f"{(a.get('distance', 0) / 1000):.2f} km",
            'calories': a.get('calories', 0),
            'active_calories': a.get('active_calories', 0),
            'soft_activity': f"{a.get('soft', 0)} min",
            'moderate_activity': f"{a.get('moderate', 0)} min",
            'intense_activity': f"{a.get('intense', 0)} min"
        })
    
    print(json.dumps(list(reversed(activities)), indent=2))


def get_sleep(user_id='default', days=7):
    """Fetch sleep data."""
    token = get_valid_token(user_id)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = post_request('/v2/sleep', {
        'action': 'getsummary',
        'access_token': token,
        'startdateymd': start_date.strftime('%Y-%m-%d'),
        'enddateymd': end_date.strftime('%Y-%m-%d')
    })
    
    if not data.get('series'):
        print("[]")
        return
    
    def format_duration(seconds):
        if not seconds:
            return '0min'
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}min" if h > 0 else f"{m}min"
    
    def format_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M')
    
    sleep_data = []
    for s in data['series']:
        d = s.get('data', {})
        sleep_data.append({
            'date': s['date'],
            'start': format_time(s['startdate']),
            'end': format_time(s['enddate']),
            'duration': format_duration(d.get('total_sleep_time') or d.get('durationtosleep', 0)),
            'deep_sleep': format_duration(d.get('deepsleepduration', 0)),
            'light_sleep': format_duration(d.get('lightsleepduration', 0)),
            'rem_sleep': format_duration(d.get('remsleepduration', 0)),
            'awake': format_duration(d.get('wakeupduration', 0)),
            'sleep_score': d.get('sleep_score')
        })
    
    print(json.dumps(list(reversed(sleep_data)), indent=2))


def main():
    args = sys.argv[1:]
    
    # Parse: [userId] <command> [params...]
    valid_commands = ['auth', 'weight', 'body', 'activity', 'sleep']
    
    user_id = 'default'
    command = args[0] if args else None
    params = args[1:] if args else []
    
    # If first arg is not a command, treat it as userId
    if len(args) > 1 and args[0] not in valid_commands:
        user_id = args[0]
        command = args[1]
        params = args[2:]
    
    if command == 'auth':
        auth(user_id, params[0] if params else None)
    elif command == 'weight':
        get_weight(user_id)
    elif command == 'body':
        limit = int(params[0]) if params and params[0] != 'all' else None
        get_body(user_id, limit)
    elif command == 'activity':
        days = int(params[0]) if params else 7
        get_activity(user_id, days)
    elif command == 'sleep':
        days = int(params[0]) if params else 7
        get_sleep(user_id, days)
    else:
        print("Usage: python3 withings.py [userId] <command> [params]")
        print("Commands: auth [code], weight, body [limit|all], activity [days], sleep [days]")
        print("\nExamples:")
        print("  python3 withings.py alice auth")
        print("  python3 withings.py alice auth CODE_HERE")
        print("  python3 withings.py bob weight")
        print("  python3 withings.py charlie body all")
        print("  python3 withings.py alice activity 30")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
