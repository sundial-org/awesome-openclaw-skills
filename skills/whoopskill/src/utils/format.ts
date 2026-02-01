import type { WhoopData } from '../types/whoop.js';

export function formatPretty(data: WhoopData): string {
  const lines: string[] = [];
  lines.push(`📅 ${data.date}`);
  lines.push('');

  if (data.profile) {
    lines.push(`👤 ${data.profile.first_name} ${data.profile.last_name}`);
  }

  if (data.body) {
    const b = data.body;
    lines.push(`📏 ${b.height_meter}m | ${b.weight_kilogram}kg | Max HR: ${b.max_heart_rate}`);
  }

  if (data.recovery?.length) {
    const r = data.recovery[0].score;
    lines.push(`💚 Recovery: ${r.recovery_score}% | HRV: ${r.hrv_rmssd_milli.toFixed(1)}ms | RHR: ${r.resting_heart_rate}bpm`);
    if (r.spo2_percentage) lines.push(`   SpO2: ${r.spo2_percentage}% | Skin temp: ${r.skin_temp_celsius?.toFixed(1)}°C`);
  }

  if (data.sleep?.length) {
    const s = data.sleep[0].score;
    const hours = (s.stage_summary.total_in_bed_time_milli / 3600000).toFixed(1);
    lines.push(`😴 Sleep: ${s.sleep_performance_percentage}% | ${hours}h | Efficiency: ${s.sleep_efficiency_percentage.toFixed(0)}%`);
    lines.push(`   REM: ${(s.stage_summary.total_rem_sleep_time_milli / 60000).toFixed(0)}min | Deep: ${(s.stage_summary.total_slow_wave_sleep_time_milli / 60000).toFixed(0)}min`);
  }

  if (data.workout?.length) {
    lines.push(`🏋️ Workouts:`);
    for (const w of data.workout) {
      const sc = w.score;
      lines.push(`   ${w.sport_name}: Strain ${sc.strain.toFixed(1)} | Avg HR: ${sc.average_heart_rate} | ${(sc.kilojoule / 4.184).toFixed(0)} cal`);
    }
  }

  if (data.cycle?.length) {
    const c = data.cycle[0].score;
    lines.push(`🔄 Day strain: ${c.strain.toFixed(1)} | ${(c.kilojoule / 4.184).toFixed(0)} cal | Avg HR: ${c.average_heart_rate}`);
  }

  return lines.join('\n');
}

export function formatSummary(data: WhoopData): string {
  const parts: string[] = [];

  if (data.recovery?.length) {
    const r = data.recovery[0].score;
    parts.push(`Recovery: ${r.recovery_score}%`);
    parts.push(`HRV: ${r.hrv_rmssd_milli.toFixed(0)}ms`);
    parts.push(`RHR: ${r.resting_heart_rate}`);
  }

  if (data.sleep?.length) {
    const s = data.sleep[0].score;
    parts.push(`Sleep: ${s.sleep_performance_percentage}%`);
  }

  if (data.cycle?.length) {
    parts.push(`Strain: ${data.cycle[0].score.strain.toFixed(1)}`);
  }

  if (data.workout?.length) {
    parts.push(`Workouts: ${data.workout.length}`);
  }

  return parts.length ? `${data.date} | ${parts.join(' | ')}` : `${data.date} | No data`;
}

function statusIcon(value: number, green: number, yellow: number, invert = false): string {
  if (invert) {
    return value <= green ? '🟢' : value <= yellow ? '🟡' : '🔴';
  }
  return value >= green ? '🟢' : value >= yellow ? '🟡' : '🔴';
}

export function formatSummaryColor(data: WhoopData): string {
  const lines: string[] = [`📅 ${data.date}`];

  if (data.recovery?.length) {
    const r = data.recovery[0].score;
    const icon = statusIcon(r.recovery_score, 67, 34);
    lines.push(`${icon} Recovery: ${r.recovery_score}% | HRV: ${r.hrv_rmssd_milli.toFixed(0)}ms | RHR: ${r.resting_heart_rate}bpm`);
  }

  if (data.sleep?.length) {
    const s = data.sleep[0].score;
    const icon = statusIcon(s.sleep_performance_percentage, 85, 70);
    const hours = (s.stage_summary.total_in_bed_time_milli / 3600000).toFixed(1);
    lines.push(`${icon} Sleep: ${s.sleep_performance_percentage}% | ${hours}h | Efficiency: ${s.sleep_efficiency_percentage.toFixed(0)}%`);
  }

  if (data.cycle?.length) {
    const c = data.cycle[0].score;
    const recoveryScore = data.recovery?.[0]?.score?.recovery_score ?? 50;
    const optimal = recoveryScore >= 67 ? 14 : recoveryScore >= 34 ? 10 : 6;
    const diff = Math.abs(c.strain - optimal);
    const icon = diff <= 2 ? '🟢' : diff <= 4 ? '🟡' : '🔴';
    lines.push(`${icon} Strain: ${c.strain.toFixed(1)} (optimal: ~${optimal}) | ${(c.kilojoule / 4.184).toFixed(0)} cal`);
  }

  if (data.workout?.length) {
    lines.push(`🏋️ Workouts: ${data.workout.length} | ${data.workout.map(w => w.sport_name).join(', ')}`);
  }

  return lines.join('\n');
}
