"""Pinterest bulk-upload CSVs (Settings > Bulk create Pins), scheduled as a drip.

Usage: python3 scripts/pinterest_csv.py [start YYYY-MM-DD] [per_day=5]
Writes seo/pinterest/pins-<n>.csv (Pinterest accepts at most 200 rows per file).
One pin per perfume page, most searched first, board by gender (board names must match the boards on the account).
"""
import csv, json, glob, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
start = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today() + datetime.timedelta(days=1)
per_day = int(sys.argv[2]) if len(sys.argv) > 2 else 5
BOARD = {'Feminine': 'Parfums femme : notes, avis et parfums similaires', 'Masculine': 'Parfums homme : notes, avis et parfums similaires',
         'Unisex': 'Parfums mixtes : notes, avis et parfums similaires'}
HOURS = [8, 11, 14, 18, 21]
P = json.load(open(ROOT / 'src/data/perfumes.json'))
ED = {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/perfumes-[0-9]*.json')):
    ED.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
NAMES = json.load(open(ROOT / 'src/data/editorial/note-names.json'))
for fn in glob.glob(str(ROOT / 'src/data/editorial/notes-*.json')):
    NAMES.update({k: v['name_fr'] for k, v in json.load(open(fn)).items() if not k.startswith('_')})
pool = json.load(open(ROOT / 'src/data/game-pool.json'))
rank = {s: i for i, s in enumerate(pool)}
items = sorted((p for p in P if (ROOT / f"public/pins/{p['slug']}.jpg").exists()), key=lambda p: (rank.get(p['slug'], 999), p['id']))
out = ROOT / 'seo/pinterest'; out.mkdir(parents=True, exist_ok=True)
rows = []
for i, p in enumerate(items):
    day = start + datetime.timedelta(days=i // per_day)
    when = datetime.datetime.combine(day, datetime.time(HOURS[i % per_day % len(HOURS)]))
    name = p['name'] if p['brand'].lower() in p['name'].lower() else f"{p['name']} de {p['brand']}"
    notes = [NAMES.get(n, n).lower() for n in (p['notes']['top'] + p['notes']['heart'] + p['notes']['base'])[:6]]
    tagline = (ED.get(p['slug']) or {}).get('fr', {}).get('tagline', '')
    rows.append({
        'Title': f'{name} : notes, avis et parfums similaires'[:100],
        'Media URL': f"https://perfumdle.com/pins/{p['slug']}.jpg",
        'Pinterest board': BOARD[p['gender']],
        'Thumbnail': '',
        'Description': f"{tagline} {p['name']} ({p['brand']}, {p['year']}). Notes : {', '.join(notes)}. Pyramide olfactive complète, avis et parfums qui lui ressemblent.".strip()[:500],
        'Link': f"https://perfumdle.com/fr/parfum/{p['slug']}/",
        'Publish date': when.strftime('%Y-%m-%dT%H:%M:%S'),
        'Keywords': ', '.join(dict.fromkeys([p['brand'].lower(), 'parfum', 'notes de parfum', 'avis parfum'] + notes[:3])),
    })
for n in range(0, len(rows), 200):
    path = out / f'pins-{n // 200 + 1}.csv'
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows[n:n + 200])
    print(path, len(rows[n:n + 200]), 'pins,', rows[n]['Publish date'], '->', rows[min(n + 199, len(rows) - 1)]['Publish date'])
