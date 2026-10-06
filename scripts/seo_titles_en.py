"""EN titles aligned on real Search Console queries (Oct 2026): "what does ylang ylang smell like in perfume",
"famous chypre perfumes", "oriental floral perfumes". Idempotent."""
import json, glob, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

for fn in sorted(glob.glob(str(ROOT / 'src/data/editorial/notes-*.json'))):
    data = json.load(open(fn))
    for key, v in data.items():
        if key.startswith('_'):
            continue
        name = v['name_en']
        en = v['en']
        for t in (f'{name} in Perfume: What It Smells Like & Best Fragrances', f'{name} in Perfume: Smell & Best Fragrances', f'{name} Perfumes: Smell & Icons'):
            if len(t) <= 65:
                en['title'] = t
                break
        en['h1'] = f'What does {name.lower() if name.isupper() is False and name not in ("Ambroxan", "Cashmeran") else name} smell like in perfume?'
    json.dump(data, open(fn, 'w'), ensure_ascii=False, indent=1)
    open(fn, 'a').write('\n')

p = ROOT / 'src/data/editorial/hubs.json'
h = json.load(open(p))
h['families']['chypre']['en']['title'] = 'Famous Chypre Perfumes: History, Oakmoss and Icons'
h['families']['oriental']['en']['title'] = 'Oriental and Floral Oriental Perfumes: Amber, Vanilla'
h['families']['floral']['en']['title'] = 'Floral Perfumes: Famous Floral Fragrances and History'
json.dump(h, open(p, 'w'), ensure_ascii=False, indent=1)
open(p, 'a').write('\n')
print('ok')
