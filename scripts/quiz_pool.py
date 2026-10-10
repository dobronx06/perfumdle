"""Perfume quiz pool: every perfume with a bottle image, a full pyramid and editorial data (seasons, occasions, intensity).

Usage: python3 scripts/quiz_pool.py  -> src/data/quiz-pool.json
Compact keys, read by src/views/QuizView.astro (which adds localized note/family names and the similar-page flag):
  s slug, n name, b brand, i image, g gender (F/M/U), m main family, f families, t/h/d top/heart/base notes,
  se seasons, o occasions, x intensity 1-5, p popularity 0-1 (Haloscan FR search score, log scaled, used as a tie-breaker).
"""
import json, csv, glob, math, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.load(open(ROOT / 'src/data/perfumes.json'))

ed = {}
for f in glob.glob(str(ROOT / 'src/data/editorial/perfumes-*.json')):
    for k, v in json.load(open(f)).items():
        if not k.startswith('_'):
            ed[k] = v

CLAMP = {'louis-vuitton-ombre-nomade': 3000}
score = {}
for r in csv.DictReader(open(ROOT / 'seo/haloscan/perfume_volumes.tsv'), delimiter='\t'):
    score[r['slug']] = min(int(r['volume'] or 0), CLAMP.get(r['slug'], 10**9)) + 20 * int(r['alt_volume'] or 0) + 3 * int(r['info_volume'] or 0)
top = math.log1p(max(score.values()))

# Main family = facet named by the first word of the dataset label (same rule as the daily game).
FIRST_WORD = {
    'floral': 'floral', 'oriental': 'oriental', 'amber': 'oriental', 'ambery': 'oriental', 'woody': 'woody', 'chypre': 'chypre',
    'fougère': 'fougere', 'fougere': 'fougere', 'citrus': 'citrus', 'gourmand': 'gourmand', 'leather': 'leather', 'aquatic': 'aquatic',
    'marine': 'aquatic', 'aromatic': 'aromatic', 'fruity': 'fruity', 'spicy': 'spicy', 'musk': 'musky', 'musky': 'musky',
    'green': 'green', 'powdery': 'powdery', 'aldehyde': 'powdery',
}
G = {'Feminine': 'F', 'Masculine': 'M', 'Unisex': 'U'}

pool = []
for p in P:
    e = ed.get(p['slug'])
    if not (p.get('image') and e and all(p['notes'][t] for t in ('top', 'heart', 'base'))):
        continue
    pool.append({
        's': p['slug'], 'n': p['name'], 'b': p['brand'], 'i': p['image'], 'g': G[p['gender']],
        'm': FIRST_WORD.get(p['family'].split(' ')[0].lower(), p['families'][0]), 'f': p['families'],
        't': p['notes']['top'], 'h': p['notes']['heart'], 'd': p['notes']['base'],
        'se': e.get('seasons', []), 'o': e.get('occasions', []), 'x': e.get('intensity', 3),
        'p': round(math.log1p(score.get(p['slug'], 0)) / top, 2),
    })
pool.sort(key=lambda x: -x['p'])
json.dump(pool, open(ROOT / 'src/data/quiz-pool.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(pool), 'perfumes in the quiz pool')
