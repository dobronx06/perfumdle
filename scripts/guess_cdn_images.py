"""Guess Fragella CDN image URLs (no API quota) for perfumes without an image, keep every hit as a candidate.

Pattern seen on the CDN: https://cdn.fragella.com/images/<name>-<brand>-for-<women|men|women-and-men>.webp
Usage: python3 scripts/guess_cdn_images.py <candidates_dir>
Candidates must be checked by eye before being recorded in scripts/image-fixes.json.
"""
import json, re, sys, pathlib, subprocess, unicodedata, itertools
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).resolve().parent.parent
CDN = 'https://cdn.fragella.com/images'
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)


def slug(s):
    s = unicodedata.normalize('NFKD', s.replace('°', 'o').replace('&', ' ')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r"['’`*]", '', s)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


BRAND_VARIANTS = {
    'Dior': ['christian-dior', 'dior'], 'Estée Lauder': ['estee-lauder'], 'Dolce & Gabbana': ['dolce-gabbana', 'dolce-and-gabbana'],
    'Mugler': ['mugler', 'thierry-mugler'], 'Jean Paul Gaultier': ['jean-paul-gaultier'], 'Issey Miyake': ['issey-miyake'],
    'Parfums de Marly': ['parfums-de-marly'], 'Giorgio Armani': ['giorgio-armani', 'armani'], 'Calvin Klein': ['calvin-klein'],
    'Abercrombie & Fitch': ['abercrombie-fitch', 'abercrombie-and-fitch'], 'Escentric Molecules': ['escentric-molecules'],
    'Louis Vuitton': ['louis-vuitton'], 'Jo Malone': ['jo-malone-london', 'jo-malone'], 'Yves Saint Laurent': ['yves-saint-laurent', 'ysl'],
    'Hermès': ['hermes'], 'Chanel': ['chanel'], 'Byredo': ['byredo'], 'Acqua di Parma': ['acqua-di-parma'], 'Carolina Herrera': ['carolina-herrera'], 'Lancôme': ['lancome'],
}
# Hand-written name variants for names the generic rules miss (second pass).
EXTRA_NAMES = {
    'thierry-mugler-amen': ['a-men', 'amen', 'angel-men', 'a-men-angel-men'],
    'calvin-klein-ck-eternity-for-men': ['eternity-for-men', 'eternity'],
    'dolce-gabbana-d-g-light-blue-pour-homme': ['light-blue-pour-homme'],
    'dolce-gabbana-limperatrice': ['3-l-imperatrice', 'l-imperatrice', 'limperatrice', '3-limperatrice'],
    'chanel-n-22': ['no-22', 'n-22', 'n22', 'no22', 'les-exclusifs-de-chanel-no-22'],
    'chanel-coromandel': ['coromandel', 'les-exclusifs-de-chanel-coromandel'],
    'dior-dior-joy': ['joy-by-dior', 'joy-by-dior-eau-de-parfum'],
    'escentric-molecules-molecule-01': ['molecule-01', 'molecule-1'],
    'escentric-molecules-molecule-02': ['molecule-02', 'molecule-2'],
    'yves-saint-laurent-tuxedo': ['tuxedo', 'le-vestiaire-des-parfums-tuxedo'],
    'hermes-rouge': ['rouge-hermes', 'rouge'],
    'gucci-gucci-pour-homme-ii': ['gucci-pour-homme-ii'],
}
GENDER = {'Feminine': ['for-women', 'for-women-and-men'], 'Masculine': ['for-men', 'for-women-and-men'],
          'Unisex': ['for-women-and-men', 'for-men', 'for-women']}


ALL_G = ['for-women-and-men', 'for-men', 'for-women']


def name_variants(p):
    n = p['name']
    b = p['brand']
    base = {slug(n)}
    base.add(slug(re.sub(rf'^{re.escape(b)}\s+', '', n)))              # "Gucci Pour Homme II" -> keep, "Dolce & Gabbana Pour Femme"
    base.add(slug(n.replace('N°', 'No ').replace('N° ', 'No ')))
    base.add(slug(n.replace('N°', 'N')))
    base.add(slug(n.replace("L'", 'L ').replace("d'", 'd ')))
    base.add(slug(n + ' Eau de Parfum'))
    base.add(slug(n + ' Eau de Toilette'))
    base.add(slug(n + ' ' + p['concentration']))
    if p['name'].startswith(b):
        base.add(slug(n[len(b):]))
    base.add(slug(n.replace('&', ' and ')))
    base.add(slug(n.replace('&', ' and ') + ' Cologne'))
    base.update(EXTRA_NAMES.get(p['slug'], []))
    return [x for x in base if x]


def candidates(p):
    brands = BRAND_VARIANTS.get(p['brand'], [slug(p['brand'])])
    urls = []
    for n, b, g in itertools.product(name_variants(p), brands, ALL_G):
        urls.append(f'{CDN}/{n}-{b}-{g}.webp')
    for n, b in itertools.product(name_variants(p), brands):
        urls += [f'{CDN}/{n}-by-{b}.webp', f'{CDN}/{b}-{n}.webp', f'{CDN}/{n}.webp']
    return list(dict.fromkeys(urls))


def exists(url):
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code} %{size_download}', '--max-time', '8', url],
                       capture_output=True, text=True).stdout.split()
    return len(r) == 2 and r[0] == '200' and int(r[1]) > 500


perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
todo = [p for p in perfumes if not p.get('image')]
report = {}
with ThreadPoolExecutor(12) as ex:
    for p in todo:
        urls = candidates(p)
        hits = [u for u, ok in zip(urls, ex.map(exists, urls)) if ok]
        files = []
        for i, u in enumerate(hits[:4]):
            f = out / f"{p['slug']}__cdn{i}.webp"
            subprocess.run(['curl', '-s', '-o', str(f), '--max-time', '10', u])
            files.append({'url': u, 'file': str(f)})
        report[p['slug']] = {'want': f"{p['brand']} {p['name']} ({p['year']}, {p['gender']}, {p['concentration']})", 'candidates': files}
        print(f"{p['slug']}: {len(hits)} hit(s) / {len(urls)} tried", flush=True)
json.dump(report, open(out / 'cdn_candidates.json', 'w'), ensure_ascii=False, indent=1)
print('with candidates:', sum(1 for v in report.values() if v['candidates']), '/', len(todo))
