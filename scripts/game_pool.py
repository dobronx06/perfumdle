"""Daily-game pool: the 100 best-known perfumes (Haloscan FR search score) with a bottle image and a full pyramid.

Usage: python3 scripts/game_pool.py [size=100]  -> src/data/game-pool.json
Every perfume stays guessable; only the mystery perfume is drawn from this pool, so casual players know it.
"""
import json, csv, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
size = int(sys.argv[1]) if len(sys.argv) > 1 else 100
P = json.load(open(ROOT / 'src/data/perfumes.json'))
CLAMP = {'louis-vuitton-ombre-nomade': 3000}
score = {}
for r in csv.DictReader(open(ROOT / 'seo/haloscan/perfume_volumes.tsv'), delimiter='\t'):
    score[r['slug']] = min(int(r['volume'] or 0), CLAMP.get(r['slug'], 10**9)) + 20 * int(r['alt_volume'] or 0) + 3 * int(r['info_volume'] or 0)
pool = [p['slug'] for p in sorted(P, key=lambda p: (-score.get(p['slug'], 0), p['id'])) if p.get('image') and all(p['notes'][t] for t in ('top', 'heart', 'base'))][:size]
json.dump(pool, open(ROOT / 'src/data/game-pool.json', 'w'), indent=1)
print(len(pool), 'perfumes in the daily pool; last:', pool[-5:])
