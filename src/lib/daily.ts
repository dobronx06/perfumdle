/**
 * Daily perfume draw, shared by the game and the embeddable widget so both always show the same perfume.
 * Runs in the browser: `today` is the visitor's local calendar day (YYYY-MM-DD).
 */

function mulberry32(a: number) {
  return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

const pad = (n: number) => String(n).padStart(2, '0');
export const dayStr = (d = new Date()) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

/** Days since the game started (2026-09-01 is day 0). */
export function dayIndex(today: string): number {
  const [y, m, d] = today.split('-').map(Number);
  return Math.floor((Date.UTC(y, m - 1, d) - Date.UTC(2026, 8, 1)) / 86400000);
}

/** Same perfume for everyone on a given day; no repeat until the whole pool has been played. */
export function dailySlug(pool: string[], today: string): string {
  const idx = dayIndex(today);
  const n = pool.length;
  const cycle = Math.floor(idx / n);
  const order = pool.slice();
  const rnd = mulberry32(cycle * 7919 + 17);
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
  return order[((idx % n) + n) % n];
}
