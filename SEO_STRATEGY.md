# Perfumdle — stratégie SEO & contenu

> Positionnement : **l'encyclopédie éditoriale des parfums iconiques** (FR d'abord, EN en miroir).
> Le jeu quotidien devient une porte d'entrée secondaire (`/fr/jeu/`), plus le cœur du site.

## 1. Pourquoi ce virage

- Le site était une page de jeu + ~26 pages minces. Aucune requête « parfum » n'y trouvait de réponse.
- Les requêtes à volume sont informationnelles et transactionnelles-douces : *notes de Sauvage*, *parfum à la vanille*,
  *parfum qui ressemble à Baccarat Rouge*, *parfums Guerlain*, *parfum boisé homme*, *parfum d'hiver*, *parfums années 80*.
- On possède déjà la donnée qui y répond : 307 parfums × pyramide olfactive complète (320 notes). Elle n'était pas exploitée.

## 2. Architecture (silos + maillage)

```
/fr/                                   Home = hub des hubs (liens vers toutes les grandes catégories)
├── parfums/                           catalogue filtrable (307)
│   └── parfum/<slug>/                 fiche parfum (money page informationnelle)
├── marques/  ─ marques/<slug>/        77 maisons (histoire, signature, parfums, maisons proches)
├── notes/    ─ notes/<slug>/          99 notes (odeur, origine, usage, parfums, accords fréquents)
├── familles/ ─ familles/<slug>/       14 familles olfactives
├── epoques/  ─ epoques/<slug>/        14 décennies (1880 → 2020)
├── parfums-femme|homme|mixtes/        3 sélections genre
├── parfums-printemps|ete|automne|hiver/  4 sélections saison
├── parfums-similaires/<slug>/         307 pages « alternatives » — publiées au goutte-à-goutte
├── <11 guides longs existants>
└── jeu/                               le jeu (secondaire)
/en/ … miroir complet (houses/, families/, eras/, similar-perfumes/, game/)
```

Maillage interne dense et **calculé** (jamais à la main) :
- Fiche parfum → maison, décennie, genre, famille(s), chaque note (si page), saisons, 8 parfums similaires, 8 de la même maison.
- Note → parfums qui la contiennent (+ position tête/cœur/fond), 10 notes souvent associées (co-occurrence), maisons.
- Maison → tous ses parfums, notes signatures, 8 maisons « affines » (similarité olfactive moyenne).
- Famille / époque → parfums, notes dominantes, maisons, pagination précédent/suivant.
- Footer : top maisons, top notes, familles, genres, saisons, guides — chaque page est à ≤ 3 clics de la home.

## 3. Contenu (anti-spam)

Chaque page programmatique a **du texte éditorial unique**, rédigé par entité, pas un template à trous :

| Type | Pages / langue | Contenu unique |
|---|---|---|
| Parfum | 307 | accroche, histoire + description olfactive (90–140 mots), quand le porter, verdict critique, parfumeur (si documenté), saisons, occasions, intensité |
| Note | 99 | intro « réponse directe », odeur, origine/fabrication, usage en parfumerie, conseil, 3 FAQ |
| Maison | 77 | pays, fondation, fondateur, histoire (120–180 mots), signature, comment choisir, 3 FAQ |
| Famille | 14 | définition, histoire, sous-familles, comment la porter, 4 FAQ |
| Époque | 14 | contexte culturel et olfactif, 3 FAQ |
| Genre / saison | 7 | texte de fond + 3 FAQ |

Règles appliquées (voir `scripts/STYLE_GUIDE.md`) : faits vérifiables uniquement (sinon omis), aucun prix/chiffre inventé,
liste de clichés IA interdits, FR natif accentué, EN réécrit (pas traduit). Les incohérences de données repérées sont listées
dans `_data_issues` de chaque fichier `src/data/editorial/*.json`.

**Qualité image** : un audit visuel a retiré 30 visuels faux ou inutilisables (ex. « Chanel N°5 » montrait un flacon Rosendo Mateu,
« Bleu de Chanel » un déodorant). Ils sont remplacés par un placeholder propre en attendant de vrais visuels.

## 4. Technique

