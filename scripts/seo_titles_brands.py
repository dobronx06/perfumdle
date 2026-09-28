"""One-off (2026-09 Haloscan pass): align FR house titles on real search phrasing.

Haloscan FR: « parfum dior » 22 583, « parfum yves saint laurent » 24 636, « parfum guerlain » 9 000 —
the singular « Parfum <maison> » wins for most houses; the plural only wins where it is the best
measured form (Tom Ford, Diptyque, Byredo, Lanvin, Clinique…). Gender is added where
« parfum <maison> homme/femme » carries real volume. Data: seo/haloscan/brands_*.tsv.
"""
import json, glob, csv, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

TITLES = {
    'Yves Saint Laurent': 'Parfum Yves Saint Laurent femme et homme : Libre, Opium',
    'Dior': 'Parfum Dior femme et homme : Sauvage, J’adore, Miss Dior',
    'Chanel': 'Parfum Chanel femme et homme : N°5, Bleu de Chanel',
    'Guerlain': 'Parfum Guerlain : histoire, Shalimar et Guerlinade',
    'Louis Vuitton': 'Parfum Louis Vuitton : histoire, Ombre Nomade et plus',
    'Hugo Boss': 'Parfum Hugo Boss homme : histoire, Boss Bottled, The Scent',
    'Prada': 'Parfum Prada : histoire, Luna Rossa, Candy et iris',
    'Hermès': 'Parfum Hermès : histoire, Terre d’Hermès et Jardins',
    'Jean Paul Gaultier': 'Parfum Jean Paul Gaultier : Le Mâle, Scandal, histoire',
    'Azzaro': 'Parfum Azzaro homme : Wanted, Chrome et fougères',
    'Giorgio Armani': 'Parfum Armani : Acqua di Giò, Sì, Code et histoire',
    'Montblanc': 'Parfum Montblanc homme : histoire et Explorer',
    'Givenchy': 'Parfum Givenchy homme et femme : L’Interdit, Gentleman',
    'Gucci': 'Parfum Gucci femme et homme : Bloom, Guilty et Flora',
    'Lancôme': 'Parfum Lancôme femme : La Vie est Belle, Idôle, Trésor',
    'Maison Francis Kurkdjian': 'Maison Francis Kurkdjian : Baccarat Rouge 540 et histoire',
    'Parfums de Marly': 'Parfum de Marly : histoire, Layton, Delina et plus',
    'By Kilian': 'Parfum Kilian : histoire, Angels’ Share et gourmands',
}

best = {r['brand'].strip(): r['best_keyword'] for r in csv.DictReader(open(ROOT / 'seo/haloscan/brands_summary.tsv'), delimiter='\t')}

for fn in sorted(glob.glob(str(ROOT / 'src/data/editorial/brands-*.json'))):
    data = json.load(open(fn))
    for name, v in data.items():
        if name.startswith('_'):
            continue
        fr = v['fr']
        if name in TITLES:
            fr['title'] = TITLES[name]
        elif fr['title'].startswith('Parfums ') and not best.get(name, '').startswith('parfums '):
            fr['title'] = 'Parfum ' + fr['title'][len('Parfums '):]
        assert len(fr['title']) <= 65, (name, fr['title'], len(fr['title']))
    json.dump(data, open(fn, 'w'), ensure_ascii=False, indent=1)
