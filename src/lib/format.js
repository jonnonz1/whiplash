/* Shared formatting + timeline helpers. */

export const TIMELINE_FROM = 2008;

export function nowFrac() {
  return dateToFrac(new Date().toISOString().slice(0, 10));
}

/* "2024-01-14" -> 2024.04 */
export function dateToFrac(iso) {
  if (!iso) return null;
  const [y, m, d] = iso.split('-').map(Number);
  const start = Date.UTC(y, 0, 1);
  const t = Date.UTC(y, (m || 1) - 1, d || 1);
  const yearMs = Date.UTC(y + 1, 0, 1) - start;
  return y + (t - start) / yearMs;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/* Calendar-consistent inverse of dateToFrac. Millisecond rounding matters:
   without it, float error lands 1ms before midnight on ~46% of month starts. */
export function fracToDate(frac) {
  const y = Math.floor(frac);
  const start = Date.UTC(y, 0, 1);
  const yearMs = Date.UTC(y + 1, 0, 1) - start;
  return new Date(Math.round(start + (frac - y) * yearMs));
}

export function fracLabel(frac) {
  const d = fracToDate(frac);
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

export function dateLabel(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return d && m ? `${d} ${MONTHS[m - 1]} ${y}` : `${y}`;
}

export function fmtMoney(n) {
  if (n == null) return '—';
  if (n === 0) return '$0';
  if (n >= 1e9) return '$' + (n / 1e9).toFixed(n >= 1e10 ? 0 : 2) + 'b';
  if (n >= 1e6) {
    const m = n / 1e6;
    return '$' + (Number.isInteger(m) ? m : m.toFixed(1)) + 'm';
  }
  if (n >= 1e3) return '$' + Math.round(n / 1e3) + 'k';
  return '$' + n;
}

/* Marker radius (px) by sunk cost — log scale with a floor for
   salient-but-$0/unknown projects. */
export function markerRadius(sunk) {
  if (!sunk || sunk <= 0) return 8;
  return Math.max(9, Math.min(26, 7 + 5.5 * Math.log10(sunk / 1e6)));
}

export function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}
