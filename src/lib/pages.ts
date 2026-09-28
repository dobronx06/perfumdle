/**
 * Builds CollectionView props for every hub type (brand, note, family, era, gender, season).
 * Route files stay one-liners; all content logic lives here.
 */
import type { Locale } from '../i18n';
import {
  url, brands, notes, families, eras, genders, seasons, noteName, familyName, eraName, topNotes, pairedNotes,
  similarity, brandByName, noteByKey, decadeOf, perfumeEditorial, GENDER_LABEL, type Perfume, type Faq, type Brand,
} from './catalog';
import { rankedLinks } from './ranked';

const other = (l: Locale): Locale => (l === 'fr' ? 'en' : 'fr');
const home = (l: Locale) => ({ name: l === 'fr' ? 'Accueil' : 'Home', href: url.home(l) });
const lc = (l: Locale, s: string) => (l === 'fr' ? s.toLowerCase() : s);
const trim = (s: string, n = 158) => (s.length <= n ? s : `${s.slice(0, n - 1).replace(/\s+\S*$/, '')}…`);

function noteGroup(l: Locale, list: Perfume[], exclude?: string) {
  const fr = l === 'fr';
  return {
    eyebrow: fr ? 'Signature' : 'Signature',
    title: fr ? 'Notes les plus présentes' : 'Most frequent notes',
    items: topNotes(list, 13).filter((n) => n.key !== exclude).slice(0, 12).map((n) => ({ label: noteName(n.key, l), href: url.note(l, n.key), count: n.count })),
  };
}

function houseGroup(l: Locale, list: Perfume[]) {
  const counts = new Map<string, number>();
  for (const p of list) counts.set(p.brand, (counts.get(p.brand) ?? 0) + 1);
  return {
    eyebrow: l === 'fr' ? 'Les maisons' : 'The houses',
    title: l === 'fr' ? 'Maisons les plus représentées' : 'Most represented houses',
    variant: 'houses' as const,
    items: [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12).map(([b, c]) => ({ label: b, href: url.brand(l, b), count: c })),
  };
}

/** Links to live ranked selections (note × genre, meilleurs parfums…), or nothing. */
function selectionGroup(l: Locale, title: string, items: { label: string; href: string }[]) {
  return items.length ? [{ eyebrow: l === 'fr' ? 'Sélections commentées' : 'Curated selections', title, items }] : [];
}

const byYear = (a: Perfume, b: Perfume) => a.year - b.year;
const byFame = (a: Perfume, b: Perfume) => a.id - b.id; // dataset is ordered by notoriety

/* ------------------------------------------------------------------ brand */

