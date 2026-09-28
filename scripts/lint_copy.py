"""Lint editorial copy of ranked pages against scripts/WRITING_RULES.md.

Usage: python3 scripts/lint_copy.py src/data/editorial/ranked-*.json
Exit 1 on any error. Warnings are printed but do not fail.
"""
import json, re, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFS = {d['id']: d for d in json.load(open(ROOT / 'src/data/ranked-pages.json'))}
PERFUMES = {p['slug'] for p in json.load(open(ROOT / 'src/data/perfumes.json'))}
DEEP_FIELDS = {'history': (130, 260), 'review': (130, 260), 'rivals': (100, 220), 'performance': (70, 160)}

BANNED_FR = [
    'véritable', 'incontournable', 'envoûtant', 'sublim', 'subtil équilibre', 'alliance parfaite', 'mariage parfait',
    'que vous soyez', 'plongez', 'découvrez', 'laissez-vous', "n'hésitez pas", 'n’hésitez pas', 'en somme', 'en définitive',
    'en conclusion', 'il est important de noter', 'il convient de', 'un must', 'intemporel', 'voyage olfactif',
    'sillage inoubliable', 'ode à', 'invitation à', 'symphonie', 'explosion de', 'bien plus qu', 'tout simplement',
    'résolument', 'audacieu', 'témoigne de', 'marque un tournant', "incarne l'essence", 'incarne l’essence',
    'les experts', 'selon les amateurs',
]
BANNED_EN = [
    'delve', 'tapestry', 'testament to', 'a true ', 'timeless', 'must-have', 'elevate', 'captivating', "whether you're",
    'whether you are', "it's not just", 'more than just', 'olfactory journey', 'symphony', 'nestled', 'in the world of',
    'boasts', 'seamlessly', 'vibrant', 'embark', 'unleash', 'game-changer', 'game changer',
]
MAX_PER_FILE = {'iconique': 3, 'iconic': 3, 'au fil des heures': 1, 'jus': 2}

errors, warns = [], []


def strings(node, path=''):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, f'{path}.{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings(v, f'{path}[{i}]')


def words(s):
    return len(s.split())


for fn in sys.argv[1:]:
    try:
        data = json.load(open(fn))
    except Exception as e:  # noqa: BLE001
        errors.append(f'{fn}: invalid JSON: {e}')
        continue
    counts = collections.Counter()
    for pid, page in data.items():
        if pid.startswith('_'):
            continue
        for lang in ('fr', 'en'):
            t = page.get(lang)
            if not t:
                errors.append(f'{pid}: missing {lang}')
                continue
            banned = BANNED_FR if lang == 'fr' else BANNED_EN
            for path, s in strings(t, f'{pid}.{lang}'):
                low = s.lower()
                for ch, name in (('—', 'tiret cadratin'), ('–', 'demi-cadratin'), ('!', "point d'exclamation"), ('**', 'markdown')):
                    if ch in s:
                        errors.append(f'{path}: {name}')
                for b in banned:
                    if b in low:
                        errors.append(f'{path}: formule bannie « {b} »')
                for k in MAX_PER_FILE:
                    counts[k] += len(re.findall(rf'\b{re.escape(k)}\b', low))
                for sent in re.split(r'(?<=[.?;])\s+', s):
                    c = sent.count(',')
                    if c > 3:
                        errors.append(f'{path}: {c} virgules dans « {sent[:70]}… »')
                    elif c == 3:
                        warns.append(f'{path}: 3 virgules dans « {sent[:60]}… »')
            # structure
            if pid in PERFUMES:  # deep perfume copy (src/data/editorial/deep-*.json)
                for f, (lo, hi) in DEEP_FIELDS.items():
                    n = words(t.get(f, ''))
                    if not lo <= n <= hi:
                        errors.append(f'{pid}.{lang}.{f} {n} mots ({lo}–{hi})')
                continue
            if pid.startswith('hub:'):
                continue
            d = DEFS.get(pid)
            if not d:
                errors.append(f'{pid}: unknown page id')
                continue
            if len(t.get('title', '')) > 65:
                errors.append(f'{pid}.{lang}.title > 65 car. ({len(t["title"])})')
            m = len(t.get('meta', ''))
            if not 110 <= m <= 160:
                errors.append(f'{pid}.{lang}.meta {m} car. (110–160)')
            if not 40 <= words(t.get('intro', '')) <= 120:
                errors.append(f'{pid}.{lang}.intro {words(t.get("intro", ""))} mots (40–120)')
            secs = t.get('sections', [])
            if len(secs) < 2:
                errors.append(f'{pid}.{lang}: < 2 sections')
            for i, sct in enumerate(secs):
                if words(sct.get('body', '')) < 80:
                    errors.append(f'{pid}.{lang}.sections[{i}] < 80 mots')
            if len(t.get('faq', [])) < 3:
                errors.append(f'{pid}.{lang}: < 3 FAQ')
            why = t.get('why', {})
            picks = page.get('picks', [])
            for s in picks:
                if s not in why:
                    errors.append(f'{pid}.{lang}.why: manque {s}')
                elif words(why[s]) < 30:
                    errors.append(f'{pid}.{lang}.why.{s} < 30 mots')
            firsts = collections.Counter(re.sub(r'\W', '', why[s].split()[0].lower()) for s in picks if why.get(s))
            for w, c in firsts.items():
                if c > 1:
                    warns.append(f'{pid}.{lang}.why: {c} ouvertures par « {w} »')
        if pid.startswith('hub:') or pid in PERFUMES:
            continue
        d = DEFS.get(pid)
        if d:
            picks = page.get('picks', [])
            bad = [s for s in picks if s not in d['pool']]
            if bad:
                errors.append(f'{pid}.picks hors pool: {bad}')
            lo = min(3, len(d['pool'])) if d['kind'] == 'nose' else min(6, len(d['pool']))
            if len(picks) < lo or len(picks) > 12 or len(set(picks)) != len(picks):
                errors.append(f'{pid}.picks: {len(picks)} (attendu {lo}–12, sans doublon)')
    for k, mx in MAX_PER_FILE.items():
        if counts[k] > mx * max(1, len([p for p in data if not p.startswith('_')]) // 3):
            warns.append(f'{fn}: « {k} » ×{counts[k]}')

for w in warns[:60]:
    print('WARN ', w)
for e in errors:
    print('ERROR', e)
print('OK' if not errors else f'{len(errors)} erreur(s)')
sys.exit(1 if errors else 0)
