#!/usr/bin/env python3
"""Fetch remaining perfume images directly from CDN by guessing slugs."""

import json
import os
import re
import subprocess

CDN_BASE = "https://cdn.fragella.com/images"
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
    s = re.sub(r'[*]', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

def try_download(url, filepath):
    """Try to download, return True if 200 and file > 500 bytes."""
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "8", "-o", filepath, "-w", "%{http_code}", url],
        capture_output=True, text=True
    )
    code = result.stdout.strip()
    if code == "200" and os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        return True
    # Clean up failed download
    if os.path.exists(filepath):
        os.remove(filepath)
    return False

def generate_slug_candidates(name, brand):
    """Generate multiple possible CDN slugs for a perfume."""
    name_slug = slugify(name)
    brand_slug = slugify(brand)

    candidates = [
        name_slug,                          # jadore, angel, flowerbomb
        f"{brand_slug}-{name_slug}",        # dior-sauvage, creed-aventus
        f"{name_slug}-{brand_slug}",        # sauvage-dior (less common)
    ]

    # Handle "N°" -> "no" or "n"
    if "n-" in name_slug and name_slug.startswith("n-"):
        candidates.append(name_slug.replace("n-", "no", 1))

    # Handle brands with special chars
    # D&G -> dolce-gabbana
    if "&" in brand:
        short_brand = slugify(brand.split("&")[0].strip())
        candidates.append(f"{short_brand}-{name_slug}")

    # Remove "eau de" prefix variations
    for prefix in ["eau-de-", "eau-du-"]:
        if name_slug.startswith(prefix):
            candidates.append(name_slug[len(prefix):])
            candidates.append(f"{brand_slug}-{name_slug[len(prefix):]}")

    # Try with "pour homme"/"pour femme" removed
    for suffix in ["-pour-homme", "-pour-femme", "-for-her", "-for-men"]:
        if name_slug.endswith(suffix):
            stripped = name_slug[:len(name_slug)-len(suffix)]
            candidates.append(stripped)
            candidates.append(f"{brand_slug}-{stripped}")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return unique

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
        local_slug = slugify(f"{brand}-{name}")

        # Check if already have image
        has_image = False
        for ext in ['.webp', '.jpg']:
            p = f"{IMG_DIR}/{local_slug}{ext}"
            if os.path.exists(p) and os.path.getsize(p) > 500:
                has_image = True
                break

        # Also check if entity already has image set
        if name in entity_map:
            idx = entity_map[name]
            existing = template["entites"][idx].get("image", "")
            if existing and os.path.exists(f"public{existing}"):
                has_image = True

        if has_image:
            already += 1
            continue

        num = found + not_found + already + 1
        candidates = generate_slug_candidates(name, brand)

        downloaded = False
        for slug in candidates:
            url = f"{CDN_BASE}/{slug}.webp"
            filepath = f"{IMG_DIR}/{local_slug}.webp"

            if try_download(url, filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"[{num}/150] {name} ({brand}) -> {slug}.webp OK ({size_kb:.0f}KB)")
                found += 1
                if name in entity_map:
                    idx = entity_map[name]
                    template["entites"][idx]["image"] = f"/img/{local_slug}.webp"
                downloaded = True
                break

        if not downloaded:
            # Try .jpg as well
            for slug in candidates:
                url = f"{CDN_BASE}/{slug}.jpg"
                filepath = f"{IMG_DIR}/{local_slug}.jpg"

                if try_download(url, filepath):
                    size_kb = os.path.getsize(filepath) / 1024
                    print(f"[{num}/150] {name} ({brand}) -> {slug}.jpg OK ({size_kb:.0f}KB)")
                    found += 1
                    if name in entity_map:
                        idx = entity_map[name]
                        template["entites"][idx]["image"] = f"/img/{local_slug}.jpg"
                    downloaded = True
                    break

        if not downloaded:
            tried = ", ".join(candidates)
            print(f"[{num}/150] {name} ({brand}) -> MISS (tried: {tried})")
            not_found += 1

    # Save updated template data
    with open(OUT_FILE, 'w') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Found: {found}, Already cached: {already}, Not found: {not_found}")
    total = found + already
    print(f"Total images: {total}/150")

if __name__ == "__main__":
    main()