export function brandPage(b: Brand, l: Locale) {
  const fr = l === 'fr';
  const ed = b.ed?.[l];
  const years = b.perfumes.map((p) => p.year);
  const similarHouses = brands
    .filter((o) => o.name !== b.name)
    .map((o) => ({ o, s: avgSim(b.perfumes, o.perfumes) }))
    .sort((a, z) => z.s - a.s)
    .slice(0, 8);
  const intro = ed?.intro ?? (fr
    ? `${b.name} compte ${b.perfumes.length} parfum${b.perfumes.length > 1 ? 's' : ''} dans notre encyclopédie, de ${Math.min(...years)} à ${Math.max(...years)}.`
    : `${b.name} has ${b.perfumes.length} perfume${b.perfumes.length > 1 ? 's' : ''} in our encyclopedia, from ${Math.min(...years)} to ${Math.max(...years)}.`);
  const facts = [
    b.ed?.country && { label: fr ? 'Pays' : 'Country', value: countryName(b.ed.country, l) },
    b.ed?.founded && { label: fr ? 'Fondation' : 'Founded', value: String(b.ed.founded) },
    b.ed?.founder && { label: fr ? 'Fondateur' : 'Founder', value: b.ed.founder },
    { label: fr ? 'Parfums' : 'Perfumes', value: String(b.perfumes.length) },
    { label: fr ? 'Période' : 'Span', value: Math.min(...years) === Math.max(...years) ? String(years[0]) : `${Math.min(...years)} – ${Math.max(...years)}` },
    b.ed?.type && { label: fr ? 'Catégorie' : 'Type', value: typeName(b.ed.type, l) },
  ].filter(Boolean) as { label: string; value: string }[];

  return {
    locale: l,
    title: ed?.title ?? (fr ? `Parfums ${b.name} : histoire, icônes et notes` : `${b.name} perfumes: history, icons and notes`),
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Maison de parfum' : 'Perfume house',
    h1: fr ? `Les parfums ${b.name}` : `${b.name} perfumes`,
    intro,
    crumbs: [home(l), { name: fr ? 'Maisons' : 'Houses', href: url.brands(l) }, { name: b.name }],
    alternates: { [l]: url.brand(l, b.name), [other(l)]: url.brand(other(l), b.name) } as Record<Locale, string>,
    tint: '#E9E1D6',
    facts,
    sections: [
      { title: fr ? `L'histoire de ${b.name}` : `The story of ${b.name}`, body: ed?.history },
      { title: fr ? 'Une signature olfactive' : 'An olfactory signature', body: ed?.signature },
      { title: fr ? `Quel parfum ${b.name} choisir ?` : `Which ${b.name} perfume to choose?`, body: ed?.howToChoose },
    ],
    perfumes: b.perfumes.slice().sort(byYear),
    perfumesTitle: fr ? `Tous les parfums ${b.name}` : `All ${b.name} perfumes`,
    groups: [
      noteGroup(l, b.perfumes),
      {
        eyebrow: fr ? 'Affinités' : 'Affinities',
        title: fr ? `Si vous aimez ${b.name}` : `If you like ${b.name}`,
        variant: 'houses' as const,
        items: similarHouses.map(({ o }) => ({ label: o.name, href: url.brand(l, o.name), count: o.perfumes.length })),
      },
      ...selectionGroup(l, fr ? `Les meilleurs parfums ${b.name}` : `The best ${b.name} perfumes`, rankedLinks(l, (d) => d.brand === b.name)),
    ],
    faq: ed?.faq,
  };
}

function avgSim(a: Perfume[], b: Perfume[]) {
  let s = 0;
  for (const x of a) for (const y of b) s += similarity(x, y);
  return s / (a.length * b.length) + Math.min(b.length, 6) * 0.05;
}

const COUNTRY_FR: Record<string, string> = {
  France: 'France', Italy: 'Italie', 'United States': 'États-Unis', USA: 'États-Unis', 'United Kingdom': 'Royaume-Uni', UK: 'Royaume-Uni',
  Spain: 'Espagne', Germany: 'Allemagne', Japan: 'Japon', Sweden: 'Suède', Oman: 'Oman', Turkey: 'Turquie', Switzerland: 'Suisse',
  'United Arab Emirates': 'Émirats arabes unis', Brazil: 'Brésil', Venezuela: 'Venezuela', Netherlands: 'Pays-Bas',
};
function countryName(c: string, l: Locale) { return l === 'fr' ? COUNTRY_FR[c] ?? c : c; }
function typeName(t: string, l: Locale) {
  const m: Record<string, [string, string]> = {
    heritage: ['Maison historique', 'Heritage house'], designer: ['Créateur', 'Designer'], niche: ['Niche', 'Niche'],
    celebrity: ['Parfum de célébrité', 'Celebrity'], 'fashion-house': ['Maison de mode', 'Fashion house'],
    'middle-eastern': ['Parfumerie orientale', 'Middle Eastern'], mass: ['Grande diffusion', 'Mass market'],
  };
  return (m[t] ?? [t, t])[l === 'fr' ? 0 : 1];
}

/* ------------------------------------------------------------------- note */

