# Perfumdle : règles d'écriture « humaine » (anti AI slop)

À lire avant d'écrire, à relire avant de rendre. Complète `scripts/STYLE_GUIDE.md` (faits, voix, JSON).
Le linter `python3 scripts/lint_copy.py <fichier>` doit sortir propre avant livraison.

## 1. Interdits absolus (le linter bloque)
- **Aucun tiret cadratin « — » ni demi-cadratin « – »**, nulle part, dans aucune langue. Pour une incise :
  un point, deux-points, des parenthèses, ou une virgule si la phrase reste courte. Plages de dates : « de 1990 à 2000 ».
- Pas de point d'exclamation. Pas d'emoji. Pas de markdown (**gras**, listes à puces) dans les chaînes.
- Formules bannies (FR) : « véritable », « incontournable », « envoûtant », « sublime » (verbe ou adjectif),
  « subtil équilibre », « alliance parfaite », « mariage parfait », « à la fois … et », « que vous soyez », « plongez »,
  « découvrez », « laissez-vous », « n'hésitez pas », « en somme », « en définitive », « en conclusion », « il est important de noter »,
  « il convient de », « un must », « intemporel », « signature olfactive unique », « voyage olfactif », « sillage inoubliable »,
  « ode à », « invitation à », « symphonie », « explosion de », « bouquet de saveurs », « au fil des heures » (max 1 par fichier),
  « ne … pas seulement … mais », « pas juste … c'est », « bien plus qu'un », « tout simplement », « résolument », « audacieux ».
- Formules bannies (EN) : "delve", "tapestry", "testament to", "a true", "timeless", "must-have", "elevate", "captivating",
  "whether you're", "it's not just", "more than just", "olfactory journey", "symphony", "nestled", "in the world of",
  "boasts", "seamlessly", "vibrant", "embark", "unleash", "game-changer", "iconic" (max 2 per file).

## 2. Ce qui trahit une IA (à éviter, le linter en signale une partie)
- **Les virgules en rafale.** Une phrase = une idée. Au-delà de deux virgules, coupez. Pas d'empilement d'adjectifs
  (« chaud, sensuel, enveloppant et mystérieux ») : un seul adjectif précis vaut mieux que quatre.
- **Le rythme ternaire systématique** (« frais, floral et élégant », trois exemples, trois arguments). Variez : deux, un, quatre.
- **Les phrases toutes de la même longueur.** Alternez une phrase de 6 mots et une de 25. Une phrase nominale, parfois.
- **L'importance gonflée** : « marque un tournant », « témoigne de », « a révolutionné », « incarne l'essence de ». Dites le fait.
- **Les participes présents en fin de phrase** qui ajoutent un faux sens (« …, offrant une touche de fraîcheur »).
- **Les attributions vagues** : « les experts s'accordent », « beaucoup considèrent », « selon les amateurs ».
- **La conclusion générique** qui résume ce qui vient d'être dit. La dernière phrase doit apporter une info ou un avis.
- **Les questions rhétoriques** en ouverture de paragraphe.
- **La synonymie tournante** (« la fragrance », « le jus », « la création », « l'élixir » pour éviter de répéter « parfum »).
  Répéter « parfum » est normal. « Jus » est accepté une fois par page.
- **La neutralité molle.** Un bon rédacteur a un avis : « Il tient mal sur peau sèche », « on le préfère en extrait »,
  « trop sucré pour le bureau ». Les défauts se disent.
- **Les ouvertures identiques.** Deux paragraphes ou deux « why » ne commencent jamais par le même mot.

## 3. Ce qui fait un texte humain
- Du concret : une matière, une date, un parfumeur, une sensation physique (« une odeur de crayon taillé », « le fond
  de tasse de café », « la peau après la plage »). Toujours tiré des données fournies ou d'un fait sûr.
- Des comparaisons entre parfums de la même page (« plus sec que X », « moins sucré que Y ») : c'est la vraie valeur
  d'une sélection, et aucune IA générique ne peut les inventer sans les données.
- Un conseil d'usage précis : moment, saison, peau, nombre de pulvérisations, sur quoi le vaporiser.
- Le « vous » est permis, sans insister. Le « nous » éditorial est permis (« notre choix », « on le classe premier parce que »).
- FR : typographie française (espace avant « : ; ? », guillemets « »), accents partout, œ, apostrophe ’ ou '.
- EN : réécrit nativement pour un lecteur anglophone, jamais traduit mot à mot. Ton plus direct, phrases plus courtes.

## 4. Auto-relecture obligatoire (passe « humanizer »)
Après le premier jet, relisez chaque bloc avec cette grille et réécrivez ce qui accroche :
1. Chercher « — », « – », « ! ». Remplacer.
2. Compter les virgules phrase par phrase. Couper au-delà de deux.
3. Repérer tout triplet d'adjectifs ou d'exemples. En casser la moitié.
4. Repérer les mots de la liste bannie et les tournures de §2.
5. Lire les premières lettres de chaque « why » : aucune ouverture répétée.
6. Vérifier chaque fait (année, maison, parfumeur, note) contre le brief. Dans le doute : supprimer.
7. Lancer `python3 scripts/lint_copy.py <fichier>` et corriger jusqu'à « OK ».
