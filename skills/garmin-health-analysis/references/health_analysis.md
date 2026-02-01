# Health Data Analysis Guide - Garmin Edition

Science-backed framework for interpreting Garmin health metrics. Use this when the user asks about their health, trends, or wants insights from their data.

## HRV (Heart Rate Variability) - Nightly Average

### What it means
HRV measures the variation in time between heartbeats. It reflects autonomic nervous system (ANS) balance — specifically parasympathetic (rest-and-digest) activity. Higher HRV = more adaptable, resilient nervous system.

### Normal ranges (wrist-based wearable)
| Age | Low | Normal | High |
|-----|-----|--------|------|
| 20-29 | <25ms | 25-105ms | >105ms |
| 30-39 | <20ms | 20-80ms | >80ms |
| 40-49 | <15ms | 15-60ms | >60ms |
| 50-59 | <12ms | 12-45ms | >45ms |
| 60+ | <10ms | 10-35ms | >35ms |

*Note: Wrist-based HRV tends to read lower than chest strap. Individual baseline matters more than population norms.*

### Interpretation
- **Trend matters more than absolute value** — compare to personal weekly/monthly average
- **Declining HRV trend** (>10% below baseline for 3+ days): suggests accumulated stress, poor recovery, illness onset, or overtraining
- **Rising HRV trend**: improved fitness, better recovery, reduced stress
- **Acute drop**: poor sleep, alcohol, illness, intense training, emotional stress
- **Very low HRV** (<15ms consistently): consider medical consultation — linked to cardiovascular risk, chronic stress

### Garmin-specific notes
- Garmin calculates HRV during sleep (nightly average)
- Shows 7-day rolling average and baseline ranges (balanced low/high)
- **Status indicator**: Balanced, Unbalanced, Poor, Low
- Look for trends over weeks, not single days

### Key research findings
- Low HRV is associated with increased cardiovascular mortality (Harvard Health, PMC5624990)
- HRV reflects both physical AND psychological stress load
- 7-day rolling average provides more meaningful context than daily values

---

## Body Battery (0-100)

### What it means
Garmin's proprietary recovery metric based on:
- Heart rate variability
- Stress levels
- Sleep quality
- Activity intensity

Body Battery "charges" during rest/sleep and "drains" during activity/stress.

### Zones
| Level | Range | Meaning | Recommendation |
|-------|-------|---------|---------------|
| High | 75-100 | Fully charged, optimal energy | Ready for high-intensity training |
| Medium | 50-74 | Moderate energy | Good for regular workouts |
| Low | 25-49 | Limited energy reserves | Light activity, recovery focus |
| Very Low | 0-24 | Depleted | Prioritize rest and recovery |

### Patterns to watch
- **Peak daily value** (highest point after sleep): indicates overnight recovery quality
- **Charging rate** (how much you gain during sleep): poor charging = poor sleep/recovery
- **Draining rate** (how fast it depletes): rapid drain = high stress/activity
- **Consistently <50 peak**: chronic under-recovery — review sleep, stress, training load
- **Not fully charging** (peak <75 for 3+ days): accumulated fatigue

### Optimal pattern
- Charge to 75-100 overnight
- Maintain 50+ through most of the day
- Drop to 25-50 by evening
- Recharge during sleep

---

## Resting Heart Rate (RHR)

### Normal ranges
| Fitness level | RHR (bpm) |
|--------------|-----------|
| Athlete | 40-55 |
| Active adult | 55-65 |
| Average adult | 60-80 |
| Sedentary | 70-90 |
| Concerning | >90 |

### Interpretation
- **Trend matters**: RHR rising 3-5+ bpm above personal baseline for several days suggests accumulated fatigue, stress, illness, or dehydration
- **Acute spike**: alcohol, poor sleep, illness onset, overtraining
- **Decreasing RHR over weeks/months**: improving cardiovascular fitness
- **High RHR + Low HRV**: strong signal of poor recovery or health concern

### Garmin-specific
- Measured during sleep periods
- Tracks 7-day average and long-term trends
- Sudden increases often visible before illness symptoms

---

## Sleep Analysis

