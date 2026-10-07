type HistoricalDate = string | { $date?: string | number };

export const formatChangePercent = (value: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'percent',
    maximumFractionDigits: 2,
    signDisplay: 'exceptZero',
  }).format(value);

export const calendarDate = (date: HistoricalDate) => {
  const raw = typeof date === 'string' ? date : date?.$date;
  if (typeof raw === 'string') {
    const match = raw.match(/^(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : null;
  }
  if (typeof raw === 'number') {
    return new Date(raw).toISOString().slice(0, 10);
  }
  return null;
};

export const formatLocalDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const percentChange = (
  current: number | null | undefined,
  reference: number | null | undefined,
) => {
  if (current == null || reference == null || reference === 0) return null;
  return (current - reference) / reference;
};

export const oneMonthAgo = (from = new Date()) => {
  const year = from.getFullYear();
  const month = from.getMonth() - 1;
  const day = from.getDate();
  const candidate = new Date(year, month, day);
  return candidate.getDate() === day ? candidate : new Date(year, month + 1, 0);
};
