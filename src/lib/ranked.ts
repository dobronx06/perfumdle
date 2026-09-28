/**
 * Ranked pages ("sélections commentées"): note × genre, famille × genre, saison × genre,
 * meilleurs parfums, parfumeurs, guides d'usage. Definitions come from src/data/ranked-pages.json
 * (built by scripts/ranked_pages.py), copy from src/data/editorial/ranked-*.json.
 * A page exists only once it has copy AND its publish date (publish-schedule.json → "ranked") has passed.
 */
import defsRaw from '../data/ranked-pages.json';
import type { Locale } from '../i18n';
import {
  url, perfumeBySlug, noteName, noteSlug, familyName, familyInfo, seasonInfo, genderInfo, brandByName,
  type Perfume, type Faq,
} from './catalog';
import { isPublished } from './schedule';

export type Kind = 'ng' | 'fg' | 'sg' | 'best' | 'nose' | 'guide';

export interface RankedDef {
  id: string; kind: Kind; slug_fr: string; slug_en: string; volume: number; pool: string[];
  note?: string; family?: string; season?: string; gender?: string; brand?: string; perfumer?: string;
}

interface Copy { title: string; meta: string; h1: string; intro: string; sections: { title: string; body: string }[]; why?: Record<string, string>; faq: Faq[] }
export interface RankedCopy { picks?: string[]; fr: Copy; en: Copy }

const files = import.meta.glob('../data/editorial/ranked-*.json', { eager: true, import: 'default' }) as Record<string, Record<string, unknown>>;
const copy: Record<string, RankedCopy> = {};
for (const content of Object.values(files)) for (const [k, v] of Object.entries(content)) if (!k.startsWith('_')) copy[k] = v as RankedCopy;

export const rankedDefs = defsRaw as RankedDef[];
export const rankedById = new Map(rankedDefs.map((d) => [d.id, d]));

export function hubCopy(kind: 'best' | 'nose' | 'guide'): RankedCopy | undefined {
  return copy[`hub:${kind}`];
}

/** Live pages only: copy written and publish date reached. */
export const livePages: RankedDef[] = rankedDefs.filter((d) => copy[d.id] && isPublished('ranked', d.id));
const liveIds = new Set(livePages.map((d) => d.id));
export const isLive = (id: string) => liveIds.has(id);
export const liveOfKind = (k: Kind) => livePages.filter((d) => d.kind === k);

const GSEG = { fr: { Feminine: 'femme', Masculine: 'homme' }, en: { Feminine: 'women', Masculine: 'men' } } as const;
export const genderWord = (g: string | undefined, l: Locale) => (g ? (GSEG[l] as Record<string, string>)[g] ?? '' : '');

export const rankedBase = {
  best: (l: Locale) => `/${l}/${l === 'fr' ? 'meilleurs-parfums' : 'best-perfumes'}/`,
  nose: (l: Locale) => `/${l}/${l === 'fr' ? 'parfumeurs' : 'perfumers'}/`,
  guide: (l: Locale) => `/${l}/guides/`,
};

export function rankedUrl(d: RankedDef, l: Locale): string {
  const g = genderWord(d.gender, l);
  switch (d.kind) {
    case 'ng': return `/${l}/notes/${noteSlug(d.note!, l)}/${g}/`;
    case 'fg': return `/${l}/${l === 'fr' ? 'familles' : 'families'}/${familyInfo(d.family!)[l === 'fr' ? 'slug_fr' : 'slug_en']}/${g}/`;
    case 'sg': return `/${l}/${seasonInfo(d.season!)[l === 'fr' ? 'slug_fr' : 'slug_en']}/${g}/`;
    default: return `${rankedBase[d.kind](l)}${l === 'fr' ? d.slug_fr : d.slug_en}/`;
  }
}

/** Short human label, used for cross-links ("Vanille femme", "Meilleurs parfums Dior femme"…). */
export function rankedLabel(d: RankedDef, l: Locale): string {
  const fr = l === 'fr';
  const g = d.gender === 'Feminine' ? (fr ? 'femme' : 'for women') : d.gender === 'Masculine' ? (fr ? 'homme' : 'for men') : '';
  switch (d.kind) {
    case 'ng': return `${noteName(d.note!, l)} ${g}`;
    case 'fg': return fr ? `${familyName(d.family!, l)} ${g}` : `${familyName(d.family!, l)} ${g}`;
    case 'sg': return `${fr ? seasonInfo(d.season!).name_fr : seasonInfo(d.season!).name_en} ${g}`;
    case 'nose': return d.perfumer!;
    default: return copy[d.id]?.[l].h1 ?? d.id;
  }
}

/** Cross-links helper: live pages matching a predicate, as chip items. */
export function rankedLinks(l: Locale, pred: (d: RankedDef) => boolean) {
  return livePages.filter(pred).map((d) => ({ label: rankedLabel(d, l), href: rankedUrl(d, l) }));
}

export function rankedCopy(id: string) { return copy[id]; }

export function picksOf(d: RankedDef): Perfume[] {
  return (copy[d.id]?.picks ?? []).map((s) => perfumeBySlug.get(s)).filter(Boolean) as Perfume[];
}

export function othersOf(d: RankedDef): Perfume[] {
  const picked = new Set(copy[d.id]?.picks ?? []);
  return d.pool.filter((s) => !picked.has(s)).map((s) => perfumeBySlug.get(s)!).filter(Boolean);
}

/** Parent hub (breadcrumb) for each kind. */
export function parentOf(d: RankedDef, l: Locale): { name: string; href: string } {
  const fr = l === 'fr';
  switch (d.kind) {
    case 'ng': return { name: noteName(d.note!, l), href: url.note(l, d.note!) };
    case 'fg': return { name: familyName(d.family!, l), href: url.family(l, d.family!) };
    case 'sg': return { name: fr ? seasonInfo(d.season!).name_fr : seasonInfo(d.season!).name_en, href: url.season(l, d.season!) };
    case 'best': return { name: fr ? 'Meilleurs parfums' : 'Best perfumes', href: rankedBase.best(l) };
    case 'nose': return { name: fr ? 'Parfumeurs' : 'Perfumers', href: rankedBase.nose(l) };
    default: return { name: 'Guides', href: rankedBase.guide(l) };
  }
}

/** Sibling pages shown at the bottom: same note / family / season / kind, other gender first. */
export function relatedOf(d: RankedDef, l: Locale) {
  const same = (x: RankedDef) => x.id !== d.id && x.kind === d.kind;
  const sibling = livePages.filter((x) => same(x) && (
    (d.note && x.note === d.note) || (d.family && x.family === d.family) || (d.season && x.season === d.season) ||
    (d.brand && x.brand === d.brand)));
  const sameGender = livePages.filter((x) => same(x) && x.gender && x.gender === d.gender && !sibling.includes(x));
  const rest = livePages.filter((x) => same(x) && !sibling.includes(x) && !sameGender.includes(x));
  return [...sibling, ...sameGender, ...rest].slice(0, 14).map((x) => ({ label: rankedLabel(x, l), href: rankedUrl(x, l) }));
}

export { genderInfo, brandByName };
