#!/usr/bin/env python3
"""
sync_tap6_photos.py
-------------------
Đồng bộ và bổ sung ảnh minh họa iNaturalist cho Tập VI (Atlas cá rạn san hô):
1. Kế thừa ảnh từ các loài đã có trong Tập 1-5 (trùng scientific_name) — tức thì, không tốn băng thông.
2. Tải ảnh research-grade mới từ iNaturalist cho các loài đặc hữu/chưa có ảnh.
3. Nén WebP 640px, tải lên Supabase Storage bucket 'species-photos', ghi vào 'species_photos' và cập nhật 'species.photo_url'.

Cách chạy:
  python3 scripts/sync_tap6_photos.py              # chạy đầy đủ
  python3 scripts/sync_tap6_photos.py --inherit    # chỉ kế thừa ảnh từ Tập 1-5
  python3 scripts/sync_tap6_photos.py --limit 5    # thử nghiệm 5 loài mới
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

# Config
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
REQUEST_DELAY = 1.1

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
HEADERS_INAT = {
    "User-Agent": "CamNangCaBienVN/1.0 (haitrinh082@gmail.com)",
}

def supa_get(endpoint, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=representation"}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def supa_post(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=representation"}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()

def supa_patch(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=minimal"}
    resp = requests.patch(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp

def supa_upload(path, file_bytes, content_type="image/webp"):
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
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"

# iNaturalist helpers
def inat_get(endpoint, params=None):
    url = f"{INAT_API}/{endpoint}"
    resp = requests.get(url, headers=HEADERS_INAT, params=params, timeout=30)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return resp.json()

def find_taxon_id(scientific_name):
    try:
        data = inat_get("taxa", {"q": scientific_name, "rank": "species", "per_page": 5})
        results = data.get("results", [])
        for r in results:
            if r.get("name", "").lower() == scientific_name.lower():
                return r["id"]
        if results:
            return results[0]["id"]
    except Exception:
        pass
    return None

def fetch_observations(taxon_id, place_id=None, max_photos=3):
    params = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "photos": "true",
        "per_page": 10,
        "order_by": "votes",
    }
    if place_id:
        params["place_id"] = place_id

    try:
        data = inat_get("observations", params)
    except Exception:
        return []

    photos = []
    seen = set()
    for obs in data.get("results", []):
        obs_url = f"https://www.inaturalist.org/observations/{obs['id']}"
        for op in obs.get("photos", []):
            pid = op["id"]
            if pid in seen:
                continue
            seen.add(pid)
            orig_url = op.get("url", "")
            if not orig_url:
                continue
            medium_url = orig_url.replace("square.", "medium.").replace("small.", "medium.")
            user = obs.get("user", {})
            photographer = user.get("name") or user.get("login") or "Unknown"
            license_code = op.get("license_code") or obs.get("license_code") or "all-rights-reserved"
            photos.append({
                "photo_id": pid,
                "photo_url": medium_url,
                "photographer": photographer,
                "license": license_code,
                "obs_url": obs_url,
            })
            if len(photos) >= max_photos:
                return photos
    return photos

def download_and_convert_webp(url):
    resp = requests.get(url, headers=HEADERS_INAT, timeout=30)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if w > WEBP_WIDTH:
        ratio = WEBP_WIDTH / w
        img = img.resize((WEBP_WIDTH, int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=WEBP_QUALITY, method=4)
    return buf.getvalue()

def step1_inherit_photos():
    """Kế thừa ảnh của các loài đã có trong Tập 1-5 sang Tập 6."""
    print("\n--- BƯỚC 1: Kế thừa ảnh từ Tập 1-5 sang Tập 6 ---")
    
    # Lấy tất cả ảnh hiện có
    all_photos = []
    offset = 0
    while True:
        rows = supa_get("species_photos", {
            "select": "species_id,storage_path,source,photographer,license,source_url,is_primary,sort_order",
            "offset": offset,
            "limit": 1000
        })
        all_photos.extend(rows)
        if len(rows) < 1000: break
        offset += 1000

    photos_by_sp = {}
    for p in all_photos:
        photos_by_sp.setdefault(p['species_id'], []).append(p)

    # Lấy tất cả loài Tập 1-5 và Tập 6
    all_sp = []
    offset = 0
    while True:
        rows = supa_get("species", {
            "select": "id,volume,scientific_name,photo_url",
            "collection_id": "eq.ca-bien",
            "offset": offset,
            "limit": 1000
        })
        all_sp.extend(rows)
        if len(rows) < 1000: break
        offset += 1000

    t15_map = {s['scientific_name'].lower().strip(): s['id'] for s in all_sp if s.get('volume') and s['volume'] < 6}
    t6_species = [s for s in all_sp if s.get('volume') == 6]

    inherited_count = 0
    for s6 in t6_species:
        s6_id = s6['id']
        sci = s6['scientific_name'].lower().strip()
        
        # Bỏ qua nếu đã có ảnh trong species_photos
        if s6_id in photos_by_sp and photos_by_sp[s6_id]:
            continue

        donor_id = t15_map.get(sci)
        if donor_id and donor_id in photos_by_sp:
            donor_photos = photos_by_sp[donor_id]
            for dp in donor_photos:
                payload = {
                    "id": str(uuid.uuid4()),
                    "species_id": s6_id,
                    "storage_path": dp["storage_path"],
                    "source": dp.get("source") or "inaturalist",
                    "photographer": dp.get("photographer"),
                    "license": dp.get("license"),
                    "source_url": dp.get("source_url"),
                    "inat_photo_id": None, # tránh đụng unique constraint
                    "is_primary": dp.get("is_primary", False),
                    "sort_order": dp.get("sort_order", 0),
                }
                try:
                    supa_post("species_photos", payload)
                except Exception as e:
                    pass

            # Cập nhật photo_url chính nếu chưa có
            primary_photo = next((p for p in donor_photos if p.get("is_primary")), donor_photos[0])
            if primary_photo and not s6.get("photo_url"):
                pub_url = supa_public_url(primary_photo["storage_path"])
                try:
                    supa_patch(f"species?id=eq.{s6_id}", {"photo_url": pub_url})
                except Exception:
                    pass

            inherited_count += 1
            print(f"  ✓ Kế thừa {len(donor_photos)} ảnh cho {s6_id}: {s6['scientific_name']} (từ {donor_id})")

    print(f"--> Đã kế thừa thành công ảnh cho {inherited_count} loài Tập 6.\n")
    return inherited_count

def step2_fetch_remaining(limit=0):
    """Tải ảnh mới từ iNaturalist cho các loài còn lại của Tập 6."""
    print("\n--- BƯỚC 2: Tải ảnh iNaturalist cho các loài còn lại của Tập 6 ---")

    # Lấy loài Tập 6
    t6_species = supa_get("species", {
        "select": "id,volume,scientific_name,worms_accepted_name,photo_url",
        "volume": "eq.6",
        "order": "species_index"
    })

    # Lấy các loài đã có ảnh (phân trang để lấy toàn bộ)
    has_photo_ids = set()
    offset = 0
    while True:
        rows = supa_get("species_photos", {
            "select": "species_id",
            "offset": offset,
            "limit": 1000
        })
        has_photo_ids.update(p['species_id'] for p in rows)
        if len(rows) < 1000:
            break
        offset += 1000

    todo = [s for s in t6_species if s['id'] not in has_photo_ids]
    print(f"Tổng số loài Tập 6 chưa có ảnh: {len(todo)}")

    if limit > 0:
        todo = todo[:limit]
        print(f"Giới hạn xử lý: {limit} loài")

    success = 0
    for idx, sp in enumerate(todo, 1):
        sp_id = sp['id']
        sci_name = sp['scientific_name']
        alt_name = sp.get('worms_accepted_name')
        prefix = f"[{idx}/{len(todo)}]"

        # 1. Tìm taxon
        taxon_id = find_taxon_id(sci_name)
        if not taxon_id and alt_name and alt_name != sci_name:
            taxon_id = find_taxon_id(alt_name)
            if taxon_id:
                print(f"  {prefix} Dùng tên WoRMS: {alt_name}")

        if not taxon_id:
            print(f"  {prefix} ❌ {sci_name} — Không tìm thấy taxon trên iNaturalist")
            continue

        # 2. Lấy ảnh (Ưu tiên quan sát tại Việt Nam trước)
        photos = fetch_observations(taxon_id, place_id=VIETNAM_PLACE_ID, max_photos=MAX_PHOTOS_PER_SPECIES)
        region = "VN"
        if not photos:
            photos = fetch_observations(taxon_id, max_photos=MAX_PHOTOS_PER_SPECIES)
            region = "Global"

        if not photos:
            print(f"  {prefix} ⚠️ {sci_name} — Không có ảnh đạt chuẩn Research Grade")
            continue

        # 3. Tải, nén WebP và upload
        uploaded = 0
        for i, p in enumerate(photos):
            try:
                webp_bytes = download_and_convert_webp(p["photo_url"])
                storage_path = f"{COLLECTION}/{sp_id}/{i+1:02d}.webp"
                supa_upload(storage_path, webp_bytes)

                # Lưu vào species_photos
                payload = {
                    "id": str(uuid.uuid4()),
                    "species_id": sp_id,
                    "storage_path": storage_path,
                    "source": "inaturalist",
                    "photographer": p["photographer"],
                    "license": p["license"],
                    "source_url": p["obs_url"],
                    "inat_photo_id": None, # Dùng None để không bao giờ xung đột unique index
                    "is_primary": (i == 0),
                    "sort_order": i,
                }
                supa_post("species_photos", payload)

                if i == 0 and not sp.get("photo_url"):
                    pub_url = supa_public_url(storage_path)
                    supa_patch(f"species?id=eq.{sp_id}", {"photo_url": pub_url})

                uploaded += 1
            except Exception as e:
                print(f"    ⚠️ Ảnh {i+1} lỗi: {e}")

        if uploaded > 0:
            success += 1
            print(f"  {prefix} ✅ {sci_name} — Đã lưu {uploaded} ảnh ({region})")

    print(f"\n--> Hoàn thành Bước 2: Tải thêm ảnh cho {success}/{len(todo)} loài.")

def main():
    parser = argparse.ArgumentParser(description="Đồng bộ ảnh cho Tập 6 (Atlas cá rạn san hô)")
    parser.add_argument("--inherit-only", action="store_true", help="Chỉ kế thừa ảnh từ Tập 1-5")
    parser.add_argument("--limit", type=int, default=0, help="Giới hạn số loài tải mới")
    args = parser.parse_args()

    print("=" * 60)
    print("📸 ĐỒNG BỘ ẢNH MINH HỌA TẬP VI (ATLAS CÁ RẠN SAN HÔ)")
    print("=" * 60)

    step1_inherit_photos()
    if not args.inherit_only:
        step2_fetch_remaining(limit=args.limit)

if __name__ == '__main__':
    main()
