import type { WhoopRecovery, WhoopSleep, WhoopCycle, WhoopWorkout } from '../types/whoop.js';

export interface TrendStats {
  avg: number;
  min: number;
  max: number;
  current: number;
  trend: 'up' | 'down' | 'stable';
  values: number[];
}

export interface TrendData {
  period: number;
  recovery: TrendStats | null;
  hrv: TrendStats | null;
  rhr: TrendStats | null;
  sleepPerformance: TrendStats | null;
  sleepHours: TrendStats | null;
  strain: TrendStats | null;
}

export interface Insight {
  category: 'recovery' | 'sleep' | 'strain' | 'hrv';
  level: 'good' | 'warning' | 'critical';
  title: string;
  message: string;
  action?: string;
}

function calcStats(values: number[]): TrendStats | null {
  if (values.length === 0) return null;
  const current = values[0];
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  const recentAvg = values.slice(0, Math.min(3, values.length)).reduce((a, b) => a + b, 0) / Math.min(3, values.length);
  const olderAvg = values.length > 3
    ? values.slice(3).reduce((a, b) => a + b, 0) / values.slice(3).length
    : recentAvg;

  const diff = recentAvg - olderAvg;
  const threshold = avg * 0.05;

  return {
    avg: Math.round(avg * 10) / 10,
    min: Math.min(...values),
    max: Math.max(...values),
    current,
    trend: diff > threshold ? 'up' : diff < -threshold ? 'down' : 'stable',
    values,
  };
}

export function analyzeTrends(
  recovery: WhoopRecovery[],
  sleep: WhoopSleep[],
  cycle: WhoopCycle[],
  period: number
): TrendData {
  const sortedRecovery = [...recovery].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );
  const sortedSleep = [...sleep].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );
  const sortedCycle = [...cycle].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );

  const recoveryScores = sortedRecovery
    .filter(r => r.score?.recovery_score != null)
    .map(r => r.score.recovery_score);

  const hrvValues = sortedRecovery
    .filter(r => r.score?.hrv_rmssd_milli != null)
    .map(r => r.score.hrv_rmssd_milli);

  const rhrValues = sortedRecovery
    .filter(r => r.score?.resting_heart_rate != null)
    .map(r => r.score.resting_heart_rate);

  const sleepPerf = sortedSleep
    .filter(s => s.score?.sleep_performance_percentage != null && !s.nap)
    .map(s => s.score.sleep_performance_percentage);

  const sleepHours = sortedSleep
    .filter(s => s.score?.stage_summary?.total_in_bed_time_milli != null && !s.nap)
    .map(s => s.score.stage_summary.total_in_bed_time_milli / 3600000);

  const strainValues = sortedCycle
    .filter(c => c.score?.strain != null)
    .map(c => c.score.strain);

  return {
    period,
    recovery: calcStats(recoveryScores),
    hrv: calcStats(hrvValues),
    rhr: calcStats(rhrValues),
    sleepPerformance: calcStats(sleepPerf),
    sleepHours: calcStats(sleepHours),
    strain: calcStats(strainValues),
  };
}

