"""Merge data.json (notes) + src/data/data.json (slugs/images) into
src/data/perfumes.json with normalized brands, notes and families."""
import json, re, unicodedata, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
raw = json.load(open(ROOT / 'data.json'))['entities']
site = json.load(open(ROOT / 'src/data/data.json'))['entites']

BRAND_ALIASES = {
    'Hermes': 'Hermès', 'Lancome': 'Lancôme',
    'Editions de Parfums Frederic Malle': 'Frédéric Malle',
    'Editions de Parfums Frédéric Malle': 'Frédéric Malle',
    'Initio Parfums Prives': 'Initio Parfums Privés',
    'Thierry Mugler': 'Mugler', 'Jean Patou': 'Patou',
}
NOTE_ALIASES = {
    'Blackcurrant': 'Black Currant', 'Agarwood': 'Oud', 'Orris': 'Iris',
    'Olibanum': 'Incense', 'Frankincense': 'Incense', 'Tobacco Leaf': 'Tobacco',
    'Jasmine Sambac': 'Jasmine', 'Turkish Rose': 'Rose', 'Bulgarian Rose': 'Rose',
    'May Rose': 'Rose', 'Damask Rose': 'Rose', 'Rose de Mai': 'Rose',
    'Black Pepper': 'Pepper', 'Fougere': 'Fougère', 'Bitter Almond': 'Almond',
    'Madagascar Vanilla': 'Vanilla', 'Bourbon Vanilla': 'Vanilla',
    'Virginia Cedar': 'Cedar', 'Atlas Cedar': 'Cedar', 'Cedarwood': 'Cedar',
    'Calabrian Bergamot': 'Bergamot', 'Sicilian Lemon': 'Lemon',
    'African Orange Flower': 'Orange Blossom', 'Orange Flower': 'Orange Blossom',
    'Tonka': 'Tonka Bean', 'Gaiac Wood': 'Guaiac Wood', 'Cassis': 'Black Currant', 'Currant': 'Black Currant', 'Violet Leaves': 'Violet Leaf', 'Tangerine': 'Mandarin', 'Citrus Notes': 'Citrus', 'Citruses': 'Citrus', 'Tuberose Absolute': 'Tuberose', 'Indian Tuberose': 'Tuberose', 'Egyptian Jasmine': 'Jasmine', 'Jasmine Bud': 'Jasmine', 'Jasmine Petals': 'Jasmine', 'Ambrox': 'Ambroxan', 'White Musk': 'Musk', 'Musks': 'Musk',
}
NAME_FIXES = {}  # names are now corrected at the source (data.json)
# family facets: a perfume appears on every facet page its family string mentions
FAMILY_FACETS = [
    ('floral', ['floral']), ('oriental', ['oriental', 'amber', 'ambery']),
    ('woody', ['woody']), ('chypre', ['chypre']), ('fougere', ['fougère', 'fougere']),
    ('citrus', ['citrus']), ('gourmand', ['gourmand']), ('leather', ['leather']),
    ('aquatic', ['aquatic', 'marine']), ('aromatic', ['aromatic']),
    ('fruity', ['fruity']), ('spicy', ['spicy']), ('musky', ['musk', 'musky']),
    ('green', ['green']), ('powdery', ['powdery', 'aldehyde']),
]

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def norm_note(n):
    n = n.strip()
    return NOTE_ALIASES.get(n, n)

# Images flagged by the visual audit (scripts/image-audit-*.json) are dropped: a placeholder beats a wrong bottle.
BAD_IMAGES = set()
for f in ROOT.glob('scripts/image-audit-*.json'):
    BAD_IMAGES |= {slug for slug, v in json.load(open(f)).items() if v['verdict'] in ('wrong', 'poor', 'unsure')}

# Replacement bottles checked by eye after the audit (scripts/fetch_missing_images.py): slug -> /img/... path.
FIXES_PATH = ROOT / 'scripts/image-fixes.json'
IMAGE_FIXES = json.load(open(FIXES_PATH)) if FIXES_PATH.exists() else {}

def image_of(s):
    if s['slug'] in IMAGE_FIXES:
        return IMAGE_FIXES[s['slug']]
    return None if s['slug'] in BAD_IMAGES else (s.get('image') or None)

out = []
for r, s in zip(raw, site):
    assert r['name'] == s['nom']
    fam = r['family'].replace('Fougere', 'Fougère')
    fl = fam.lower()
    facets = [k for k, words in FAMILY_FACETS if any(w in fl for w in words)]
    if 'Tabac Blond' in r['name'] and 'leather' not in facets:
        facets.append('leather')  # historically a leather perfume; the raw family label omits it
    notes, seen = {}, set()
    for k in ('top', 'heart', 'base'):  # a material listed in several tiers is kept at its first (highest) tier
        notes[k] = [n for n in dict.fromkeys(norm_note(x) for x in r[k + 'Notes']) if n not in seen]
        seen.update(notes[k])
    out.append({
        'id': s['id'], 'slug': s['slug'], 'name': NAME_FIXES.get(r['name'], r['name']),
        'brand': BRAND_ALIASES.get(r['brand'], r['brand']),
        'year': r['year'], 'gender': r['gender'], 'family': fam,
        'families': facets, 'concentration': r['concentration'],
        'notes': notes, 'image': image_of(s),
    })

brands = collections.Counter(p['brand'] for p in out)
notes = collections.Counter(n for p in out for n in set(sum(p['notes'].values(), [])))
json.dump(out, open(ROOT / 'src/data/perfumes.json', 'w'), ensure_ascii=False, indent=1)
# keep the game's dataset in sync so it never reveals a wrong bottle either
game = json.load(open(ROOT / 'src/data/data.json'))
for e in game['entites']:
    if e['slug'] in IMAGE_FIXES:
        e['image'] = IMAGE_FIXES[e['slug']]
    elif e['slug'] in BAD_IMAGES:
        e.pop('image', None)
json.dump(game, open(ROOT / 'src/data/data.json', 'w'), ensure_ascii=False, indent=2)
print(len(BAD_IMAGES), 'images dropped by audit')
print(len(out), 'perfumes |', len(brands), 'brands |', sum(1 for v in notes.values() if v >= 4), 'notes>=4')
json.dump({'brands': sorted(brands), 'notes': sorted(n for n, v in notes.items() if v >= 4 and n != 'Woody Notes')},
          open(ROOT / 'scripts/keys.json', 'w'), ensure_ascii=False, indent=1)
