/**
 * Catalog — single source of truth for every content page.
 * Merges the perfume dataset (src/data/perfumes.json, built by scripts/prepare_data.py)
 * with the editorial JSON files in src/data/editorial/.
 */
import perfumesRaw from '../data/perfumes.json';
import type { Locale } from '../i18n';

export const SITE = 'https://perfumdle.com';

/* ------------------------------------------------------------------ types */

export interface Faq { q: string; a: string }

export interface Perfume {
  id: number;
  slug: string;
  name: string;
  brand: string;
  year: number;
  gender: 'Feminine' | 'Masculine' | 'Unisex';
  family: string;
  families: string[];
  concentration: string;
  notes: { top: string[]; heart: string[]; base: string[] };
  image: string | null;
}

export interface PerfumeEditorial {
  perfumer: string | null;
  seasons: string[];
  occasions: string[];
  intensity: number;
  fr: { tagline: string; story: string; wear: string; verdict: string };
  en: { tagline: string; story: string; wear: string; verdict: string };
}

type Localized<T> = { fr: T; en: T };

interface NoteText { title: string; meta: string; h1: string; intro: string; smell: string; origin: string; craft: string; wear: string; faq: Faq[] }
export interface NoteEditorial extends Localized<NoteText> {
  slug_fr: string; slug_en: string; name_fr: string; name_en: string; category: string; source: string;
}

interface BrandText { title: string; meta: string; intro: string; history: string; signature: string; howToChoose: string; faq: Faq[] }
export interface BrandEditorial extends Localized<BrandText> {
  slug: string; country: string | null; founded: number | null; founder: string | null; type: string;
}

interface HubText { title: string; meta: string; h1: string; intro: string; body?: string; history?: string; subfamilies?: string; howToWear?: string; context?: string; faq: Faq[] }
export interface HubEditorial extends Localized<HubText> { slug_fr: string; slug_en: string; name_fr?: string; name_en?: string }

/* --------------------------------------------------------------- editorial */

