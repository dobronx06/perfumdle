"""Lint the Christmas gift pages (src/data/noel/*.json) against scripts/WRITING_RULES.md and the sourcing rules.

Usage: python3 scripts/lint_noel.py [src/data/noel/*.json]   (no argument: every file in src/data/noel/)
Exit 1 on any error. Warnings are printed but do not fail.
Picks (and the "about" perfume of a "like" page) must have a live fiche on the page's own publish date.
Two non-advice pages may not share 5 picks or more, so each page keeps its own angle.
"""
import json, re, sys, pathlib, urllib.parse, collections, itertools
ROOT = pathlib.Path(__file__).resolve().parent.parent
PERFUMES = {p['slug']: p for p in json.load(open(ROOT / 'src/data/perfumes.json'))}
SCHEDULE = json.load(open(ROOT / 'src/data/publish-schedule.json'))
GROUPS = ('who', 'age', 'like', 'taste', 'style', 'advice')
FILES = sys.argv[1:] or sorted(str(f) for f in (ROOT / 'src/data/noel').glob('*.json'))
ALL = {}
for fn in FILES: ALL.update(json.load(open(fn)))

def live_on(slug, day):
    """A perfume fiche exists on `day` unless it is drip-fed with a later date."""
    d = SCHEDULE['perfume'].get(slug)
    return slug in PERFUMES and (d is None or (day is not None and d <= day))
BANNED = ['véritable', 'incontournable', 'envoûtant', 'sublim', 'subtil équilibre', 'alliance parfaite', 'mariage parfait',
          'que vous soyez', 'plongez', 'découvrez', 'laissez-vous', "n'hésitez pas", 'n’hésitez pas', 'en somme', 'en définitive',
          'en conclusion', 'il est important de noter', 'il convient de', 'un must', 'intemporel', 'voyage olfactif',
          'sillage inoubliable', 'ode à', 'invitation à', 'symphonie', 'explosion de', 'bien plus qu', 'tout simplement',
          'résolument', 'audacieu', 'témoigne de', 'marque un tournant', 'les experts', 'selon les amateurs', 'pas seulement',
          'dupe', 'à ne pas manquer', 'bon plan', 'ne ratez pas', 'profitez', 'promo', 'remise', '€', 'fragrantica', 'basenotes', 'parfumo']
SWEET = re.compile(r'vanill|tonka|praline|caramel|chocolate|cocoa|\bhoney\b|sugar|toffee', re.I)
errors, warns = [], []
h1s, titles = collections.Counter(), collections.Counter()

