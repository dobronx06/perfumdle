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
/** Where the page sits in the section's navigation: by recipient, by taste, or buying advice. */
export type NoelGroup = 'who' | 'taste' | 'advice';
export interface NoelPage {
  kind: NoelKind; group?: NoelGroup; target: string; label: string;
  title: string; meta: string; h1: string; intro: string;
  sections: { title: string; body: string }[];
  picks?: string[]; why?: Record<string, string>; faq: Faq[]; sources: string[];
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
  { key: 'taste', title: 'Selon ses goûts' },
  { key: 'advice', title: 'Bien choisir et bien offrir' },
];
