export interface WhoopProfile {
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface WhoopBody {
  height_meter: number;
  weight_kilogram: number;
  max_heart_rate: number;
}

export interface SleepStageSummary {
  total_in_bed_time_milli: number;
  total_awake_time_milli: number;
  total_no_data_time_milli: number;
  total_light_sleep_time_milli: number;
  total_slow_wave_sleep_time_milli: number;
  total_rem_sleep_time_milli: number;
  sleep_cycle_count: number;
  disturbance_count: number;
}

export interface SleepNeeded {
  baseline_milli: number;
  need_from_sleep_debt_milli: number;
  need_from_recent_strain_milli: number;
  need_from_recent_nap_milli: number;
}

export interface SleepScore {
  stage_summary: SleepStageSummary;
  sleep_needed: SleepNeeded;
  respiratory_rate: number;
  sleep_performance_percentage: number;
  sleep_consistency_percentage: number;
  sleep_efficiency_percentage: number;
}

export interface WhoopSleep {
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
  start: string;
  end: string;
  timezone_offset: string;
  nap: boolean;
  score: SleepScore;
}

export interface RecoveryScore {
  user_calibrating: boolean;
  recovery_score: number;
  resting_heart_rate: number;
  hrv_rmssd_milli: number;
  spo2_percentage?: number;
  skin_temp_celsius?: number;
}

export interface WhoopRecovery {
  cycle_id: number;
  sleep_id: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  score_state: string;
  score: RecoveryScore;
}

export interface WorkoutScore {
  strain: number;
  average_heart_rate: number;
  max_heart_rate: number;
  kilojoule: number;
  percent_recorded?: number;
  distance_meter?: number;
  altitude_gain_meter?: number;
  zone_durations?: {
    zone_zero_milli: number;
    zone_one_milli: number;
    zone_two_milli: number;
    zone_three_milli: number;
    zone_four_milli: number;
    zone_five_milli: number;
  };
}

export interface WhoopWorkout {
  id: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  start: string;
  end: string;
  timezone_offset: string;
  sport_id: number;
  sport_name: string;
  score_state: string;
  score: WorkoutScore;
}

export interface CycleScore {
  strain: number;
  kilojoule: number;
  average_heart_rate: number;
  max_heart_rate: number;
}

export interface CycleRecovery {
  id: number;
  score: number;
  user_calibrating: boolean;
  recovery_score: number;
  resting_heart_rate: number;
  hrv_rmssd_milli: number;
  spo2_percentage: number;
  skin_temp_celsius: number;
}

export interface WhoopCycle {
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
  start: string;
  end: string;
  timezone_offset: string;
  score: CycleScore;
  recovery: CycleRecovery;
}

export interface ApiResponse<T> {
  records: T[];
  next_token?: string;
}

export interface TokenData {
  access_token: string;
  refresh_token: string;
  expires_at: number;
  token_type: string;
  scope: string;
}

export interface OAuthTokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  scope: string;
}

export type DataType = 'profile' | 'body' | 'sleep' | 'recovery' | 'workout' | 'cycle';

export interface DateRange {
  start?: string;
  end?: string;
}

export interface QueryParams extends DateRange {
  limit?: number;
  nextToken?: string;
}

export interface CombinedOutput {
  profile?: WhoopProfile;
  body?: WhoopBody;
  sleep?: WhoopSleep[];
  recovery?: WhoopRecovery[];
  workout?: WhoopWorkout[];
  cycle?: WhoopCycle[];
  date: string;
  fetched_at: string;
}

export type WhoopData = CombinedOutput;
