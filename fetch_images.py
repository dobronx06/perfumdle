#!/usr/bin/env python3
"""Fetch perfume images from Fragella API and save locally."""

import json
import os
import re
import subprocess
import time

API_KEY = "a6df7575bd29d258eea8f84444a8271ae4d4159e9b51d9aab774635c8ca5c7f2"
API_BASE = "https://api.fragella.com/api/v1"
IMG_DIR = "public/img"
DATA_FILE = "data.json"
OUT_FILE = "src/data/data.json"

def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'[àáâãäå]', 'a', s)
    s = re.sub(r'[èéêë]', 'e', s)
    s = re.sub(r'[ìíîï]', 'i', s)
    s = re.sub(r'[òóôõö]', 'o', s)
    s = re.sub(r'[ùúûü]', 'u', s)
    s = re.sub(r'[ñ]', 'n', s)
    s = re.sub(r'[ç]', 'c', s)
    s = re.sub(r"[''`]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

def curl_json(url):
    """Fetch JSON from URL using curl (handles macOS SSL properly)."""
    result = subprocess.run(
        ["curl", "-s", "-H", f"x-api-key: {API_KEY}", "--max-time", "10", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def curl_download(url, filepath):
    """Download a file using curl."""
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "15", "-o", filepath, url],
        capture_output=True
    )
    return result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 500

def api_search(name, brand):
    """Search for a fragrance, try name first, then name+brand."""
    import urllib.parse
    queries = [name, f"{name} {brand}"]
    for q in queries:
        encoded = urllib.parse.quote(q)
        url = f"{API_BASE}/fragrances?search={encoded}&limit=3"
        data = curl_json(url)
        if not data or not isinstance(data, list) or len(data) == 0:
            continue
        # Try to find exact match by brand
        for item in data:
            if item.get("Brand", "").lower() == brand.lower():
                return item
        # Fallback to first result
        return data[0]
    return None

def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    with open(DATA_FILE) as f:
        raw = json.load(f)

    with open(OUT_FILE) as f:
        template = json.load(f)

    # Build lookup: perfume name -> entity index
    entity_map = {}
    for i, ent in enumerate(template["entites"]):
        entity_map[ent["nom"]] = i

    found = 0
    not_found = 0
    already = 0

    for perfume in raw["entities"]:
        name = perfume["name"]
        brand = perfume["brand"]
        slug = slugify(f"{brand}-{name}")
        img_path = f"{IMG_DIR}/{slug}.webp"
        web_path = f"/img/{slug}.webp"

        # Skip if already downloaded
        if os.path.exists(img_path) and os.path.getsize(img_path) > 500:
            if name in entity_map:
                idx = entity_map[name]
                template["entites"][idx]["image"] = web_path
            already += 1
            continue
        # Also check jpg variant
        jpg_path = img_path.replace('.webp', '.jpg')
        jpg_web = web_path.replace('.webp', '.jpg')
        if os.path.exists(jpg_path) and os.path.getsize(jpg_path) > 500:
            if name in entity_map:
                idx = entity_map[name]
                template["entites"][idx]["image"] = jpg_web
            already += 1
            continue

        num = found + not_found + already + 1
        total = len(raw["entities"])
        print(f"[{num}/{total}] {name} ({brand})...", end=" ", flush=True)

        result = api_search(name, brand)
        if not result:
            print("NOT FOUND")
            not_found += 1
            time.sleep(0.3)
            continue

        # Prefer transparent webp, fallback to jpg
        img_url = result.get("Image URL Transparent") or result.get("Image URL")
        if not img_url:
            print("NO IMAGE")
            not_found += 1
            time.sleep(0.3)
            continue

        # Use jpg extension if URL is jpg
        dl_path = img_path
        dl_web = web_path
        if not img_url.endswith('.webp'):
            dl_path = img_path.replace('.webp', '.jpg')
            dl_web = web_path.replace('.webp', '.jpg')

        if curl_download(img_url, dl_path):
            size_kb = os.path.getsize(dl_path) / 1024
            print(f"OK ({size_kb:.0f}KB)")
            found += 1
            if name in entity_map:
                idx = entity_map[name]
                template["entites"][idx]["image"] = dl_web
        else:
            print("DOWNLOAD FAILED")
            not_found += 1

        # Rate limit: ~3 requests/sec
        time.sleep(0.35)

    # Save updated template data
    with open(OUT_FILE, 'w') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Found: {found}, Already cached: {already}, Not found: {not_found}")
    print(f"Updated {OUT_FILE} with image paths.")

if __name__ == "__main__":
    main()
