"""Schedule the ranked pages (src/data/ranked-pages.json) into publish-schedule.json → "ranked".

Usage: python3 scripts/schedule_ranked.py [start YYYY-MM-DD] [end YYYY-MM-DD] [--reorder]
Irregular on purpose: a seeded random number of pages per day (some days 0, some days 4), summing exactly
to the number of pages and spread over the whole window, so Google sees organic growth, not a batch.
Order: search volume, with in-season pages (autumn / winter) first. Pages already live keep their date.
"""
import json, sys, random, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]
start = datetime.date.fromisoformat(args[0] if args else '2026-10-01')
end = datetime.date.fromisoformat(args[1] if len(args) > 1 else '2026-11-30')
today = datetime.date.today().isoformat()

defs = json.load(open(ROOT / 'src/data/ranked-pages.json'))
path = ROOT / 'src/data/publish-schedule.json'
sched = json.load(open(path))
ranked = sched.setdefault('ranked', {})
if '--reorder' in sys.argv:
    ranked = {k: v for k, v in ranked.items() if v <= today}

BOOST = {'sg:winter:F': 5000, 'sg:winter:M': 5000, 'sg:autumn:F': 800, 'sg:autumn:M': 800}
todo = [d['id'] for d in sorted(defs, key=lambda d: -(d['volume'] + BOOST.get(d['id'], 0))) if d['id'] not in ranked]

rng = random.Random(20261001)
days = [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]
weights = [0 if rng.random() < 0.18 else rng.choice([0.5, 1, 1, 1.5, 2, 2.5, 3]) for _ in days]
total, acc, prev, counts = sum(weights), 0.0, 0, []
for w in weights:  # cumulative rounding → exact total, irregular per day
    acc += w
    cur = round(acc / total * len(todo))
    counts.append(cur - prev)
    prev = cur
i = 0
for day, n in zip(days, counts):
    for _ in range(n):
        ranked[todo[i]] = day.isoformat()
        i += 1

sched['ranked'] = dict(sorted(ranked.items(), key=lambda kv: kv[1]))
json.dump(sched, open(path, 'w'), indent=1)
per_day = [c for c in counts]
print(f'{len(todo)} ranked pages scheduled {start} → {end}; per day min {min(per_day)} max {max(per_day)}, '
      f'{per_day.count(0)} days without publication')
