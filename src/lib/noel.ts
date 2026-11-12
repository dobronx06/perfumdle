/**
 * Christmas gift section (French only): /fr/cadeau-parfum/ (hub with the "Quel parfum offrir ?" quiz) and one page
 * per recipient, taste or buying question. Copy lives in src/data/noel/*.json and is linted with
 * scripts/lint_noel.py. Facts about perfumes (notes, year, perfumer) come from our own data files; no price,
 * promotion or coffret is announced unless an official brand page confirms it.
 * A page goes live on its date in publish-schedule.json → "noel".
 */
import type { Faq } from './catalog';
import { isPublished } from './schedule';

export type NoelKind = 'hub' | 'profile' | 'guide' | 'coffret';
/** Where the page sits in the section's navigation: by recipient, by age, by a perfume the person already loves,
 *  by taste, by style, or buying advice. */
export type NoelGroup = 'who' | 'age' | 'like' | 'taste' | 'style' | 'advice';
export interface NoelPage {
  kind: NoelKind; group?: NoelGroup; target: string; label: string;
  title: string; meta: string; h1: string; intro: string;
  sections: { title: string; body: string }[];
  picks?: string[]; why?: Record<string, string>; faq: Faq[]; sources: string[];
  /** "like" pages: the perfume the person already wears (its fiche and similar page are linked at the top). */
  about?: string;
  /** Hand-picked neighbouring pages of the section, shown as "À lire aussi" (only those already live). */
  related?: string[];
}

const files = import.meta.glob('../data/noel/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, NoelPage>>;
const all: Record<string, NoelPage> = {};
for (const content of Object.values(files)) Object.assign(all, content);

export const NOEL_HUB = 'hub';
export const NOEL_BASE = '/fr/cadeau-parfum/';
export const noelUrl = (slug: string) => (slug === NOEL_HUB ? NOEL_BASE : `${NOEL_BASE}${slug}/`);
export const noelLive = Object.keys(all).filter((s) => isPublished('noel', s));
export const noelPage = (slug: string) => all[slug];
export const isNoelLive = (slug: string) => noelLive.includes(slug);
export const noelOfGroup = (g: NoelGroup) => noelLive.filter((s) => all[s].group === g);
export const NOEL_GROUPS: { key: NoelGroup; title: string }[] = [
  { key: 'who', title: 'Un parfum pour qui ?' },
  { key: 'age', title: 'Selon son âge' },
  { key: 'like', title: 'Il ou elle aime déjà un parfum' },
  { key: 'taste', title: 'Selon ses goûts' },
  { key: 'style', title: 'Selon son style' },
  { key: 'advice', title: 'Bien choisir et bien offrir' },
];
