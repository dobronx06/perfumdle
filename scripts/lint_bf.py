"""Lint Black Friday pages (src/data/blackfriday/*.json) against scripts/WRITING_RULES.md and the sourcing rules.

Usage: python3 scripts/lint_bf.py src/data/blackfriday/bf-p01.json [...]
Exit 1 on any error. Warnings are printed but do not fail.
"""
import json, re, sys, pathlib, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
PERFUMES = {p['slug'] for p in json.load(open(ROOT / 'src/data/perfumes.json'))}
BANNED = ['véritable', 'incontournable', 'envoûtant', 'sublim', 'subtil équilibre', 'alliance parfaite', 'mariage parfait',
          'que vous soyez', 'plongez', 'découvrez', 'laissez-vous', "n'hésitez pas", 'n’hésitez pas', 'en somme', 'en définitive',
          'en conclusion', 'il est important de noter', 'il convient de', 'un must', 'intemporel', 'voyage olfactif',
          'sillage inoubliable', 'ode à', 'invitation à', 'symphonie', 'explosion de', 'bien plus qu', 'tout simplement',
          'résolument', 'audacieu', 'témoigne de', 'marque un tournant', 'les experts', 'selon les amateurs', 'pas seulement',
          'dupe', 'à ne pas manquer', 'bon plan ultime', 'ne ratez pas', 'profitez']
errors, warns = [], []

def strings(node, path=''):
    if isinstance(node, str): yield path, node
    elif isinstance(node, dict):
        for k, v in node.items(): yield from strings(v, f'{path}.{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from strings(v, f'{path}[{i}]')

for fn in sys.argv[1:]:
    data = json.load(open(fn))
    for slug, c in data.items():
        tag = f'{pathlib.Path(fn).name}:{slug}'
        for k in ('kind', 'target', 'title', 'meta', 'h1', 'intro', 'sections', 'faq', 'sources'):
            if not c.get(k): errors.append(f'{tag}: missing {k}')
        if len(c.get('title', '')) > 62: errors.append(f'{tag}: title {len(c["title"])} chars')
        if not 110 <= len(c.get('meta', '')) <= 165: warns.append(f'{tag}: meta {len(c.get("meta", ""))} chars')
        if 'black friday' not in c.get('title', '').lower(): errors.append(f'{tag}: title without Black Friday')
        for s in c.get('picks', []):
            if s not in PERFUMES: errors.append(f'{tag}: unknown pick {s}')
        if c.get('perfume') and c['perfume'] not in PERFUMES: errors.append(f'{tag}: unknown perfume {c["perfume"]}')
        for r in c.get('prices', []):
            for k in ('shop', 'item', 'price', 'seen', 'url'):
                if not r.get(k): errors.append(f'{tag}: price without {k}')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', r.get('seen', '')): errors.append(f'{tag}: bad date {r.get("seen")}')
            if not urllib.parse.urlparse(r.get('url', '')).netloc: errors.append(f'{tag}: bad url {r.get("url")}')
        for u in c.get('sources', []):
            if not urllib.parse.urlparse(u).netloc: errors.append(f'{tag}: bad source {u}')
        if c.get('kind') == 'perfume' and not c.get('prices'): warns.append(f'{tag}: no price')
        words = 0
        for path, text in strings({k: c.get(k) for k in ('title', 'meta', 'h1', 'intro', 'sections', 'why', 'faq')}):
            low = text.lower()
            words += len(text.split())
            if re.search('[—–]', text): errors.append(f'{tag}{path}: dash')
            if '!' in text: errors.append(f'{tag}{path}: exclamation')
            if '**' in text: errors.append(f'{tag}{path}: markdown')
            for b in BANNED:
                if b in low: errors.append(f'{tag}{path}: banned "{b}"')
            for sent in re.split(r'[.?:;]\s', text):
                if sent.count(',') > 2: warns.append(f'{tag}{path}: {sent.count(",")} commas')
        if words < 220: errors.append(f'{tag}: only {words} words')
for w in warns: print('WARN', w)
for e in errors: print('ERR', e)
print('OK' if not errors else f'{len(errors)} errors', f'({len(warns)} warnings)')
sys.exit(1 if errors else 0)
