"""Writer briefs for ranked pages: one JSON per batch with the page definition + full data of each candidate perfume.

Usage: python3 scripts/briefs.py <out_dir>
Batches are grouped so one writer handles sibling pages (e.g. vanille femme + vanille homme) and can differentiate them.
"""
import json, glob, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
P = {p['slug']: p for p in json.load(open(ROOT / 'src/data/perfumes.json'))}
ED, NOTES = {}, {}
for fn in glob.glob(str(ROOT / 'src/data/editorial/perfumes-*.json')):
    ED.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
for fn in glob.glob(str(ROOT / 'src/data/editorial/notes-*.json')):
    NOTES.update({k: v for k, v in json.load(open(fn)).items() if not k.startswith('_')})
NFR = json.load(open(ROOT / 'src/data/editorial/note-names.json'))
DEFS = json.load(open(ROOT / 'src/data/ranked-pages.json'))


def nfr(n):
    return NOTES[n]['name_fr'] if n in NOTES else NFR.get(n, n)


def perfume(slug):
    p, e = P[slug], ED.get(slug, {})
    return {
        'slug': slug, 'name': p['name'], 'brand': p['brand'], 'year': p['year'], 'gender': p['gender'],
        'families': p['families'], 'concentration': p['concentration'],
        'notes_fr': {t: [nfr(n) for n in p['notes'][t]] for t in ('top', 'heart', 'base')},
        'notes_en': p['notes'], 'perfumer': e.get('perfumer'), 'intensity_1_5': e.get('intensity'),
        'seasons': e.get('seasons'), 'occasions': e.get('occasions'),
        'tagline_fr': e.get('fr', {}).get('tagline'), 'verdict_fr': e.get('fr', {}).get('verdict'),
        'wear_fr': e.get('fr', {}).get('wear'), 'tagline_en': e.get('en', {}).get('tagline'),
    }


def url(d, l):
    base = {'ng': 'notes', 'fg': 'familles' if l == 'fr' else 'families', 'sg': '',
            'best': 'meilleurs-parfums' if l == 'fr' else 'best-perfumes',
            'nose': 'parfumeurs' if l == 'fr' else 'perfumers', 'guide': 'guides'}[d['kind']]
    s = d['slug_fr' if l == 'fr' else 'slug_en']
    return f"/{l}/{base + '/' if base else ''}{s}/"


by = collections.defaultdict(list)
for d in DEFS:
    by[d['kind']].append(d)
ng = sorted(by['ng'], key=lambda d: (d['note'], d['gender']))
batches = {
    'best-a': [d for d in by['best'] if 'brand' not in d],
    'best-b': [d for d in by['best'] if 'brand' in d],
    'guide-a': [d for d in by['guide'] if d['id'] in ('guide:musc-blanc', 'guide:ado-garcon', 'guide:ado-fille', 'guide:pyramide')],
    'guide-b': [d for d in by['guide'] if d['id'] in ('guide:tenue-femme', 'guide:tenue-homme', 'guide:attire-femmes', 'guide:attire-hommes')],
    'nose-a': by['nose'][:8], 'nose-b': by['nose'][8:],
    'fg-a': by['fg'][:9], 'fg-b': by['fg'][9:], 'sg': by['sg'],
}
chunk = (len(ng) + 5) // 6
for i in range(6):
    batches[f'ng-{"abcdef"[i]}'] = ng[i * chunk:(i + 1) * chunk]

for name, ds in batches.items():
    pages = []
    for d in ds:
        page = {k: v for k, v in d.items() if k != 'pool'}
        page['url_fr'], page['url_en'] = url(d, 'fr'), url(d, 'en')
        if d['kind'] == 'ng':
            e = NOTES[d['note']]
            page['note_page_context_fr'] = {'intro': e['fr']['intro'], 'smell': e['fr']['smell']}
        page['pool'] = [perfume(s) for s in d['pool']]
        pages.append(page)
    json.dump({'batch': name, 'pages': pages}, open(out / f'{name}.json', 'w'), ensure_ascii=False, indent=1)
    print(name, len(pages), [d['id'] for d in ds])
