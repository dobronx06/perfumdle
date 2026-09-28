"""Build src/data/publish-schedule.json — the drip-feed calendar for programmatic pages.

Usage: python3 scripts/schedule.py [start YYYY-MM-DD] [per_day]
Pages are released in order of notoriety (dataset order), `per_day` perfumes per day
(each perfume = 1 FR + 1 EN URL). Already-scheduled dates are preserved.
"""
import json, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
start = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
per_day = int(sys.argv[2]) if len(sys.argv) > 2 else 8
perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
path = ROOT / 'src/data/publish-schedule.json'
sched = json.load(open(path)) if path.exists() else {}
sim = sched.setdefault('similar', {})
sched.setdefault('compare', {})
todo = [p['slug'] for p in sorted(perfumes, key=lambda p: p['id']) if p['slug'] not in sim]
for i, slug in enumerate(todo):
    sim[slug] = (start + datetime.timedelta(days=i // per_day)).isoformat()
json.dump(sched, open(path, 'w'), indent=1)
last = max(sim.values()) if sim else None
print(f"{len(todo)} new similar pages scheduled, {per_day}/day, from {start} to {last}")
