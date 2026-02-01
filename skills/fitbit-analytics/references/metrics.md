# Fitbit Metrics Reference

## Activity Metrics

| Metric | Healthy Range | Notes |
|--------|---------------|-------|
| Steps | 8,000-12,000 | 10K often recommended |
| Calories Burned | 1,800-2,500 | Varies by body/activity |
| Distance | 5-10 km | Depends on step count |
| Floors | 10-20 | Proxy for vertical movement |
| Active Minutes | 30-60 | Moderate + vigorous |

## Heart Rate Zones

| Zone | % Max HR | Purpose |
|------|----------|---------|
| Out of Range | 50-60% | Rest, light activity |
| Fat Burn | 60-70% | Light exercise, weight loss |
| Cardio | 70-80% | Cardiovascular fitness |
| Peak | 80-100% | High-intensity intervals |

## Heart Rate Metrics

| Metric | Healthy Range | Warning |
|--------|---------------|---------|
| Resting HR (RHR) | 60-100 bpm | <50 or >100 |
| HRV | 20-80 ms | Low HRV = stress |
| Time in Cardio | 20-40 min | Higher = better fitness |
| Time in Peak | 10-20 min | High-intensity capacity |

## Sleep Stages (Typical)

| Stage | % of Night | Duration | Purpose |
|-------|------------|----------|---------|
| Deep | 13-23% | 1-2 hrs | Physical recovery |
| REM | 20-25% | 1.5-2 hrs | Memory, cognition |
| Light | 45-55% | 3-4 hrs | Transition |
| Wake | <5% | <30 min | Minimal is ideal |

## Sleep Quality Indicators

| Metric | Healthy | Poor |
|--------|---------|------|
| Sleep Duration | 7-9 hours | <6 or >9 |
| Sleep Efficiency | >90% | <85% |
| Time to Fall Asleep | <20 min | >30 min |
| Wake Episodes | <2 | >4 |
| Resting HR During Sleep | Lower than waking | Elevated |

## Health Score Calculation

```python
# Activity Score (0-100)
activity_score = min(100, (steps / 10000) * 50 + (active_minutes / 60) * 50)

# Sleep Score (0-100)
sleep_score = (sleep_duration / 8) * 40 + (sleep_efficiency / 100) * 40 + (deep_sleep / 2) * 20

# Overall Health Score
health_score = (activity_score + sleep_score) / 2
```

## Goals & Targets

| Goal | Target | Benefit |
|------|--------|---------|
| Steps | 10,000/day | Cardiovascular health |
| Active Zone Minutes | 30/day | Longevity |
| Sleep | 7-9 hours | Recovery, cognition |
| Sleep Efficiency | >90% | Quality rest |
| RHR | 60-80 bpm | Cardiovascular fitness |

## Alerts & Thresholds

| Condition | Alert | Action |
|-----------|-------|--------|
| Steps < 5,000 | Low activity | Move more |
| Sedentary > 10 hrs | Sedentary warning | Take breaks |
| RHR elevated | HR anomaly | Check stress/sleep |
| Sleep < 6 hrs | Sleep debt | Prioritize rest |
| SpO2 < 95% | Low oxygen | Consult doctor |
