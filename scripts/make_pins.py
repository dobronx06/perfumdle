"""Render one vertical Pinterest pin (1000x1500, 2:3) per perfume with a bottle image -> public/pins/<slug>.jpg

Usage: python3 scripts/make_pins.py [--force]
Design matches the site: paper background, family-tinted panel with the bottle (multiply blend), Bodoni title
(lining figures: Didot's old-style 0 reads as an o),
house + year, three signature notes, perfumdle.com. French copy (FR boards first).
"""
import json, glob, os, sys, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageChops
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'public/pins'; OUT.mkdir(exist_ok=True)
force = '--force' in sys.argv
W, H = 1000, 1500
TINT = {'floral': '#F3DCDC', 'oriental': '#EFD9BF', 'woody': '#DDD5C8', 'chypre': '#D9DECB', 'fougere': '#DCDAE8',
        'citrus': '#F2E9C4', 'gourmand': '#EAD3C0', 'leather': '#D9C6B4', 'aquatic': '#D3E1E6', 'aromatic': '#D8E2D3',
        'fruity': '#F2D8CF', 'spicy': '#EBCDBE', 'musky': '#E9E1DC', 'powdery': '#EADDE6', 'green': '#D5E3CD'}
NOTES, NFR = {}, json.load(open(ROOT / 'src/data/editorial/note-names.json'))
for fn in glob.glob(str(ROOT / 'src/data/editorial/notes-*.json')):
    NOTES.update({k: v['name_fr'] for k, v in json.load(open(fn)).items() if not k.startswith('_')})
nfr = lambda n: NOTES.get(n) or NFR.get(n, n)


def font(names, size):
    for n in names:
        for base in ('/System/Library/Fonts/Supplemental/', '/Library/Fonts/', '/System/Library/Fonts/'):
            if os.path.exists(base + n):
                return ImageFont.truetype(base + n, size)
    return ImageFont.load_default()


def fit_lines(d, text, names, max_size, min_size, width, max_lines=2):
    """Largest font size at which `text` wraps into <= max_lines lines of `width` px."""
    for size in range(max_size, min_size - 1, -4):
        f = font(names, size)
        words, lines, cur = text.split(), [], ''
        for w in words:
            t = f'{cur} {w}'.strip()
            if d.textlength(t, font=f) <= width:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= max_lines and all(d.textlength(x, font=f) <= width for x in lines):
            return f, lines
    return font(names, min_size), [text]


def pin(p):
    im = Image.new('RGB', (W, H), '#F7F3EE'); d = ImageDraw.Draw(im)
    box = (60, 60, 940, 980); size = (box[2] - box[0], box[3] - box[1])
    src = Image.open(ROOT / f"public{p['image']}").convert('RGBA')
    white = Image.new('RGBA', src.size, 'white'); white.alpha_composite(src)
    bottle = white.convert('RGB'); bottle.thumbnail((640, 760))
    tile = Image.new('RGB', size, 'white'); tile.paste(bottle, ((size[0] - bottle.size[0]) // 2, (size[1] - bottle.size[1]) // 2))
    panel = ImageChops.multiply(Image.new('RGB', size, TINT.get(p['families'][0] if p['families'] else '', '#E9E3DA')), tile)
    mask = Image.new('L', size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=44, fill=255)
    im.paste(panel, box[:2], mask)

    sans = font(['Helvetica.ttc', 'Arial.ttf'], 30); sans_small = font(['Helvetica.ttc', 'Arial.ttf'], 28)
    d.text((70, 1020), f"{p['brand'].upper()} · {p['year']}", font=sans, fill='#7A1F2B')
    tf, lines = fit_lines(d, p['name'], ['Bodoni 72.ttc', 'Didot.ttc', 'Georgia.ttf'], 104, 56, 860)
    y = 1066
    for line in lines:
        d.text((64, y), line, font=tf, fill='#1A1411'); y += int(tf.size * 1.08)
    it = font(['Georgia Italic.ttf', 'Georgia.ttf'], 38)
    d.text((70, y + 14), 'Notes, avis et parfums similaires', font=it, fill='#4A3F39')
    notes = [nfr(n) for n in (p['notes']['top'][:1] + p['notes']['heart'][:1] + p['notes']['base'][:1])]
    d.text((70, y + 76), '  ·  '.join(notes), font=sans_small, fill='#6B605A')
    d.line((70, 1418, 930, 1418), fill='#D8CFC4', width=2)
    d.text((70, 1436), 'perfumdle.com', font=sans_small, fill='#1A1411')
    jeu = 'Le jeu du parfum du jour'
    d.text((930 - d.textlength(jeu, font=sans_small), 1436), jeu, font=sans_small, fill='#7A1F2B')
    im.save(OUT / f"{p['slug']}.jpg", quality=82, optimize=True, progressive=True)


perfumes = [p for p in json.load(open(ROOT / 'src/data/perfumes.json')) if p.get('image')]
n = 0
for p in perfumes:
    if force or not (OUT / f"{p['slug']}.jpg").exists():
        pin(p); n += 1
total = sum(f.stat().st_size for f in OUT.glob('*.jpg'))
print(f'{n} pins rendered, {len(list(OUT.glob("*.jpg")))} in public/pins ({total // 1024 // 1024} MB)')
