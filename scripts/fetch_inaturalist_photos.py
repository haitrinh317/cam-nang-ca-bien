#!/usr/bin/env python3
"""
Fetch research-grade photos from iNaturalist for ca-bien species.

Usage:
  python scripts/fetch_inaturalist_photos.py              # full run
  python scripts/fetch_inaturalist_photos.py --limit 5    # test 5 species
  python scripts/fetch_inaturalist_photos.py --dry-run    # preview only
  python scripts/fetch_inaturalist_photos.py --offset 100 # resume from #100
"""

import argparse
import io
import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# ── Config ──────────────────────────────────────────────────────────
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ["NEXT_PUBLIC_SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = "species-photos"
COLLECTION = "ca-bien"
INAT_API = "https://api.inaturalist.org/v1"
VIETNAM_PLACE_ID = 6878
MAX_PHOTOS_PER_SPECIES = 3
WEBP_WIDTH = 640
WEBP_QUALITY = 75
REQUEST_DELAY = 1.1  # seconds between iNaturalist API calls

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
HEADERS_INAT = {
    "User-Agent": "CamNangCaBienVN/1.0 (haitrinh082@gmail.com)",
}

# ── Supabase helpers ────────────────────────────────────────────────

def supa_get(endpoint, params=None):
    """GET from Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=representation"}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def supa_post(endpoint, data):
    """POST to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=representation"}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def supa_patch(endpoint, data):
    """PATCH to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=minimal"}
    resp = requests.patch(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp


def supa_upload(path, file_bytes, content_type="image/webp"):
    """Upload file to Supabase Storage."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    resp = requests.post(url, headers=headers, data=file_bytes, timeout=60)
    resp.raise_for_status()
    return resp.json()


def supa_public_url(path):
    """Get public URL for a storage object."""
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"


# ── iNaturalist helpers ─────────────────────────────────────────────

def inat_get(endpoint, params=None):
    """GET from iNaturalist API with rate limiting."""
    url = f"{INAT_API}/{endpoint}"
    resp = requests.get(url, headers=HEADERS_INAT, params=params, timeout=30)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return resp.json()


def find_taxon_id(scientific_name):
    """Look up iNaturalist taxon ID for a scientific name."""
    data = inat_get("taxa", {"q": scientific_name, "rank": "species", "per_page": 5})
    results = data.get("results", [])
    # Exact match first
    for t in results:
        if t.get("name", "").lower() == scientific_name.lower():
            return t["id"]
    # Partial match fallback
    if results:
        return results[0]["id"]
    return None


def fetch_observations(taxon_id, place_id=None, max_photos=3):
    """
    Fetch research-grade observations with CC-licensed photos.
    Returns list of {photo_id, photo_url, photographer, license, obs_url}.
    """
    params = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "photo_license": "cc-by,cc-by-nc,cc0",
        "photos": "true",
        "order_by": "votes",
        "per_page": 10,  # fetch more, pick best
    }
    if place_id:
        params["place_id"] = place_id

    data = inat_get("observations", params)
    results = data.get("results", [])

    photos = []
    seen_ids = set()
    for obs in results:
        obs_url = f"https://www.inaturalist.org/observations/{obs['id']}"
        observer = obs.get("user", {}).get("login", "Unknown")
        for p in obs.get("photos", []):
            pid = p.get("id")
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            # Get medium URL (max 500px wide on iNaturalist)
            medium_url = p.get("url", "").replace("square", "medium")
            if not medium_url:
                continue
            # Parse license
            lic = p.get("license_code", "") or ""
            photos.append({
                "photo_id": pid,
                "photo_url": medium_url,
                "photographer": observer,
                "license": lic.lower().replace("_", "-") if lic else "cc-by-nc",
                "obs_url": obs_url,
            })
            if len(photos) >= max_photos:
                return photos
    return photos


# ── Image processing ────────────────────────────────────────────────

def download_and_convert_webp(url):
    """Download image and convert to WebP, resize to WEBP_WIDTH."""
    resp = requests.get(url, headers=HEADERS_INAT, timeout=30)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))
    # Convert to RGB if needed (e.g. RGBA PNGs)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Resize maintaining aspect ratio
    w, h = img.size
    if w > WEBP_WIDTH:
        ratio = WEBP_WIDTH / w
        img = img.resize((WEBP_WIDTH, int(h * ratio)), Image.LANCZOS)
    # Save to WebP
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=WEBP_QUALITY, method=4)
    return buf.getvalue()


# ── Main logic ──────────────────────────────────────────────────────

def get_all_species(volume=None):
    """Fetch all ca-bien species from Supabase."""
    all_species = []
    offset = 0
    batch = 500
    while True:
        params = {
            "select": "id,scientific_name,worms_accepted_name,photo_url",
            "collection_id": f"eq.{COLLECTION}",
            "order": "volume,species_index",
            "offset": offset,
            "limit": batch,
        }
        if volume:
            params["volume"] = f"eq.{volume}"
        rows = supa_get("species", params)
        all_species.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    return all_species


def get_existing_photo_species():
    """Get set of species_ids that already have photos."""
    existing = set()
    offset = 0
    batch = 500
    while True:
        rows = supa_get("species_photos", {
            "select": "species_id",
            "offset": offset,
            "limit": batch,
        })
        existing.update(r["species_id"] for r in rows)
        if len(rows) < batch:
            break
        offset += batch
    return existing


