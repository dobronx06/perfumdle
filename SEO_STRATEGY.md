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
| ~2 500 | comparatifs `X vs Y` (paires les plus proches + duels célèbres : Sauvage vs Bleu de Chanel…) | intention forte, SERP peu défendues |
| ~3 500 | croisements note × genre (« parfum vanille homme »), note × saison, famille × genre | longue traîne pure, contenu calculé + court texte unique |
| ~5 000 | +300 parfums (étendre le dataset) → fiches + similaires | la donnée est le moteur de tout le site |
| ~10 000 | parfumeurs (nez), accords, guides « meilleurs parfums pour… », pages marque × famille | autorité thématique |

Règle d'or : **ne publier une famille de pages que si chaque page a une donnée ou un texte qui n'existe nulle part ailleurs sur le site**
— sinon on fusionne (noindex ou pas de page).

## 7. Mesure & boucle d'amélioration

1. Brancher Google Search Console (+ soumettre `sitemap-index.xml`) et suivre impressions / clics / positions par silo.
2. À 8 semaines : renforcer les pages en positions 5–20 (texte, FAQ, liens internes), fusionner celles à 0 impression.
3. Retravailler les `<title>` des pages à fort taux d'impressions et faible CTR.

## 8. Mots-clés & concurrence (Haloscan)

Le MCP Haloscan n'est pas connecté dans cette session. Pour l'activer (clé API Haloscan, plan Starter minimum) :

```bash
claude mcp add haloscan --env HALOSCAN_API_KEY=VOTRE_CLE -- npx -y @occirank/haloscan-server start
```

Ensuite : valider les volumes des clusters ci-dessus, repérer les SERP faibles (concurrents : Fragrantica, Auparfum, Nez,
Sephora/Nocibé, sites de dupes) et prioriser l'ordre du drip.

## 9. Ce qui a volontairement été écarté

Le deuxième thread partagé décrit un SEO « black hat » (churn & burn, PBN, domaines expirés, parasite SEO).
Incompatible avec l'objectif « site professionnel qui dure » et à fort risque de pénalité : non appliqué.
On en garde les idées saines : templates à variations sémantiques, FAQ, pages comparatives.