def strings(node, path=''):
    if isinstance(node, str): yield path, node
    elif isinstance(node, dict):
        for k, v in node.items(): yield from strings(v, f'{path}.{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from strings(v, f'{path}[{i}]')

for fn in FILES:
    data = json.load(open(fn))
    for slug, c in data.items():
        tag = f'{pathlib.Path(fn).name}:{slug}'
        for k in ('kind', 'label', 'target', 'title', 'meta', 'h1', 'intro', 'sections', 'faq'):
            if not c.get(k): errors.append(f'{tag}: missing {k}')
        if 'sources' not in c: errors.append(f'{tag}: missing sources')
        if c.get('kind') != 'hub' and c.get('group') not in GROUPS: errors.append(f'{tag}: bad group')
        day = SCHEDULE['noel'].get(slug)
        if not day: errors.append(f'{tag}: no date in publish-schedule.json noel')
        if c.get('group') == 'like':
            a = c.get('about')
            if not a or a not in PERFUMES: errors.append(f'{tag}: like page without a valid about')
            elif not live_on(a, day): errors.append(f'{tag}: about {a} not live on {day}')
            elif a in c.get('picks', []): errors.append(f'{tag}: about {a} is also a pick')
        for r in c.get('related', []):
            if r not in ALL or r == slug: errors.append(f'{tag}: bad related {r}')
            elif SCHEDULE['noel'].get(r, '9999') > (day or ''): errors.append(f'{tag}: related {r} goes live after this page')
        if len(c.get('title', '')) > 60: errors.append(f'{tag}: title {len(c["title"])} chars')
        if len(c.get('meta', '')) > 155: errors.append(f'{tag}: meta {len(c["meta"])} chars')
        if len(c.get('meta', '')) < 110: warns.append(f'{tag}: meta {len(c.get("meta", ""))} chars')
        h1s[c.get('h1')] += 1; titles[c.get('title')] += 1
        picks = c.get('picks', [])
        if c.get('kind') == 'profile' and not 6 <= len(picks) <= 10: errors.append(f'{tag}: {len(picks)} picks')
        if not 3 <= len(c.get('faq', [])) <= 4: errors.append(f'{tag}: {len(c.get("faq", []))} FAQ')
        for s in picks:
            if s not in PERFUMES: errors.append(f'{tag}: unknown pick {s}')
            elif not live_on(s, day): errors.append(f'{tag}: pick {s} has no live fiche on {day}')
            elif not c.get('why', {}).get(s): errors.append(f'{tag}: pick without why {s}')
            else:
                for y in re.findall(r"(?<!années )\b(?:19|20)\d\d\b", c["why"][s]):
                    if int(y) != PERFUMES[s]['year']: warns.append(f'{tag}: why {s} mentions {y}, fiche says {PERFUMES[s]["year"]}')
        if len(set(picks)) != len(picks): errors.append(f'{tag}: duplicate pick')
        for s in c.get('why', {}):
            if s not in picks: errors.append(f'{tag}: why for non-pick {s}')
        if slug == 'parfum-pas-sucre':
            for s in picks:
                p = PERFUMES.get(s)
                if p and any(SWEET.search(n) for n in p['notes']['top'] + p['notes']['heart'] + p['notes']['base']): errors.append(f'{tag}: sweet note in {s}')
        for u in c.get('sources', []):
            if not urllib.parse.urlparse(u).netloc: errors.append(f'{tag}: bad source {u}')
        firsts = collections.Counter(v.split()[0].lower() for v in c.get('why', {}).values() if v)
        for w, n in firsts.items():
            if n > 1: errors.append(f'{tag}: {n} "why" open with "{w}"')
        words = 0
        for path, text in strings({k: c.get(k) for k in ('title', 'meta', 'h1', 'intro', 'sections', 'why', 'faq')}):
            low = text.lower()
            words += len(text.split())
            if re.search('[—–]', text): errors.append(f'{tag}{path}: dash')
            if '!' in text: errors.append(f'{tag}{path}: exclamation')
            if '**' in text: errors.append(f'{tag}{path}: markdown')
            for b in BANNED:
                if b in low: errors.append(f'{tag}{path}: banned "{b}"')
            for sent in re.split(r'(?<=[.?;])\s+', text):
                n = sent.count(',')
                if n > 3: errors.append(f'{tag}{path}: {n} commas in "{sent[:60]}"')
                elif n == 3: warns.append(f'{tag}{path}: 3 commas in "{sent[:60]}"')
        if words < 350: errors.append(f'{tag}: only {words} words')
pages = {s: set(c.get('picks', [])) for s, c in ALL.items() if c.get('group') not in (None, 'advice')}
for a, b in itertools.combinations(sorted(pages), 2):
    n = len(pages[a] & pages[b])
    if n >= 5: errors.append(f'{a} / {b}: {n} shared picks')
    elif n == 4: warns.append(f'{a} / {b}: 4 shared picks')
for k, n in h1s.items():
    if n > 1: errors.append(f'duplicate h1: {k}')
for k, n in titles.items():
    if n > 1: errors.append(f'duplicate title: {k}')
for w in warns: print('WARN', w)
for e in errors: print('ERR', e)
print('OK' if not errors else f'{len(errors)} errors', f'({len(warns)} warnings)')
sys.exit(1 if errors else 0)