export function generateInsights(
  recovery: WhoopRecovery[],
  sleep: WhoopSleep[],
  cycle: WhoopCycle[],
  workout: WhoopWorkout[]
): Insight[] {
  const insights: Insight[] = [];

  const sortedRecovery = [...recovery].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );
  const sortedSleep = [...sleep].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );
  const sortedCycle = [...cycle].sort((a, b) =>
    new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  );

  const today = sortedRecovery[0]?.score;
  const todaySleep = sortedSleep.find(s => !s.nap)?.score;
  const todayCycle = sortedCycle[0]?.score;

  if (today) {
    if (today.recovery_score >= 67) {
      insights.push({
        category: 'recovery',
        level: 'good',
        title: 'Green Recovery',
        message: `Recovery at ${today.recovery_score}% — body is primed for high strain.`,
        action: 'Great day for intense training or competition.',
      });
    } else if (today.recovery_score >= 34) {
      insights.push({
        category: 'recovery',
        level: 'warning',
        title: 'Yellow Recovery',
        message: `Recovery at ${today.recovery_score}% — moderate readiness.`,
        action: 'Consider moderate activity. Avoid max efforts.',
      });
    } else {
      insights.push({
        category: 'recovery',
        level: 'critical',
        title: 'Red Recovery',
        message: `Recovery at ${today.recovery_score}% — body needs rest.`,
        action: 'Prioritize rest, hydration, and sleep tonight.',
      });
    }

    const hrvRecords = sortedRecovery.slice(0, 7).filter(r => r.score?.hrv_rmssd_milli);
    const avgHrv = hrvRecords.length > 0
      ? hrvRecords.reduce((a, r) => a + r.score.hrv_rmssd_milli, 0) / hrvRecords.length
      : 0;

    if (avgHrv > 0 && today.hrv_rmssd_milli < avgHrv * 0.8) {
      insights.push({
        category: 'hrv',
        level: 'warning',
        title: 'HRV Below Baseline',
        message: `Today's HRV (${today.hrv_rmssd_milli.toFixed(0)}ms) is ${((1 - today.hrv_rmssd_milli / avgHrv) * 100).toFixed(0)}% below your 7-day average.`,
        action: 'Possible stress, poor sleep, or overtraining. Monitor closely.',
      });
    } else if (avgHrv > 0 && today.hrv_rmssd_milli > avgHrv * 1.1) {
      insights.push({
        category: 'hrv',
        level: 'good',
        title: 'HRV Above Baseline',
        message: `Today's HRV (${today.hrv_rmssd_milli.toFixed(0)}ms) is ${((today.hrv_rmssd_milli / avgHrv - 1) * 100).toFixed(0)}% above your 7-day average.`,
        action: 'Excellent recovery. Good day for peak performance.',
      });
    }
  }

  if (todaySleep) {
    const sleepDebt = todaySleep.sleep_needed.need_from_sleep_debt_milli / 3600000;
    if (sleepDebt > 2) {
      insights.push({
        category: 'sleep',
        level: 'critical',
        title: 'Significant Sleep Debt',
        message: `You have ${sleepDebt.toFixed(1)} hours of accumulated sleep debt.`,
        action: 'Try to get to bed 30-60 min earlier for the next few days.',
      });
    } else if (sleepDebt > 1) {
      insights.push({
        category: 'sleep',
        level: 'warning',
        title: 'Mild Sleep Debt',
        message: `You have ${sleepDebt.toFixed(1)} hours of sleep debt.`,
        action: 'Consider an earlier bedtime tonight.',
      });
    }

    if (todaySleep.sleep_efficiency_percentage < 85) {
      insights.push({
        category: 'sleep',
        level: 'warning',
        title: 'Low Sleep Efficiency',
        message: `Sleep efficiency at ${todaySleep.sleep_efficiency_percentage.toFixed(0)}% (target: 85%+).`,
        action: 'Limit screen time before bed. Keep room cool and dark.',
      });
    }

    const actualSleepTime = todaySleep.stage_summary.total_in_bed_time_milli - todaySleep.stage_summary.total_awake_time_milli;
    const remPct = actualSleepTime > 0
      ? (todaySleep.stage_summary.total_rem_sleep_time_milli / actualSleepTime) * 100
      : 0;
    if (remPct > 0 && remPct < 15) {
      insights.push({
        category: 'sleep',
        level: 'warning',
        title: 'Low REM Sleep',
        message: `REM was only ${remPct.toFixed(0)}% of sleep (target: 20-25%).`,
        action: 'Avoid alcohol and late meals. Maintain consistent wake time.',
      });
    }
  }

  if (todayCycle && today) {
    const optimalStrain = today.recovery_score >= 67 ? 14
      : today.recovery_score >= 34 ? 10
      : 6;

    const remaining = optimalStrain - todayCycle.strain;
    if (remaining > 2) {
      insights.push({
        category: 'strain',
        level: 'good',
        title: 'Strain Capacity Available',
        message: `Current strain: ${todayCycle.strain.toFixed(1)}. Optimal target: ~${optimalStrain}.`,
        action: `Room for ${remaining.toFixed(1)} more strain today.`,
      });
    } else if (todayCycle.strain > optimalStrain + 2) {
      insights.push({
        category: 'strain',
        level: 'warning',
        title: 'Strain Exceeds Optimal',
        message: `Strain (${todayCycle.strain.toFixed(1)}) is above optimal (${optimalStrain}) for your recovery.`,
        action: 'Wind down. Focus on recovery for the rest of the day.',
      });
    }
  }

  if (workout.length === 0 && today?.recovery_score >= 67) {
    insights.push({
      category: 'strain',
      level: 'good',
      title: 'No Workout Yet',
      message: 'High recovery day with no recorded workout.',
      action: 'Great opportunity for an intense session.',
    });
  }

  return insights;
}

export function formatTrends(data: TrendData, pretty: boolean): string {
  if (!pretty) return JSON.stringify(data, null, 2);

  const arrow = (t: 'up' | 'down' | 'stable') => t === 'up' ? '↑' : t === 'down' ? '↓' : '→';
  const lines: string[] = [`📊 ${data.period}-Day Trends`, ''];

  if (data.recovery) {
    lines.push(`💚 Recovery: ${data.recovery.avg}% avg (${data.recovery.min}-${data.recovery.max}) ${arrow(data.recovery.trend)}`);
  }
  if (data.hrv) {
    lines.push(`💓 HRV: ${data.hrv.avg}ms avg (${data.hrv.min.toFixed(0)}-${data.hrv.max.toFixed(0)}) ${arrow(data.hrv.trend)}`);
  }
  if (data.rhr) {
    lines.push(`❤️ RHR: ${data.rhr.avg}bpm avg (${data.rhr.min}-${data.rhr.max}) ${arrow(data.rhr.trend)}`);
  }
  if (data.sleepPerformance) {
    lines.push(`😴 Sleep: ${data.sleepPerformance.avg}% avg (${data.sleepPerformance.min}-${data.sleepPerformance.max}) ${arrow(data.sleepPerformance.trend)}`);
  }
  if (data.sleepHours) {
    lines.push(`🛏️ Hours: ${data.sleepHours.avg.toFixed(1)}h avg (${data.sleepHours.min.toFixed(1)}-${data.sleepHours.max.toFixed(1)}) ${arrow(data.sleepHours.trend)}`);
  }
  if (data.strain) {
    lines.push(`🔥 Strain: ${data.strain.avg.toFixed(1)} avg (${data.strain.min.toFixed(1)}-${data.strain.max.toFixed(1)}) ${arrow(data.strain.trend)}`);
  }

  return lines.join('\n');
}

export function formatInsights(insights: Insight[], pretty: boolean): string {
  if (!pretty) return JSON.stringify(insights, null, 2);

  if (insights.length === 0) return '✅ No actionable insights — all metrics look healthy!';

  const icon = (level: 'good' | 'warning' | 'critical') =>
    level === 'good' ? '✅' : level === 'warning' ? '⚠️' : '🔴';

  const lines: string[] = ['💡 Insights & Recommendations', ''];

  for (const i of insights) {
    lines.push(`${icon(i.level)} ${i.title}`);
    lines.push(`   ${i.message}`);
    if (i.action) lines.push(`   → ${i.action}`);
    lines.push('');
  }

  return lines.join('\n').trim();
}
