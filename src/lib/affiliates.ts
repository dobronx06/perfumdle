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
/** Only a CJ click URL earns a commission: an offer pointing straight at the shop is never shown. */
const TRACKED = /^https:\/\/www\.(jdoqocy|kqzyfj|dpbolvw|anrdoezrs|tkqlhce)\.(com|net)\/click-/;

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
    return feed[slug] && TRACKED.test(feed[slug].url) ? [{ shop, offer: feed[slug] }] : [];
  });
  // Cheapest per ml first, so a 60 ml bottle does not pass for cheaper than a 100 ml one
  const unit = (o?: Offer) => (o ? (o.ml ? o.price / o.ml : o.price / 100) : Infinity);
  return list.sort((a, b) => unit(a.offer) - unit(b.offer));
}

const SIZES = [5, 7.5, 10, 15, 20, 30, 35, 40, 45, 50, 60, 65, 75, 80, 90, 100, 110, 120, 125, 150, 175, 180, 200];
/** The bottle size as sold (101 ml read from "3.4 oz" is a 100 ml bottle). */
export function bottleMl(ml: number | null | undefined): number | null {
  if (!ml) return null;
  const near = SIZES.reduce((a, b) => (Math.abs(b - ml) < Math.abs(a - ml) ? b : a));
  return Math.abs(near - ml) <= ml * 0.06 ? near : ml;
}

/** The on-site affiliate link (functions/go): crawlers are kept out by robots.txt, people get a 302 to CJ. */
export const goLink = (s: Shop, slug?: string) => (slug ? `/go/${s.id}/${slug}/` : `/go/${s.id}/`);

/** The cheapest tracked offer for a perfume in this locale, if any shop sells it. */
export function bestOffer(l: Locale, slug: string): { shop: Shop; offer: Offer } | undefined {
  const first = shopsForPerfume(l, slug)[0];
  return first?.offer ? { shop: first.shop, offer: first.offer } : undefined;
}

export function shopLink(s: Shop, query: string): string {
  const target = (s.search ?? '').replace('{q}', encodeURIComponent(query).replace(/%20/g, '+'));
  return (s.click ?? '') + encodeURIComponent(target);
}

export function formatPrice(o: Offer, l: Locale): string {
  return new Intl.NumberFormat(l === 'fr' ? 'fr-FR' : 'en-US', { style: 'currency', currency: o.currency }).format(o.price);
}
