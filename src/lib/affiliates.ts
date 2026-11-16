/**
 * Affiliate shops ("voir le prix"). Each shop in src/data/affiliates.json lists the locales it serves,
 * its network click URL (deep link prefix) and a search URL template. Shops with "catalog": true are
 * matched daily against their product feed (scripts/affiliate_offers.py → affiliate-offers.json): once
 * that feed exists, the button only shows on perfumes the shop sells, with its price and product link.
 * Until then the button opens the shop's search for the perfume.
 * Add a shop only once its programme has accepted the site.
 */
import data from '../data/affiliates.json';
import offersData from '../data/affiliate-offers.json';
import type { Locale } from '../i18n';

export interface Shop { id: string; name: string; locales: string[]; click?: string; search?: string; catalog?: boolean }
export interface Offer { price: number; currency: string; ml: number | null; title: string; url: string }

const shops = data.shops as Shop[];
const offers = offersData as { generated: string | null; shops: Record<string, Record<string, Offer>> };

export const offersDate = offers.generated;
export const shopsFor = (l: Locale) => shops.filter((s) => s.locales.includes(l));

/**
 * The shops to show for a perfume, cheapest offer first. A catalogue shop shows only on perfumes its feed
 * sells; one whose feed has not been fetched yet falls back to its search link, or is hidden if it has none.
 */
export function shopsForPerfume(l: Locale, slug: string): { shop: Shop; offer?: Offer }[] {
  const list = shopsFor(l).flatMap((shop): { shop: Shop; offer?: Offer }[] => {
    const feed = shop.catalog ? offers.shops[shop.id] : undefined;
    if (!feed) return shop.click && shop.search ? [{ shop }] : [];
    return feed[slug] ? [{ shop, offer: feed[slug] }] : [];
  });
  return list.sort((a, b) => (a.offer?.price ?? Infinity) - (b.offer?.price ?? Infinity));
}

export function shopLink(s: Shop, query: string): string {
  const target = (s.search ?? '').replace('{q}', encodeURIComponent(query).replace(/%20/g, '+'));
  return (s.click ?? '') + encodeURIComponent(target);
}

export function formatPrice(o: Offer, l: Locale): string {
  return new Intl.NumberFormat(l === 'fr' ? 'fr-FR' : 'en-US', { style: 'currency', currency: o.currency }).format(o.price);
}
