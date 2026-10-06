/**
 * Cloudflare Pages middleware: permanent redirects that must hold whatever Pages does with public/_redirects
 * once a Function is present.
 * 1. One canonical host: www.perfumdle.com answered 200 and Google indexed both hosts (Search Console, Oct 2026).
 * 2. EN guides moved from French slugs to English slugs (Oct 2026). Same list as public/_redirects.
 * 3. "/" sends a real 302 to /fr/ or /en/ from Accept-Language (French by default, as x-default),
 *    instead of the meta-refresh page, which stays in public/index.html as a fallback.
 */
const MOVED = {
  'guide-familles-olfactives': 'olfactory-families-guide',
  'difference-edp-edt-parfum': 'edp-vs-edt-difference',
  'histoire-parfums-par-decennie': 'perfume-history-by-decade',
  'parfums-maisons-niche-vs-designer': 'niche-vs-designer-perfumes',
  'parfums-iconiques-chanel': 'iconic-chanel-perfumes',
  'parfums-iconiques-dior': 'iconic-dior-perfumes',
  'parfums-orientaux-iconiques': 'iconic-oriental-perfumes',
  'parfums-chypres-histoire': 'chypre-perfumes-history',
  'parfums-gourmands-guide': 'gourmand-perfumes-guide',
  'parfums-unisexes-tendance': 'unisex-perfumes-trend',
  'guide-strategie-perfumdle': 'perfumdle-strategy-guide',
};

export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  let changed = false;
  if (url.hostname === 'www.perfumdle.com') {
    url.hostname = 'perfumdle.com';
    changed = true;
  }
  const m = url.pathname.match(/^\/en\/([a-z0-9-]+)\/?$/);
  if (m && MOVED[m[1]]) {
    url.pathname = `/en/${MOVED[m[1]]}/`;
    changed = true;
  }
  if (changed) return Response.redirect(url.toString(), 301);
  if (url.pathname === '/') {
    const lang = /^en\b/i.test(request.headers.get('Accept-Language') ?? '') ? 'en' : 'fr';
    return Response.redirect(`${url.origin}/${lang}/`, 302);
  }
  return next();
}
