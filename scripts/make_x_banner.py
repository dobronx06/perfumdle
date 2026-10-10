"""X (Twitter) header 1500x500 -> seo/x/banner.jpg. Same look as the pins: paper, tinted rounded tiles, Bodoni."""
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageChops
ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1500, 500
TILES = [('guerlain-shalimar-v2', '#EFD9BF'), ('chanel-coco-mademoiselle-v2', '#F3DCDC'), ('dior-sauvage', '#DCDAE8'),
         ('maison-francis-kurkdjian-baccarat-rouge-540', '#EADDE6'), ('lancome-la-vie-est-belle', '#EAD3C0')]

def font(names, size):
    for n in names:
        for base in ('/System/Library/Fonts/Supplemental/', '/Library/Fonts/', '/System/Library/Fonts/'):
            try: return ImageFont.truetype(base + n, size)
            except OSError: pass
    return ImageFont.load_default()

im = Image.new('RGB', (W, H), '#F7F3EE'); d = ImageDraw.Draw(im)
# right half: five tiles (left ~430px stay clear of the avatar overlap on profile pages)
tw, th, gap, y0 = 168, 300, 16, 120
x = W - 60 - 5 * tw - 4 * gap
for name, tint in TILES:
    src = Image.open(ROOT / f'public/img/{name}.webp').convert('RGBA')
    white = Image.new('RGBA', src.size, 'white'); white.alpha_composite(src)
    b = white.convert('RGB'); b = b.crop(ImageChops.difference(b, Image.new('RGB', b.size, 'white')).getbbox()); b.thumbnail((tw - 36, th - 56))
    tile = Image.new('RGB', (tw, th), 'white'); tile.paste(b, ((tw - b.size[0]) // 2, (th - b.size[1]) // 2))
    panel = ImageChops.multiply(Image.new('RGB', (tw, th), tint), tile)
    mask = Image.new('L', (tw, th), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, tw - 1, th - 1), radius=22, fill=255)
    im.paste(panel, (x, y0), mask); x += tw + gap
title = font(['Bodoni 72.ttc', 'Didot.ttc', 'Georgia.ttf'], 96)
d.text((60, 56), 'Perfumdle', font=title, fill='#1A1411')
it = font(['Georgia Italic.ttf', 'Georgia.ttf'], 34)
d.text((64, 178), 'Devinez le parfum du jour', font=it, fill='#7A1F2B')
sans = font(['Helvetica.ttc', 'Arial.ttf'], 24)
d.text((64, 236), 'Notes, avis et parfums similaires', font=sans, fill='#4A3F39')
d.text((64, 270), 'pour 300 parfums célèbres', font=sans, fill='#4A3F39')
d.text((64, 336), 'perfumdle.com', font=font(['Helvetica.ttc', 'Arial.ttf'], 26), fill='#1A1411')
out = ROOT / 'seo/x/banner.jpg'; im.save(out, quality=92); print(out)
