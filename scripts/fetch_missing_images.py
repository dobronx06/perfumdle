"""Fetch candidate bottle images for perfumes that have none (missing or dropped by the visual audit).

Usage: python3 scripts/fetch_missing_images.py <candidates_dir>
Writes <dir>/<slug>__<n>.<ext> + <dir>/candidates.json. Nothing goes to public/ until a human (or a
reviewing agent) has checked each bottle; accepted ones are recorded in scripts/image-fixes.json.
"""
import json, sys, pathlib, time, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fetch_images import curl_json, curl_download, API_BASE  # noqa: E402  (reuses the Fragella client)

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
todo = [p for p in perfumes if not p.get('image')]
report = {}
for i, p in enumerate(todo, 1):
    seen, cands = set(), []
    for q in (f"{p['name']} {p['brand']}", p['name'], f"{p['brand']} {p['name']}"):
        data = curl_json(f"{API_BASE}/fragrances?search={urllib.parse.quote(q)}&limit=5") or []
        for item in data if isinstance(data, list) else []:
            url = item.get('Image URL Transparent') or item.get('Image URL')
            key = (item.get('Name'), item.get('Brand'))
            if not url or key in seen:
                continue
            seen.add(key)
            cands.append({'name': item.get('Name'), 'brand': item.get('Brand'), 'year': item.get('Year'), 'url': url,
                          'brand_match': (item.get('Brand') or '').lower() in p['brand'].lower() or p['brand'].lower() in (item.get('Brand') or '').lower()})
        time.sleep(0.35)
    cands.sort(key=lambda c: not c['brand_match'])
    kept = []
    for n, c in enumerate(cands[:4]):
        ext = 'webp' if c['url'].endswith('.webp') else 'jpg'
        f = out / f"{p['slug']}__{n}.{ext}"
        if curl_download(c['url'], str(f)):
            c['file'] = str(f)
            kept.append(c)
    report[p['slug']] = {'want': f"{p['brand']} {p['name']} ({p['year']}, {p['concentration']})", 'candidates': kept}
    print(f"[{i}/{len(todo)}] {p['slug']}: {len(kept)} candidates", flush=True)
json.dump(report, open(out / 'candidates.json', 'w'), ensure_ascii=False, indent=1)
print('done', sum(1 for v in report.values() if v['candidates']), '/', len(todo), 'with candidates')
