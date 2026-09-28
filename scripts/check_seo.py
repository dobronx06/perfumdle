"""Post-build SEO audit of dist/: titles, descriptions, h1, canonical, hreflang, broken internal links."""
import pathlib, re, collections, sys, html
ROOT = pathlib.Path(__file__).resolve().parent.parent / 'dist'
pages = {('/' + str(p.relative_to(ROOT)).replace('index.html', '')): p.read_text() for p in ROOT.rglob('index.html')}
titles = collections.defaultdict(list); descs = collections.defaultdict(list)
problems = collections.Counter(); examples = collections.defaultdict(list)
def flag(kind, url):
    problems[kind] += 1
    if len(examples[kind]) < 5: examples[kind].append(url)
for url, h in pages.items():
    if 'http-equiv="refresh"' in h: continue
    t = re.search(r'<title>(.*?)</title>', h, re.S); d = re.search(r'<meta name="description" content="(.*?)"', h)
    t = html.unescape(t.group(1)) if t else ''; d = html.unescape(d.group(1)) if d else ''
    titles[t].append(url); descs[d].append(url)
    if not t: flag('missing title', url)
    elif len(t) > 70: flag('title > 70 chars', url)
    if not d: flag('missing description', url)
    elif len(d) > 165: flag('description > 165 chars', url)
    elif len(d) < 70: flag('description < 70 chars', url)
    n_h1 = len(re.findall(r'<h1[\s>]', h))
    if n_h1 != 1: flag(f'{n_h1} h1', url)
    if 'rel="canonical"' not in h: flag('missing canonical', url)
    if 'hreflang="en"' not in h: flag('missing hreflang', url)
    words = len(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)).split())
    if words < 350: flag('thin (<350 words)', url)
    for href in re.findall(r'href="(/[^"#?]*)"', h):
        if href.startswith(('/_astro', '/img', '/favicon', '/og-')) or '.' in href.rsplit('/', 1)[-1]: continue
        if not href.endswith('/'): href += '/'
        if href not in pages: flag('broken internal link', f'{url} -> {href}')
for t, urls in titles.items():
    if len(urls) > 1: flag('duplicate title', f'{t!r} x{len(urls)}')
for d, urls in descs.items():
    if d and len(urls) > 1: flag('duplicate description', f'{urls[0]} x{len(urls)}')
print(f'{len(pages)} pages audited')
for k, v in problems.most_common():
    print(f'  {v:5d}  {k}   e.g. {examples[k][:3]}')
sys.exit(1 if problems['broken internal link'] else 0)
