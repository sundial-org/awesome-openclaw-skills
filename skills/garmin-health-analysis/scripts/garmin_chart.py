#!/usr/bin/env python3
"""
Generate interactive HTML charts from Garmin health data.
Uses Chart.js for visualizations.
"""

import json
import sys
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

# Import auth and data helpers
sys.path.insert(0, str(Path(__file__).parent))
from garmin_auth import get_client
from garmin_data import fetch_sleep, fetch_hrv, fetch_body_battery, fetch_heart_rate, fetch_activities, fetch_stress


def generate_html(charts_data, title="Garmin Health Dashboard"):
    """Generate HTML with Chart.js visualizations."""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }}
        .chart-container {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .chart-title {{
            font-size: 1.3rem;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }}
        canvas {{
            max-height: 400px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.6;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="stats-grid" id="stats"></div>
        
        <div class="charts-grid" id="charts"></div>
        
        <div class="footer">
            Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
    
    <script>
        Chart.defaults.color = '#fff';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        
        const chartsData = {json.dumps(charts_data)};
        
        // Render stats cards
        function renderStats(stats) {{
            const container = document.getElementById('stats');
            for (const [label, value] of Object.entries(stats)) {{
                const card = document.createElement('div');
                card.className = 'stat-card';
                card.innerHTML = `
                    <div class="stat-label">${{label}}</div>
                    <div class="stat-value">${{value}}</div>
                `;
                container.appendChild(card);
            }}
        }}
        
        // Render chart
        function renderChart(config) {{
            const container = document.createElement('div');
            container.className = 'chart-container';
            
            const title = document.createElement('div');
            title.className = 'chart-title';
            title.textContent = config.title;
            container.appendChild(title);
            
            const canvas = document.createElement('canvas');
            container.appendChild(canvas);
            
            document.getElementById('charts').appendChild(container);
            
            new Chart(canvas, config.chart);
        }}
        
        // Render all data
        if (chartsData.stats) {{
            renderStats(chartsData.stats);
        }}
        
        if (chartsData.charts) {{
            chartsData.charts.forEach(renderChart);
        }}
    </script>
</body>
</html>"""
    
    return html


def create_sleep_chart(sleep_data):
    """Create sleep analysis chart."""
    dates = [s["date"] for s in sleep_data if s.get("sleep_time_seconds")]
    hours = [s["sleep_time_seconds"] / 3600 for s in sleep_data if s.get("sleep_time_seconds")]
    scores = [s.get("sleep_score", 0) for s in sleep_data if s.get("sleep_score")]
    
    avg_hours = sum(hours) / len(hours) if hours else 0
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "stats": {
            "Avg Sleep": f"{avg_hours:.1f}h",
            "Avg Score": f"{avg_score:.0f}/100"
        },
        "chart": {
            "title": "Sleep Analysis",
            "chart": {
                "type": "bar",
                "data": {
                    "labels": dates,
                    "datasets": [
                        {
                            "label": "Sleep Hours",
                            "data": hours,
                            "backgroundColor": "rgba(54, 162, 235, 0.6)",
                            "borderColor": "rgba(54, 162, 235, 1)",
                            "borderWidth": 2,
                            "yAxisID": "y"
                        },
                        {
                            "label": "Sleep Score",
                            "data": scores,
                            "type": "line",
                            "borderColor": "rgba(255, 206, 86, 1)",
                            "backgroundColor": "rgba(255, 206, 86, 0.1)",
                            "borderWidth": 3,
                            "tension": 0.4,
                            "yAxisID": "y1"
                        }
                    ]
                },
                "options": {
                    "responsive": True,
                    "interaction": {
                        "mode": "index",
                        "intersect": False
                    },
                    "scales": {
                        "y": {
                            "type": "linear",
                            "display": True,
                            "position": "left",
                            "title": {
                                "display": True,
                                "text": "Hours"
                            }
                        },
                        "y1": {
                            "type": "linear",
                            "display": True,
                            "position": "right",
                            "title": {
                                "display": True,
                                "text": "Score"
                            },
                            "grid": {
                                "drawOnChartArea": False
                            },
                            "max": 100
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": True
                        }
                    }
                }
            }
        }
    }


def create_body_battery_chart(bb_data):
    """Create Body Battery (recovery) chart."""
    dates = [b["date"] for b in bb_data if b.get("charged") is not None]
    charged = [b.get("charged", 0) for b in bb_data if b.get("charged") is not None]
    highest = [b.get("highest", 0) for b in bb_data if b.get("highest") is not None]
    
    avg_charged = sum(charged) / len(charged) if charged else 0
    avg_highest = sum(highest) / len(highest) if highest else 0
    
    # Color code based on levels
    colors = []
    for val in highest:
        if val >= 75:
            colors.append("rgba(75, 192, 192, 0.6)")  # Green
        elif val >= 50:
            colors.append("rgba(255, 206, 86, 0.6)")  # Yellow
        elif val >= 25:
            colors.append("rgba(255, 159, 64, 0.6)")  # Orange
        else:
            colors.append("rgba(255, 99, 132, 0.6)")  # Red
    
    return {
        "stats": {
            "Avg Charged": f"+{avg_charged:.0f}",
            "Avg Peak": f"{avg_highest:.0f}/100"
        },
        "chart": {
            "title": "Body Battery (Recovery)",
            "chart": {
                "type": "bar",
                "data": {
                    "labels": dates,
                    "datasets": [{
                        "label": "Highest Body Battery",
                        "data": highest,
                        "backgroundColor": colors,
                        "borderWidth": 0
                    }]
                },
                "options": {
                    "responsive": True,
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "max": 100,
                            "title": {
                                "display": True,
                                "text": "Body Battery"
                            }
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": False
                        }
                    }
                }
            }
        }
    }


def create_hrv_chart(hrv_data, hr_data):
    """Create HRV and resting heart rate trend chart."""
    dates = [h["date"] for h in hrv_data if h.get("last_night_avg")]
    hrv_values = [h.get("last_night_avg", 0) for h in hrv_data if h.get("last_night_avg")]
    
    # Match dates with heart rate data
    hr_map = {h["date"]: h.get("resting_hr") for h in hr_data if h.get("resting_hr")}
    rhr_values = [hr_map.get(date, 0) for date in dates]
    
    avg_hrv = sum(hrv_values) / len(hrv_values) if hrv_values else 0
    avg_rhr = sum(rhr_values) / len(rhr_values) if rhr_values else 0
    
    return {
        "stats": {
            "Avg HRV": f"{avg_hrv:.0f} ms",
            "Avg RHR": f"{avg_rhr:.0f} bpm"
        },
        "chart": {
            "title": "HRV & Resting Heart Rate",
            "chart": {
                "type": "line",
                "data": {
                    "labels": dates,
                    "datasets": [
                        {
                            "label": "HRV (ms)",
                            "data": hrv_values,
                            "borderColor": "rgba(153, 102, 255, 1)",
                            "backgroundColor": "rgba(153, 102, 255, 0.1)",
                            "borderWidth": 3,
                            "tension": 0.4,
                            "yAxisID": "y"
                        },
                        {
                            "label": "Resting HR (bpm)",
                            "data": rhr_values,
                            "borderColor": "rgba(255, 99, 132, 1)",
                            "backgroundColor": "rgba(255, 99, 132, 0.1)",
                            "borderWidth": 3,
                            "tension": 0.4,
                            "yAxisID": "y1"
                        }
                    ]
                },
                "options": {
                    "responsive": True,
                    "interaction": {
                        "mode": "index",
                        "intersect": False
                    },
                    "scales": {
                        "y": {
                            "type": "linear",
                            "display": True,
                            "position": "left",
                            "title": {
                                "display": True,
                                "text": "HRV (ms)"
                            }
                        },
                        "y1": {
                            "type": "linear",
                            "display": True,
                            "position": "right",
                            "title": {
                                "display": True,
                                "text": "Heart Rate (bpm)"
                            },
                            "grid": {
                                "drawOnChartArea": False
                            }
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": True
                        }
                    }
                }
            }
        }
    }


def create_activities_chart(activities_data):
    """Create activities/workouts summary chart."""
    # Group by type
    types = {}
    for activity in activities_data:
        activity_type = activity.get("activity_type", "Unknown")
        if activity_type not in types:
            types[activity_type] = {"count": 0, "calories": 0, "duration": 0}
        types[activity_type]["count"] += 1
        types[activity_type]["calories"] += activity.get("calories", 0)
        types[activity_type]["duration"] += activity.get("duration_seconds", 0) / 3600
    
    labels = list(types.keys())
    counts = [types[t]["count"] for t in labels]
    calories = [types[t]["calories"] for t in labels]
    
    total_activities = sum(counts)
    total_calories = sum(calories)
    
    return {
        "stats": {
            "Activities": f"{total_activities}",
            "Total Calories": f"{total_calories:.0f}"
        },
        "chart": {
            "title": "Activities Summary",
            "chart": {
                "type": "bar",
                "data": {
                    "labels": labels,
                    "datasets": [
                        {
                            "label": "Count",
                            "data": counts,
                            "backgroundColor": "rgba(75, 192, 192, 0.6)",
                            "borderColor": "rgba(75, 192, 192, 1)",
                            "borderWidth": 2,
                            "yAxisID": "y"
                        },
                        {
                            "label": "Calories",
                            "data": calories,
                            "backgroundColor": "rgba(255, 159, 64, 0.6)",
                            "borderColor": "rgba(255, 159, 64, 1)",
                            "borderWidth": 2,
                            "yAxisID": "y1"
                        }
                    ]
                },
                "options": {
                    "responsive": True,
                    "scales": {
                        "y": {
                            "type": "linear",
                            "display": True,
                            "position": "left",
                            "title": {
                                "display": True,
                                "text": "Count"
                            }
                        },
                        "y1": {
                            "type": "linear",
                            "display": True,
                            "position": "right",
                            "title": {
                                "display": True,
                                "text": "Calories"
                            },
                            "grid": {
                                "drawOnChartArea": False
                            }
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": True
                        }
                    }
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Garmin health charts")
    parser.add_argument("chart", choices=["sleep", "body_battery", "hrv", "activities", "dashboard"],
                       help="Type of chart to generate")
    parser.add_argument("--days", type=int, default=30, help="Number of days (default: 30)")
    parser.add_argument("--output", help="Output HTML file (default: opens in browser)")
    
    args = parser.parse_args()
    
    # Get authenticated client
    client = get_client()
    if not client:
        print("❌ Not authenticated. Run: python3 scripts/garmin_auth.py login", file=sys.stderr)
        sys.exit(1)
    
    print(f"📊 Fetching {args.days} days of data...", file=sys.stderr)
    
    # Prepare chart data
    charts_data = {"stats": {}, "charts": []}
    
    if args.chart in ["sleep", "dashboard"]:
        print("  - Sleep data", file=sys.stderr)
        sleep_data = fetch_sleep(client, args.days).get("sleep", [])
        if sleep_data:
            result = create_sleep_chart(sleep_data)
            charts_data["stats"].update(result.get("stats", {}))
            charts_data["charts"].append(result["chart"])
    
    if args.chart in ["body_battery", "dashboard"]:
        print("  - Body Battery data", file=sys.stderr)
        bb_data = fetch_body_battery(client, args.days).get("body_battery", [])
        if bb_data:
            result = create_body_battery_chart(bb_data)
            charts_data["stats"].update(result.get("stats", {}))
            charts_data["charts"].append(result["chart"])
    
    if args.chart in ["hrv", "dashboard"]:
        print("  - HRV & Heart Rate data", file=sys.stderr)
        hrv_data = fetch_hrv(client, args.days).get("hrv", [])
        hr_data = fetch_heart_rate(client, args.days).get("heart_rate", [])
        if hrv_data:
            result = create_hrv_chart(hrv_data, hr_data)
            charts_data["stats"].update(result.get("stats", {}))
            charts_data["charts"].append(result["chart"])
    
    if args.chart in ["activities", "dashboard"]:
        print("  - Activities data", file=sys.stderr)
        activities_data = fetch_activities(client, args.days).get("activities", [])
        if activities_data:
            result = create_activities_chart(activities_data)
            charts_data["stats"].update(result.get("stats", {}))
            charts_data["charts"].append(result["chart"])
    
    # Generate HTML
    title = f"Garmin {args.chart.title()} - Last {args.days} Days"
    html = generate_html(charts_data, title)
    
    # Save or open
    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.write_text(html)
        print(f"✅ Chart saved to {output_path}", file=sys.stderr)
    else:
        # Save to temp file and open
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html)
            temp_path = f.name
        
        print(f"✅ Opening chart in browser...", file=sys.stderr)
        webbrowser.open(f"file://{temp_path}")


if __name__ == "__main__":
    main()
