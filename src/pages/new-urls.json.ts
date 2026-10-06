/**
 * URLs that went live in this build (drip-fed pages whose publish date is today) plus the hubs that
 * now link to them. The daily GitHub Action posts this list to IndexNow (Bing, Yandex, Seznam, Naver…)
 * once the deploy is live, so new pages reach Bing (and the AI answers built on it) the same morning.
 */
import type { APIRoute } from 'astro';
import { SITE, url } from '../lib/catalog';
import { buildDay, publishedToday } from '../lib/schedule';
import { rankedById, rankedUrl, parentOf, rankedBase, type RankedDef } from '../lib/ranked';

export const GET: APIRoute = () => {
  const urls = new Set<string>();
  for (const slug of publishedToday('similar')) {
    urls.add(url.similar('fr', slug)); urls.add(url.similar('en', slug));
    urls.add(url.perfume('fr', slug)); urls.add(url.perfume('en', slug)); // now links to its similar page
  }
  for (const id of publishedToday('ranked')) {
    const d = rankedById.get(id) as RankedDef | undefined;
    if (!d) continue;
    for (const l of ['fr', 'en'] as const) {
      urls.add(rankedUrl(d, l));
      urls.add(parentOf(d, l).href);
      if (d.kind === 'best' || d.kind === 'nose' || d.kind === 'guide') urls.add(rankedBase[d.kind](l));
    }
  }
  if (urls.size) { urls.add('/fr/'); urls.add('/en/'); urls.add('/llms.txt'); }
  const body = { date: buildDay, urls: [...urls].map((u) => `${SITE}${u}`) };
  return new Response(JSON.stringify(body, null, 1), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
