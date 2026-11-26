/**
 * /go/<shop>/<perfume-slug>/ and /go/<shop>/ : the site's affiliate links.
 *
 * Only a real click on a perfumdle.com page is redirected straight to the tracked CJ or Awin link.
 * CJ counted 8,418 clicks between Nov 7 and 26, 2026 against about 23 real ones: scrapers that pose as
 * Chrome still requested /go/ URLs, and every request became a click without a sale at the shop.
 *
 * A click from one of our pages is a top-level navigation that the browser marks as same-origin and
 * user-activated (Sec-Fetch-Site / Sec-Fetch-Mode / Sec-Fetch-User, sent by Chrome, Edge, Firefox and
 * Safari 16.4+), or, on browsers without these headers, carries a perfumdle.com Referer.
 * Anything else (scrapers, prefetchers, a link pasted in a chat) gets a small page with a button.
 * The button posts the form back here, which redirects: no affiliate URL is ever written in that page,
 * so a crawler reading it has nothing to follow. robots.txt disallows /go/, and known bots get plain text.
 * Only links from src/data/affiliate-offers.json and the shops' home links are ever redirected to.
 */
import offers from '../../src/data/affiliate-offers.json';
import affiliates from '../../src/data/affiliates.json';

const BOT = /bot|crawl|spider|slurp|preview|scan|fetch|monitor|headless|python|curl|wget|httpclient|facebookexternalhit|embedly|whatsapp|telegram|discord|skype|bitly|mediapartners|adsbot|lighthouse|pagespeed|google-|apis-google/i;
const TRACKED = /^https:\/\/www\.(?:(?:jdoqocy|kqzyfj|dpbolvw|anrdoezrs|tkqlhce)\.(?:com|net)\/click-|awin1\.com\/(?:pclick|cread)\.php\?)/;
const HOSTS = new Set(['perfumdle.com', 'www.perfumdle.com']);

/** The shop's home page through its CJ click prefix (taken from one of its tracked offers). */
function homeLink(shopId) {
  const shop = affiliates.shops.find((s) => s.id === shopId);
  if (shop?.network === 'awin' && shop.home) {
    return `https://www.awin1.com/cread.php?awinmid=${shop.awin_advertiser}&awinaffid=3135609&ued=${encodeURIComponent(shop.home)}`;
  }
  const any = Object.values(offers.shops[shopId] ?? {}).find((o) => TRACKED.test(o.url));
  if (!shop?.home || !any) return null;
  return `${any.url.split('?url=')[0]}?url=${encodeURIComponent(shop.home)}`;
}

const fromOurSite = (value) => {
  try { return HOSTS.has(new URL(value).hostname); } catch { return false; }
};

/** A click on one of our pages (GET) or on the button of the page below (POST from our origin). */
function isRealClick(request) {
  const h = request.headers;
  const site = h.get('Sec-Fetch-Site');
  if (request.method === 'POST') {
    return (site === 'same-origin' || (!site && fromOurSite(h.get('Origin') ?? h.get('Referer') ?? '')));
  }
  if (site) {
    return site === 'same-origin' && h.get('Sec-Fetch-Mode') === 'navigate' && h.get('Sec-Fetch-User') === '?1';
  }
  return fromOurSite(h.get('Referer') ?? '');
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

function confirmPage(shopName, fr) {
  const title = fr ? `Continuer vers ${shopName}` : `Continue to ${shopName}`;
  return `<!doctype html><html lang="${fr ? 'fr' : 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>${esc(title)}</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#F6F2EC;color:#1E1A16;font:16px/1.5 system-ui,sans-serif}main{max-width:26rem;padding:2rem;text-align:center}button{margin-top:1rem;padding:.8rem 1.4rem;border:0;border-radius:999px;background:#2E6B3E;color:#fff;font:600 1rem system-ui,sans-serif;cursor:pointer}a{color:inherit}</style></head>
<body><main><p>${fr ? 'Ce lien mène à la boutique' : 'This link leads to the shop'} <strong>${esc(shopName)}</strong>.</p>
<form method="post"><button type="submit">${esc(title)}</button></form>
<p><small>${fr ? 'Lien affilié : Perfumdle peut toucher une commission, sans surcoût pour vous.' : 'Affiliate link: Perfumdle may earn a commission at no extra cost to you.'} <a href="/${fr ? 'fr' : 'en'}/">Perfumdle</a></small></p></main></body></html>`;
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
  if (request.method !== 'GET' && request.method !== 'POST') {
    return new Response(null, { status: 405, headers: { ...headers, Allow: 'GET, POST' } });
  }
  if (isRealClick(request)) {
    return new Response(null, { status: request.method === 'POST' ? 303 : 302, headers: { ...headers, Location: target } });
  }
  const shop = affiliates.shops.find((s) => s.id === shopId);
  const fr = /^fr\b/i.test(request.headers.get('Accept-Language') ?? '') || shop?.locales?.join() === 'fr';
  return new Response(confirmPage(shop?.name ?? shopId, fr), {
    status: 200,
    headers: { ...headers, 'Content-Type': 'text/html; charset=utf-8', 'Referrer-Policy': 'same-origin' },
  });
}
