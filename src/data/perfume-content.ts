import type { Locale } from '../i18n';

/* ---- Root family extraction ---- */
export function getFamilyRoot(family: string): string {
  const w = family.split(/\s+/)[0];
  return w === 'Fougere' ? 'Fougere' : w;
}

/* ---- Family descriptions ---- */
const FAM: Record<string, Record<Locale, string>> = {
  Floral: {
    fr: "Les parfums floraux captent l'essence des fleurs — rose, jasmin, tubereuse, iris. Parmi les familles les plus anciennes de la parfumerie, ils vont du soliflore delicat au bouquet riche et enveloppant, et restent la famille la plus representee en parfumerie feminine.",
    en: "Floral perfumes capture the essence of flowers — rose, jasmine, tuberose, iris. Among the oldest fragrance families, they range from delicate soliflores to rich, enveloping bouquets, and remain the most represented family in feminine perfumery."
  },
  Oriental: {
    fr: "Les parfums orientaux se distinguent par leur richesse et leur chaleur sensuelle. Construits autour de notes ambrees, vanillees ou epicees, ils evoquent l'opulence et le mystere. Leur sillage genereux les rend ideaux pour les soirees et les saisons froides.",
    en: "Oriental perfumes stand out for their richness and sensual warmth. Built around amber, vanilla, or spicy notes, they evoke opulence and mystery. Their generous trail makes them ideal for evening wear and cold seasons."
  },
  Chypre: {
    fr: "La famille chypree, nee de la creation eponyme de Francois Coty en 1917, repose sur un accord bergamote-mousse de chene-labdanum. Ces parfums sont elegants, profonds et intemporels, prises par les connaisseurs de parfumerie.",
    en: "The chypre family, born from Francois Coty's 1917 creation, is built on a bergamot-oakmoss-labdanum accord. These fragrances are elegant, deep, and timeless, favored by perfume connoisseurs."
  },
  Woody: {
    fr: "Les parfums boises s'articulent autour du cedre, santal, vetiver ou oud. Ils offrent une structure solide et une allure sophistiquee, declines aussi bien en versions fraiches que chaleureuses et opaques.",
    en: "Woody perfumes revolve around cedar, sandalwood, vetiver, or oud. They provide solid structure and a sophisticated allure, available in both fresh and warm, opaque versions."
  },
  Fougere: {
    fr: "La famille fougere, nee de Fougere Royale (Houbigant, 1882), marie lavande, geranium et coumarine. Pilier de la parfumerie masculine classique, elle incarne la fraicheur maitrisee et l'elegance virile.",
    en: "The fougere family, born from Fougere Royale (Houbigant, 1882), blends lavender, geranium, and coumarin. A pillar of classic masculine perfumery, it embodies controlled freshness and virile elegance."
  },
  Gourmand: {
    fr: "Les parfums gourmands jouent sur des notes comestibles — vanille, caramel, chocolat, praline. Nes dans les annees 1990 avec Angel de Thierry Mugler, ils seduisent par leur cote reconfortant et addictif.",
    en: "Gourmand perfumes play on edible notes — vanilla, caramel, chocolate, praline. Born in the 1990s with Thierry Mugler's Angel, they seduce with their comforting, addictive character."
  },
  Aquatic: {
    fr: "Les parfums aquatiques evoquent l'ocean, la brise marine ou la pluie fraiche. Popularises dans les annees 1990 avec des succes comme L'Eau d'Issey, ils sont legers, modernes et universels.",
    en: "Aquatic perfumes evoke the ocean, sea breeze, or fresh rain. Popularized in the 1990s with hits like L'Eau d'Issey, they are light, modern, and universal."
  },
  Citrus: {
    fr: "Les parfums hesperides s'ouvrent sur des agrumes vifs — bergamote, citron, orange, pamplemousse. Ils incarnent la fraicheur et l'energie, parfaits pour le quotidien et les journees chaudes.",
    en: "Citrus perfumes open with bright citrus notes — bergamot, lemon, orange, grapefruit. They embody freshness and energy, perfect for daily wear and warm days."
  },
  Amber: {
    fr: "Les parfums ambres enveloppent de chaleur et de douceur. L'accord ambre, mariant vanille, benjoin et labdanum, cree un sillage capiteux et persistant, ideal pour les soirees.",
    en: "Amber perfumes envelop with warmth and softness. The amber accord, blending vanilla, benzoin, and labdanum, creates a heady, persistent trail ideal for evening wear."
  },
  Leather: {
    fr: "Les parfums cuires recreent l'odeur du cuir travaille, souvent associee a des notes fumees, de bouleau ou de tabac. Ils incarnent l'elegance brute et le caractere affirme.",
    en: "Leather perfumes recreate the scent of worked leather, often paired with smoky, birch, or tobacco notes. They embody raw elegance and bold character."
  },
  Aromatic: {
    fr: "Les parfums aromatiques puisent dans les herbes et plantes — lavande, romarin, thym, sauge. Ils offrent une fraicheur naturelle et une noblesse vegetale, tres apprecies en parfumerie masculine.",
    en: "Aromatic perfumes draw from herbs and plants — lavender, rosemary, thyme, sage. They offer natural freshness and vegetal nobility, highly valued in masculine perfumery."
  },
  Fruity: {
    fr: "Les parfums fruites mettent en avant peche, poire, fruits rouges ou fruits tropicaux. Juteux et joyeux, ils apportent de l'energie et de la bonne humeur a toute composition.",
    en: "Fruity perfumes highlight peach, pear, red berries, or tropical fruits. Juicy and joyful, they bring energy and good spirits to any composition."
  },
  Green: {
    fr: "Les parfums verts evoquent la nature vegetale — feuilles froissees, herbe coupee, galbanum. Frais et vifs, ils sont associes a une elegance decontractee et naturelle.",
    en: "Green perfumes evoke vegetal nature — crushed leaves, cut grass, galbanum. Fresh and vivid, they are associated with effortless, natural elegance."
  },
  Musk: {
    fr: "Les parfums musques reposent sur des muscs blancs synthetiques, creant un effet seconde peau, propre et sensuel. Minimalistes et addictifs, ils sont parfaits au quotidien.",
    en: "Musky perfumes rely on synthetic white musks, creating a clean, sensual second-skin effect. Minimalist and addictive, they are perfect for daily wear."
  },
  Spicy: {
    fr: "Les parfums epices integrent cannelle, cardamome, poivre ou girofle. Ils ajoutent chaleur, caractere et une dimension intrigante a la composition.",
    en: "Spicy perfumes integrate cinnamon, cardamom, pepper, or clove. They add warmth, character, and an intriguing dimension to the composition."
  },
  Marine: {
    fr: "Les parfums marins capturent l'essence de l'ocean, du sel et des embruns. Frais et lumineux, ils evoquent des horizons ouverts et un sentiment de liberte.",
    en: "Marine perfumes capture the ocean's essence, salt, and sea spray. Fresh and luminous, they evoke open horizons and a sense of freedom."
  },
  Powdery: {
    fr: "Les parfums poudres evoquent la douceur de l'iris, de la violette ou de l'heliotrope. Retro-chic, ils sont a la fois doux, sophistiques et reconfortants.",
    en: "Powdery perfumes evoke the softness of iris, violet, or heliotrope. Retro-chic, they are gentle, sophisticated, and comforting."
  },
  Sweet: {
    fr: "Les parfums sucres misent sur des notes enveloppantes — vanille, toffee, praline — pour un sillage reconfortant et addictif qui laisse une empreinte memorable.",
    en: "Sweet perfumes rely on enveloping notes — vanilla, toffee, praline — for a comforting, addictive trail that leaves a memorable impression."
  },
  Fresh: {
    fr: "Les parfums frais combinent notes hesperidees, aquatiques et vertes pour un resultat vivifiant et lumineux, ideal au quotidien et par temps chaud.",
    en: "Fresh perfumes combine citrus, aquatic, and green notes for an invigorating, luminous result, ideal for everyday wear and warm weather."
  },
  Vanilla: {
    fr: "Les parfums vanilles s'articulent autour de la vanille, creant un sillage doux, cremeux et intemporel. Universellement appreciee, la vanille traverse les epoques et les genres.",
    en: "Vanilla perfumes center on vanilla, creating a soft, creamy, timeless trail. Universally loved, vanilla transcends eras and genders."
  }
};

