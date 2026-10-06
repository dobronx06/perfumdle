"""Submit URLs to IndexNow (Bing, Yandex, Seznam, Naver; Bing feeds ChatGPT search and Copilot).

Usage:
  python3 scripts/indexnow.py new        # today's new URLs, read from https://perfumdle.com/new-urls.json
                                         # (waits until the live file carries today's date, i.e. the deploy is done)
  python3 scripts/indexnow.py sitemap    # every URL of the live sitemap (one-off, after big changes)
The key file lives at https://perfumdle.com/<KEY>.txt (public/<KEY>.txt). Standard library only (runs on GitHub Actions).
"""
import json, sys, time, re, datetime, urllib.request

HOST = 'perfumdle.com'
KEY = '54084590cdfd93d0fe91759676f0b452'
UA = {'User-Agent': 'perfumdle-indexnow/1.0'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode()


def submit(urls):
    for i in range(0, len(urls), 10000):
        body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls[i:i + 10000]}).encode()
        req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, method='POST',
                                     headers={'Content-Type': 'application/json; charset=utf-8', **UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            print('IndexNow', r.status, len(urls[i:i + 10000]), 'URLs')


mode = sys.argv[1] if len(sys.argv) > 1 else 'new'
if mode == 'sitemap':
    index = get(f'https://{HOST}/sitemap-index.xml')
    urls = []
    for sm in re.findall(r'<loc>(.*?)</loc>', index):
        urls += re.findall(r'<loc>(.*?)</loc>', get(sm))
    submit(urls)
else:
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    for attempt in range(30):  # the deploy usually takes 1 to 3 minutes
        data = json.loads(get(f'https://{HOST}/new-urls.json?t={time.time()}'))
        if data.get('date') == today:
            break
        time.sleep(30)
    else:
        sys.exit(f'new-urls.json still dated {data.get("date")}, deploy not live yet')
    if data['urls']:
        submit(data['urls'])
    else:
        print('No new URL today')