def process_species(sp, idx, total, dry_run=False):
    """Process a single species: find photos, download, upload, insert DB."""
    species_id = sp["id"]
    sci_name = sp["scientific_name"]
    alt_name = sp.get("worms_accepted_name")

    prefix = f"[{idx}/{total}]"

    # 1. Find taxon on iNaturalist
    taxon_id = find_taxon_id(sci_name)
    if not taxon_id and alt_name and alt_name != sci_name:
        taxon_id = find_taxon_id(alt_name)
        if taxon_id:
            print(f"  {prefix} Used WoRMS accepted name: {alt_name}")

    if not taxon_id:
        print(f"  {prefix} ❌ {sci_name} — not found on iNaturalist")
        return 0

    # 2. Fetch photos — Vietnam first
    photos = fetch_observations(taxon_id, place_id=VIETNAM_PLACE_ID, max_photos=MAX_PHOTOS_PER_SPECIES)
    source_region = "VN"

    # 3. Fallback to global if < 2 photos from VN
    if len(photos) < 2:
        vn_ids = {p["photo_id"] for p in photos}
        global_photos = fetch_observations(taxon_id, place_id=None, max_photos=MAX_PHOTOS_PER_SPECIES)
        # Merge, VN first, avoid duplicates
        for gp in global_photos:
            if gp["photo_id"] not in vn_ids and len(photos) < MAX_PHOTOS_PER_SPECIES:
                photos.append(gp)
        if len(photos) > len(vn_ids):
            source_region = "VN+Global"
        if not photos:
            source_region = "Global"

    if not photos:
        print(f"  {prefix} ⚠️  {sci_name} — no CC-licensed research-grade photos")
        return 0

    if dry_run:
        print(f"  {prefix} 🔍 {sci_name} — {len(photos)} photos ({source_region}) [DRY RUN]")
        return len(photos)

    # 4. Download, convert, upload each photo
    uploaded = 0
    for i, p in enumerate(photos):
        try:
            webp_bytes = download_and_convert_webp(p["photo_url"])
            storage_path = f"{COLLECTION}/{species_id}/{i+1:02d}.webp"
            supa_upload(storage_path, webp_bytes)

            # 5. Insert into species_photos
            supa_post("species_photos", {
                "id": str(uuid.uuid4()),
                "species_id": species_id,
                "storage_path": storage_path,
                "source": "inaturalist",
                "photographer": p["photographer"],
                "license": p["license"],
                "source_url": p["obs_url"],
                "inat_photo_id": p["photo_id"],
                "is_primary": (i == 0),
                "sort_order": i,
            })
            if i == 0 and not sp.get("photo_url"):
                public_url = supa_public_url(storage_path)
                try:
                    supa_patch(f"species?id=eq.{species_id}", {"photo_url": public_url})
                except Exception:
                    pass
            uploaded += 1
        except Exception as e:
            print(f"    ⚠️  Photo {i+1} failed: {e}")

    size_kb = sum(len(download_and_convert_webp(p["photo_url"])) for p in []) / 1024  # ponytail: don't re-download
    print(f"  {prefix} ✅ {sci_name} — {uploaded} photos ({source_region})")
    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Fetch iNaturalist photos for ca-bien species")
    parser.add_argument("--volume", type=int, default=None, help="Process only specific volume (e.g. 6)")
    parser.add_argument("--limit", type=int, default=0, help="Process only N species (0 = all)")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N species")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't download/upload")
    args = parser.parse_args()

    print("=" * 60)
    print("🐟 iNaturalist Photo Fetcher — Cẩm Nang Cá Biển VN")
    if args.volume:
        print(f"   Chỉ áp dụng cho: Tập {args.volume}")
    print("=" * 60)

    # Get all species
    print("\n📋 Loading species from Supabase...")
    all_species = get_all_species(volume=args.volume)
    print(f"   Total ca-bien species: {len(all_species)}")

    # Get existing photos (for incremental)
    existing = get_existing_photo_species()
    print(f"   Species already with photos: {len(existing)}")

    # Filter out species that already have photos
    todo = [sp for sp in all_species if sp["id"] not in existing]
    print(f"   Species to process: {len(todo)}")

    # Apply offset/limit
    if args.offset:
        todo = todo[args.offset:]
        print(f"   After offset {args.offset}: {len(todo)}")
    if args.limit:
        todo = todo[:args.limit]
        print(f"   After limit {args.limit}: {len(todo)}")

    if not todo:
        print("\n✅ Nothing to do!")
        return

    print(f"\n{'🔍 DRY RUN' if args.dry_run else '🚀 Starting'} — {len(todo)} species\n")

    total_photos = 0
    found = 0
    not_found = 0
    start_time = time.time()

    for i, sp in enumerate(todo, 1):
        try:
            n = process_species(sp, i, len(todo), dry_run=args.dry_run)
            if n > 0:
                found += 1
                total_photos += n
            else:
                not_found += 1
        except Exception as e:
            print(f"  [{i}/{len(todo)}] 💥 {sp['scientific_name']} — ERROR: {e}")
            not_found += 1

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"📊 Summary:")
    print(f"   Species with photos: {found}")
    print(f"   Species without:     {not_found}")
    print(f"   Total photos:        {total_photos}")
    print(f"   Time:                {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