export function getFamilyDescription(locale: Locale, family: string): string {
  const root = getFamilyRoot(family);
  return FAM[root]?.[locale] ?? FAM['Floral'][locale];
}

/* ---- Concentration descriptions ---- */
const CONC: Record<string, Record<Locale, string>> = {
  'Parfum': {
    fr: "Le Parfum (ou Extrait de Parfum) represente la concentration la plus elevee, entre 20 et 40% d'huiles essentielles. Il offre un sillage intime mais extremement persistant, souvent superieur a 8 heures. C'est la forme la plus luxueuse d'une fragrance.",
    en: "Parfum (or Extrait de Parfum) is the highest concentration, between 20-40% essential oils. It offers an intimate yet extremely long-lasting trail, often exceeding 8 hours. It is the most luxurious form of a fragrance."
  },
  'Eau de Parfum': {
    fr: "L'Eau de Parfum (EDP) contient 15 a 20% d'huiles essentielles. Format le plus populaire en parfumerie moderne, il offre un excellent equilibre entre intensite, projection et longevite, avec une tenue de 6 a 8 heures en moyenne.",
    en: "Eau de Parfum (EDP) contains 15-20% essential oils. The most popular format in modern perfumery, it offers an excellent balance of intensity, projection, and longevity, lasting 6-8 hours on average."
  },
  'Eau de Toilette': {
    fr: "L'Eau de Toilette (EDT) affiche une concentration de 5 a 15% d'huiles essentielles. Plus legere et fraiche que l'EDP, elle est ideale pour un usage quotidien avec une tenue de 4 a 6 heures.",
    en: "Eau de Toilette (EDT) features a 5-15% essential oil concentration. Lighter and fresher than EDP, it's ideal for daily wear with 4-6 hours of staying power."
  },
  'Eau de Cologne': {
    fr: "L'Eau de Cologne (EDC) contient 2 a 5% d'huiles essentielles. Tres fraiche et legere, elle offre une sensation vivifiante mais s'estompe en 2 a 3 heures, invitant a se re-parfumer.",
    en: "Eau de Cologne (EDC) contains 2-5% essential oils. Very fresh and light, it provides an invigorating sensation but fades within 2-3 hours, inviting reapplication."
  },
  'Elixir': {
    fr: "L'Elixir est une concentration intense depassant souvent 30% d'huiles essentielles. Version plus profonde et tenace de la fragrance originale, c'est un choix pour les amateurs de sillage puissant et durable.",
    en: "Elixir is an intense concentration often exceeding 30% essential oils. A deeper, more tenacious version of the original fragrance, it's a choice for those who love a powerful, lasting trail."
  }
};