### Optimal distribution (for 7-8h total sleep)
| Stage | % of total | Ideal duration (8h) | Function |
|-------|-----------|---------------------|----------|
| Deep | 15-25% | 1.2-2.0h | Physical restoration, growth hormone, immune function, memory consolidation |
| REM | 20-25% | 1.6-2.0h | Emotional processing, learning, creativity, memory |
| Light | 50-60% | 4.0-4.8h | Transition stage, some memory processing |
| Awake | <10% | <0.8h | Normal brief awakenings |

### Sleep Score (0-100)
Garmin's composite score based on:
- Total sleep duration
- Sleep stage distribution
- Movement/restlessness
- Respiration quality
- Heart rate stability

| Score | Quality | Interpretation |
|-------|---------|---------------|
| 90-100 | Excellent | Optimal restorative sleep |
| 80-89 | Good | Quality sleep with minor issues |
| 60-79 | Fair | Adequate but could improve |
| 0-59 | Poor | Significant sleep deficiencies |

### Key thresholds
- **Total sleep needed** (adults): 7-9 hours (CDC recommendation)
- **Deep sleep <1h**: concerning — reduced physical recovery, weakened immunity
- **REM sleep <1.2h**: may affect emotional regulation, learning
- **Restless periods >15**: possible environment issues, sleep apnea, stress
- **Avg Sleep Score <70**: chronic sleep issues — review habits, environment, schedule

### Factors that reduce deep sleep
- Alcohol, caffeine (within 6h), late heavy meals, screen time, irregular schedule, aging

### Factors that increase deep sleep
- Exercise (not too close to bedtime), cool room temperature (60-67°F), consistent schedule, stress management

---

## Stress Levels

### What it means
Garmin calculates stress from HRV analysis throughout the day. Lower HRV = higher stress.

### Ranges
| Level | Score | Interpretation |
|-------|-------|---------------|
| Rest | 0-25 | Relaxed, recovering |
| Low | 26-50 | Calm, light activity |
| Medium | 51-75 | Moderate stress, normal activity |
| High | 76-100 | High stress, intense activity, or emotional pressure |

### Interpretation
- **All-day stress average**: Should be <50 for most days
- **High stress duration**: >4h per day may indicate chronic stress
- **Rest periods**: Should have some rest periods (0-25) throughout day
- **No rest periods**: concerning — may need stress management techniques
- **Stress spikes without activity**: emotional/mental stress

### Healthy pattern
- Morning rise (waking up)
- Activity-related spikes
- Several rest periods
- Evening decline
- Low stress during sleep

---

## Respiration Rate

### Normal ranges (breaths per minute during sleep)
| Range | Interpretation |
|-------|---------------|
| 12-16 | Normal, healthy |
| 10-12 | Normal for athletes |
| <10 or >20 | May indicate health concern |

### What to watch
- **Sudden increase**: illness, allergies, sleep apnea, stress
- **Consistently elevated**: chronic respiratory issues, poor fitness
- **High variability**: possible sleep-disordered breathing

---

## VO2 Max

### What it means
Maximum oxygen uptake during intense exercise (ml/kg/min). Gold standard for cardiorespiratory fitness.

### Ranges by age and gender (general population)
#### Men
| Age | Poor | Fair | Good | Excellent | Superior |
|-----|------|------|------|-----------|----------|
| 20-29 | <40 | 40-43 | 44-51 | 52-56 | >56 |
| 30-39 | <38 | 38-41 | 42-49 | 50-54 | >54 |
| 40-49 | <35 | 35-38 | 39-45 | 46-52 | >52 |
| 50-59 | <32 | 32-35 | 36-43 | 44-48 | >48 |

#### Women
| Age | Poor | Fair | Good | Excellent | Superior |
|-----|------|------|------|-----------|----------|
| 20-29 | <32 | 32-36 | 37-41 | 42-46 | >46 |
| 30-39 | <30 | 30-33 | 34-39 | 40-44 | >44 |
| 40-49 | <27 | 27-31 | 32-36 | 37-41 | >41 |
| 50-59 | <25 | 25-28 | 29-33 | 34-38 | >38 |

