"""Fetch affiliate shop catalogues and match them to our perfumes.

Writes src/data/affiliate-offers.json: for each shop with "catalog": true in src/data/affiliates.json,
the cheapest full-size bottle it sells for each perfume we have, with its price, size and tracked link.
The site then shows the buy button only on perfumes the shop really sells.

CJ shops use the CJ Product Search API (GraphQL). The token comes from the CJ_TOKEN environment variable
or from ~/.config/perfumdle/affiliate.env (CJ_TOKEN=...). It is never printed.

Usage: python3 scripts/affiliate_offers.py
"""
import json, os, re, sys, time, unicodedata, datetime, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
CJ_CID = '8110171'      # CJ company (publisher) ID
CJ_PID = '101915272'    # CJ website ID for perfumdle.com
OUT = ROOT / 'src/data/affiliate-offers.json'


def token():
    if os.environ.get('CJ_TOKEN'):
        return os.environ['CJ_TOKEN']
    env = pathlib.Path.home() / '.config/perfumdle/affiliate.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith('CJ_TOKEN='):
                return line.split('=', 1)[1].strip()
    sys.exit('CJ_TOKEN missing (env var or ~/.config/perfumdle/affiliate.env)')


def norm(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def cj_products(tok, advertiser):
    fields = 'id title brand price { amount currency } link ... on Shopping { availability } linkCode(pid: "%s") { clickUrl }' % CJ_PID
    out, offset = [], 0
    while True:
        q = '{ products(companyId: "%s", partnerIds: ["%s"], limit: 1000, offset: %d) { totalCount count resultList { %s } } }' % (
            CJ_CID, advertiser, offset, fields)
        req = urllib.request.Request('https://ads.api.cj.com/query', data=json.dumps({'query': q}).encode(),
                                     headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
        try:
            res = json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            sys.exit(f'CJ API HTTP {e.code}: {e.read().decode(errors="replace")[:800]}')
        if res.get('errors'):
            sys.exit(f'CJ API error: {res["errors"]}')
        p = res['data']['products']
        out += p['resultList']
        offset += p['count']
        if not p['count'] or offset >= p['totalCount'] or offset >= 10000:
            return out
        time.sleep(1)


def size_ml(title):
    m = re.search(r'\((\d+(?:\.\d+)?)\s*ml\)', title.lower()) or re.search(r'(\d+(?:\.\d+)?)\s*(oz|ml)\b', title.lower())
    if not m:
        return None
    v = float(m.group(1))
    return round(v * 29.57) if len(m.groups()) > 1 and m.group(2) == 'oz' else round(v)


TITLE = re.compile(r'^(?P<name>.+?)\s+(?:perfume|cologne)?\s*for (?:women|men|unisex)\s+by\s+(?P<rest>.+)$', re.I)
# Imitation oils ("Type Perfume Oil"), testers, unboxed bottles, sets and body products are never offered
EXCLUDE = re.compile(r'\b(type perfume oil|roll ?on|tester|unboxed|set|gift|sample|vial|mini|deodorant|deo|lotion|shower|gel|balm|after ?shave|body|hair|candle|travel|refill)\b', re.I)


def parse(p):
    """FragranceShop titles: '<Name> Perfume for Women by <Brand> Eau de Parfum Spray 3.4 oz (100ml)'."""
    m = TITLE.match(p['title'].strip())
    if not m or EXCLUDE.search(p['title']):
        return None
    brand = norm(p.get('brand') or '')
    rest = norm(m.group('rest'))
    conc = rest[len(brand):] if brand and rest.startswith(brand) else rest
    return {'name': norm(m.group('name')), 'brand': brand, 'conc': f' {conc} '}


def brand_words(b):
    return set(norm(b).replace('ysl', '').split()) - {'christian', 'thierry', 'parfums', 'paris', 'by', 'and'}


def same_concentration(conc, padded):
    """Reject an eau de parfum for an eau de toilette fiche and the reverse."""
    c = conc.lower()
    edt = ' toilette ' in padded or ' edt ' in padded
    edp = ' eau de parfum ' in padded or ' edp ' in padded
    if 'toilette' in c:
        return not edp and edt
    if 'eau de parfum' in c:
        return edp
    if c.strip() == 'parfum' or 'extrait' in c:
        return not edt and not edp
    return True


def match(products, perfumes):
    """Best offer per perfume slug: same brand, same name once the brand is removed, same concentration,
    a real bottle of 30 ml or more. The cheapest such bottle wins."""
    rows = []
    for p in products:
        if not p.get('price') or (p.get('availability') or 'in stock').lower().replace('_', ' ') == 'out of stock':
            continue
        x = parse(p)
        if x:
            rows.append((x, p))
    offers = {}
    for pf in perfumes:
        bw = brand_words(pf['brand'])
        if not bw:
            continue
        name = ' '.join(w for w in norm(pf['name']).split() if w not in bw)
        if not name:
            continue
        best = None
        for x, p in rows:
            pb = brand_words(x['brand'])
            if not (bw <= pb or pb <= bw) or not pb:
                continue
            pname = ' '.join(w for w in x['name'].split() if w not in pb and w not in bw)
            if pname != name:
                continue
            if not same_concentration(pf.get('concentration') or '', x['conc']):
                continue
            ml = size_ml(p['title'])
            if ml is not None and ml < 30:
                continue
            price = float(p['price']['amount'])
            if not best or price < best['price']:
                best = {'price': price, 'currency': p['price']['currency'], 'ml': ml, 'title': p['title'],
                        'url': (p.get('linkCode') or {}).get('clickUrl') or p['link']}
        if best:
            offers[pf['slug']] = best
    return offers


def main():
    shops = json.load(open(ROOT / 'src/data/affiliates.json'))['shops']
    perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
    data = {'generated': datetime.date.today().isoformat(), 'shops': {}}
    tok = None
    for s in shops:
        if not s.get('catalog'):
            continue
        if s.get('network') == 'cj':
            tok = tok or token()
            products = cj_products(tok, s['cj_advertiser'])
        else:
            continue
        offers = match(products, perfumes)
        data['shops'][s['id']] = offers
        print(f"{s['id']}: {len(products)} products, {len(offers)} perfumes matched")
        if os.environ.get('CATALOG_SAMPLE'):
            for p in products[:: max(1, len(products) // 60)][:60]:
                print('SAMPLE', p.get('brand'), '|', p['title'], '|', (p.get('price') or {}).get('amount'), '|', p.get('availability'))
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
