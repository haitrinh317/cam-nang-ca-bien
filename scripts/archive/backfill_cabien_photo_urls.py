#!/usr/bin/env python3
"""
Backfill photo_url in species table for ca-bien species that already have photos in species_photos.

Usage:
  python scripts/backfill_cabien_photo_urls.py
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
BUCKET = "species-photos"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def get_public_url(storage_path):
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"

def main():
    print("=" * 60)
    print("🖼️ Backfill ca-bien photo_url from species_photos")
    print("=" * 60)

    # 1. Get ca-bien species with empty photo_url
    print("\n📋 1. Loading ca-bien species from Supabase...")
    all_cabien = []
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&select=id,scientific_name,photo_url&offset={offset}&limit=1000"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        rows = r.json()
        all_cabien.extend(rows)
        if len(rows) < 1000:
            break
        offset += 1000
    print(f"   Total ca-bien species: {len(all_cabien)}")

    # 2. Get photos from species_photos
    print("\n📸 2. Loading species_photos...")
    all_photos = []
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/species_photos?select=species_id,storage_path,is_primary,sort_order&offset={offset}&limit=1000"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        rows = r.json()
        all_photos.extend(rows)
        if len(rows) < 1000:
            break
        offset += 1000
    print(f"   Total photo records: {len(all_photos)}")

    # Map primary photo for each species
    photo_map = {}
    for p in all_photos:
        sp_id = p["species_id"]
        # Prioritize is_primary or sort_order == 0
        if sp_id not in photo_map:
            photo_map[sp_id] = p["storage_path"]
        elif p.get("is_primary") or p.get("sort_order") == 0:
            photo_map[sp_id] = p["storage_path"]

    # 3. Identify species needing backfill
    to_update = []
    for sp in all_cabien:
        curr_url = sp.get("photo_url") or ""
        sp_id = sp["id"]
        if not curr_url and sp_id in photo_map:
            storage_path = photo_map[sp_id]
            pub_url = get_public_url(storage_path)
            to_update.append((sp_id, sp["scientific_name"], pub_url))

    print(f"\n🎯 Species needing photo_url backfill: {len(to_update)}")
    if not to_update:
        print("✅ Everything is already up to date!")
        return

    # 4. Patch species table in batches
    print("\n🚀 Patching species records...")
    success = 0
    fail = 0

    for idx, (sp_id, sci_name, pub_url) in enumerate(to_update, 1):
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        resp = requests.patch(patch_url, headers={**HEADERS, "Prefer": "return=minimal"}, json={"photo_url": pub_url}, timeout=30)
        if resp.ok:
            success += 1
            if idx % 50 == 0 or idx == len(to_update):
                print(f"   [{idx}/{len(to_update)}] ✅ Updated {sci_name} ({sp_id})")
        else:
            fail += 1
            print(f"   [{idx}/{len(to_update)}] ❌ Failed {sci_name}: {resp.status_code} {resp.text}")

    print("\n" + "=" * 60)
    print(f"📊 Backfill Summary:")
    print(f"   Successfully updated: {success}")
    print(f"   Failed:               {fail}")
    print(f"   Total photo coverage now: {len([s for s in all_cabien if s.get('photo_url')]) + success} / {len(all_cabien)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
