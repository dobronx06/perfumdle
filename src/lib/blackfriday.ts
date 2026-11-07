/**
 * Black Friday section (French only): /fr/black-friday/ and one page per perfume, house, retailer or topic.
 * Copy and reference prices live in src/data/blackfriday/*.json. Every price comes from a dated source:
 * these are the prices to compare against on the day, never announced discounts.
 * A page goes live on its date in publish-schedule.json → "bf".
 */
import type { Faq } from './catalog';
import { isPublished } from './schedule';

export type BfKind = 'hub' | 'shop' | 'theme' | 'brand' | 'perfume';
export interface BfPrice { shop: string; item: string; price: string; seen: string; url: string }
export interface BfPage {
  kind: BfKind; target: string; perfume?: string; brand?: string;
  title: string; meta: string; h1: string; intro: string;
  prices?: BfPrice[]; sections: { title: string; body: string }[];
  picks?: string[]; why?: Record<string, string>; faq: Faq[]; sources: string[];
}

const files = import.meta.glob('../data/blackfriday/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, BfPage>>;
const all: Record<string, BfPage> = {};
for (const content of Object.values(files)) Object.assign(all, content);

export const BF_HUB = 'hub';
export const bfUrl = (slug: string) => (slug === BF_HUB ? '/fr/black-friday/' : `/fr/black-friday/${slug}/`);
export const bfLive = Object.keys(all).filter((s) => isPublished('bf', s));
export const bfPage = (slug: string) => all[slug];
export const isBfLive = (slug: string) => bfLive.includes(slug);
export const bfOfKind = (k: BfKind) => bfLive.filter((s) => all[s].kind === k);
/** Live page of a perfume's fiche or house, used for cross-links. */
export const bfForPerfume = (perfumeSlug: string) => (isBfLive(perfumeSlug) && all[perfumeSlug].kind === 'perfume' ? perfumeSlug : undefined);
