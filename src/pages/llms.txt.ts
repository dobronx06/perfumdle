/** llms.txt — a plain map of the site for AI assistants and answer engines (GEO). */
import type { APIRoute } from 'astro';
import { SITE, url, brands, notes, families, eras, noteName, familyName, eraName, perfumes, GUIDES, guideUrl } from '../lib/catalog';
import { livePages, rankedUrl, rankedCopy } from '../lib/ranked';

export const GET: APIRoute = () => {
  const l = 'fr' as const;
  const lines = [
    '# Perfumdle',
    '',
    `> Encyclopédie éditoriale indépendante et bilingue (FR/EN) de ${perfumes.length} parfums iconiques : pyramides olfactives, histoire des ${brands.length} maisons, ${notes.length} notes olfactives expliquées, familles et époques. Inclut un jeu quotidien de devinette de parfum.`,
    '',
    'Chaque fiche parfum indique maison, année, genre, famille olfactive, concentration, notes de tête/cœur/fond, parfumeur quand il est documenté, saisons conseillées et parfums similaires (calculés à partir des notes communes).',
    '',
    '## Index',
    `- [Tous les parfums](${SITE}${url.perfumes(l)})`,
    `- [Maisons de parfum](${SITE}${url.brands(l)})`,
    `- [Notes olfactives](${SITE}${url.notes(l)})`,
    `- [Familles olfactives](${SITE}${url.families(l)})`,
    `- [Époques](${SITE}${url.eras(l)})`,
    `- [English version](${SITE}/en/)`,
    '',
    '## Familles olfactives',
    ...families.map((f) => `- [${familyName(f.key, l)}](${SITE}${url.family(l, f.key)}): ${f.perfumes.length} parfums`),
    '',
    '## Notes',
    ...notes.map((n) => `- [${noteName(n.key, l)}](${SITE}${url.note(l, n.key)}): ${n.perfumes.length} parfums`),
    '',
    '## Maisons',
    ...brands.map((b) => `- [${b.name}](${SITE}${url.brand(l, b.name)}): ${b.perfumes.length} parfums`),
    '',
    '## Époques',
    ...eras.map((e) => `- [${eraName(e.decade, l)}](${SITE}${url.era(l, e.decade)})`),
    '',
    '## Guides',
    ...GUIDES.map((g) => `- [${g.fr}](${SITE}/fr/${g.slug}/)`),
    '',
    ...(livePages.length ? ['## Sélections commentées', ...livePages.map((d) => `- [${rankedCopy(d.id)!.fr.h1}](${SITE}${rankedUrl(d, l)})`), ''] : []),
    '## English',
    `- [Home](${SITE}/en/)`,
    `- [All perfumes](${SITE}${url.perfumes('en')})`,
    `- [Perfume houses](${SITE}${url.brands('en')})`,
    `- [Fragrance notes](${SITE}${url.notes('en')})`,
    `- [Olfactory families](${SITE}${url.families('en')})`,
    `- [Eras](${SITE}${url.eras('en')})`,
    `- [Daily perfume guessing game](${SITE}${url.game('en')})`,
    ...GUIDES.map((g) => `- [${g.en}](${SITE}${guideUrl(g.slug, 'en')})`),
    '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