export function getConcentrationDescription(locale: Locale, concentration: string): string {
  return CONC[concentration]?.[locale] ?? CONC['Eau de Parfum'][locale];
}

/* ---- Decade context ---- */
const DECADE: Record<string, Record<Locale, string>> = {
  '1920': {
    fr: "Les annees 1920, ere du jazz et de l'emancipation feminine, ont vu naitre les premiers parfums abstraits modernes comme N°5. Rompant avec les soliflores du XIXe siecle, cette decennie a transforme la parfumerie en art a part entiere.",
    en: "The 1920s, the jazz era, saw the birth of modern abstract perfumes like N°5. Breaking from 19th-century soliflores, this decade transformed perfumery into an art form in its own right."
  },
  '1930': {
    fr: "Les annees 1930, malgre la Grande Depression, ont produit des parfums d'une sophistication remarquable, entre glamour hollywoodien et raffinement europeen, posant les bases de la parfumerie de luxe moderne.",
    en: "The 1930s, despite the Great Depression, produced perfumes of remarkable sophistication, bridging Hollywood glamour and European refinement, laying the foundations of modern luxury perfumery."
  },
  '1940': {
    fr: "Les annees 1940, marquees par la Seconde Guerre mondiale, ont vu emerger des parfums resilients, souvent floraux ou chypres. Symboles d'elegance dans l'adversite, ils temoignent de la force creatrice de la parfumerie.",
    en: "The 1940s, marked by World War II, saw resilient perfumes emerge, often floral or chypre. Symbols of elegance in adversity, they testify to perfumery's creative strength."
  },
  '1950': {
    fr: "Les annees 1950 incarnent l'age d'or de la haute parfumerie. Dans un monde en pleine reconstruction, les creations de cette epoque allient raffinement classique et feminite affirmee, avec des compositions devenues legendaires.",
    en: "The 1950s represent haute perfumery's golden age. In a world rebuilding itself, this era's creations combined classical refinement with assertive femininity, producing compositions that became legendary."
  },
  '1960': {
    fr: "Les annees 1960, decennie de la contre-culture et de la jeunesse, ont donne naissance a des parfums plus frais et libres. Refletant l'optimisme ambiant, ils marquent une rupture avec la parfumerie classique.",
    en: "The 1960s, the decade of counterculture and youth, gave birth to fresher, freer perfumes. Reflecting the era's optimism, they marked a break from classical perfumery."
  },
  '1970': {
    fr: "Les annees 1970, entre flower power et disco, ont produit des parfums audacieux et expressifs. Souvent riches en patchouli et notes vertes, ils refletent une epoque de liberte et d'experimentation.",
    en: "The 1970s, between flower power and disco, produced bold, expressive perfumes. Often rich in patchouli and green notes, they reflect an era of freedom and experimentation."
  },
  '1980': {
    fr: "Les annees 1980, decennie de l'exces et de l'affirmation, ont engendre les power scents — des parfums puissants au sillage imposant, comme Poison ou Obsession, symboles de confiance et d'ambition.",
    en: "The 1980s, the decade of excess and self-assertion, spawned power scents — bold perfumes with imposing projection, like Poison or Obsession, symbolizing confidence and ambition."
  },
  '1990': {
    fr: "Les annees 1990 ont marque un tournant majeur avec l'apparition des parfums aquatiques (L'Eau d'Issey, CK One) et des premiers gourmands (Angel), ouvrant une nouvelle ere olfactive plus diversifiee.",
    en: "The 1990s marked a major turning point with aquatic perfumes (L'Eau d'Issey, CK One) and the first gourmands (Angel), ushering in a more diverse olfactory era."
  },
  '2000': {
    fr: "Les annees 2000 ont vu l'essor spectaculaire de la parfumerie de niche et le retour des compositions complexes. Portees par une clientele en quete d'originalite, les maisons independantes se sont multipliees.",
    en: "The 2000s saw the spectacular rise of niche perfumery and a return to complex compositions. Driven by consumers seeking originality, independent houses multiplied."
  },
  '2010': {
    fr: "Les annees 2010 ont consacre la parfumerie de niche, les fragrances unisexes et les notes d'oud. Le marche, de plus en plus fragmente et mondialise, a vu naitre de nouvelles tendances comme le clean perfumery.",
    en: "The 2010s cemented niche perfumery, unisex fragrances, and oud notes. The increasingly fragmented, globalized market saw new trends like clean perfumery emerge."
  },
  '2020': {
    fr: "Les annees 2020 poursuivent la quete de singularite, avec un interet croissant pour les ingredients durables, la transparence des formulations et le parfum comme expression identitaire personnelle.",
    en: "The 2020s continue the quest for individuality, with growing interest in sustainable ingredients, formula transparency, and perfume as personal identity expression."
  }
};