export function notePage(key: string, l: Locale) {
  const fr = l === 'fr';
  const n = noteByKey.get(key)!;
  const ed = n.ed?.[l];
  const name = noteName(key, l);
  const tiers = { top: 0, heart: 0, base: 0 };
  for (const p of n.perfumes) for (const t of ['top', 'heart', 'base'] as const) if (p.notes[t].includes(key)) tiers[t]++;
  const pos = (p: Perfume) => (p.notes.top.includes(key) ? (fr ? 'En tête' : 'Top note') : p.notes.heart.includes(key) ? (fr ? 'En cœur' : 'Heart note') : (fr ? 'En fond' : 'Base note'));
  const intro = ed?.intro ?? (fr
    ? `${name} apparaît dans ${n.perfumes.length} parfums de notre encyclopédie.`
    : `${name} appears in ${n.perfumes.length} perfumes in our encyclopedia.`);
  const genderSplit = (['Feminine', 'Masculine', 'Unisex'] as const).map((g) => n.perfumes.filter((p) => p.gender === g).length);

  return {
    locale: l,
    title: ed?.title ?? (fr ? `Parfums à la note ${name} : odeur et sélection` : `${name} perfumes: smell and best picks`),
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Note olfactive' : 'Fragrance note',
    h1: ed?.h1 ?? (fr ? `La note ${lc(l, name)} en parfumerie` : `${name} in perfumery`),
    intro,
    crumbs: [home(l), { name: 'Notes', href: url.notes(l) }, { name }],
    alternates: { [l]: url.note(l, key), [other(l)]: url.note(other(l), key) } as Record<Locale, string>,
    tint: '#E6DDD0',
    stats: [
      { value: String(n.perfumes.length), label: fr ? 'parfums' : 'perfumes' },
      { value: String(tiers.top), label: fr ? 'en tête' : 'as top note' },
      { value: String(tiers.heart), label: fr ? 'en cœur' : 'as heart note' },
      { value: String(tiers.base), label: fr ? 'en fond' : 'as base note' },
    ],
    sections: [
      { title: fr ? `${name} : quelle odeur ?` : `What does ${lc(l, name)} smell like?`, body: ed?.smell },
      { title: fr ? 'Origine et fabrication' : 'Origin and production', body: ed?.origin },
      { title: fr ? "L'usage en parfumerie" : 'How perfumers use it', body: ed?.craft },
      { title: fr ? 'Comment la porter' : 'How to wear it', body: ed?.wear },
    ],
    perfumes: n.perfumes.slice().sort(byFame),
    perfumesTitle: fr ? `Parfums avec la note ${lc(l, name)}` : `Perfumes with ${lc(l, name)}`,
    perfumeNote: pos,
    groups: [
      {
        eyebrow: fr ? 'Accords' : 'Pairings',
        title: fr ? `Souvent associée à` : 'Often paired with',
        items: pairedNotes(key, 10).map((x) => ({ label: noteName(x.key, l), href: url.note(l, x.key), count: x.count })),
      },
      ...selectionGroup(l, fr ? `${name} : sélection femme ou homme` : `${name}: for women or for men`, rankedLinks(l, (d) => d.kind === 'ng' && d.note === key)),
      houseGroup(l, n.perfumes),
    ],
    faq: ed?.faq ?? [],
    filterable: n.perfumes.length > 12 && genderSplit.filter(Boolean).length > 1,
  };
}

/* ----------------------------------------------------------------- family */

