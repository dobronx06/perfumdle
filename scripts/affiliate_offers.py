"""Fetch affiliate shop catalogues and match them to our perfumes.

Writes src/data/affiliate-offers.json: for each shop with "catalog": true in src/data/affiliates.json,
the cheapest full-size bottle it sells for each perfume we have, with its price, size and tracked link.
The site then shows the buy button only on perfumes the shop really sells.

CJ shops use the CJ Product Search API (GraphQL). The token comes from the CJ_TOKEN environment variable
or from ~/.config/perfumdle/affiliate.env (CJ_TOKEN=...). It is never printed.

Usage: python3 scripts/affiliate_offers.py
"""
import json, os, re, sys, time, unicodedata, datetime, pathlib, urllib.request, urllib.error, urllib.parse

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


def cj_deeplink_prefix(tok, advertiser):
    """A tracked deep-link prefix for shops whose product feed gives no clickUrl (Perfumania, Fragrance Outlet):
    one of the advertiser's evergreen text links from the CJ Link Search API, with the product URL appended.
    Returns None if the shop has no usable link: its offers are then dropped, never published untracked."""
    q = urllib.parse.urlencode({'website-id': CJ_PID, 'advertiser-ids': advertiser, 'link-type': 'Text Link', 'records-per-page': 100})
    req = urllib.request.Request(f'https://link-search.api.cj.com/v2/link-search?{q}', headers={'Authorization': f'Bearer {tok}'})
    try:
        xml = urllib.request.urlopen(req, timeout=60).read().decode()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f'CJ link search failed for {advertiser}: {e}')
        return None
    best = None
    for link in re.findall(r'<link>(.*?)</link>', xml, re.S):
        get = lambda t: (re.search(f'<{t}>(.*?)</{t}>', link, re.S) or [None, ''])[1].strip()
        lid, end = get('link-id'), get('promotion-end-date')
        if not lid.isdigit():
            continue
        # A link with no end date keeps tracking after the season; a dated promo link is a last resort
        rank_ = (1 if end else 0, lid)
        if not best or rank_ < best[0]:
            best = (rank_, lid)
    if not best:
        print(f'CJ link search: no text link for {advertiser}')
        return None
    print(f'CJ deep links for {advertiser} via link {best[1]}')
    return f'https://www.jdoqocy.com/click-{CJ_PID}-{best[1]}?url='


