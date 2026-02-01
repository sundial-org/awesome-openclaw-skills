# Extended Garmin Capabilities

This skill now supports **comprehensive health tracking, time-based queries, and activity file analysis**.

## 🎯 Time-Based Queries

Ask questions like:
- "What was my heart rate at 3pm yesterday?"
- "What was my stress level at 10:30 this morning?"
- "What was my Body Battery at noon?"

### Usage

```bash
# Heart rate at specific time
python3 scripts/garmin_query.py heart_rate "3:00 PM" --date 2026-01-24

# Stress level
python3 scripts/garmin_query.py stress "14:30"

# Body Battery
python3 scripts/garmin_query.py body_battery "10:00 AM" --date 2026-01-23

# Steps at time
python3 scripts/garmin_query.py steps "17:00"
```

**Time formats supported:**
- `3:00 PM`, `3 PM` (12-hour)
- `15:00`, `15:30:45` (24-hour)
- `2026-01-24 15:30` (full datetime)

## 📊 Extended Metrics

### Training & Performance

```bash
# Training readiness (daily readiness score)
python3 scripts/garmin_data_extended.py training_readiness

# Training status (load, VO2 max trends)
python3 scripts/garmin_data_extended.py training_status

# Endurance score
python3 scripts/garmin_data_extended.py endurance_score

# Hill score
python3 scripts/garmin_data_extended.py hill_score

# Max metrics (VO2 max, etc.)
python3 scripts/garmin_data_extended.py max_metrics

# Fitness age
python3 scripts/garmin_data_extended.py fitness_age
```

### Body Composition & Health

```bash
# Body composition (weight, body fat %, muscle mass, BMI)
python3 scripts/garmin_data_extended.py body_composition --date 2026-01-24

# Weight history
python3 scripts/garmin_data_extended.py weigh_ins --start 2026-01-01 --end 2026-01-24

# Blood oxygen (SPO2)
python3 scripts/garmin_data_extended.py spo2 --date 2026-01-24

# Respiration (breathing rate throughout day)
python3 scripts/garmin_data_extended.py respiration
```

### Activity Metrics

```bash
# Detailed steps (time-series)
python3 scripts/garmin_data_extended.py steps --date 2026-01-24

# Floors climbed
python3 scripts/garmin_data_extended.py floors

# Intensity minutes (vigorous/moderate)
python3 scripts/garmin_data_extended.py intensity_minutes

# Hydration/water intake
python3 scripts/garmin_data_extended.py hydration

# Detailed stress (time-series throughout day)
python3 scripts/garmin_data_extended.py stress_detailed

# Intraday heart rate (all HR samples)
python3 scripts/garmin_data_extended.py hr_intraday
```

## 🗺️ Activity File Analysis (FIT/GPX)

Download and analyze activity files to answer questions like:
- "What was my elevation at mile 2?"
- "What was my pace when my heart rate was above 160?"
- "Show me my route on a map"

### Download Activity Files

```bash
# Download FIT file
python3 scripts/garmin_activity_files.py download --activity-id 12345678 --format fit

# Download GPX file (for GPS visualization)
python3 scripts/garmin_activity_files.py download --activity-id 12345678 --format gpx

# Download TCX file
python3 scripts/garmin_activity_files.py download --activity-id 12345678 --format tcx
```

### Parse Activity Files

```bash
# Parse FIT file (detailed metrics)
python3 scripts/garmin_activity_files.py parse --file /tmp/activity_12345678.fit

# Parse GPX file (GPS track)
python3 scripts/garmin_activity_files.py parse --file /tmp/activity_12345678.gpx
```

**FIT files contain:**
- GPS coordinates (lat/lon)
- Elevation/altitude
- Heart rate
- Cadence (steps/min for running, rpm for cycling)
- Power (watts, for cycling)
- Speed & pace
- Temperature
- Lap splits

### Query Activity Data

```bash
# What was my heart rate/elevation at 1500 meters into the run?
python3 scripts/garmin_activity_files.py query --file /tmp/activity_12345678.fit --distance 1500

# What was my data at a specific time during the activity?
python3 scripts/garmin_activity_files.py query --file /tmp/activity_12345678.fit --time "2026-01-24T10:15:30"
```

### Analyze Activity

```bash
# Get comprehensive statistics
python3 scripts/garmin_activity_files.py analyze --file /tmp/activity_12345678.fit
```

**Returns:**
- Average/max/min heart rate
- Elevation gain/max/min
- Average/max speed
- Average cadence
- Average/max power (cycling)
- Total distance
- Duration

## 🔍 Use Cases

### Health Monitoring
- "How has my VO2 max changed over the past month?"
- "What's my fitness age compared to my actual age?"
- "Show me my training load trend"
- "What was my SPO2 during sleep last night?"

### Activity Analysis
- "Map my running route from yesterday"
- "What was my heart rate at the steepest hill?"
- "Show me my pace per mile with elevation profile"
- "How does my cadence correlate with my heart rate?"

### Recovery Tracking
- "What's my training readiness today?"
- "When did my Body Battery start draining yesterday?"
- "How many intensity minutes did I get this week?"

### Time-Series Analysis
- "Graph my heart rate from 8am to 6pm"
- "Show me stress levels throughout the workday"
- "When was my Body Battery fully charged?"

## 📦 Dependencies

```bash
pip3 install garminconnect fitparse gpxpy
```

- **garminconnect**: Garmin Connect API wrapper
- **fitparse**: Parse FIT files (Garmin's binary format)
- **gpxpy**: Parse GPX files (GPS track format)

## 🛠️ Advanced Tips

### Get Activity ID

The activity ID is visible in the Garmin Connect URL:
```
https://connect.garmin.com/modern/activity/12345678
                                        ^^^^^^^^
```

Or find it programmatically:
```bash
python3 scripts/garmin_data.py activities --days 7
# Look for "activity_id" in each activity
```

### Batch Processing

```bash
# Get recent activity IDs
activities=$(python3 scripts/garmin_data.py activities --days 7 | jq -r '.activities[].activityId')

# Download all FIT files
for id in $activities; do
  python3 scripts/garmin_activity_files.py download --activity-id $id --format fit
done
```

### Visualization Ideas

1. **Route Maps**: Use GPX files with Leaflet.js or Google Maps
2. **Elevation Profiles**: Plot elevation vs distance
3. **Heart Rate Zones**: Color-code route by HR zones
4. **Pace Heatmap**: Show where you were fastest/slowest
5. **Power/Cadence Correlation**: Cycling efficiency analysis

## 🚀 Future Enhancements

Potential additions:
- [ ] Automated route visualization
- [ ] Training plan tracking
- [ ] Workout recommendations
- [ ] Gear tracking & wear analysis
- [ ] Weather correlation with performance
- [ ] Social challenges & badges
- [ ] Menstrual cycle tracking
- [ ] Pregnancy tracking
- [ ] Race prediction accuracy tracking