export function familyPage(key: string, l: Locale) {
  const fr = l === 'fr';
  const f = families.find((x) => x.key === key)!;
  const ed = f.ed?.[l];
  const name = familyName(key, l);
  const intro = ed?.intro ?? (fr ? `La famille ${lc(l, name)} regroupe ${f.perfumes.length} parfums de notre sélection.` : `The ${name} family covers ${f.perfumes.length} perfumes in our selection.`);
  const i = families.findIndex((x) => x.key === key);
  const prev = families[i - 1];
  const next = families[i + 1];
  return {
    locale: l,
    title: ed?.title ?? (fr ? `Parfums ${lc(l, name)}s : la famille olfactive expliquée` : `${name} perfumes: the olfactory family explained`),
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Famille olfactive' : 'Olfactory family',
    h1: ed?.h1 ?? (fr ? `La famille ${lc(l, name)}` : `The ${name} family`),
    intro,
    crumbs: [home(l), { name: fr ? 'Familles' : 'Families', href: url.families(l) }, { name }],
    alternates: { [l]: url.family(l, key), [other(l)]: url.family(other(l), key) } as Record<Locale, string>,
    tint: f.tint,
    stats: [
      { value: String(f.perfumes.length), label: fr ? 'parfums' : 'perfumes' },
      { value: String(new Set(f.perfumes.map((p) => p.brand)).size), label: fr ? 'maisons' : 'houses' },
      { value: String(Math.min(...f.perfumes.map((p) => p.year))), label: fr ? 'le plus ancien' : 'oldest' },
    ],
    sections: [
      { title: fr ? 'Histoire de la famille' : 'A short history', body: ed?.history },
      { title: fr ? 'Les sous-familles' : 'Sub-families', body: ed?.subfamilies },
      { title: fr ? 'Comment la porter' : 'How to wear it', body: ed?.howToWear },
    ],
    perfumes: f.perfumes.slice().sort(byFame),
    perfumesTitle: fr ? `Les parfums de la famille ${lc(l, name)}` : `${name} perfumes`,
    groups: [
      noteGroup(l, f.perfumes),
      ...selectionGroup(l, fr ? `${name} : sélection femme ou homme` : `${name}: for women or for men`, rankedLinks(l, (d) => d.kind === 'fg' && d.family === key)),
      houseGroup(l, f.perfumes),
    ],
    faq: ed?.faq ?? [],
    filterable: true,
    pager: {
      prev: prev && { label: familyName(prev.key, l), href: url.family(l, prev.key) },
      next: next && { label: familyName(next.key, l), href: url.family(l, next.key) },
    },
  };
}

/* -------------------------------------------------------------------- era */

export function eraPage(decade: number, l: Locale) {
  const fr = l === 'fr';
  const i = eras.findIndex((e) => e.decade === decade);
  const e = eras[i];
  const ed = e.ed?.[l];
  const name = eraName(decade, l);
  const intro = ed?.intro ?? (fr ? `${e.perfumes.length} parfums de notre encyclopédie sont nés dans les ${lc(l, name)}.` : `${e.perfumes.length} perfumes in our encyclopedia were born in ${name.toLowerCase()}.`);
  return {
    locale: l,
    title: ed?.title ?? (fr ? `Parfums des ${lc(l, name)} : les icônes d'une époque` : `Perfumes of ${name.toLowerCase()}: the icons of an era`),
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Époque' : 'Era',
    h1: ed?.h1 ?? (fr ? `Les parfums des ${lc(l, name)}` : `Perfumes of ${name.toLowerCase()}`),
    intro,
    crumbs: [home(l), { name: fr ? 'Époques' : 'Eras', href: url.eras(l) }, { name }],
    alternates: { [l]: url.era(l, decade), [other(l)]: url.era(other(l), decade) } as Record<Locale, string>,
    tint: '#E4DACB',
    stats: [
      { value: String(e.perfumes.length), label: fr ? 'parfums' : 'perfumes' },
      { value: String(new Set(e.perfumes.map((p) => p.brand)).size), label: fr ? 'maisons' : 'houses' },
    ],
    sections: [{ title: fr ? "L'esprit d'une décennie" : 'The spirit of a decade', body: ed?.context }],
    perfumes: e.perfumes,
    perfumesTitle: fr ? `Les parfums lancés dans les ${lc(l, name)}` : `Perfumes launched in ${name.toLowerCase()}`,
    perfumeNote: (p: Perfume) => String(p.year),
    groups: [noteGroup(l, e.perfumes), houseGroup(l, e.perfumes)],
    faq: ed?.faq ?? [],
    filterable: e.perfumes.length > 12,
    pager: {
      prev: eras[i - 1] && { label: eraName(eras[i - 1].decade, l), href: url.era(l, eras[i - 1].decade) },
      next: eras[i + 1] && { label: eraName(eras[i + 1].decade, l), href: url.era(l, eras[i + 1].decade) },
    },
  };
}

