"""Render public/og-default.jpg (1200x630 social card) from three flacon shots."""
from PIL import Image, ImageDraw, ImageFont, ImageChops
import os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 630
im = Image.new('RGB', (W, H), '#F7F3EE'); d = ImageDraw.Draw(im)
for i, (tint, slug) in enumerate(zip(['#EBCDBE', '#D9DCE0', '#EFD9BF'],
                                     ['yves-saint-laurent-opium', 'dior-sauvage', 'maison-francis-kurkdjian-baccarat-rouge-540'])):
    x0 = 640 + i * 180; box = (x0, 60, x0 + 165, 570); size = (box[2] - box[0], box[3] - box[1])
    src = Image.open(ROOT / f'public/img/{slug}.webp').convert('RGBA')
    white = Image.new('RGBA', src.size, 'white'); white.alpha_composite(src); b = white.convert('RGB')
    b.thumbnail((220, 220))
    tile = Image.new('RGB', size, 'white'); tile.paste(b, ((size[0] - b.size[0]) // 2, (size[1] - b.size[1]) // 2))
    panel = ImageChops.multiply(Image.new('RGB', size, tint), tile)
    mask = Image.new('L', size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=26, fill=255)
    im.paste(panel, box[:2], mask)
def font(names, size):
    for n in names:
        for base in ['/System/Library/Fonts/Supplemental/', '/Library/Fonts/', '/System/Library/Fonts/']:
            if os.path.exists(base + n): return ImageFont.truetype(base + n, size)
    return ImageFont.load_default()
serif = font(['Didot.ttc', 'Georgia.ttf'], 96); it = font(['Georgia Italic.ttf', 'Georgia.ttf'], 36); sans = font(['Helvetica.ttc', 'Arial.ttf'], 21)
d.text((70, 100), 'ENCYCLOPÉDIE DES PARFUMS', font=sans, fill='#7A1F2B')
d.text((64, 150), 'Perfumdle', font=serif, fill='#1A1411')
for j, line in enumerate(['Notes, maisons, familles,', 'époques, et un parfum', 'mystère chaque jour.']):
    d.text((70, 300 + j * 48), line, font=it, fill='#4A3F39')
d.text((70, 530), 'perfumdle.com', font=sans, fill='#6B605A')
im.save(ROOT / 'public/og-default.jpg', quality=88)