def cj_products(tok, advertiser):
    fields = 'id title brand price { amount currency } link ... on Shopping { availability } linkCode(pid: "%s") { clickUrl }' % CJ_PID
    out, offset = [], 0
    while True:
        q = '{ products(companyId: "%s", partnerIds: ["%s"], limit: 1000, offset: %d) { totalCount count resultList { %s } } }' % (
            CJ_CID, advertiser, offset, fields)
        req = urllib.request.Request('https://ads.api.cj.com/query', data=json.dumps({'query': q}).encode(),
                                     headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'})
        # CJ sometimes stalls for minutes: retry the page instead of losing the day's prices.
        for attempt in range(4):
            try:
                res = json.load(urllib.request.urlopen(req, timeout=120))
                break
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == 3:
                    sys.exit(f'CJ API HTTP {e.code}: {e.read().decode(errors="replace")[:800]}')
            except (TimeoutError, urllib.error.URLError) as e:
                if attempt == 3:
                    sys.exit(f'CJ API unreachable after 4 tries: {e}')
            print(f'CJ API slow or failing (offset {offset}), retry {attempt + 1}/3', flush=True)
            time.sleep(30 * (attempt + 1))
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


TITLE = re.compile(r'^(?P<name>.+?)\s+(?:perfume|cologne)?\s*for (?P<gender>women|men|unisex)\s+by\s+(?P<rest>.+)$', re.I)
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
    return {'name': norm(m.group('name')), 'brand': brand, 'conc': f' {conc} ', 'gender': m.group('gender').lower()}


# Generic titles ("Gucci Bloom Eau de Parfum Spray 3.3 oz", "Bloom by Gucci for Women - 3.3 oz EDP Spray"):
# everything that is not the perfume's name is stripped, the brand words are removed later in match().
CONC = re.compile(r'\b(eau de parfum|eau de toilette|eau de cologne|eau fraiche|extrait de parfum|parfum|edp|edt|edc)\b')
SIZE = re.compile(r'\(.*?\)|\b\d+(?:[.,]\d+)?\s*(?:fl\.?\s*)?(?:oz|ml)\b', re.I)  # on the raw title, before norm() splits "3.4"
NOISE = re.compile(r'\b(?:for|pour)\s+(?:women|men|unisex|her|him)\b'
                   r'|\b(?:womens|mens|women|men|unisex|spray|natural|vaporisateur|vapo|perfume|cologne|fragrance|by|new packaging|refillable|splash)\b')
GENDER = {'women': 'women', 'womens': 'women', 'her': 'women', 'men': 'men', 'mens': 'men', 'him': 'men', 'unisex': 'unisex'}


def parse_generic(p):
    title = p['title'].strip()
    brand = norm(p.get('brand') or '')
    if not brand or EXCLUDE.search(title):
        return None
    t = norm(SIZE.sub(' ', title).replace("'s ", 's '))
    g = re.search(r'\b(?:for\s+)?(womens|mens|women|men|unisex|her|him)\b', t)
    conc = ' '.join(CONC.findall(t))
    # "Sauvage by Christian Dior": the whole "by ..." credit goes, not only the brand's own words
    t = re.sub(rf'\bby\s+(?:\w+\s+){{0,3}}?{re.escape(brand.split()[-1])}\b', ' ', t)
    name = ' '.join(NOISE.sub(' ', CONC.sub(' ', t)).split())
    if not name:
        return None
    # Perfumania and Fragrance Outlet titles rarely say the concentration ("La Vie Est Belle Perfume - 2.5 oz."):
    # None means unknown, and match() then skips the concentration check instead of rejecting the bottle.
    return {'name': name, 'brand': brand, 'conc': f' {conc} ' if conc else None, 'gender': GENDER.get(g.group(1)) if g else None}


PARSERS = {'fragranceshop': parse, 'generic': parse_generic}


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


def rank(o):
    """The 100 ml bottle (90 to 125 ml) when the shop has one, else the cheapest bottle."""
    hundred = o['ml'] is not None and 90 <= o['ml'] <= 125
    return (0 if hundred else 1, abs((o['ml'] or 0) - 100) if hundred else 0, o['price'])


def tracked(url):
    """Only CJ click URLs earn a commission: an offer without one is never shown."""
    return bool(url) and re.match(r'^https://www\.(jdoqocy|kqzyfj|dpbolvw|anrdoezrs|tkqlhce)\.(com|net)/click-', url) is not None


def match(products, perfumes, parser=parse, deeplink=None):
    """Best offer per perfume slug: same brand, same name once the brand is removed, same concentration,
    a real bottle of 30 ml or more. The 100 ml bottle wins when there is one, else the cheapest."""
    rows = []
    for p in products:
        if not p.get('price') or (p.get('availability') or 'in stock').lower().replace('_', ' ') == 'out of stock':
            continue
        x = parser(p)
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
            # "Twilly Dhermes" is Twilly d'Hermès: the names are compared without their spaces
            if pname.replace(' ', '') != name.replace(' ', ''):
                continue
            if x['conc'] is not None and not same_concentration(pf.get('concentration') or '', x['conc']):
                continue
            # "Aventus for Women" is another perfume than Aventus
            if x['gender'] and {'Masculine': 'women', 'Feminine': 'men'}.get(pf.get('gender')) == x['gender']:
                continue
            ml = size_ml(p['title'])
            if ml is not None and ml < 30:
                continue
            price = float(p['price']['amount'])
            url = (p.get('linkCode') or {}).get('clickUrl') or (deeplink + urllib.parse.quote(p['link'], safe='') if deeplink and p.get('link') else None)
            if not tracked(url):
                continue
            cand = {'price': price, 'currency': p['price']['currency'], 'ml': ml, 'title': p['title'], 'url': url}
            if not best or rank(cand) < rank(best):
                best = cand
        if best:
            offers[pf['slug']] = best
    return offers


def main():
    shops = json.load(open(ROOT / 'src/data/affiliates.json'))['shops']
    perfumes = json.load(open(ROOT / 'src/data/perfumes.json'))
    previous = json.load(open(OUT))['shops'] if OUT.exists() else {}
    data = {'generated': datetime.date.today().isoformat(), 'shops': {}}
    tok = None
    for s in shops:
        if not s.get('catalog'):
            continue
        if s.get('network') == 'cj':
            tok = tok or token()
            # One shop's feed failing must not lose the other shops' prices: keep its last offers.
            try:
                products = cj_products(tok, s['cj_advertiser'])
            except SystemExit as e:
                print(f"{s['id']}: {e}, previous offers kept")
                if s['id'] in previous:
                    data['shops'][s['id']] = {k: o for k, o in previous[s['id']].items() if tracked(o.get('url'))}
                continue
        else:
            continue
        deeplink = None
        if s.get('network') == 'cj' and not any((p.get('linkCode') or {}).get('clickUrl') for p in products[:200]):
            deeplink = cj_deeplink_prefix(tok, s['cj_advertiser'])
        offers = match(products, perfumes, PARSERS[s.get('parser', 'fragranceshop')], deeplink)
        data['shops'][s['id']] = offers
        print(f"{s['id']}: {len(products)} products, {len(offers)} perfumes matched")
        if os.environ.get('CATALOG_SAMPLE'):
            for p in products[:: max(1, len(products) // 60)][:60]:
                print('SAMPLE', p.get('brand'), '|', p['title'], '|', (p.get('price') or {}).get('amount'), '|', p.get('availability'))
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
