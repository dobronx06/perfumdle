/**
 * Hand-written <title> and meta description per perfume fiche (src/data/seo-titles/*.json), chosen from what
 * people actually search for that perfume (HaloScan keyword variants, Nov 2026): notes for one, "avis" or the
 * flanker difference for another, the perfumes that smell alike for a third. A fiche without an entry keeps the
 * generic template in PerfumeView.astro.
 */
type Entry = { title: string; meta: string };
type PerfumeSeo = { fr?: Entry; en?: Entry; angle?: string };
const files = import.meta.glob('../data/seo-titles/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, PerfumeSeo>>;
const all: Record<string, PerfumeSeo> = {};
for (const content of Object.values(files)) Object.assign(all, content);
export const perfumeSeo = (slug: string, lang: 'fr' | 'en'): Entry | undefined => all[slug]?.[lang];
