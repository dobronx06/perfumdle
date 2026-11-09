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
OK_TAIL = {'eau', 'de', 'toilette', 'parfum', 'cologne', 'edt', 'edp', 'spray', 'vaporisateur', 'for', 'men', 'women', 'unisex',
           'him', 'her', 'by', 'oz', 'ml', 'fl', 'new', 'packaging'}
SKIP = re.compile(r'\b(tester|unboxed|sample|vial|mini|miniature|gift set|set|coffret|deodorant|deo|lotion|shower|gel|balm|after ?shave|body|hair|candle|travel|refill)\b')


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
    m = re.search(r'(\d+(?:\.\d+)?)\s*(oz|ml)\b', title.lower())
    if not m:
        return None
    v = float(m.group(1))
    return round(v * 29.57) if m.group(2) == 'oz' else round(v)


def same_concentration(conc, padded):
    """Reject an eau de parfum for an eau de toilette fiche and the reverse, when the title says which it is."""
    c = conc.lower()
    edt = ' toilette ' in padded or ' edt ' in padded
    edp = ' eau de parfum ' in padded or ' edp ' in padded
    if 'toilette' in c:
        return not edp
    if 'eau de parfum' in c:
        return not edt and ' cologne ' not in padded
    return True


def match(products, perfumes):
    """Best (cheapest bottle of 30 ml or more) product per perfume slug: brand and the full name must appear."""
    offers = {}
    rows = [(norm(f"{p.get('brand') or ''} {p['title']}"), p) for p in products
            if p.get('price') and (p.get('availability') or 'in stock').lower().replace('_', ' ') != 'out of stock']
    for pf in perfumes:
        brand = norm(pf['brand']).replace('thierry ', '')
        name = norm(pf['name'])
        if not name:
            continue
        best = None
        for text, p in rows:
            padded = f' {text} '
            if f' {brand} ' not in padded or SKIP.search(text):
                continue
            if f' {name} ' not in padded:
                continue
            if not same_concentration(pf.get('concentration') or '', padded):
                continue
            # "Sauvage" must not catch "Eau Sauvage" or "Sauvage Elixir": around the name, only brand,
            # concentration and size words are allowed
            head, tail = padded.split(f' {name} ', 1)
            house = set(brand.split()) | {'christian', 'thierry', 'paris', 'by'}
            if any(w not in house for w in head.split()):
                continue
            if any(w not in OK_TAIL | house and not re.fullmatch(r'[\d.]+', w) for w in tail.split()):
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
