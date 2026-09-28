"""Build src/data/ranked-pages.json: the definitions of every "ranked" page (sélections commentées).

Families of pages (roadmap §8.4 of SEO_STRATEGY.md, volumes Haloscan FR 2026-09):
  ng    note × genre            /fr/notes/<note>/<femme|homme>/
  fg    famille × genre         /fr/familles/<famille>/<femme|homme>/
  sg    saison × genre          /fr/parfums-<saison>/<femme|homme>/
  best  meilleurs parfums       /fr/meilleurs-parfums/<id>/
  nose  parfumeurs              /fr/parfumeurs/<slug>/
  guide guides d'usage          /fr/guides/<slug>/

Each definition carries the candidate pool (perfume slugs) the editorial picks must come from.
Usage: python3 scripts/ranked_pages.py   (then scripts/briefs.py for writer briefs)
"""
import json, glob, csv, re, unicodedata, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.load(open(ROOT / 'src/data/perfumes.json'))
ED = {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/perfumes-*.json')):
    ED.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
NOTES = {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/notes-*.json')):
    NOTES.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
BRANDS = {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/brands-*.json')):
    BRANDS.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
HUBS = json.load(open(ROOT / 'src/data/editorial/hubs.json'))


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def notes_of(p):
    return set(p['notes']['top'] + p['notes']['heart'] + p['notes']['base'])


def perfumers_of(slug):
    raw = (ED.get(slug) or {}).get('perfumer') or ''
    return [n.strip() for n in re.split(r',| et | and |&', raw) if n.strip()]


def pool(pred, gender=None, cap=30, with_unisex=True):
    """Exact gender first (dataset order = notoriety), then unisex."""
    exact = [p['slug'] for p in P if pred(p) and (gender is None or p['gender'] == gender)]
    uni = [p['slug'] for p in P if pred(p) and gender and with_unisex and p['gender'] == 'Unisex']
    return (exact[: cap - min(len(uni), cap // 3)] + uni)[:cap] if gender else exact[:cap]


G = {'F': ('Feminine', 'femme', 'women'), 'M': ('Masculine', 'homme', 'men')}
FAM = {  # key: (fr adjective, fr slug, en slug, en name)
    'floral': 'floral', 'oriental': 'oriental-ambre', 'woody': 'boise', 'chypre': 'chypre', 'fougere': 'fougere',
    'citrus': 'hesperide', 'gourmand': 'gourmand', 'aquatic': 'aquatique', 'aromatic': 'aromatique', 'fruity': 'fruite',
    'spicy': 'epice', 'musky': 'musque', 'powdery': 'poudre', 'leather': 'cuir',
}
FAM_EN = {'oriental': 'oriental-amber', 'woody': 'woody', 'citrus': 'citrus', 'aquatic': 'aquatic', 'aromatic': 'aromatic',
          'fruity': 'fruity', 'spicy': 'spicy', 'musky': 'musky', 'powdery': 'powdery', 'leather': 'leather'}
SEASON = {'spring': ('parfums-printemps', 'spring-perfumes'), 'summer': ('parfums-ete', 'summer-perfumes'),
          'autumn': ('parfums-automne', 'autumn-perfumes'), 'winter': ('parfums-hiver', 'winter-perfumes')}


def fam_slug(key, l):
    h = HUBS['families'].get(key, {})
    return h.get('slug_fr' if l == 'fr' else 'slug_en') or (FAM[key] if l == 'fr' else FAM_EN.get(key, key))


# ---------------------------------------------------------------- volumes
vol = collections.defaultdict(list)  # (cluster key) -> [(kw, volume)]
for r in csv.reader(open(ROOT / 'seo/haloscan/notes_volumes.tsv'), delimiter='\t'):
    if r and r[0] == 'note' and r[3].isdigit():
        vol[('note', r[1])].append((r[2], int(r[3])))
for r in csv.reader(open(ROOT / 'seo/haloscan/roadmap_volumes.tsv'), delimiter='\t'):
    if len(r) > 2 and r[2].isdigit():
        vol[('kw', r[1])].append((r[1], int(r[2])))
EXTRA = {  # measured 2026-09-28 (bulk calls in the session, see SEO_STRATEGY §8)
    'parfum fougère homme': 50, 'parfum aromatique homme': 20, 'parfum musqué femme': 40, 'parfum hespéridé homme': 70,
    'parfum floral homme': 50, 'parfum marin homme': 70, 'parfum aquatique homme': 20, 'parfum printemps femme': 50,
    'parfum printemps homme': 30, 'parfum automne homme': 10, 'parfum ado garçon': 880, 'parfum ado fille': 720,
    'parfum qui tient longtemps femme': 390, 'parfum qui tient longtemps homme': 140, 'parfum musc blanc homme': 170,
    'pyramide olfactive': 80, 'meilleur parfum yves saint laurent femme': 170, 'meilleur parfum dior': 90,
    'meilleur parfum tom ford': 70, 'meilleur parfum gucci femme': 70, 'meilleur parfum armani homme': 30,
    'meilleur parfum mixte': 20, 'meilleur parfum de niche': 140, 'meilleur parfum chanel': 20,
}


def kwvol(*kws):
    found = []
    for k in kws:
        v = EXTRA.get(k) or next((x for kw, x in vol[('kw', k)]), 0)
        if not v:
            for (c, _), rows in vol.items():
                v = v or next((x for kw, x in rows if kw == k), 0)
        found.append((k, v))
    return found


defs = []


def add(id, kind, slug_fr, slug_en, pool_, keywords, **extra):
    total = sum(v for _, v in keywords)
    defs.append({'id': id, 'kind': kind, 'slug_fr': slug_fr, 'slug_en': slug_en, 'volume': total,
                 'keywords': [{'kw': k, 'volume': v} for k, v in keywords if v], 'pool': pool_, **extra})


# ------------------------------------------------------------ note × genre
by_fr = {v['name_fr']: k for k, v in NOTES.items()}
NG_EXTRA = {('Oud', 'F'), ('Pepper', 'F')}  # strong demand, pool completed by unisex perfumes
for (cluster, name_fr), rows in vol.items():
    if cluster != 'note' or name_fr not in by_fr:
        continue
    key = by_fr[name_fr]
    for g, (gender, gfr, gen) in G.items():
        kws = [(kw, v) for kw, v in rows if gfr in kw]
        v = sum(x for _, x in kws)
        exact = sum(1 for p in P if p['gender'] == gender and key in notes_of(p))
        uni = sum(1 for p in P if p['gender'] == 'Unisex' and key in notes_of(p))
        if not ((v >= 30 and exact >= 3 and exact + uni >= 6) or ((key, g) in NG_EXTRA)):
            continue
        n = NOTES[key]
        add(f'ng:{key}:{g}', 'ng', f"{n['slug_fr']}/{gfr}", f"{n['slug_en']}/{gen}",
            pool(lambda p: key in notes_of(p), gender), kws, note=key, gender=gender,
            name_fr=n['name_fr'], name_en=n['name_en'])

# --------------------------------------------------------- famille × genre
FG = {('floral', 'F'): ['parfum floral femme'], ('floral', 'M'): ['parfum floral homme'],
      ('oriental', 'F'): ['parfum oriental femme'], ('oriental', 'M'): ['parfum oriental homme'],
      ('woody', 'F'): ['parfum boisé femme'], ('woody', 'M'): ['parfum boisé homme'],
      ('chypre', 'F'): ['parfum chypré femme'], ('fruity', 'F'): ['parfum fruité femme'],
      ('gourmand', 'F'): ['parfum gourmand femme'], ('spicy', 'F'): ['parfum épicé femme'],
      ('spicy', 'M'): ['parfum épicé homme'], ('aromatic', 'M'): ['parfum aromatique homme'],
      ('fougere', 'M'): ['parfum fougère homme'], ('musky', 'F'): ['parfum musqué femme'],
      ('citrus', 'M'): ['parfum hespéridé homme'], ('aquatic', 'M'): ['parfum marin homme', 'parfum aquatique homme'],
      ('powdery', 'F'): ['parfum poudré femme']}
for (fam, g), kws in FG.items():
    gender, gfr, gen = G[g]
    add(f'fg:{fam}:{g}', 'fg', f"{fam_slug(fam, 'fr')}/{gfr}", f"{fam_slug(fam, 'en')}/{gen}",
        pool(lambda p: fam in p['families'], gender), kwvol(*kws), family=fam, gender=gender)

# --------------------------------------------------------- saison × genre
SG = {'spring': ['parfum printemps femme', 'parfum printemps homme'], 'summer': ['parfum été femme', 'parfum été homme'],
      'autumn': ['parfum automne femme', 'parfum automne homme'], 'winter': ['parfum hiver femme', 'parfum hiver homme']}
for s, (sfr, sen) in SEASON.items():
    for g, (gender, gfr, gen) in G.items():
        kws = [k for k in SG[s] if gfr in k] + ([f"parfum d hiver {gfr}"] if s == 'winter' else [])
        add(f'sg:{s}:{g}', 'sg', f"{sfr}/{gfr}", f"{sen}/{gen}",
            pool(lambda p: s in (ED.get(p['slug']) or {}).get('seasons', []), gender), kwvol(*kws), season=s, gender=gender)

# ------------------------------------------------------- meilleurs parfums
niche = {b for b, v in BRANDS.items() if v.get('type') == 'niche'}
add('best:homme', 'best', 'homme', 'men', pool(lambda p: True, 'Masculine', cap=45, with_unisex=False),
    kwvol('meilleur parfum homme', 'meilleurs parfums homme'), gender='Masculine')
add('best:femme', 'best', 'femme', 'women', pool(lambda p: True, 'Feminine', cap=45, with_unisex=False),
    kwvol('meilleur parfum femme', 'meilleurs parfums femme'), gender='Feminine')
add('best:mixtes', 'best', 'mixtes', 'unisex', pool(lambda p: p['gender'] == 'Unisex', None, cap=40),
    kwvol('meilleur parfum mixte'), gender='Unisex')
add('best:niche', 'best', 'niche', 'niche', pool(lambda p: p['brand'] in niche, None, cap=45),
    kwvol('meilleur parfum de niche', 'parfum de niche', 'parfum niche'))
HOUSES = [('Dior', 'F', ['meilleur parfum dior femme', 'meilleur parfum dior']), ('Dior', 'M', ['meilleur parfum dior homme']),
          ('Chanel', 'F', ['meilleur parfum chanel femme', 'meilleur parfum chanel']),
          ('Guerlain', 'F', ['meilleur parfum guerlain femme']),
          ('Yves Saint Laurent', 'F', ['meilleur parfum yves saint laurent femme']),
          ('Tom Ford', 'M', ['meilleur parfum tom ford homme', 'meilleur parfum tom ford']),
          ('Giorgio Armani', 'M', ['meilleur parfum armani homme'])]
for brand, g, kws in HOUSES:
    gender, gfr, gen = G[g]
    bslug = BRANDS[brand]['slug']
    add(f'best:{bslug}:{g}', 'best', f'{bslug}-{gfr}', f'{bslug}-{gen}',
        pool(lambda p: p['brand'] == brand, gender, cap=20), kwvol(*kws), brand=brand, gender=gender)

# ------------------------------------------------------------- parfumeurs
count = collections.Counter(n for p in P for n in perfumers_of(p['slug']))
NOSES = [n for n, c in count.most_common() if c >= 4] + ['Thierry Wasser', 'Jean-Claude Ellena', 'Jacques Guerlain']
for n in NOSES:
    s = slugify(n)
    add(f'nose:{s}', 'nose', s, s, [p['slug'] for p in P if n in perfumers_of(p['slug'])],
        kwvol(n.lower(), f'parfumeur {n.lower()}'), perfumer=n)

# ---------------------------------------------------------------- guides
intense = lambda p: (ED.get(p['slug']) or {}).get('intensity', 3) >= 4
light = lambda p: (ED.get(p['slug']) or {}).get('intensity', 3) <= 3
GUIDES = [
    ('musc-blanc', 'parfum-musc-blanc', 'white-musk-perfume', pool(lambda p: 'Musk' in notes_of(p), None, cap=40),
     ['parfum musc blanc', 'parfum musc blanc femme', 'parfum musc blanc homme']),
    ('ado-garcon', 'parfum-ado-garcon', 'teen-boy-fragrance', pool(light, 'Masculine', cap=35), ['parfum ado garçon']),
    ('ado-fille', 'parfum-ado-fille', 'teen-girl-perfume', pool(light, 'Feminine', cap=35), ['parfum ado fille']),
    ('tenue-femme', 'parfum-qui-tient-longtemps-femme', 'long-lasting-perfume-women', pool(intense, 'Feminine', cap=35),
     ['parfum qui tient longtemps femme', 'parfum qui tient longtemps']),
    ('tenue-homme', 'parfum-qui-tient-longtemps-homme', 'long-lasting-cologne-men', pool(intense, 'Masculine', cap=35),
     ['parfum qui tient longtemps homme']),
    ('attire-femmes', 'parfum-qui-attire-les-femmes', 'most-complimented-mens-fragrances', pool(lambda p: True, 'Masculine', cap=40),
     ['parfum qui attire les femmes']),
    ('attire-hommes', 'parfum-qui-attire-les-hommes', 'most-complimented-womens-perfumes', pool(lambda p: True, 'Feminine', cap=40),
     ['parfum qui attire les hommes']),
    ('pyramide', 'pyramide-olfactive', 'fragrance-pyramid', [p['slug'] for p in P[:25]],
     ['note olfactive', 'notes de tête', 'pyramide olfactive']),
]
for gid, sfr, sen, pl, kws in GUIDES:
    add(f'guide:{gid}', 'guide', sfr, sen, pl, kwvol(*kws))

defs.sort(key=lambda d: -d['volume'])
out = ROOT / 'src/data/ranked-pages.json'
json.dump(defs, open(out, 'w'), ensure_ascii=False, indent=1)
print(len(defs), 'pages →', out)
print(collections.Counter(d['kind'] for d in defs))
for d in defs:
    print(f"{d['volume']:6d}  {d['id']:40s} pool={len(d['pool'])}")
