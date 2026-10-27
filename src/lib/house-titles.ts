/**
 * Title and meta description of house pages, written for clicks on brand queries
 * ("parfum guerlain", "versace perfume"). See seo/titres-top50.md for the reasoning:
 * query words first, "meilleurs/best" (SearchPilot +11% on listing pages), two famous
 * names the searcher recognises, a count, 40 to 60 characters, no separators or brackets.
 */
import type { Locale } from '../i18n';
import type { Perfume } from './catalog';
import popularity from '../data/perfume-popularity.json';

const pop = popularity as Record<string, number>;

/** Best-known perfumes per house as [label shown in the title, name in perfumes.json]. */
const ICONS: Record<string, [string, string][]> = {
  Guerlain: [['Shalimar', 'Shalimar'], ['Mon Guerlain', 'Mon Guerlain']],
  Versace: [['Eros', 'Eros'], ['Dylan Blue', 'Dylan Blue Pour Homme']],
  'Paco Rabanne': [['1 Million', '1 Million'], ['Invictus', 'Invictus']],
  'Tom Ford': [['Tobacco Vanille', 'Tobacco Vanille'], ['Ombre Leather', 'Ombre Leather']],
  'Initio Parfums Privés': [['Oud for Greatness', 'Oud for Greatness'], ['Side Effect', 'Side Effect']],
  Gucci: [['Bloom', 'Bloom'], ['Guilty', 'Guilty']],
  'Issey Miyake': [["L'Eau d'Issey", "L'Eau d'Issey"]],
  Azzaro: [['Wanted', 'Wanted'], ['Chrome', 'Chrome']],
  Prada: [['Luna Rossa', 'Luna Rossa'], ['Paradoxe', 'Paradoxe']],
  Mugler: [['Angel', 'Angel'], ['Alien', 'Alien']],
  Creed: [['Aventus', 'Aventus'], ['Green Irish Tweed', 'Green Irish Tweed']],
  Davidoff: [['Cool Water', 'Cool Water']],
  Nishane: [['Hacivat', 'Hacivat'], ['Ani', 'Ani']],
  Mancera: [['Instant Crush', 'Instant Crush'], ['Cedrat Boise', 'Cedrat Boise']],
  'Elizabeth Taylor': [['White Diamonds', 'White Diamonds']],
  'Estée Lauder': [['Youth Dew', 'Youth Dew'], ['Beautiful', 'Beautiful']],
  'Britney Spears': [['Fantasy', 'Fantasy']],
  'Maison Francis Kurkdjian': [['Baccarat Rouge 540', 'Baccarat Rouge 540']],
  Byredo: [['Gypsy Water', 'Gypsy Water'], ['Mojave Ghost', 'Mojave Ghost']],
  'Hugo Boss': [['Boss Bottled', 'Boss Bottled'], ['The Scent', 'Boss The Scent']],
  'Carolina Herrera': [['Good Girl', 'Good Girl'], ['212 VIP', '212 VIP']],
  Chanel: [['N°5', 'N°5'], ['Bleu de Chanel', 'Bleu de Chanel']],
  Dior: [['Sauvage', 'Sauvage'], ["J'adore", "J'adore"]],
  'Lancôme': [['La Vie Est Belle', 'La Vie Est Belle'], ['Idôle', 'Idôle']],
  'Yves Saint Laurent': [['Libre', 'Libre'], ['Black Opium', 'Black Opium']],
  Givenchy: [["L'Interdit", "L'Interdit"], ['Gentleman', 'Gentleman']],
  'Nina Ricci': [['Nina', 'Nina'], ["L'Air du Temps", "L'Air du Temps"]],
  Cerruti: [['1881', '1881']],
  'Hermès': [["Terre d'Hermès", "Terre d'Hermès"], ['Twilly', "Twilly d'Hermès"]],
  'Jean Paul Gaultier': [['Le Mâle', 'Le Mâle'], ['Scandal', 'Scandal']],
  'Giorgio Armani': [['Acqua di Gio', 'Acqua di Gio'], ['Sì', 'Sì']],
  Kenzo: [['Flower by Kenzo', 'Flower by Kenzo']],
  Cacharel: [['Anaïs Anaïs', 'Anaïs Anaïs'], ['Amor Amor', 'Amor Amor']],
  Rochas: [['Eau de Rochas', 'Eau de Rochas'], ['Tocade', 'Tocade']],
  'Parfums de Marly': [['Layton', 'Layton'], ['Delina', 'Delina']],
  'Marc Jacobs': [['Daisy', 'Daisy']],
  'Narciso Rodriguez': [['For Her', 'Narciso Rodriguez for Her']],
  Clinique: [['Happy', 'Happy'], ['Aromatics Elixir', 'Aromatics Elixir']],
  'Viktor & Rolf': [['Flowerbomb', 'Flowerbomb'], ['Spicebomb', 'Spicebomb']],
  Valentino: [['Born in Roma', 'Donna Born in Roma']],
  'Dolce & Gabbana': [['Light Blue', 'Light Blue'], ['The One', 'The One']],
  Burberry: [['Her', 'Her'], ['Brit', 'Brit for Her']],
  'Calvin Klein': [['CK One', 'CK One'], ['Eternity', 'Eternity']],
  Montblanc: [['Legend', 'Legend']],
  Xerjoff: [['Naxos', 'Naxos']],
  'Lolita Lempicka': [['Le Premier Parfum', 'Le Premier Parfum']],
  'By Kilian': [["Love Don't Be Shy", "Love Don't Be Shy"], ["Angels' Share", "Angels' Share"]],
  Amouage: [['Interlude Man', 'Interlude Man'], ['Reflection Man', 'Reflection Man']],
  Diptyque: [['Philosykos', 'Philosykos'], ['Tam Dao', 'Tam Dao']],
  'Le Labo': [['Santal 33', 'Santal 33']],
  'Serge Lutens': [['Chergui', 'Chergui'], ['Ambre Sultan', 'Ambre Sultan']],
  Repetto: [['Dance with Repetto', 'Dance with Repetto']],
};

