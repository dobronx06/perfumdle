# Perfumdle — editorial style guide (for content writers)

Site: perfumdle.com — a bilingual (FR primary, EN) editorial encyclopedia of iconic perfumes
(307 perfumes, 77 houses, ~100 notes) plus a daily perfume-guessing game.
Source data: src/data/perfumes.json (name, brand, year, gender, family, families facets,
concentration, notes.top/heart/base, slug). Always ground statements in this data first.

## Voice
- Expert, sensual, precise — the tone of a good perfume magazine (Nez, Auparfum, Fragrantica editorials),
  never a generic AI blog. Concrete sensory vocabulary (resinous, powdery, salty, ink, suede, sap, zest…).
- FRENCH IS THE PRIMARY LANGUAGE: native, idiomatic French with all accents (é, è, à, ç, œ, «  »).
  English is an adaptation written natively, not a literal translation.
- Vary sentence openings and structure between entries. Each entry must read as individually written.
- BANNED clichés (FR/EN): "véritable voyage olfactif", "incontournable", "envoûtant" (max once per file),
  "sillage inoubliable", "un must-have", "olfactory journey", "a true masterpiece", "timeless elegance",
  "in the world of perfumery", "dans l'univers de la parfumerie", "Que vous soyez… ou…", "Plongez dans".
- No markdown inside strings. No emojis. Straight apostrophes are fine in JSON (FR: ’ or ' both ok).

## Accuracy (critical — this content must be trustworthy for Google E-E-A-T)
- Only state facts you are confident about (well-documented launch context, perfumer, founder, history).
- If unsure about a perfumer, founder, date or anecdote: OMIT it (use null), never guess.
- Do not invent statistics, sales figures, prices, awards or quotes.
- No health claims, no disparagement of brands, no "dupe"/counterfeit promotion.
- Do not contradict the dataset (year, family, concentration, notes). If you believe the dataset is wrong,
  write around it and add the slug + issue to the "_data_issues" array at the top level of your output file.

## Output
- Valid JSON (UTF-8), exactly the schema requested. Validate by running
  `python3 -c "import json;json.load(open('<file>'))"` after writing. Fix until it parses.
- Write large files in a few chunks if needed (e.g. write partial files then merge with a small python script),
  but the final deliverable is ONE file at the path given.
