#!/usr/bin/env python3
"""
Fitbit Web API Wrapper with Auto-Refresh and Token Persistence

Usage:
    python fitbit_api.py activity --days 7
    python fitbit_api.py heartrate --days 7
    python fitbit_api.py sleep --days 7
    python fitbit_api.py report --type weekly
"""

import os
import sys
import json
import argparse
import base64
import stat
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SECRETS_PATH = Path.home() / ".config" / "systemd" / "user" / "secrets.conf"
TOKEN_CACHE_PATH = Path.home() / ".fitbit-analytics" / "tokens.json"


class FitbitClient:
    """Fitbit Web API client with auto-refresh and token persistence"""

    BASE_URL = "https://api.fitbit.com"
    TOKEN_REFRESH_THRESHOLD_HOURS = 1  # Refresh if expires within 1 hour

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        self.client_id = client_id or self._load_env_from_secrets("FITBIT_CLIENT_ID")
        self.client_secret = client_secret or self._load_env_from_secrets("FITBIT_CLIENT_SECRET")
        self._access_token = access_token or self._load_env_from_secrets("FITBIT_ACCESS_TOKEN")
        self._refresh_token = refresh_token or self._load_env_from_secrets("FITBIT_REFRESH_TOKEN")
        self._token_expires_at = None
        self._load_token_expiry()

        if not self._access_token:
            raise ValueError("FITBIT_ACCESS_TOKEN not set. Get tokens via OAuth flow.")

        self.headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

    def _load_env_from_secrets(self, key):
        """Load env var from secrets.conf if not already set"""
        if os.environ.get(key):
            return os.environ[key]
        if SECRETS_PATH.exists():
            for line in SECRETS_PATH.read_text().split('\n'):
                if '=' in line and key in line:
                    return line.split('=', 1)[1].strip().strip('"')
        return None

    def _load_token_expiry(self):
        """Load token expiry from cache file or JWT decode"""
        if TOKEN_CACHE_PATH.exists():
            try:
                data = json.loads(TOKEN_CACHE_PATH.read_text())
                expires_at = data.get("expires_at")
                if expires_at:
                    self._token_expires_at = datetime.fromisoformat(expires_at)
                    return
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: decode from JWT
        if self._access_token:
            self._decode_jwt_expiry()

    def _decode_jwt_expiry(self):
        """Decode access token JWT to get expiry timestamp"""
        try:
            payload = self._access_token.split('.')[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            data = json.loads(base64.b64decode(payload))
            exp = data.get("exp")
            if exp:
                self._token_expires_at = datetime.fromtimestamp(exp)
        except (IndexError, json.JSONDecodeError, TypeError):
            self._token_expires_at = None

    def _should_refresh(self):
        """Check if token should be refreshed"""
        if not self._token_expires_at:
            return True
        threshold = datetime.now() + timedelta(hours=self.TOKEN_REFRESH_THRESHOLD_HOURS)
        return self._token_expires_at < threshold

    def _save_tokens(self, access_token, refresh_token, expires_in):
        """Save tokens to secrets.conf and cache file"""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Update secrets.conf
        if SECRETS_PATH.exists():
            content = SECRETS_PATH.read_text()
            updates = {
                "FITBIT_ACCESS_TOKEN": access_token,
                "FITBIT_REFRESH_TOKEN": refresh_token
            }
            for key, value in updates.items():
                if f'{key}="' in content:
                    import re
                    pattern = rf'({key}=")([^"]*)(")'
                    content = re.sub(pattern, rf'\1{value}\3', content)
                else:
                    content += f'\n{key}="{value}"'
            SECRETS_PATH.write_text(content)
            os.chmod(str(SECRETS_PATH), stat.S_IRUSR | stat.S_IWUSR)

        # Save to cache file
        TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE_PATH.write_text(json.dumps({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": self._token_expires_at.isoformat()
        }, indent=2))
        os.chmod(str(TOKEN_CACHE_PATH), stat.S_IRUSR | stat.S_IWUSR)

    def _request(self, endpoint, date_type="date"):
        """Make API request with auto-refresh"""
        url = f"{self.BASE_URL}/{endpoint}"
        req = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401 and self._should_refresh():
                if self._refresh_access_token():
                    return self._request(endpoint, date_type)
            raise

    def _refresh_access_token(self):
        """Refresh access token and persist"""
        if not self.client_id or not self.client_secret or not self._refresh_token:
            return False

        auth_b64 = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token
        }).encode()

        req = urllib.request.Request(
            "https://api.fitbit.com/oauth2/token",
            data=data,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                tokens = json.loads(resp.read().decode("utf-8"))
                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")
                expires_in = tokens.get("expires_in", 28800)

                self._save_tokens(access_token, refresh_token, expires_in)
                self.headers["Authorization"] = f"Bearer {self._access_token}"
                return True
        except urllib.error.HTTPError as e:
            print(f"Token refresh failed: {e.code} {e.reason}", file=sys.stderr)
            return False

    def get_steps(self, start_date, end_date):
        """Fetch step data"""
        endpoint = f"1/user/-/activities/steps/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_calories(self, start_date, end_date):
        """Fetch calorie data"""
        endpoint = f"1/user/-/activities/calories/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_distance(self, start_date, end_date):
        """Fetch distance data"""
        endpoint = f"1/user/-/activities/distance/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_activity_summary(self, start_date, end_date):
        """Fetch activity summary"""
        endpoint = f"1/user/-/activities/date/{start_date}.json"
        return self._request(endpoint)

    def get_heartrate(self, start_date, end_date):
        """Fetch heart rate data"""
        endpoint = f"1/user/-/activities/heart/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_sleep(self, start_date, end_date):
        """Fetch sleep data (summary)"""
        endpoint = f"1.2/user/-/sleep/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_sleep_stages(self, start_date, end_date):
        """Fetch detailed sleep stages"""
        endpoint = f"1.3/user/-/sleep/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_spo2(self, start_date, end_date):
        """Fetch blood oxygen data"""
        endpoint = f"1/user/-/spo2/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_weight(self, start_date, end_date):
        """Fetch weight data"""
        endpoint = f"1/user/-/body/weight/date/{start_date}/{end_date}.json"
        return self._request(endpoint)

    def get_active_zone_minutes(self, start_date, end_date):
        """Fetch Active Zone Minutes (AZM) data
        
        Returns AZM breakdown:
        - activeZoneMinutes (total)
        - fatBurnActiveZoneMinutes (1× credit)
        - cardioActiveZoneMinutes (2× credit)
        - peakActiveZoneMinutes (2× credit)
        """
        # Calculate number of days between start and end
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        # Use period format: 1d, 7d, 30d, etc.
        period = f"{days}d" if days <= 30 else "30d"
        
        endpoint = f"1/user/-/activities/active-zone-minutes/date/{start_date}/{period}.json"
        return self._request(endpoint)


class FitbitAnalyzer:
    """Analyze Fitbit data"""

    def __init__(self, steps_data=None, hr_data=None, sleep_data=None, activity_data=None):
        self.steps = steps_data or []
        self.hr = hr_data or []
        self.sleep = sleep_data or []
        self.activity = activity_data or []

    def average_metric(self, data, key):
        """Calculate average of a metric"""
        if not data:
            return None
        # Convert to float to handle string values from API
        values = []
        for d in data:
            val = d.get(key)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue
        return sum(values) / len(values) if values else None

    def trend(self, data, key, days=7):
        """Calculate trend over N days"""
        if len(data) < 2:
            return 0
        recent = data[-days:]
        if len(recent) < 2:
            return 0
        try:
            first = float(recent[0].get(key, 0))
            last = float(recent[-1].get(key, 0))
            return last - first
        except (ValueError, TypeError):
            return 0

    def summary(self):
        """Generate summary"""
        steps_data = self.steps.get("activities-steps", []) if self.steps else []
        hr_data = self.hr.get("activities-heart", []) if self.hr else []

        avg_steps = self.average_metric(steps_data, "value")

        # Extract resting HR
        resting_hrs = []
        for day in hr_data:
            value = day.get("value", {})
            if isinstance(value, dict):
                resting_hrs.append(value.get("restingHeartRate"))
            else:
                resting_hrs.append(value)

        avg_rhr = sum([r for r in resting_hrs if r]) / len([r for r in resting_hrs if r]) if resting_hrs else None

        return {
            "avg_steps": avg_steps,
            "avg_resting_hr": avg_rhr,
            "steps_trend": self.trend(steps_data, "value"),
            "days_tracked": len(steps_data)
        }


class FitbitReporter:
    """Generate Fitbit reports"""

    def __init__(self, client):
        self.client = client

    def generate_report(self, report_type="weekly", days=None):
        """Generate report"""
        if not days:
            days = 7 if report_type == "weekly" else 30

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        steps = self.client.get_steps(start_date, end_date)
        hr = self.client.get_heartrate(start_date, end_date)
        sleep = self.client.get_sleep(start_date, end_date)

        analyzer = FitbitAnalyzer(steps, hr, sleep)
        summary = analyzer.summary()

        return {
            "report_type": report_type,
            "period": f"{start_date} to {end_date}",
            "summary": summary,
            "data": {
                "steps": steps,
                "heartrate": hr,
                "sleep": sleep
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Fitbit Analytics CLI")
    parser.add_argument("command", choices=["activity", "steps", "calories", "heartrate", "sleep", "report", "summary"],
                       help="Data type to fetch or report type")
    parser.add_argument("--days", type=int, default=7, help="Number of days")
    parser.add_argument("--type", default="weekly", help="Report type")
    parser.add_argument("--client-id", help="Fitbit client ID")
    parser.add_argument("--client-secret", help="Fitbit client secret")
    parser.add_argument("--access-token", help="Fitbit access token")

    args = parser.parse_args()

    try:
        client = FitbitClient(
            client_id=args.client_id,
            client_secret=args.client_secret,
            access_token=args.access_token
        )

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

        if args.command in ["activity", "steps"]:
            data = client.get_steps(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "calories":
            data = client.get_calories(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "heartrate":
            data = client.get_heartrate(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "sleep":
            data = client.get_sleep(start_date, end_date)
            print(json.dumps(data, indent=2))

        elif args.command == "summary":
            steps = client.get_steps(start_date, end_date)
            hr = client.get_heartrate(start_date, end_date)
            analyzer = FitbitAnalyzer(steps, hr)
            summary = analyzer.summary()
            print(json.dumps(summary, indent=2))

        elif args.command == "report":
            reporter = FitbitReporter(client)
            report = reporter.generate_report(args.type, args.days)
            print(json.dumps(report, indent=2))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Set FITBIT_ACCESS_TOKEN or use --access-token", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