/** The house's best-known published perfumes: curated icons first, then search volume. */
function icons(brand: string, list: Perfume[]): string[] {
  const names = new Set(list.map((p) => p.name));
  const out = (ICONS[brand] ?? []).filter(([, name]) => names.has(name)).map(([label]) => label);
  const rest = list
    .filter((p) => !out.includes(p.name) && !(ICONS[brand] ?? []).some(([, n]) => n === p.name))
    .sort((a, b) => (pop[b.slug] ?? 0) - (pop[a.slug] ?? 0));
  for (const p of rest) if (out.length < 2) out.push(p.name);
  return out;
}

const MAX = 60;
/** Shorter name people actually type, where the official one eats the whole title. */
const SHORT: Record<string, string> = { 'Initio Parfums Privés': 'Initio' };

export function houseTitle(house: string, list: Perfume[], l: Locale): string {
  const fr = l === 'fr';
  const n = list.length;
  const [a, b] = icons(house, list);
  const brand = SHORT[house] ?? house;
  if (n >= 5) {
    const candidates = fr
      ? [`Meilleurs parfums ${brand} : ${a}, ${b} et ${n - 2} autres`, `Meilleurs parfums ${brand} : ${a} et ${n - 1} autres`, `${brand} : ${a} et ${n - 1} autres parfums`, `${brand} : ${a} et ${n - 1} autres`, `Meilleurs parfums ${brand} : les ${n} par année`, `Parfums ${brand} : les ${n} par année`]
      : [`Best ${brand} Perfumes: ${a}, ${b} and ${n - 2} More`, `Best ${brand} Perfumes: ${a} and ${n - 1} More`, `${brand}: ${a} and ${n - 1} More Perfumes`, `${brand}: ${a} and ${n - 1} More`, `Best ${brand} Perfumes: All ${n} by Year`, `${brand} Perfumes: ${n} by Year`];
    return candidates.find((t) => t.length <= MAX) ?? candidates[candidates.length - 1];
  }
  if (n >= 2) {
    const candidates = fr
      ? [`Parfums ${brand} : ${a} et ${b}, notes et avis`, `Parfums ${brand} : ${a} et ${b}`, `Parfums ${brand} : notes et avis`]
      : [`${brand} Perfumes: ${a} and ${b}, Notes and Reviews`, `${brand} Perfumes: ${a} and ${b}`, `${brand} Perfumes: Notes and Reviews`];
    return candidates.find((t) => t.length <= MAX) ?? candidates[candidates.length - 1];
  }
  const candidates = fr ? [`Parfum ${brand} : ${a}, notes et avis`, `Parfum ${brand} : notes et avis`] : [`${brand} Perfume: ${a} Notes and Review`, `${brand} Perfume: Notes and Review`];
  return candidates.find((t) => t.length <= MAX) ?? candidates[candidates.length - 1];
}

export function houseDescription(brand: string, list: Perfume[], l: Locale): string {
  const fr = l === 'fr';
  const sorted = list.slice().sort((x, y) => x.year - y.year);
  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  const n = list.length;
  const genders = new Set(list.map((p) => p.gender));
  const forWhom = genders.size > 1 || genders.has('Unisex')
    ? (fr ? 'femme et homme' : 'for women and men')
    : genders.has('Feminine') ? (fr ? 'pour femme' : 'for women') : (fr ? 'pour homme' : 'for men');
  if (n === 1) {
    return fr
      ? `${first.name} de ${brand} (${first.year}) : notes de tête, de cœur et de fond, avis et parfums proches.`
      : `${first.name} by ${brand} (${first.year}): top, heart and base notes, our review and similar perfumes to try.`;
  }
  return fr
    ? `${n} parfums ${brand} ${forWhom} classés par année, de ${first.name} (${first.year}) à ${last.name} (${last.year}). Notes, avis et lequel choisir.`
    : `${n} ${brand} perfumes ${forWhom}, listed by year from ${first.name} (${first.year}) to ${last.name} (${last.year}). Notes, reviews and which one to pick.`;
}
