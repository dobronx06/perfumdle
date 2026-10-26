/**
 * Opening clues of every perfume in the game pool, per language, for the "parfum du jour" block
 * shown on content pages. The block draws today's perfume client-side (src/lib/daily.ts) and reads
 * its two opening clues here, so pages stay static and the game keeps a single source of truth.
 */
import type { APIRoute } from 'astro';
import pool from '../data/game-pool.json';
import { perfumeBySlug, mainFamily, familyName, noteName } from '../lib/catalog';

export const GET: APIRoute = () => {
  const out: Record<string, Record<string, [string, string]>> = { fr: {}, en: {} };
  for (const s of pool as string[]) {
    const p = perfumeBySlug.get(s);
    if (!p) continue;
    const base = p.notes.base[0] ?? p.notes.heart[0] ?? p.notes.top[0];
    for (const l of ['fr', 'en'] as const) out[l][s] = [familyName(mainFamily(p), l), noteName(base, l)];
  }
  return new Response(JSON.stringify({ pool, clues: out }), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
