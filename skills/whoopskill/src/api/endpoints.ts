export const BASE_URL = 'https://api.prod.whoop.com/developer/v2';

export const ENDPOINTS = {
  profile: '/user/profile/basic',
  body: '/user/measurement/body',
  workout: '/activity/workout',
  sleep: '/activity/sleep',
  recovery: '/recovery',
  cycle: '/cycle',
} as const;
