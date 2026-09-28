"""Briefs to deepen the most-searched perfume pages (history, detailed review, rivals, performance).

Usage: python3 scripts/deep_briefs.py <out_dir> [top_n=100] [per_batch=10]
Top = score used by the drip (seo/haloscan/perfume_volumes.tsv). Each perfume gets its data, current copy
(so writers don't repeat it) and its 3 closest perfumes by the site's similarity formula.
"""
import json, glob, csv, math, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
per = int(sys.argv[3]) if len(sys.argv) > 3 else 10
P = json.load(open(ROOT / 'src/data/perfumes.json'))
BY = {p['slug']: p for p in P}
ED = {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/perfumes-[0-9]*.json')):
    ED.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})

notes = lambda p: set(p['notes']['top'] + p['notes']['heart'] + p['notes']['base'])
cnt = collections.Counter(n for p in P for n in notes(p))
IDF = {n: math.log(len(P) / c) for n, c in cnt.items()}


def sim(a, b):  # mirrors similarity() in src/lib/catalog.ts
    s = sum(IDF[n] for n in notes(b) & notes(a))
    s += len(set(a['families']) & set(b['families'])) * 1.2
    s += 1.5 if a['family'] == b['family'] else 0
    s += 0.6 if a['gender'] == b['gender'] else 0
    return s


CLAMP = {'louis-vuitton-ombre-nomade': 3000}
score = {}
for r in csv.DictReader(open(ROOT / 'seo/haloscan/perfume_volumes.tsv'), delimiter='\t'):
    score[r['slug']] = min(int(r['volume'] or 0), CLAMP.get(r['slug'], 10**9)) + 20 * int(r['alt_volume'] or 0) + 3 * int(r['info_volume'] or 0)
top = sorted(P, key=lambda p: (-score.get(p['slug'], 0), p['id']))[:top_n]

items = []
for p in top:
    e = ED.get(p['slug'], {})
    rivals = sorted((o for o in P if o['slug'] != p['slug']), key=lambda o: -sim(p, o))[:3]
    items.append({
        'slug': p['slug'], 'name': p['name'], 'brand': p['brand'], 'year': p['year'], 'gender': p['gender'],
        'family': p['family'], 'concentration': p['concentration'], 'notes': p['notes'],
        'perfumer': e.get('perfumer'), 'intensity_1_5': e.get('intensity'), 'seasons': e.get('seasons'),
        'occasions': e.get('occasions'), 'search_volume_fr': score.get(p['slug'], 0),
        'current_copy': {'fr': e.get('fr'), 'en': e.get('en')},
        'rivals': [{'slug': o['slug'], 'name': o['name'], 'brand': o['brand'], 'year': o['year'], 'notes': o['notes'],
                    'tagline_fr': ED.get(o['slug'], {}).get('fr', {}).get('tagline')} for o in rivals],
    })
for i in range(0, len(items), per):
    name = f'deep-{i // per + 1:02d}'
    json.dump({'batch': name, 'perfumes': items[i:i + per]}, open(out / f'{name}.json', 'w'), ensure_ascii=False, indent=1)
    print(name, [x['slug'] for x in items[i:i + per]])
