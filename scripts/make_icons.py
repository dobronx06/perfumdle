"""Raster icons from the same geometry as public/favicon.svg (flacon on wine): apple-touch-icon, PWA, 32px fallback.
Usage: python3 scripts/make_icons.py"""
from PIL import Image, ImageDraw
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent


def draw(size, rounded=True):
    k = 16  # supersampling
    S = size * k; u = S / 64
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    R = lambda x0, y0, x1, y1: tuple(round(v * u) for v in (x0, y0, x1, y1))
    if rounded:
        d.rounded_rectangle(R(0, 0, 64, 64), radius=round(15 * u), fill='#7A1F2B')
    else:
        d.rectangle(R(0, 0, 64, 64), fill='#7A1F2B')
    d.rounded_rectangle(R(24, 8, 40, 18), radius=round(2.5 * u), fill='#D9B97A')
    d.rectangle(R(28, 17, 36, 23), fill='#D9B97A')
    d.rounded_rectangle(R(14, 22, 50, 56), radius=round(8 * u), fill='#F7F3EE')
    # drop: circle (centre 32,43.6, r 7) + the two tangent lines from the tip (32,31), as in the SVG path
    d.ellipse(R(25, 36.6, 39, 50.6), fill='#7A1F2B')
    d.polygon([tuple(round(v * u) for v in p) for p in ((32, 31), (37.82, 39.71), (32, 43.6), (26.18, 39.71))], fill='#7A1F2B')
    return im.resize((size, size), Image.LANCZOS)


out = ROOT / 'public'
draw(180, rounded=False).convert('RGB').save(out / 'apple-touch-icon.png')
draw(192).save(out / 'icon-192.png')
draw(512).save(out / 'icon-512.png')
draw(32).save(out / 'favicon-32.png')
print('icons written')
