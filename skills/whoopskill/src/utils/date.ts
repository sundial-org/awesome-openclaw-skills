const WHOOP_DAY_START_HOUR = 4;

export function getWhoopDay(date?: string): string {
  const d = date ? new Date(date) : new Date();

  if (d.getHours() < WHOOP_DAY_START_HOUR) {
    d.setDate(d.getDate() - 1);
  }

  return formatDate(d);
}

export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function getDateRange(date: string): { start: string; end: string } {
  const d = new Date(date);
  const start = new Date(d);
  start.setHours(WHOOP_DAY_START_HOUR, 0, 0, 0);

  const end = new Date(start);
  end.setDate(end.getDate() + 1);

  return {
    start: start.toISOString(),
    end: end.toISOString(),
  };
}

export function validateISODate(date: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(date)) return false;

  const d = new Date(date);
  return !isNaN(d.getTime());
}

export function nowISO(): string {
  return new Date().toISOString();
}

export function getDaysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return formatDate(d);
}
