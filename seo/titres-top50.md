# Titres des 50 pages les plus vues sur Google (Search Console, 3 mois au 25 octobre 2026)

Source : Search Console, 90 jours, http et www fusionnés. Position = position moyenne pondérée par les impressions.
Les 50 pages font 6 677 impressions et 61 clics. Sans le jeu et l'accueil, il reste 21 clics.

## Diagnostic

**1. Deux groupes de pages, deux problèmes différents.**
- **21 pages en position 4 à 15 (2 830 impressions, 55 clics dont 34 pour le jeu).** Elles apparaissent en bas de la première page ou en haut de la deuxième. C'est là que le titre décide du clic. Guerlain, Versace, Initio, Azzaro, Issey Miyake, Ultra Male, Dior Homme Intense, Oajan… : 0 ou 1 clic chacune.
- **20 pages au-delà de la position 30 (2 834 impressions, 0 clic).** Rose, musc, jasmin, boisé, oud, parfums d'hiver, unisexe… On sort en 5e à 9e page sur « rose perfume » ou « woody perfumes ». Personne ne voit ces titres : un meilleur titre n'y changera presque rien. Le levier est le classement (contenu, liens), pas le titre.

**2. Les titres décrivent la page au lieu de répondre à la requête.**
- Les gens tapent « versace perfume », « nishane », « davidoff ». Ils veulent choisir un parfum. Nos titres promettent « history » : « Versace fragrances: history, Eros, Dylan Blue, Crystal ». Le mot « history » apparaît dans 14 des 50 titres.
- Les gens tapent « ultra male notes », « dior homme intense notes », « burberry her perfume notes ». Ils veulent la réponse tout de suite. Notre titre dit seulement « Notes, Review & Similar Perfumes », sans donner une seule note. Le concurrent qui écrit « Ultra Male : poire, lavande, vanille » prend le clic.

**3. Les titres sont tous coulés dans le même moule.**
- Les 10 pages notes du top 50 ont exactement la même forme : « X in Perfume: What It Smells Like & Best Fragrances ».
- Les 1 500 fiches parfum aussi : « X by Y: Notes, Review & Similar Perfumes ». C'est un gabarit unique dans `src/views/PerfumeView.astro`.
- Rien ne distingue une page d'une autre dans les résultats : pas de chiffre, pas de détail, pas de promesse.

**4. Il manque le mot que les gens tapent, ou il n'est pas en tête.**
- « perfume » est absent des titres maisons (« Versace fragrances »), alors que la requête est « versace perfume ».
- « Mugler » est la requête, mais la page FR s'appelle « Parfum Mugler » et se classe 50e. Sur les requêtes de marque, la page EN gagnerait à être plus proche de « Mugler Perfume ».

## Ce que je propose

