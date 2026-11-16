/**
 * Shop promotions (Black Friday, Cyber Monday) shown next to the buy buttons on EN pages.
 * src/data/promos.json holds the shops' own offers; a promo whose end has passed at build time is left out,
 * and the page script only reveals a promo between its start and end, so it appears and goes on time
 * between two daily rebuilds.
 */
import data from '../data/promos.json';
import { shopsFor, type Shop } from './affiliates';
import type { Locale } from '../i18n';

export interface Promo { shop: string; start: string; end: string; label: string; text: string; code?: string; dates: string }

const promos = (data.promos as Promo[]).filter((p) => Date.parse(p.end) > Date.now());

/** Promos still to come or running for these shops, with the shop they belong to. */
export function promosFor(l: Locale, shopIds?: string[]): { promo: Promo; shop: Shop }[] {
  const shops = shopsFor(l);
  return promos.flatMap((promo) => {
    const shop = shops.find((s) => s.id === promo.shop);
    return shop && (!shopIds || shopIds.includes(shop.id)) ? [{ promo, shop }] : [];
  });
}
