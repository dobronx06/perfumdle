/**
 * RSS feeds for Pinterest "auto-publish from RSS" (one feed per board): /pinterest/femme.xml, /homme.xml, /mixte.xml.
 * Each item = one perfume page, with its vertical pin image (public/pins/<slug>.jpg, scripts/make_pins.py).
 * Ordered by search demand (game pool first), so the best-known perfumes are pinned first.
 */
import type { APIRoute, GetStaticPaths } from 'astro';
import fs from 'node:fs';
import { SITE, url, perfumes, perfumeEditorial, allNotes, noteName, familyLabel } from '../../lib/catalog';
import pool from '../../data/game-pool.json';

const BOARDS = { femme: 'Feminine', homme: 'Masculine', mixte: 'Unisex' } as const;
type Board = keyof typeof BOARDS;

export const getStaticPaths: GetStaticPaths = () => (Object.keys(BOARDS) as Board[]).map((board) => ({ params: { board } }));

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const rank = new Map((pool as string[]).map((s, i) => [s, i]));

export const GET: APIRoute = ({ params }) => {
  const board = params.board as Board;
  const items = perfumes
    .filter((p) => p.gender === BOARDS[board] && fs.existsSync(`public/pins/${p.slug}.jpg`))
    .sort((a, b) => (rank.get(a.slug) ?? 999 + a.id) - (rank.get(b.slug) ?? 999 + b.id));
  const now = Date.now();
  const xml = items.map((p, i) => {
    const ed = perfumeEditorial(p.slug)?.fr;
    const link = `${SITE}${url.perfume('fr', p.slug)}`;
    const img = `${SITE}/pins/${p.slug}.jpg`;
    const notes = allNotes(p).slice(0, 6).map((n) => noteName(n, 'fr').toLowerCase()).join(', ');
    const title = p.name.toLowerCase().includes(p.brand.toLowerCase())
      ? `${p.name} : notes, avis et parfums similaires`
      : `${p.name} de ${p.brand} : notes, avis et parfums similaires`;
    const desc = `${ed?.tagline ?? ''} ${p.name} (${p.brand}, ${p.year}), parfum ${familyLabel(p.family, 'fr').toLowerCase()}. Notes : ${notes}. Pyramide olfactive, avis et parfums qui lui ressemblent sur Perfumdle.`.trim();
    const size = fs.statSync(`public/pins/${p.slug}.jpg`).size;
    return `<item><title>${esc(title)}</title><link>${link}</link><guid isPermaLink="true">${link}</guid>` +
      `<pubDate>${new Date(now - i * 3600_000).toUTCString()}</pubDate><description>${esc(desc)}</description>` +
      `<enclosure url="${img}" type="image/jpeg" length="${size}"/><media:content url="${img}" medium="image" type="image/jpeg" width="1000" height="1500"/></item>`;
  }).join('\n');
  const label = { femme: 'Parfums femme', homme: 'Parfums homme', mixte: 'Parfums mixtes' }[board];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>
<title>${label} | Perfumdle</title><link>${SITE}${url.gender('fr', BOARDS[board])}</link>
<description>${label} iconiques : notes, avis et parfums similaires, par Perfumdle.</description><language>fr</language>
${xml}
</channel></rss>`;
  return new Response(body, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