export function getDecade(year: number): string {
  const d = Math.floor(year / 10) * 10;
  return String(Math.max(1920, Math.min(2020, d)));
}

export function getDecadeDescription(locale: Locale, year: number): string {
  return DECADE[getDecade(year)]?.[locale] ?? DECADE['2000'][locale];
}

/* ---- Niche / Designer classification ---- */
const NICHE = new Set([
  'Maison Francis Kurkdjian', 'Creed', 'Le Labo', 'Byredo',
  'Editions de Parfums Frederic Malle', "Editions de Parfums Frederic Malle",
  'Juliette Has a Gun', 'Escentric Molecules', 'Diptyque',
  'Parfums de Marly', 'Initio Parfums Prives', 'Xerjoff', 'Amouage',
  "Penhaligon's", 'Mancera', 'Montale', 'By Kilian', 'Nishane',
  'Tiziana Terenzi', 'Atelier Cologne', 'Jo Malone', 'Acqua di Parma',
  'Louis Vuitton', 'Serge Lutens'
]);

export function isNicheHouse(house: string): boolean {
  return NICHE.has(house);
}

/* ---- Relevant guide links ---- */
export interface GuideLink {
  href: string;
  label: string;
  desc: string;
}

export function getRelevantGuides(
  locale: Locale,
  family: string,
  house: string,
  genre: string
): GuideLink[] {
  const guides: GuideLink[] = [];
  const fl = family.toLowerCase();

  if (fl.includes('chypre')) guides.push({
    href: `/${locale}/parfums-chypres-histoire/`,
    label: locale === 'fr' ? 'Parfums chypres : histoire et icones' : 'Chypre perfumes: history & icons',
    desc: locale === 'fr' ? "L'histoire de la famille chypree en parfumerie" : 'The history of the chypre family in perfumery'
  });
  if (fl.includes('gourmand')) guides.push({
    href: `/${locale}/parfums-gourmands-guide/`,
    label: locale === 'fr' ? 'Guide des parfums gourmands' : 'Gourmand perfumes guide',
    desc: locale === 'fr' ? 'Tout sur les fragrances sucrees et addictives' : 'All about sweet, addictive fragrances'
  });
  if (fl.includes('oriental')) guides.push({
    href: `/${locale}/parfums-orientaux-iconiques/`,
    label: locale === 'fr' ? 'Parfums orientaux iconiques' : 'Iconic oriental perfumes',
    desc: locale === 'fr' ? 'Les grands parfums orientaux de l\'histoire' : 'The greatest oriental perfumes in history'
  });
  if (house === 'Chanel') guides.push({
    href: `/${locale}/parfums-iconiques-chanel/`,
    label: locale === 'fr' ? 'Parfums iconiques Chanel' : 'Iconic Chanel perfumes',
    desc: locale === 'fr' ? "L'heritage olfactif de la maison Chanel" : 'The olfactory heritage of Chanel'
  });
  if (house === 'Dior') guides.push({
    href: `/${locale}/parfums-iconiques-dior/`,
    label: locale === 'fr' ? 'Parfums iconiques Dior' : 'Iconic Dior perfumes',
    desc: locale === 'fr' ? "L'univers parfume de la maison Dior" : 'The fragrant universe of Dior'
  });
  if (genre === 'Unisex') guides.push({
    href: `/${locale}/parfums-unisexes-tendance/`,
    label: locale === 'fr' ? 'Parfums unisexes tendance' : 'Trending unisex perfumes',
    desc: locale === 'fr' ? 'La tendance des parfums sans genre' : 'The genderless perfume trend'
  });

  guides.push({
    href: `/${locale}/difference-edp-edt-parfum/`,
    label: locale === 'fr' ? 'EDP, EDT, Parfum : les differences' : 'EDP, EDT, Parfum: the differences',
    desc: locale === 'fr' ? 'Comprendre les concentrations de parfum' : 'Understanding perfume concentrations'
  });
  guides.push({
    href: `/${locale}/guide-familles-olfactives/`,
    label: locale === 'fr' ? 'Guide des familles olfactives' : 'Olfactory families guide',
    desc: locale === 'fr' ? 'Les grandes familles de parfums expliquees' : 'Major perfume families explained'
  });
  guides.push({
    href: `/${locale}/histoire-parfums-par-decennie/`,
    label: locale === 'fr' ? 'Histoire des parfums par decennie' : 'Perfume history by decade',
    desc: locale === 'fr' ? "L'evolution de la parfumerie au fil du temps" : 'The evolution of perfumery over time'
  });
  guides.push({
    href: `/${locale}/parfums-maisons-niche-vs-designer/`,
    label: locale === 'fr' ? 'Niche vs. Designer' : 'Niche vs. Designer',
    desc: locale === 'fr' ? 'Ce qui distingue la parfumerie de niche' : 'What sets niche perfumery apart'
  });
  guides.push({
    href: `/${locale}/guide-strategie-perfumdle/`,
    label: locale === 'fr' ? 'Strategie Perfumdle' : 'Perfumdle strategy',
    desc: locale === 'fr' ? 'Astuces pour deviner le parfum du jour' : 'Tips to guess the daily perfume'
  });

  return guides.slice(0, 6);
}
