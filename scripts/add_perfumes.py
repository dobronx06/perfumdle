"""Append perfumes collected after launch to src/data/perfumes.json and schedule their release.

Input: scripts/new-perfumes/batch-*.json (one entry per perfume, harvested from clean sources only:
brand sites, Wikipedia, press, retailer product pages; never Fragrantica, Basenotes or Parfumo).
Entries with confidence "low" are skipped. Idempotent: an existing slug is updated in place.
Release dates go to publish-schedule.json under "perfume" (a few per day, never on top of an
existing date), so Google sees a steady trickle of new pages instead of a spike.

Run after scripts/prepare_data.py, which rebuilds perfumes.json from the launch dataset only.

Usage: python3 scripts/add_perfumes.py [--start YYYY-MM-DD] [--per-day 2]
"""
import json, re, sys, glob, pathlib, datetime, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
PERFUMES = ROOT / 'src/data/perfumes.json'
SCHEDULE = ROOT / 'src/data/publish-schedule.json'

FAMILY_FACETS = [
    ('floral', ['floral']), ('oriental', ['oriental', 'amber', 'ambery']),
    ('woody', ['woody']), ('chypre', ['chypre']), ('fougere', ['fougère', 'fougere']),
    ('citrus', ['citrus']), ('gourmand', ['gourmand']), ('leather', ['leather']),
    ('aquatic', ['aquatic', 'marine']), ('aromatic', ['aromatic']),
    ('fruity', ['fruity']), ('spicy', ['spicy']), ('musky', ['musk', 'musky']),
    ('green', ['green']), ('powdery', ['powdery', 'aldehyde']),
]
BRAND_ALIASES = {'Kilian': 'By Kilian', 'Kilian Paris': 'By Kilian', 'Hermes': 'Hermès', 'Lancome': 'Lancôme', 'Paco Rabanne': 'Paco Rabanne', 'Rabanne': 'Paco Rabanne'}


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


start = datetime.date.fromisoformat(arg('--start', (datetime.date.today() + datetime.timedelta(days=1)).isoformat()))
per_day = int(arg('--per-day', '2'))

perfumes = json.load(open(PERFUMES))
by_slug = {p['slug']: p for p in perfumes}
next_id = max(p['id'] for p in perfumes) + 1
schedule_raw = SCHEDULE.read_text()
schedule = json.loads(schedule_raw)
planned = schedule.setdefault('perfume', {})

added, skipped = [], []
for f in sorted(glob.glob(str(ROOT / 'scripts/new-perfumes/batch-*.json'))):
    for r in json.load(open(f)):
        if r.get('confidence') == 'low':
            skipped.append(f"{r['brand']} {r['name']} (low confidence)")
            continue
        brand = BRAND_ALIASES.get(r['brand'], r['brand'])
        slug = slugify(f"{brand} {r['name']}")
        fam = r['family'].replace('Fougere', 'Fougère')
        facets = [k for k, words in FAMILY_FACETS if any(w in fam.lower() for w in words)]
        notes, seen = {}, set()
        for k in ('top', 'heart', 'base'):  # a material listed twice stays at its first tier
            notes[k] = [n for n in dict.fromkeys(x.strip() for x in r['notes'].get(k, [])) if n and n not in seen]
            seen.update(notes[k])
        entry = {
            'id': by_slug[slug]['id'] if slug in by_slug else next_id, 'slug': slug, 'name': r['name'], 'brand': brand,
            'year': int(r['year']), 'gender': r['gender'], 'family': fam, 'families': facets,
            'concentration': r['concentration'], 'notes': notes, 'image': by_slug.get(slug, {}).get('image'),
        }
        if slug in by_slug:
            if slug not in planned:  # a launch perfume: never overwrite it from a batch
                skipped.append(f'{slug} (already on the site)')
                continue
            perfumes[perfumes.index(by_slug[slug])] = entry
        else:
            perfumes.append(entry)
            by_slug[slug] = entry
            next_id += 1
        added.append(slug)

# Release dates: per_day new perfumes a day from `start`, skipping slugs that already have one.
day, used = start, 0
for slug in added:
    if slug in planned:
        continue
    if used == per_day:
        day, used = day + datetime.timedelta(days=1), 0
    planned[slug] = day.isoformat()
    used += 1

json.dump(perfumes, open(PERFUMES, 'w'), ensure_ascii=False, indent=1)
json.dump(schedule, open(SCHEDULE, 'w'), ensure_ascii=False, indent=1)
print(f'{len(added)} perfumes added or updated, {len(perfumes)} in total')
print('last release:', max(planned.values()) if planned else '-')
for s in skipped:
    print('skipped:', s)