### Garmin-specific
- Estimated from running/walking activities with GPS + heart rate
- Updates after qualifying outdoor activities
- More accurate with chest strap heart rate
- Tracks trends over time

---

## Activity Intensity Minutes

### Weekly targets (WHO/AHA guidelines)
- **Moderate intensity**: 150 minutes/week
- **Vigorous intensity**: 75 minutes/week
- OR combination (2 min moderate = 1 min vigorous)

### Interpretation
- **Meeting target**: associated with reduced disease risk
- **Exceeding target**: additional health benefits up to ~300 min/week
- **Below target**: increased health risks

---

## Analysis Framework

When analyzing user data, follow this structure:

### 1. Quick Status (current state)
- Latest Body Battery level + peak value
- Last night's sleep score + hours
- Today's stress average
- Current resting heart rate
- Latest HRV reading + status

### 2. Trend Analysis (7-30 day window)
- HRV trend (rising/stable/declining vs baseline)
- Resting heart rate trend
- Sleep score average
- Body Battery charging pattern
- Activity intensity vs. recovery balance

### 3. Pattern Detection
- Day-of-week patterns (weekend effects, Monday dips)
- Sleep consistency
- Stress/recovery correlation
- Activity load vs. Body Battery recovery
- RHR elevation before illness

### 4. Actionable Insights (science-backed)
Based on data, suggest specific improvements:

**Sleep optimization:**
- Consistent bedtime/wake time (±30 min)
- 7-9 hours nightly
- Cool room (60-67°F)
- Dark, quiet environment
- No alcohol within 3h, no caffeine within 6h

**Recovery enhancement:**
- Match training intensity to Body Battery
- Build in rest days when BB not recovering above 75
- Stress management techniques when all-day stress >50
- Hydration monitoring

**Training periodization:**
- Push intensity on high Body Battery days (75+)
- Active recovery on medium days (50-74)
- Rest on low days (<50)
- Monitor HRV for overtraining signs

### 5. Flags / Alerts
- **Consistently low HRV** (<15ms) → suggest medical consultation
- **Elevated respiration** (>20 bpm during sleep) → possible breathing issue
- **RHR elevated 5+ bpm for 3+ days** → illness/overtraining watch
- **Sleep <6h average for 5+ days** → serious sleep debt, health risk
- **Body Battery not charging >75 for 5+ days** → chronic under-recovery
- **No rest stress periods** → chronic stress concern

---

## Prompt Template for Analysis

When asked "how am I doing?" or similar, fetch summary data and analyze:

```
Based on [USER]'s Garmin data for the last [N] days:

METRICS:
- Avg Body Battery Peak: X/100 (charging: good/poor)
- Avg HRV: Xms (vs baseline, trend: rising/falling/stable)
- HRV Status: Balanced/Unbalanced/Poor/Low
- Avg Resting HR: Xbpm (vs baseline: Xbpm)
- Avg Sleep: Xh, score: X/100
- Deep sleep avg: Xh (X% of total)
- REM avg: Xh (X% of total)
- Avg Stress: X (high stress duration: Xh/day)
- Activities: X workouts, X total calories

ANALYSIS:
[Apply the framework above — status, trends, patterns, insights, flags]
```

---

## Garmin vs Whoop: Key Differences

| Metric | Garmin | Whoop |
|--------|--------|-------|
| **Recovery** | Body Battery (0-100) | Recovery Score (0-100%) |
| **Strain** | Activity calories/intensity | Strain (0-21 scale) |
| **Stress** | All-day HRV-based stress | Not directly tracked |
| **Sleep scoring** | Composite score (0-100) | Performance % vs need |
| **Activities** | Extensive GPS/sport modes | Strain-focused tracking |
| **Primary use case** | Multi-sport fitness watch | Recovery-focused wearable |

---

## Important Disclaimers
- This is NOT medical advice — always recommend consulting a doctor for health concerns
- Wearable data has limitations in accuracy
- Individual baselines matter more than population norms
- One bad day doesn't indicate a problem — look for patterns over 3+ days
- Context matters: travel, altitude, menstrual cycle, medication, illness can all affect metrics
- Garmin estimates are based on algorithms and sensor data — not laboratory measurements