/* --------------------------------------------------------- gender / season */

export function genderPage(g: string, l: Locale) {
  const fr = l === 'fr';
  const x = genders.find((y) => y.key === g)!;
  const ed = x.ed?.[l];
  const name = fr ? x.name_fr : x.name_en;
  const intro = ed?.intro ?? `${x.perfumes.length} ${fr ? 'parfums' : 'perfumes'}.`;
  return {
    locale: l,
    title: ed?.title ?? `${name} : ${fr ? 'les icônes' : 'the icons'}`,
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Sélection' : 'Edit',
    h1: ed?.h1 ?? name,
    intro,
    crumbs: [home(l), { name: fr ? 'Parfums' : 'Perfumes', href: url.perfumes(l) }, { name }],
    alternates: { [l]: url.gender(l, g), [other(l)]: url.gender(other(l), g) } as Record<Locale, string>,
    tint: g === 'Feminine' ? '#F1DCDA' : g === 'Masculine' ? '#D9DCE0' : '#E6E0D6',
    stats: [
      { value: String(x.perfumes.length), label: fr ? 'parfums' : 'perfumes' },
      { value: String(new Set(x.perfumes.map((p) => p.brand)).size), label: fr ? 'maisons' : 'houses' },
    ],
    sections: [{ title: fr ? 'Ce qui définit la sélection' : 'What defines this edit', body: ed?.body }],
    perfumes: x.perfumes.slice().sort(byFame),
    perfumesTitle: name,
    groups: [
      noteGroup(l, x.perfumes),
      ...selectionGroup(l, fr ? 'Nos sélections par note, famille et saison' : 'Our selections by note, family and season', rankedLinks(l, (d) => d.gender === g && (d.kind === 'best' || d.kind === 'ng' || d.kind === 'fg' || d.kind === 'sg'))),
      houseGroup(l, x.perfumes),
    ],
    faq: ed?.faq ?? [],
  };
}

export function seasonPage(s: string, l: Locale) {
  const fr = l === 'fr';
  const x = seasons.find((y) => y.key === s)!;
  const ed = x.ed?.[l];
  const name = fr ? x.name_fr : x.name_en;
  const intro = ed?.intro ?? `${x.perfumes.length} ${fr ? 'parfums' : 'perfumes'}.`;
  return {
    locale: l,
    title: ed?.title ?? name,
    description: ed?.meta ?? trim(intro),
    eyebrow: fr ? 'Saison' : 'Season',
    h1: ed?.h1 ?? name,
    intro,
    crumbs: [home(l), { name: fr ? 'Parfums' : 'Perfumes', href: url.perfumes(l) }, { name }],
    alternates: { [l]: url.season(l, s), [other(l)]: url.season(other(l), s) } as Record<Locale, string>,
    tint: { spring: '#E3E8D2', summer: '#F2E6C6', autumn: '#EAD6C0', winter: '#DCDDE3' }[s],
    stats: [{ value: String(x.perfumes.length), label: fr ? 'parfums' : 'perfumes' }],
    sections: [{ title: fr ? 'Pourquoi la saison compte' : 'Why the season matters', body: ed?.body }],
    perfumes: x.perfumes.slice().sort(byFame),
    perfumesTitle: name,
    groups: [
      noteGroup(l, x.perfumes),
      ...selectionGroup(l, fr ? `${name} : femme ou homme` : `${name}: for women or for men`, rankedLinks(l, (d) => d.kind === 'sg' && d.season === s)),
      houseGroup(l, x.perfumes),
    ],
    faq: ed?.faq ?? [],
    filterable: true,
  };
}

export { brands, notes, families, eras, genders, seasons, perfumeEditorial, brandByName, decadeOf, GENDER_LABEL };
export type { Faq };
