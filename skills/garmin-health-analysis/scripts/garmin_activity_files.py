#!/usr/bin/env python3
"""
Download and analyze Garmin activity FIT/GPX files.
Extract GPS, elevation, pace, heart rate, power, cadence, etc.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from garmin_auth import get_client

# Check for optional dependencies
try:
    import fitparse
    HAS_FITPARSE = True
except ImportError:
    HAS_FITPARSE = False

try:
    import gpxpy
    import gpxpy.gpx
    HAS_GPXPY = True
except ImportError:
    HAS_GPXPY = False


def download_activity_file(client, activity_id, file_format="fit", output_dir="/tmp"):
    """Download activity FIT or GPX file."""
    try:
        output_path = f"{output_dir}/activity_{activity_id}.{file_format.lower()}"
        
        if file_format.lower() == "fit":
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
        elif file_format.lower() == "gpx":
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.GPX)
        elif file_format.lower() == "tcx":
            data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.TCX)
        else:
            return {"error": f"Unsupported format: {file_format}"}
        
        with open(output_path, 'wb') as f:
            f.write(data)
        
        return {"file": output_path, "activity_id": activity_id, "format": file_format}
    
    except Exception as e:
        return {"error": str(e), "activity_id": activity_id}


def parse_fit_file(file_path):
    """Parse FIT file and extract all data points."""
    if not HAS_FITPARSE:
        return {"error": "fitparse library not installed. Run: pip install fitparse"}
    
    try:
        fitfile = fitparse.FitFile(file_path)
        
        # Extract different record types
        records = []
        laps = []
        sessions = []
        
        for record in fitfile.get_messages('record'):
            data_point = {}
            for field in record:
                if field.value is not None:
                    data_point[field.name] = field.value
            if data_point:
                records.append(data_point)
        
        for record in fitfile.get_messages('lap'):
            lap_data = {}
            for field in record:
                if field.value is not None:
                    lap_data[field.name] = field.value
            if lap_data:
                laps.append(lap_data)
        
        for record in fitfile.get_messages('session'):
            session_data = {}
            for field in record:
                if field.value is not None:
                    session_data[field.name] = field.value
            if session_data:
                sessions.append(session_data)
        
        return {
            "records": records,
            "laps": laps,
            "sessions": sessions,
            "total_records": len(records)
        }
    
    except Exception as e:
        return {"error": str(e)}


def parse_gpx_file(file_path):
    """Parse GPX file and extract track points."""
    if not HAS_GPXPY:
        return {"error": "gpxpy library not installed. Run: pip install gpxpy"}
    
    try:
        with open(file_path, 'r') as f:
            gpx = gpxpy.parse(f)
        
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append({
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation,
                        "time": point.time.isoformat() if point.time else None,
                        "speed": point.speed,
                        "hr": point.extensions.get("hr") if point.extensions else None
                    })
        
        return {
            "points": points,
            "total_points": len(points),
            "bounds": {
                "min_lat": gpx.get_bounds().min_latitude,
                "max_lat": gpx.get_bounds().max_latitude,
                "min_lon": gpx.get_bounds().min_longitude,
                "max_lon": gpx.get_bounds().max_longitude
            } if gpx.get_bounds() else None
        }
    
    except Exception as e:
        return {"error": str(e)}


def query_data_at_distance(data, distance_meters):
    """Find data point closest to a specific distance."""
    if "records" in data:
        records = data["records"]
    elif "points" in data:
        records = data["points"]
    else:
        return {"error": "No data records found"}
    
    # Find closest by distance
    closest = None
    min_diff = float('inf')
    
    for record in records:
        if "distance" in record:
            diff = abs(record["distance"] - distance_meters)
            if diff < min_diff:
                min_diff = diff
                closest = record
    
    return closest


def query_data_at_time(data, target_time):
    """Find data point at a specific time."""
    if "records" in data:
        records = data["records"]
    elif "points" in data:
        records = data["points"]
    else:
        return {"error": "No data records found"}
    
    # Parse target time
    if isinstance(target_time, str):
        try:
            target_dt = datetime.fromisoformat(target_time.replace("Z", "+00:00"))
        except:
            return {"error": f"Invalid time format: {target_time}"}
    else:
        target_dt = target_time
    
    target_ts = target_dt.timestamp()
    
    closest = None
    min_diff = float('inf')
    
    for record in records:
        if "timestamp" in record:
            if isinstance(record["timestamp"], datetime):
                rec_ts = record["timestamp"].timestamp()
            else:
                continue
            
            diff = abs(rec_ts - target_ts)
            if diff < min_diff:
                min_diff = diff
                closest = record
    
    return closest


def analyze_activity(data):
    """Analyze activity data and provide insights."""
    if "error" in data:
        return data
    
    records = data.get("records", [])
    if not records:
        return {"error": "No data records to analyze"}
    
    # Calculate statistics
    hr_values = [r.get("heart_rate") for r in records if r.get("heart_rate")]
    elevation_values = [r.get("altitude") or r.get("elevation") for r in records if r.get("altitude") or r.get("elevation")]
    speed_values = [r.get("speed") for r in records if r.get("speed")]
    cadence_values = [r.get("cadence") for r in records if r.get("cadence")]
    power_values = [r.get("power") for r in records if r.get("power")]
    
    analysis = {
        "total_points": len(records),
        "duration_seconds": None,
        "distance_meters": None,
        "heart_rate": {
            "avg": sum(hr_values) / len(hr_values) if hr_values else None,
            "max": max(hr_values) if hr_values else None,
            "min": min(hr_values) if hr_values else None
        },
        "elevation": {
            "max": max(elevation_values) if elevation_values else None,
            "min": min(elevation_values) if elevation_values else None,
            "gain": None  # Would need to calculate from sequential points
        },
        "speed": {
            "avg": sum(speed_values) / len(speed_values) if speed_values else None,
            "max": max(speed_values) if speed_values else None
        },
        "cadence": {
            "avg": sum(cadence_values) / len(cadence_values) if cadence_values else None
        } if cadence_values else None,
        "power": {
            "avg": sum(power_values) / len(power_values) if power_values else None,
            "max": max(power_values) if power_values else None
        } if power_values else None
    }
    
    # Get duration and distance from first/last records
    if records:
        if "timestamp" in records[0] and "timestamp" in records[-1]:
            if isinstance(records[0]["timestamp"], datetime):
                duration = (records[-1]["timestamp"] - records[0]["timestamp"]).total_seconds()
                analysis["duration_seconds"] = duration
        
        if "distance" in records[-1]:
            analysis["distance_meters"] = records[-1]["distance"]
    
    return analysis


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Garmin activity files")
    parser.add_argument("action", choices=["download", "parse", "query", "analyze"],
                       help="Action to perform")
    parser.add_argument("--activity-id", type=int, help="Activity ID")
    parser.add_argument("--format", choices=["fit", "gpx", "tcx"], default="fit",
                       help="File format for download")
    parser.add_argument("--file", help="Path to local FIT/GPX file")
    parser.add_argument("--distance", type=float, help="Query data at distance (meters)")
    parser.add_argument("--time", help="Query data at time (ISO format)")
    parser.add_argument("--output-dir", default="/tmp", help="Output directory")
    
    args = parser.parse_args()
    
    if args.action == "download":
        if not args.activity_id:
            print('{"error": "activity-id required for download"}')
            sys.exit(1)
        
        client = get_client()
        if not client:
            print('{"error": "Not authenticated"}')
            sys.exit(1)
        
        result = download_activity_file(client, args.activity_id, args.format, args.output_dir)
        print(json.dumps(result, indent=2))
    
    elif args.action == "parse":
        if not args.file:
            print('{"error": "file path required for parse"}')
            sys.exit(1)
        
        if args.file.endswith('.fit'):
            result = parse_fit_file(args.file)
        elif args.file.endswith('.gpx'):
            result = parse_gpx_file(args.file)
        else:
            result = {"error": "Unsupported file type. Use .fit or .gpx"}
        
        print(json.dumps(result, indent=2, default=str))
    
    elif args.action == "query":
        if not args.file:
            print('{"error": "file path required for query"}')
            sys.exit(1)
        
        # First parse the file
        if args.file.endswith('.fit'):
            data = parse_fit_file(args.file)
        elif args.file.endswith('.gpx'):
            data = parse_gpx_file(args.file)
        else:
            print('{"error": "Unsupported file type"}')
            sys.exit(1)
        
        if "error" in data:
            print(json.dumps(data, indent=2))
            sys.exit(1)
        
        # Query
        if args.distance is not None:
            result = query_data_at_distance(data, args.distance)
        elif args.time:
            result = query_data_at_time(data, args.time)
        else:
            result = {"error": "Specify --distance or --time for query"}
        
        print(json.dumps(result, indent=2, default=str))
    
    elif args.action == "analyze":
        if not args.file:
            print('{"error": "file path required for analyze"}')
            sys.exit(1)
        
        # Parse and analyze
        if args.file.endswith('.fit'):
            data = parse_fit_file(args.file)
        elif args.file.endswith('.gpx'):
            data = parse_gpx_file(args.file)
        else:
            print('{"error": "Unsupported file type"}')
            sys.exit(1)
        
        result = analyze_activity(data)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
