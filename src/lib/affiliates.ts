/**
 * Affiliate shops ("voir le prix"). Each shop in src/data/affiliates.json lists the locales it serves,
 * its network click URL (deep link prefix) and a search URL template. Links point to a search for the
 * perfume on the shop, so they never claim a price or a stock we have not checked.
 * Add a shop only once its programme has accepted the site.
 */
import data from '../data/affiliates.json';
import type { Locale } from '../i18n';

export interface Shop { id: string; name: string; locales: string[]; click: string; search: string }

const shops = data.shops as Shop[];

export const shopsFor = (l: Locale) => shops.filter((s) => s.locales.includes(l));

export function shopLink(s: Shop, query: string): string {
  const target = s.search.replace('{q}', encodeURIComponent(query).replace(/%20/g, '+'));
  return s.click + encodeURIComponent(target);
}