const files = import.meta.glob('../data/editorial/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, unknown>>;

function mergeFiles(prefix: string): Record<string, any> {
  const out: Record<string, any> = {};
  for (const [path, content] of Object.entries(files)) {
    const base = path.split('/').pop()!;
    if (!base.startsWith(prefix)) continue;
    for (const [k, v] of Object.entries(content)) if (!k.startsWith('_')) out[k] = v;
  }
  return out;
}

const perfumeEd: Record<string, PerfumeEditorial> = mergeFiles('perfumes-');
const noteEd: Record<string, NoteEditorial> = mergeFiles('notes-');
const brandEd: Record<string, BrandEditorial> = mergeFiles('brands-');
const hubs: any = mergeFiles('hubs');
/** FR names for rare notes that have no page of their own. */
const noteNamesFr: Record<string, string> = mergeFiles('note-names');

/* ----------------------------------------------------------------- helpers */

export function slugify(s: string): string {
  return s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export const perfumes: Perfume[] = (perfumesRaw as Perfume[]).slice();
export const perfumeBySlug = new Map(perfumes.map((p) => [p.slug, p]));

export function perfumeEditorial(slug: string): PerfumeEditorial | undefined {
  return perfumeEd[slug];
}

export function allNotes(p: Perfume): string[] {
  return [...new Set([...p.notes.top, ...p.notes.heart, ...p.notes.base])];
}

/* ------------------------------------------------------------------ routes */

/** Localized path segments. FR is the primary market. */
export const SEG = {
  fr: { game: 'jeu', perfumes: 'parfums', perfume: 'parfum', brands: 'marques', notes: 'notes', families: 'familles', eras: 'epoques', guides: 'guides' },
  en: { game: 'game', perfumes: 'perfumes', perfume: 'parfum', brands: 'houses', notes: 'notes', families: 'families', eras: 'eras', guides: 'guides' },
} as const;

export const url = {
  home: (l: Locale) => `/${l}/`,
  game: (l: Locale) => `/${l}/${SEG[l].game}/`,
  perfumes: (l: Locale) => `/${l}/${SEG[l].perfumes}/`,
  perfume: (l: Locale, slug: string) => `/${l}/${SEG[l].perfume}/${slug}/`,
  brands: (l: Locale) => `/${l}/${SEG[l].brands}/`,
  brand: (l: Locale, brand: string) => `/${l}/${SEG[l].brands}/${brandSlug(brand)}/`,
  notes: (l: Locale) => `/${l}/${SEG[l].notes}/`,
  note: (l: Locale, note: string) => `/${l}/${SEG[l].notes}/${noteSlug(note, l)}/`,
  families: (l: Locale) => `/${l}/${SEG[l].families}/`,
  family: (l: Locale, key: string) => `/${l}/${SEG[l].families}/${familyInfo(key)[l === 'fr' ? 'slug_fr' : 'slug_en']}/`,
  eras: (l: Locale) => `/${l}/${SEG[l].eras}/`,
  era: (l: Locale, decade: number) => `/${l}/${SEG[l].eras}/${eraSlug(decade, l)}/`,
  gender: (l: Locale, g: string) => `/${l}/${genderInfo(g)[l === 'fr' ? 'slug_fr' : 'slug_en']}/`,
  season: (l: Locale, s: string) => `/${l}/${seasonInfo(s)[l === 'fr' ? 'slug_fr' : 'slug_en']}/`,
  similar: (l: Locale, slug: string) => `/${l}/${l === 'fr' ? 'parfums-similaires' : 'similar-perfumes'}/${slug}/`,
};

/* ------------------------------------------------------------------ brands */

export function brandSlug(brand: string): string {
  return brandEd[brand]?.slug ?? slugify(brand);
}

export interface Brand { name: string; slug: string; perfumes: Perfume[]; ed?: BrandEditorial }

export const brands: Brand[] = (() => {
  const map = new Map<string, Perfume[]>();
  for (const p of perfumes) map.set(p.brand, [...(map.get(p.brand) ?? []), p]);
  return [...map.entries()]
    .map(([name, list]) => ({ name, slug: brandSlug(name), perfumes: list.sort((a, b) => a.year - b.year), ed: brandEd[name] }))
    .sort((a, b) => a.name.localeCompare(b.name, 'fr'));
})();

export const brandByName = new Map(brands.map((b) => [b.name, b]));

/* ------------------------------------------------------------------- notes */

/** Notes with at least this many perfumes get their own page. */
export const NOTE_PAGE_MIN = 4;

const noteCount = new Map<string, number>();
for (const p of perfumes) for (const n of allNotes(p)) noteCount.set(n, (noteCount.get(n) ?? 0) + 1);

export function hasNotePage(note: string): boolean {
  return (noteCount.get(note) ?? 0) >= NOTE_PAGE_MIN && note !== 'Woody Notes';
}

export function noteName(note: string, l: Locale): string {
  const ed = noteEd[note];
  if (ed) return l === 'fr' ? ed.name_fr : ed.name_en;
  return l === 'fr' ? noteNamesFr[note] ?? note : note;
}

export function noteSlug(note: string, l: Locale): string {
  const ed = noteEd[note];
  return ed ? (l === 'fr' ? ed.slug_fr : ed.slug_en) : slugify(note);
}

export interface Note { key: string; perfumes: Perfume[]; ed?: NoteEditorial; category: string }

export const notes: Note[] = [...noteCount.keys()]
  .filter(hasNotePage)
  .map((key) => ({
    key,
    perfumes: perfumes.filter((p) => allNotes(p).includes(key)),
    ed: noteEd[key],
    category: noteEd[key]?.category ?? 'other',
  }))
  .sort((a, b) => b.perfumes.length - a.perfumes.length);

export const noteByKey = new Map(notes.map((n) => [n.key, n]));

/** Notes that most often appear together with `note` (co-occurrence). */
export function pairedNotes(note: string, limit = 8): { key: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const p of perfumes) {
    const ns = allNotes(p);
    if (!ns.includes(note)) continue;
    for (const n of ns) if (n !== note && hasNotePage(n)) counts.set(n, (counts.get(n) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit).map(([key, count]) => ({ key, count }));
}

/** Most frequent notes across a set of perfumes. */
export function topNotes(list: Perfume[], limit = 10): { key: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const p of list) for (const n of allNotes(p)) if (hasNotePage(n)) counts.set(n, (counts.get(n) ?? 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit).map(([key, count]) => ({ key, count }));
}

/* ---------------------------------------------------------------- families */

const FAMILY_DEFAULTS: Record<string, { fr: string; en: string; slug_fr: string; slug_en: string }> = {
  floral: { fr: 'Floral', en: 'Floral', slug_fr: 'floral', slug_en: 'floral' },
  oriental: { fr: 'Oriental / Ambré', en: 'Oriental / Amber', slug_fr: 'oriental-ambre', slug_en: 'oriental-amber' },
  woody: { fr: 'Boisé', en: 'Woody', slug_fr: 'boise', slug_en: 'woody' },
  chypre: { fr: 'Chypré', en: 'Chypre', slug_fr: 'chypre', slug_en: 'chypre' },
  fougere: { fr: 'Fougère', en: 'Fougère', slug_fr: 'fougere', slug_en: 'fougere' },
  citrus: { fr: 'Hespéridé', en: 'Citrus', slug_fr: 'hesperide', slug_en: 'citrus' },
  gourmand: { fr: 'Gourmand', en: 'Gourmand', slug_fr: 'gourmand', slug_en: 'gourmand' },
  leather: { fr: 'Cuir', en: 'Leather', slug_fr: 'cuir', slug_en: 'leather' },
  aquatic: { fr: 'Aquatique', en: 'Aquatic', slug_fr: 'aquatique', slug_en: 'aquatic' },
  aromatic: { fr: 'Aromatique', en: 'Aromatic', slug_fr: 'aromatique', slug_en: 'aromatic' },
  fruity: { fr: 'Fruité', en: 'Fruity', slug_fr: 'fruite', slug_en: 'fruity' },
  spicy: { fr: 'Épicé', en: 'Spicy', slug_fr: 'epice', slug_en: 'spicy' },
  musky: { fr: 'Musqué', en: 'Musky', slug_fr: 'musque', slug_en: 'musky' },
  powdery: { fr: 'Poudré', en: 'Powdery', slug_fr: 'poudre', slug_en: 'powdery' },
  green: { fr: 'Vert', en: 'Green', slug_fr: 'vert', slug_en: 'green' },
};

/** Soft tint per family — flacon shots (white bg) are blended onto it with mix-blend-mode: multiply. */
export const FAMILY_TINT: Record<string, string> = {
  floral: '#F3DCDC', oriental: '#EFD9BF', woody: '#DDD5C8', chypre: '#D9DECB', fougere: '#DCDAE8',
  citrus: '#F2E9C4', gourmand: '#EAD3C0', leather: '#D9C6B4', aquatic: '#D3E1E6', aromatic: '#D8E2D3',
  fruity: '#F2D8CF', spicy: '#EBCDBE', musky: '#E9E1DC', powdery: '#EADDE6', green: '#D5E3CD',
};

export function familyInfo(key: string) {
  const ed = hubs.families?.[key] as HubEditorial | undefined;
  const d = FAMILY_DEFAULTS[key];
  return {
    key,
    name_fr: ed?.name_fr ?? d.fr,
    name_en: ed?.name_en ?? d.en,
    slug_fr: ed?.slug_fr ?? d.slug_fr,
    slug_en: ed?.slug_en ?? d.slug_en,
    tint: FAMILY_TINT[key],
    ed,
  };
}

export function familyName(key: string, l: Locale) {
  const f = familyInfo(key);
  return l === 'fr' ? f.name_fr : f.name_en;
}

/** Families with at least 5 perfumes get a page. */
export const families = Object.keys(FAMILY_DEFAULTS)
  .map((key) => ({ ...familyInfo(key), perfumes: perfumes.filter((p) => p.families.includes(key)) }))
  .filter((f) => f.perfumes.length >= 5)
  .sort((a, b) => b.perfumes.length - a.perfumes.length);

/** One distinct cover image per family (first famous perfume whose primary family matches, never reused). */
export const familyCover: Record<string, string | undefined> = (() => {
  const used = new Set<string>();
  const out: Record<string, string | undefined> = {};
  for (const f of families) {
    const pick = f.perfumes.find((p) => p.image && p.families[0] === f.key && !used.has(p.image))
      ?? f.perfumes.find((p) => p.image && !used.has(p.image));
    if (pick?.image) used.add(pick.image);
    out[f.key] = pick?.image ?? undefined;
  }
  return out;
})();

export function hasFamilyPage(key: string): boolean {
  return families.some((f) => f.key === key);
}

export function tintFor(p: Perfume): string {
  return FAMILY_TINT[p.families[0]] ?? '#E9E3DA';
}

/** Translate the raw dataset family label ("Oriental Woody") word by word. */
const FAMILY_WORDS_FR: Record<string, string> = {
  Floral: 'Floral', Oriental: 'Oriental', Woody: 'Boisé', Chypre: 'Chypré', 'Fougère': 'Fougère', Citrus: 'Hespéridé',
  Gourmand: 'Gourmand', Leather: 'Cuir', Aquatic: 'Aquatique', Marine: 'Marin', Aromatic: 'Aromatique', Fruity: 'Fruité',
  Spicy: 'Épicé', Musk: 'Musqué', Musky: 'Musqué', Powdery: 'Poudré', Green: 'Vert', Aldehyde: 'Aldéhydé', Amber: 'Ambré',
  Ambery: 'Ambré', Vanilla: 'Vanillé', Sweet: 'Sucré', Fresh: 'Frais',
};
export function familyLabel(raw: string, l: Locale): string {
  if (l === 'en') return raw;
  return raw.split(' ').map((w) => FAMILY_WORDS_FR[w] ?? w).join(' ');
}

/* -------------------------------------------------------------------- eras */

export function decadeOf(year: number) { return Math.floor(year / 10) * 10; }

export function eraSlug(decade: number, l: Locale): string {
  const ed = hubs.decades?.[String(decade)] as HubEditorial | undefined;
  if (ed) return l === 'fr' ? ed.slug_fr : ed.slug_en;
  return l === 'fr' ? `annees-${decade}` : `${decade}s`;
}

export function eraName(decade: number, l: Locale): string {
  return l === 'fr' ? `Années ${decade}` : `The ${decade}s`;
}

export const eras = [...new Set(perfumes.map((p) => decadeOf(p.year)))]
  .sort((a, b) => a - b)
  .map((decade) => ({
    decade,
    perfumes: perfumes.filter((p) => decadeOf(p.year) === decade).sort((a, b) => a.year - b.year),
    ed: hubs.decades?.[String(decade)] as HubEditorial | undefined,
  }));

/* ------------------------------------------------------ genders & seasons */

const GENDER_DEFAULTS: Record<string, { slug_fr: string; slug_en: string; fr: string; en: string }> = {
  Feminine: { slug_fr: 'parfums-femme', slug_en: 'womens-perfumes', fr: 'Parfums femme', en: "Women's perfumes" },
  Masculine: { slug_fr: 'parfums-homme', slug_en: 'mens-perfumes', fr: 'Parfums homme', en: "Men's perfumes" },
  Unisex: { slug_fr: 'parfums-mixtes', slug_en: 'unisex-perfumes', fr: 'Parfums mixtes', en: 'Unisex perfumes' },
};

export function genderInfo(g: string) {
  const ed = hubs.genders?.[g] as HubEditorial | undefined;
  const d = GENDER_DEFAULTS[g];
  return { key: g, slug_fr: ed?.slug_fr ?? d.slug_fr, slug_en: ed?.slug_en ?? d.slug_en, name_fr: d.fr, name_en: d.en, ed };
}

export const genders = Object.keys(GENDER_DEFAULTS).map((g) => ({ ...genderInfo(g), perfumes: perfumes.filter((p) => p.gender === g) }));

const SEASON_DEFAULTS: Record<string, { slug_fr: string; slug_en: string; fr: string; en: string }> = {
  spring: { slug_fr: 'parfums-printemps', slug_en: 'spring-perfumes', fr: 'Parfums de printemps', en: 'Spring perfumes' },
  summer: { slug_fr: 'parfums-ete', slug_en: 'summer-perfumes', fr: "Parfums d'été", en: 'Summer perfumes' },
  autumn: { slug_fr: 'parfums-automne', slug_en: 'autumn-perfumes', fr: "Parfums d'automne", en: 'Autumn perfumes' },
  winter: { slug_fr: 'parfums-hiver', slug_en: 'winter-perfumes', fr: "Parfums d'hiver", en: 'Winter perfumes' },
};

export function seasonInfo(s: string) {
  const ed = hubs.seasons?.[s] as HubEditorial | undefined;
  const d = SEASON_DEFAULTS[s];
  return { key: s, slug_fr: ed?.slug_fr ?? d.slug_fr, slug_en: ed?.slug_en ?? d.slug_en, name_fr: d.fr, name_en: d.en, ed };
}

export const seasons = Object.keys(SEASON_DEFAULTS).map((s) => ({
  ...seasonInfo(s),
  perfumes: perfumes.filter((p) => perfumeEd[p.slug]?.seasons?.includes(s)),
}));

export function homeEditorial(l: Locale): any {
  return hubs.home?.[l];
}

/* -------------------------------------------------------------- similarity */

const IDF = new Map<string, number>();
for (const [n, c] of noteCount) IDF.set(n, Math.log(perfumes.length / c));

/** Weighted similarity: rare shared notes count more, plus family / gender / era bonus. */
export function similarity(a: Perfume, b: Perfume): number {
  const na = new Set(allNotes(a));
  let score = 0;
  for (const n of allNotes(b)) if (na.has(n)) score += IDF.get(n) ?? 1;
  const sharedFam = a.families.filter((f) => b.families.includes(f)).length;
  score += sharedFam * 1.2;
  if (a.family === b.family) score += 1.5;
  if (a.gender === b.gender) score += 0.6;
  return score;
}

export function similarPerfumes(p: Perfume, limit = 8): { perfume: Perfume; shared: string[]; score: number }[] {
  const own = new Set(allNotes(p));
  return perfumes
    .filter((o) => o.slug !== p.slug)
    .map((o) => ({ perfume: o, score: similarity(p, o), shared: allNotes(o).filter((n) => own.has(n)) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

/* ------------------------------------------------------------------ labels */

export const GENDER_LABEL = {
  fr: { Feminine: 'Féminin', Masculine: 'Masculin', Unisex: 'Mixte' },
  en: { Feminine: 'Feminine', Masculine: 'Masculine', Unisex: 'Unisex' },
} as const;

export const SEASON_LABEL = {
  fr: { spring: 'Printemps', summer: 'Été', autumn: 'Automne', winter: 'Hiver' },
  en: { spring: 'Spring', summer: 'Summer', autumn: 'Autumn', winter: 'Winter' },
} as const;

export const OCCASION_LABEL = {
  fr: { day: 'Journée', office: 'Bureau', evening: 'Soirée', date: 'Rendez-vous', casual: 'Décontracté', special: 'Grandes occasions' },
  en: { day: 'Daytime', office: 'Office', evening: 'Evening', date: 'Date night', casual: 'Casual', special: 'Special occasions' },
} as const;

export const CONCENTRATION_FR: Record<string, string> = {
  'Eau de Parfum': 'Eau de Parfum', 'Eau de Toilette': 'Eau de Toilette', Parfum: 'Parfum (extrait)',
  'Extrait de Parfum': 'Extrait de Parfum', 'Eau de Cologne': 'Eau de Cologne', 'Cologne Absolue': 'Cologne Absolue',
};

/** Existing long-form guides (hand-written .astro pages under src/pages/[lang]/). */
export const GUIDES = [
  { slug: 'guide-familles-olfactives', fr: 'Les familles olfactives, le guide complet', en: 'The olfactory families: a complete guide' },
  { slug: 'difference-edp-edt-parfum', fr: 'Eau de parfum, eau de toilette : les différences', en: 'Eau de parfum vs eau de toilette' },
  { slug: 'histoire-parfums-par-decennie', fr: "Un siècle de parfums, décennie par décennie", en: 'A century of perfume, decade by decade' },
  { slug: 'parfums-maisons-niche-vs-designer', fr: 'Parfums de niche ou de créateur ?', en: 'Niche vs designer perfumes' },
  { slug: 'parfums-iconiques-chanel', fr: 'Les parfums iconiques de Chanel', en: 'Iconic Chanel perfumes' },
  { slug: 'parfums-iconiques-dior', fr: 'Les parfums iconiques de Dior', en: 'Iconic Dior perfumes' },
  { slug: 'parfums-orientaux-iconiques', fr: 'Les grands parfums orientaux', en: 'The great oriental perfumes' },
  { slug: 'parfums-chypres-histoire', fr: 'Le chypre, histoire d’une famille', en: 'The chypre: a family history' },
  { slug: 'parfums-gourmands-guide', fr: 'Le guide des parfums gourmands', en: 'The gourmand perfume guide' },
  { slug: 'parfums-unisexes-tendance', fr: 'Les parfums unisexes', en: 'Unisex perfumes' },
  { slug: 'guide-strategie-perfumdle', fr: 'Perfumdle : stratégie et astuces', en: 'Perfumdle strategy & tips' },
];