- `<title>` ≤ 65 car. et meta description 70–160 car. uniques par page (audit : `python3 scripts/check_seo.py` après build).
- Canonical absolu, `hreflang` fr/en/x-default avec **slugs localisés** (vanille ↔ vanilla), `trailingSlash: always`.
- JSON-LD : `WebSite` + `SearchAction` + `Organization` (home), `Product` + `BreadcrumbList` + `FAQPage` (parfum),
  `Article` + `ItemList` + `BreadcrumbList` + `FAQPage` (hubs), `VideoGame` + `FAQPage` (jeu).
- Sitemap avec `lastmod`/`priority`, `robots.txt`, image OG par défaut + image produit sur les fiches.
- **GEO / IA** : `/llms.txt` (carte du site pour les assistants IA), intros en « réponse directe » citables, FAQ structurées.
- Ancienne URL `/liste-150-parfums-perfumdle/` redirigée vers le catalogue.

## 5. Rythme de publication (pas de spam)

- **Lancement** : ~440 nouvelles URLs (220 FR + 220 EN) + 614 fiches parfum réécrites. Dans la fourchette 200–500 demandée.
- **Goutte-à-goutte** : les 614 pages « parfums similaires » sortent à **8 parfums/jour (16 URLs)** du 12/10 au 19/11/2026
  (`src/data/publish-schedule.json`, généré par `python3 scripts/schedule.py <début> <par_jour>`).
  Une GitHub Action (`.github/workflows/daily-rebuild.yml`) relance le build chaque matin — il faut ajouter le secret
  `DEPLOY_HOOK_URL` (deploy hook de l'hébergeur).

## 6. Feuille de route vers 1 000 → 5 000 → 10 000 pages

| Palier | Nouvelles familles de pages | Pourquoi |
|---|---|---|
| ~1 700 (fin nov.) | fin du drip « similaires » | requête « parfum qui ressemble à X » |
| ~2 000 | ~~comparatifs `X vs Y`~~ → note × genre, famille × genre, « meilleurs parfums » (voir §8.4) | comparatifs ≈ 0 recherche (Haloscan) ; note × genre ~8 400/mois |
| ~3 500 | croisements note × genre (« parfum vanille homme »), note × saison, famille × genre | longue traîne pure, contenu calculé + court texte unique |
| ~5 000 | +300 parfums (étendre le dataset) → fiches + similaires | la donnée est le moteur de tout le site |
| ~10 000 | parfumeurs (nez), accords, guides « meilleurs parfums pour… », pages marque × famille | autorité thématique |

Règle d'or : **ne publier une famille de pages que si chaque page a une donnée ou un texte qui n'existe nulle part ailleurs sur le site**
— sinon on fusionne (noindex ou pas de page).

## 7. Mesure & boucle d'amélioration

1. Brancher Google Search Console (+ soumettre `sitemap-index.xml`) et suivre impressions / clics / positions par silo.
2. À 8 semaines : renforcer les pages en positions 5–20 (texte, FAQ, liens internes), fusionner celles à 0 impression.
3. Retravailler les `<title>` des pages à fort taux d'impressions et faible CTR.

## 8. Mots-clés & concurrence (Haloscan, Google FR, 28/09/2026)

Données brutes : `seo/haloscan/*.tsv` (~2 900 requêtes mesurées, exact match) + `seo/haloscan/serp_analysis.md` (13 SERP).
Coût réel : 22 crédits bulk (482 → 460), 13 crédits keyword, 5 crédits site.

### 8.1 Ce que disent les volumes

| Cluster | Formulation gagnante (vol./mois) | Formulation perdante | Décision |
|---|---|---|---|
| Notes | « parfum vanille » 3 400, « parfum rose » 3 100, « parfum musc » 3 100 (+ « musc blanc » 3 300), « parfum patchouli » 2 200, « parfum jasmin » 1 300 | « parfum à la vanille » 140, « à la rose » 390, « au musc » 210 | titles/H1 en **« Parfum <note> »** (99 notes). Exception : « parfum au caramel » 590 > « parfum caramel » 300 |
| Notes (variantes) | « parfum monoï » 1 600, « néroli parfum » 1 600, « parfum bois de santal » 880, « parfum oud femme » 909 (vs « parfum oud » 200) | — | intégrées aux titles concernés |
| Maisons | « parfum yves saint laurent » 24 600, « parfum dior » 22 600, « parfum louis vuitton » 13 500, « parfum guerlain » 9 000, « parfum de marly » 6 200 | « parfums <maison> » (sauf Tom Ford, Diptyque, Byredo, Lanvin, Clinique…) | titles en **« Parfum <maison> »** + genre quand « parfum <maison> homme/femme » pèse |
| Fiches parfum | La Vie est Belle 61 700, Bleu de Chanel 27 600, Miss Dior 25 000, Sauvage 23 900, Baccarat Rouge 23 900, N°5 16 500, Libre 15 600 | — | titles actuels OK (« <Parfum> de <Maison> : notes, avis et odeur ») |
| Alternatives | « dupe parfum » 3 882 (générique) ; par parfum : 470 max (La Vie est Belle), BR540 420, Petite Robe Noire 296, Bleu de Chanel 280 | « parfum qui ressemble à X » ≤ 40, « alternative X » 0 | la demande « similaires » est faible par parfum → le drip est trié par volume (§8.3) ; title « Parfums similaires à X » conservé (« similaire » 340 > « qui ressemble » 150) |
| Familles | « parfums chyprés » 1 600, « parfum boisé » 880, « parfum floral » 800, « parfum fruité femme » 800, « parfum poudré » 600 | « familles olfactives » ~0, « roue des parfums » 0 | titles familles en « Parfum <adjectif> » |
| Genres / saisons | « parfum homme » 64 600, « parfum femme » 52 900, « meilleur parfum homme » 4 900, « parfum d'été » 1 000, « parfum printemps » 1 000, « parfum été femme » 536 | « parfum automne » 140 | titles alignés ; publier les saisons avant le pic (hiver : oct.–janv.) |
| Époques | « parfum années 90 » 260, « années 80 » 210, « vintage » 170 | « parfum culte » 10 | pas d'action (volumes faibles, SERP courte) |

### 8.2 Concurrence

- **Concurrent direct : tendance-parfums.com** (~70 k mots-clés, ~114 k visites/mois estimées) : pages programmatiques
  « meilleur <famille> <genre> », « notes/<note> », « occasions/<saison>-<genre> » ; top 10 sur 8 des 13 SERP étudiées, n°1 deux fois.
  C'est exactement notre modèle : on se différencie par la donnée (pyramides complètes, co-occurrences, similarité calculée) et le texte éditorial.
- **fragrantica.fr** (~111 k mots-clés, ~487 k visites) : fort sur les noms de parfums, **faible sur les génériques** (25e sur « parfum vanille »).
- **olfastory.com** (~44 k, ~152 k visites) ; **auparfum** désormais sur `auparfum.bynez.com` (~28 k, ~37 k visites).
- Sephora / Nocibé / Marionnaud dominent les requêtes transactionnelles (« parfum <maison> », « parfum vanille ») : inutile de viser le top 3 là, viser l'angle éditorial/liste.
- Reddit traduit automatiquement est dans le top 10 de 6 SERP sur 13 : signe que le contenu éditorial manque.

**SERP faibles à attaquer en priorité** : « parfum musc blanc » 3 300 (6/10 fiches produits de petites marques),
« dupe parfum » 3 882 (top 3 DVI 31–36), « parfum boisé homme » 500 (KGR 1,07), « parfum oud femme » 909 (4/10 hors cible),
« famille olfactive » 320 (blogs DVI 19–39), « parfum hiver femme » 291, « bleu de chanel avis » 260, « différence eau de parfum eau de toilette » 1 100 (KGR 0,48).

### 8.3 Actions appliquées (commit de ce passage)

- `publish-schedule.json` réordonné par demande (`python3 scripts/schedule.py 2026-10-12 8 --reorder`) : score = volume du parfum
  + 20 × volume « dupe / similaire / pas cher » + 3 × volume « avis / notes ». Ouverture le 12/10 avec La Vie est Belle, Bleu de Chanel,
  Baccarat Rouge 540, Miss Dior, Sauvage, Libre, N°5, Acqua di Giò. Toujours 8/jour, 12/10 → 19/11.
  (Volume « Ombre Nomade » 70 300 jugé aberrant → plafonné à 3 000.)
- Titles/H1 FR : 99 notes (`scripts/seo_titles_notes.py`), 77 maisons (`scripts/seo_titles_brands.py`), 14 familles, 3 genres, 4 saisons,
  guide EDP/EDT (title « Différence entre eau de parfum et eau de toilette (et parfum) »).

### 8.4 Prochaines familles de pages, chiffrées

| Priorité | Famille | Exemples (vol./mois FR) | Potentiel cumulé estimé | Pages |
|---|---|---|---|---|
| 1 | **Note × genre** | parfum oud femme 909, vanille femme 909, vanille homme 800, musc blanc femme 720, ambre femme 655, poudré femme 500, patchouli homme 390 | ~8 400 sur 41 combinaisons mesurées | 50–80 (seulement si ≥ 6 parfums du dataset) |
| 2 | **Famille × genre** | fruité femme 800, floral femme 536, boisé homme 500, chypré femme 400 (KGR 0,23), boisé femme 390, oriental homme 390 | ~4 600 (24 combinaisons) | 28 |
| 3 | **« Meilleurs parfums »** génériques + maison × genre | meilleur parfum homme 4 900 (KGR 0,94), femme 2 400, meilleurs parfums homme 900, meilleur parfum Tom Ford homme 260, Dior femme 210 | ~9 500 | 2 + ~20 |
| 4 | **Musc blanc** (page note dédiée, distincte de « musc ») | parfum musc blanc 3 300, musc blanc femme 720 | ~4 000 | 1 |
| 5 | **Saison × genre** | été femme 536, été homme 480, hiver femme 291, hiver homme 236 | ~2 500 (saisonnier) | 8 |
| 6 | **Parfumeurs (nez)** | Francis Kurkdjian 11 400 (+ « parfumeur F. K. » 1 300, KGR 0,09), Olivier Polge 590, Dominique Ropion 500, Thierry Wasser 480, Alberto Morillas 390, Christine Nagel 390 | ~18 800 sur 19 requêtes (dont 11 400 « francis kurkdjian », plutôt navigationnel) | 15–25 (nécessite de fiabiliser le champ `perfumer`) |
| 7 | **Niche** | parfum niche 2 500, parfum de niche 800, parfumerie de niche 800, parfum de niche pas cher 210 | ~4 300 | 1 hub + filtres |
| 8 | **Usages** | parfum ado garçon 880 (KGR 0,008), ado fille 720, qui attire les femmes 720, le plus vendu au monde 480 (KGR 0,07), qui tient longtemps 260 | ~3 000 | 5–6 guides |
| 9 | **Accords / notions** | accord gourmand 320, notes de tête 210, pyramide olfactive 80 | ~1 000 | 3–5 |
| ✗ | **Comparatifs X vs Y** | sauvage vs bleu de chanel 10, aventus vs layton 0 | ~0 | **abandonné** (remplacé par EDP vs EDT, déjà couvert) |
| ✗ | « parfum qui ressemble à X » en page dédiée « dupe » | dupe baccarat rouge 540 170, dupe la vie est belle 260 | faible par page | ne pas créer de pages « dupe » (risque marque) ; le drip « similaires » suffit |

Nouveau palier réaliste : ~1 700 pages fin novembre → **~2 000** avec les priorités 1–5 (≈ 140 pages FR + EN), puis parfumeurs et extension du dataset.
Le palier « comparatifs » de la §6 est remplacé par « note × genre / famille × genre / meilleurs parfums ».

## 9. Ce qui a volontairement été écarté

Le deuxième thread partagé décrit un SEO « black hat » (churn & burn, PBN, domaines expirés, parasite SEO).
Incompatible avec l'objectif « site professionnel qui dure » et à fort risque de pénalité : non appliqué.
On en garde les idées saines : templates à variations sémantiques, FAQ, pages comparatives.
