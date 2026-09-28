"""Remove em dashes from editorial copy (house rule: no « — » anywhere).
Paired dashes in one sentence become parentheses, a lone dash becomes a colon (or a comma before a lowercase clause that
already contains a colon). Also fixes known data typos. Usage: python3 scripts/strip_dashes.py [--dry]"""
import json, glob, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
dry = '--dry' in sys.argv
FIX = {'Carlos Benaim': 'Carlos Benaïm', 'Richard Herpe ': 'Richard Herpin ', 'Richard Herpe"': 'Richard Herpin"', 'Richard Herpe.': 'Richard Herpin.', 'Richard Herpe,': 'Richard Herpin,'}

def clean(s):
    for a, b in FIX.items():
        s = s.replace(a, b)
    if '—' not in s:
        return s
    out = []
    for sent in re.split(r'(?<=[.!?])\s+', s):
        while sent.count('—') >= 2:
            sent = re.sub(r'\s*—\s*(.+?)\s*—\s*', lambda m: f' ({m.group(1)}) ', sent, count=1)
        if '—' in sent:
            sent = re.sub(r'\s*—\s*$', '.', sent)
            sent = re.sub(r'\s*—\s*', ' : ' if re.search(r'[àâçéèêëîïôûùüÿœ]', sent) else ': ', sent, count=1)
        out.append(re.sub(r'\(\s*', '(', re.sub(r'\s+\)', ')', sent)).replace(' ,', ',').replace(' .', '.'))
    return ' '.join(out)

def walk(n):
    if isinstance(n, str): return clean(n)
    if isinstance(n, list): return [walk(x) for x in n]
    if isinstance(n, dict): return {k: walk(v) for k, v in n.items()}
    return n

for fn in sorted(glob.glob(str(ROOT / 'src/data/editorial/*.json'))):
    raw = open(fn).read()
    data = json.loads(raw)
    new = walk(data)
    if new != data:
        if dry:
            a = [s for s in re.findall(r'"[^"]*—[^"]*"', raw)][:3]
            print(fn, *a[:2], sep='\n  ')
        else:
            txt = json.dumps(new, ensure_ascii=False, indent=1)
            open(fn, 'w').write(txt + ('\n' if raw.endswith('\n') else ''))
            print('cleaned', fn)