**A. Fiches parfum (gabarit, 1 500 pages d'un coup).** Mettre les 3 notes principales dans le titre, et le mot « notes » en tête :
`Ultra Male Notes: Pear, Lavender, Vanilla and Review`. En FR : `Ultra Male : notes poire, lavande, vanille et avis`.
Le texte des notes s'affiche en gras dans Google quand il correspond à la requête. C'est la proposition qui touche le plus de requêtes « X notes », sur lesquelles on est déjà en position 9 à 12.

**B. Pages maisons (titres rédigés, une par une).** Remplacer « history » par l'intention d'achat : « Best [Maison] Perfumes », avec un chiffre (nombre de parfums sur le site) et les 2 ou 3 noms les plus cherchés.

**C. Pages notes (titres rédigés).** Sortir du moule. Un titre qui promet une sélection (« Best Rose Perfumes: Fresh, Powdery or Dark ») plutôt qu'une définition. Effet limité tant qu'elles restent au-delà de la 30e place.

**D. Les pages déjà bien placées hors gabarit.** Époques (2000s en position 11,8, 1900s en 5,8) : déjà correctes, à garder.

Règles appliquées : 60 caractères maximum, pas de « dupe » (interdit par le guide de style), requête au début, un détail concret (notes, chiffre, noms), pas de tiret cadratin.

## Les 50 pages

| # | Page | Impr. | Pos. | Clics | Titre actuel | Titre proposé |
|---|---|---|---|---|---|---|
| 1 | /en/notes/rose/ | 362 | 54,4 | 0 | Rose in Perfume: What It Smells Like & Best Fragrances | Best Rose Perfumes: Fresh, Powdery or Dark (and Why) |
| 2 | /en/houses/guerlain/ | 315 | 9,9 | 1 | Guerlain Perfumes: History, Icons and the Guerlinade | Best Guerlain Perfumes: Shalimar, Mon Guerlain and 90+ More |
| 3 | /en/houses/tom-ford/ | 277 | 33,8 | 2 | Tom Ford fragrances: history, Private Blend and icons | Best Tom Ford Perfumes: Private Blend Ranked, Oud to Neroli |
| 4 | /en/notes/musk/ | 270 | 71,7 | 0 | Musk in Perfume: What It Smells Like & Best Fragrances | Best Musk Perfumes: Clean, Skin-Like or Animalic |
| 5 | /en/eras/2000s/ | 225 | 11,8 | 5 | Popular 2000s Perfumes: 67 Scents That Defined the Decade | à garder (chiffre à mettre à jour automatiquement) |
| 6 | /en/parfum/jean-paul-gaultier-ultra-male/ | 221 | 10,3 | 1 | Ultra Male (Jean Paul Gaultier): Notes & Similar Perfumes | Ultra Male Notes: Pear, Lavender, Vanilla and Review |
| 7 | /en/families/woody/ | 214 | 74,0 | 0 | Woody Perfumes for Men and Women: Cedar, Sandalwood | Best Woody Perfumes: Cedar, Sandalwood, Vetiver, Oud |
| 8 | /en/parfum/burberry-her/ | 209 | 13,0 | 0 | Her by Burberry: Notes, Review & Similar Perfumes | Burberry Her Notes: Berries, Violet, Musk and Review |
| 9 | /en/houses/versace/ | 203 | 13,6 | 0 | Versace fragrances: history, Eros, Dylan Blue, Crystal | Best Versace Perfumes: Eros, Dylan Blue, Bright Crystal |
| 10 | /en/houses/paco-rabanne/ | 186 | 20,3 | 0 | Paco Rabanne fragrances: 1 Million, Invictus, history | Best Paco Rabanne Perfumes: 1 Million, Invictus, Phantom |
| 11 | /en/houses/initio-parfums-prives/ | 179 | 8,2 | 1 | Initio Parfums Privés: History and Key Scents | Initio Perfumes: Oud for Greatness, Side Effect and More |
| 12 | /fr/marques/mugler/ | 178 | 49,7 | 0 | Parfum Mugler : histoire, Angel, Alien et A*Men | Parfums Mugler : Angel, Alien, A*Men, lequel choisir |
| 13 | /en/parfum/lancome-idole/ | 173 | 17,4 | 0 | Idôle by Lancôme: Notes, Review & Similar Perfumes | Lancôme Idôle Notes: Pear, Rose, Musk and Review |
| 14 | /en/notes/jasmine/ | 166 | 75,0 | 0 | Jasmine in Perfume: What It Smells Like & Best Fragrances | Best Jasmine Perfumes: Sambac, Grandiflorum and Icons |
| 15 | /en/houses/gucci/ | 154 | 22,8 | 0 | Gucci fragrances: history, Bloom, Guilty and Flora | Best Gucci Perfumes: Bloom, Guilty, Flora Compared |
| 16 | /en/families/woody/women/ | 138 | 49,8 | 0 | Woody perfumes for women: 8 woods, creamy to leathery | Best Woody Perfumes for Women: Creamy to Leathery |
| 17 | /en/eras/1900s/ | 135 | 5,8 | 5 | 1900s Perfume: The Belle Époque Scents of 1900 to 1909 | à garder |
| 18 | /en/houses/issey-miyake/ | 118 | 9,7 | 0 | Issey Miyake fragrances: history and L'Eau d'Issey | Best Issey Miyake Perfumes: L'Eau d'Issey and Flankers |
| 19 | /en/notes/ | 118 | 65,0 | 0 | Perfume notes: 251 fragrance materials explained | Perfume Notes List: 250+ Notes and What They Smell Like |
| 20 | /en/game/ | 117 | 4,5 | 34 | Guess the Perfume: Perfumdle, the Daily Perfume Wordle | à garder (CTR 29 %) |
| 21 | /en/parfum/parfums-de-marly-oajan/ | 114 | 10,1 | 0 | Oajan by Parfums de Marly: Notes, Review & Similar Perfumes | Oajan Notes: Honey, Cinnamon, Vanilla and Review |
| 22 | /en/parfum/dior-dior-homme-intense/ | 113 | 10,1 | 1 | Dior Homme Intense: Notes, Review & Similar Perfumes | Dior Homme Intense Notes: Iris, Lavender, Pear |
| 23 | /en/notes/iris/ | 112 | 38,6 | 0 | Iris in Perfume: What It Smells Like & Best Fragrances | Best Iris Perfumes: Powdery, Buttery, Rooty |
| 24 | /en/notes/lemon/ | 111 | 44,0 | 0 | Lemon in Perfume: What It Smells Like & Best Fragrances | Best Lemon Perfumes: Fresh Citrus That Lasts |
| 25 | /en/houses/azzaro/ | 110 | 9,0 | 0 | Azzaro fragrances: history, fougères and best-sellers | Best Azzaro Perfumes: Wanted, Chrome, Pour Homme |
| 26 | /en/unisex-perfumes/ | 110 | 85,0 | 0 | Unisex Perfumes: Iconic Scents to Share | Best Unisex Perfumes: 300 Scents for Him and Her |
| 27 | /en/notes/lily-of-the-valley/ | 107 | 32,7 | 1 | Lily of the Valley in Perfume: Smell & Best Fragrances | Best Lily of the Valley Perfumes: Diorissimo and More |
| 28 | /en/edp-vs-edt-difference/ | 104 | 49,3 | 0 | (ancienne URL /en/difference-edp-edt-parfum/) | EDP vs EDT vs Parfum: Which Lasts Longer |
| 29 | /en/houses/prada/ | 104 | 14,0 | 0 | Prada fragrances: history, Luna Rossa, Candy and iris | Best Prada Perfumes: Luna Rossa, Paradoxe, Candy |
| 30 | /en/notes/star-anise/ | 103 | 15,3 | 0 | Star Anise in Perfume: What It Smells Like & Best Fragrances | What Does Star Anise Smell Like in Perfume |
| 31 | /en/houses/britney-spears/ | 102 | 11,4 | 0 | Britney Spears Perfumes: History and Fantasy | Britney Spears Perfumes: Fantasy and Every Flanker |
| 32 | /en/winter-perfumes/ | 98 | 63,9 | 0 | Winter Perfumes: Vanilla, Amber, Resins and Oud | Best Winter Perfumes: Warm Vanilla, Amber and Oud |
| 33 | /en/parfum/hermes-eau-des-merveilles/ | 94 | 18,5 | 1 | Eau des Merveilles by Hermès: Notes, Review & Similar Perfumes | Eau des Merveilles Notes: Amber, Orange, Pepper |
| 34 | /en/notes/oud/ | 91 | 76,5 | 0 | Oud in Perfume: What It Smells Like & Best Fragrances | Best Oud Perfumes: Smoky, Rosy or Leathery |
| 35 | /en/families/spicy/ | 87 | 63,1 | 1 | Spicy Perfumes: Pepper, Cinnamon, Cardamom and Clove | Best Spicy Perfumes: Pepper, Cinnamon, Cardamom |
| 36 | /en/ | 86 | 13,9 | 6 | Perfumdle: Iconic Perfume Encyclopedia and Daily Game | à garder |
| 37 | /en/houses/davidoff/ | 86 | 12,4 | 1 | Davidoff Fragrances: History and Cool Water | Davidoff Perfumes: Cool Water and Its Best Flankers |
| 38 | /en/parfum/hermes-terre-dhermes/ | 82 | 11,5 | 0 | Terre d'Hermès: Notes, Review & Similar Perfumes | Terre d'Hermès Notes: Orange, Flint, Vetiver |
| 39 | /en/houses/mancera/ | 81 | 9,1 | 0 | Mancera perfumes: history, Cedrat Boise and style | Mancera Perfumes: Cedrat Boise and Red Tobacco |
| 40 | /en/houses/nishane/ | 81 | 15,3 | 0 | Nishane Perfumes: History, Hacivat and Ani | Nishane Perfumes: Hacivat vs Ani, Which to Choose |
| 41 | /en/parfum/paco-rabanne-phantom/ | 78 | 11,8 | 0 | Phantom by Paco Rabanne: Notes, Review & Similar Perfumes | Paco Rabanne Phantom Notes: Lavender, Lemon, Vanilla |
| 42 | /en/parfum/tom-ford-tobacco-oud/ | 78 | 12,6 | 0 | Tobacco Oud by Tom Ford: Notes, Review & Similar Perfumes | Tom Ford Tobacco Oud Notes: Whiskey, Oud, Tobacco |
| 43 | /en/notes/petitgrain/ | 78 | 26,0 | 0 | Petitgrain in Perfume: What It Smells Like & Best Fragrances | What Does Petitgrain Smell Like? Best Petitgrain Scents |
| 44 | /en/parfum/parfums-de-marly-carios/ | 74 | 12,6 | 0 | Carios by Parfums de Marly: Notes, Review & Similar Perfumes | Carios Notes: Saffron, Pepper, Ambroxan and Review |
| 45 | /en/spring-perfumes/ | 74 | 74,3 | 0 | Spring Perfumes: Flowers, Green Notes and Citrus | Best Spring Perfumes: Florals, Green and Citrus |
| 46 | /en/notes/vanilla/ | 73 | 59,8 | 0 | Vanilla in Perfume: What It Smells Like & Best Fragrances | Best Vanilla Perfumes: Gourmand, Smoky, Boozy |
| 47 | /en/houses/creed/ | 73 | 28,4 | 0 | Creed fragrances: history, Aventus and house style | Best Creed Perfumes: Aventus, Green Irish Tweed, Silver Mountain |
| 48 | /fr/marques/gucci/ | 72 | 40,8 | 0 | Parfum Gucci femme et homme : Bloom, Guilty et Flora | Parfum Gucci : Bloom, Guilty, Flora, lequel choisir |
| 49 | /en/houses/elizabeth-taylor/ | 72 | 63,1 | 0 | Elizabeth Taylor Perfumes: History and White Diamonds | Elizabeth Taylor Perfumes List: White Diamonds and More |
| 50 | /en/houses/estee-lauder/ | 71 | 16,2 | 0 | Estée Lauder Perfumes: History, Youth Dew, Beautiful | Best Estée Lauder Perfumes: Youth Dew to Pleasures |

## Requêtes qui comptent (extrait, 3 mois)

| Requête | Impr. | Pos. | Page |
|---|---|---|---|
| rose perfume | 101 | 50,5 | notes/rose |
| versace perfume | 69 | 10,2 | houses/versace |
| dior homme intense notes | 55 | 9,0 | fiche Dior Homme Intense |
| thierry mugler | 49 | 52,9 | marques/mugler |
| hermes eau des merveilles notes | 42 | 25,6 | fiche Eau des Merveilles |
| what does star anise smell like | 29 | 12,5 | notes/star-anise |
| ultra male notes (+ jpg, jean paul gaultier) | 72 | 9,7 à 11,5 | fiche Ultra Male |
| burberry her (+ notes) | 62 | 9,6 à 17,9 | fiche Burberry Her |
| nishane | 26 | 28,0 | houses/nishane |
| elizabeth taylor perfumes list | 25 | 83,9 | houses/elizabeth-taylor |

À vérifier avant de publier les titres proposés : les noms de parfums cités dans les titres maisons doivent tous exister sur le site, et les notes citées doivent correspondre aux données de la fiche.
