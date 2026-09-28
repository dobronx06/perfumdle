"""One-off (2026-09 Haloscan pass): align FR note titles/H1 on real search phrasing.

Haloscan FR volumes: « parfum vanille » 3400 vs « parfum à la vanille » 140, « parfum rose » 3100 vs
« parfum à la rose » 390, « parfum musc » 3100 / « musc blanc » 3300… → titles start with « Parfum <note> ».
Idempotent: re-running leaves already-converted titles untouched.
"""
import json, glob, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Hand-tuned titles for the notes with real volume (keyword variants measured in Haloscan).
TITLES = {
    'Musk': 'Parfum musc et musc blanc : odeur, origine et icônes',
    'Vanilla': 'Parfum vanille : odeur, origine et parfums femme et homme',
    'Patchouli': 'Parfum patchouli : odeur, origine et parfums iconiques',
    'Rose': 'Parfum rose : odeur, origine et grands parfums à la rose',
    'Coconut': 'Parfum noix de coco et monoï : odeur, accord et icônes',
    'Violet': 'Parfum violette : odeur, origine et parfums iconiques',
    'Amber': 'Parfum ambre : odeur, accord ambré et grands classiques',
    'Jasmine': 'Parfum jasmin : odeur, origine et grands classiques',
    'Pepper': 'Parfum poivre : odeur, origine et créations phares',
    'Neroli': 'Parfum néroli : odeur, origine et grandes Colognes',
    'Oud': 'Parfum oud femme et homme : odeur, bois d’agar, icônes',
    'Sandalwood': 'Parfum bois de santal : odeur, origine et icônes',
    'Caramel': 'Parfum au caramel : odeur, accord et gourmands phares',
    'Tonka Bean': 'Parfum fève tonka : odeur, origine et icônes',
    'White Flowers': 'Parfum fleurs blanches : odeur, accord et icônes',
    # plural notes read badly as « Parfum <x> »
    'Aldehydes': 'Aldéhydes en parfum : odeur, histoire et icônes',
    'Citrus': 'Parfum aux agrumes : odeur, origine et classiques',
    'Green Notes': 'Notes vertes en parfum : odeur, matières et icônes',
    'Pink Pepper': 'Baies roses en parfum : odeur, origine et icônes',
}
# H1 for the biggest clusters: keep the editorial hook, lead with the query.
H1 = {
    'Musk': 'Parfum musc : l’odeur de la peau propre',
    'Vanilla': 'Parfum vanille : la note la plus réconfortante',
    'Patchouli': 'Parfum patchouli : de la terre humide au chypre moderne',
    'Rose': 'Parfum rose : la reine des fleurs en parfumerie',
    'Coconut': 'Parfum noix de coco : lacté, solaire et crémeux',
    'Violet': 'Parfum violette : poudre sucrée et feuille verte',
    'Amber': 'Parfum ambre : un accord chaud, résineux et doré',
    'Jasmine': 'Parfum jasmin : la fleur blanche des grands classiques',
    'Pepper': 'Parfum poivre : une épice sèche qui électrise',
    'Neroli': 'Parfum néroli : la fleur d’oranger en version lumineuse',
    'Oud': 'Parfum oud : le bois le plus précieux de la parfumerie',
    'Sandalwood': 'Parfum bois de santal : le bois crémeux de la parfumerie',
    'Magnolia': 'Parfum magnolia : une fleur crémeuse et citronnée',
    'Bergamot': 'Parfum bergamote : le zeste lumineux de la parfumerie',
}
PREFIX = re.compile(r"^(Parfums (à la |à l[’']|au |aux )|)(.+?)( en parfum)? : ")

for fn in sorted(glob.glob(str(ROOT / 'src/data/editorial/notes-*.json'))):
    data = json.load(open(fn))
    for key, v in data.items():
        if key.startswith('_'):
            continue
        fr = v['fr']
        if key in TITLES:
            fr['title'] = TITLES[key]
        elif not fr['title'].startswith('Parfum ') and ' en parfum : ' not in fr['title']:
            suffix = fr['title'].split(' : ', 1)[1]
            fr['title'] = f"Parfum {v['name_fr'].lower()} : {suffix}"
        if key in H1:
            fr['h1'] = H1[key]
        assert len(fr['title']) <= 65, (key, fr['title'])
    json.dump(data, open(fn, 'w'), ensure_ascii=False, indent=1)
    open(fn, 'a').write('\n')
