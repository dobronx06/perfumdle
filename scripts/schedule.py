"""Build src/data/publish-schedule.json — the drip-feed calendar for programmatic pages.

Usage: python3 scripts/schedule.py [start YYYY-MM-DD] [per_day] [--reorder]
`per_day` perfumes per day (each perfume = 1 FR + 1 EN URL).

Order = search demand (seo/haloscan/perfume_volumes.tsv, Haloscan FR, 2026-09), then dataset order.
Score = perfume query volume + 20 × "dupe / qui ressemble / similaire / pas cher" volume
      + 3 × "avis / notes / composition" volume — the alternative intent is what the page answers.
By default already-scheduled dates are preserved; --reorder rebuilds every date that is
still in the future (pages already live keep their date).
"""
import json, sys, datetime, pathlib, csv
ROOT = pathlib.Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]
reorder = '--reorder' in sys.argv
start = datetime.date.fromisoformat(args[0]) if args else datetime.date.today()
per_day = int(args[1]) if len(args) > 1 else 8
today = datetime.date.today().isoformat()

# Outliers whose Haloscan volume is not credible for the perfume itself (clamped).
CLAMP = {'louis-vuitton-ombre-nomade': 3000}

score = {}
vol_path = ROOT / 'seo/haloscan/perfume_volumes.tsv'
if vol_path.exists():
    for r in csv.DictReader(open(vol_path), delimiter='\t'):
        v = min(int(r['volume'] or 0), CLAMP.get(r['slug'], 10**9))
        score[r['slug']] = v + 20 * int(r['alt_volume'] or 0) + 3 * int(r['info_volume'] or 0)

perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
path = ROOT / 'src/data/publish-schedule.json'
sched = json.load(open(path)) if path.exists() else {}
sim = sched.setdefault('similar', {})
sched.setdefault('compare', {})
if reorder:
    for slug in [s for s, d in sim.items() if d > today]:
        del sim[slug]
ordered = sorted(perfumes, key=lambda p: (-score.get(p['slug'], 0), p['id']))
todo = [p['slug'] for p in ordered if p['slug'] not in sim]
for i, slug in enumerate(todo):
    sim[slug] = (start + datetime.timedelta(days=i // per_day)).isoformat()
sched['similar'] = dict(sorted(sim.items(), key=lambda kv: kv[1]))
json.dump(sched, open(path, 'w'), indent=1)
last = max(sim.values()) if sim else None
print(f"{len(todo)} similar pages scheduled, {per_day}/day, from {start} to {last}")
