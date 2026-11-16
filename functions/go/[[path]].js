/**
 * /go/<shop>/<perfume-slug>/ and /go/<shop>/ : the site's affiliate links.
 * Buttons point here instead of straight at CJ so that crawlers, which follow every link, do not
 * inflate the CJ click count (1,953 CJ clicks against 17 real ones in Nov 2026): robots.txt disallows
 * /go/, and known bots get a page without redirect. People get a 302 to the tracked CJ link.
 * Only links from src/data/affiliate-offers.json and the shops' CJ home links are ever redirected to.
 */
import offers from '../../src/data/affiliate-offers.json';
import affiliates from '../../src/data/affiliates.json';

const BOT = /bot|crawl|spider|slurp|preview|scan|fetch|monitor|headless|python|curl|wget|httpclient|facebookexternalhit|embedly|whatsapp|telegram|discord|skype|bitly/i;
const TRACKED = /^https:\/\/www\.(jdoqocy|kqzyfj|dpbolvw|anrdoezrs|tkqlhce)\.(com|net)\/click-/;

/** The shop's home page through its CJ click prefix (taken from one of its tracked offers). */
function homeLink(shopId) {
  const shop = affiliates.shops.find((s) => s.id === shopId);
  const any = Object.values(offers.shops[shopId] ?? {}).find((o) => TRACKED.test(o.url));
  if (!shop?.home || !any) return null;
  return `${any.url.split('?url=')[0]}?url=${encodeURIComponent(shop.home)}`;
}

export async function onRequest({ request, params }) {
  const [shopId, slug] = (Array.isArray(params.path) ? params.path : [params.path]).filter(Boolean);
  const target = slug ? offers.shops[shopId]?.[slug]?.url : homeLink(shopId);
  const headers = { 'X-Robots-Tag': 'noindex, nofollow', 'Cache-Control': 'no-store' };
  if (!target || !TRACKED.test(target)) {
    return Response.redirect(new URL(slug ? `/en/parfum/${slug}/` : '/en/', request.url).toString(), 302);
  }
  if (BOT.test(request.headers.get('User-Agent') ?? '')) {
    return new Response('Affiliate link: open it in a browser.', { status: 200, headers: { ...headers, 'Content-Type': 'text/plain' } });
  }
  return new Response(null, { status: 302, headers: { ...headers, Location: target } });
}
