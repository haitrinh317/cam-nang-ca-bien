#!/usr/bin/env python3
"""
scripts/fetch_crustacean_photos.py
Fetch research-grade photos from iNaturalist for giap-xac species.
Supports multi-level matching:
1. WoRMS Accepted Name
2. Scientific Name (clean)
3. Subgenus variants (e.g., Fenneropenaeus merguiensis vs Penaeus merguiensis)

Usage:
  python3 scripts/fetch_crustacean_photos.py --dry-run
  python3 scripts/fetch_crustacean_photos.py --limit 10
  python3 scripts/fetch_crustacean_photos.py
"""

import argparse
import io
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# Load environment
load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
BUCKET = "species-photos"
COLLECTION = "giap-xac"
INAT_API = "https://api.inaturalist.org/v1"
VIETNAM_PLACE_ID = 6878
MAX_PHOTOS_PER_SPECIES = 3
WEBP_WIDTH = 640
WEBP_QUALITY = 75
REQUEST_DELAY = 1.2

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
    headers = {**HEADERS_SUPA, "Prefer": "resolution=ignore-duplicates,return=representation"}
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return []

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

import uuid

def inat_get(endpoint, params=None, max_retries=4):
    url = f"{INAT_API}/{endpoint}"
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS_INAT, params=params, timeout=30)
            if resp.status_code == 429:
                time.sleep(4 * (attempt + 1))
                continue
            resp.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return resp.json()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"    [!] inat_get error after {max_retries} attempts: {e}")
                return {}
            time.sleep(2 * (attempt + 1))
    return {}

def generate_search_candidates(scientific_name, worms_accepted_name):
    """Generate candidate Latin names in priority order."""
    candidates = []
    
    # 1. WoRMS accepted name first if different
    if worms_accepted_name and worms_accepted_name.strip():
        acc_clean = re.sub(r'\(.*?\)', '', worms_accepted_name).strip()
        acc_words = acc_clean.split()
        if len(acc_words) >= 2:
            candidates.append(f"{acc_words[0]} {acc_words[1]}")
            
    # 2. Subgenus extracted name: Penaeus (Melicertus) canaliculatus -> Melicertus canaliculatus
    subg_match = re.search(r'\((\w+)\)', scientific_name)
    if subg_match:
        subg = subg_match.group(1)
        words = scientific_name.split()
        sp_epithet = words[-1]
        candidates.append(f"{subg} {sp_epithet}")

    # 3. Clean binomial: Penaeus (Melicertus) canaliculatus -> Penaeus canaliculatus
    sci_clean = re.sub(r'\(.*?\)', '', scientific_name).strip()
    sci_words = sci_clean.split()
    if len(sci_words) >= 2:
        candidates.append(f"{sci_words[0]} {sci_words[1]}")
        
    # Unique preserve order
    seen = set()
    uniq = []
    for c in candidates:
        cl = c.strip()
        if cl.lower() not in seen:
            seen.add(cl.lower())
            uniq.append(cl)
    return uniq

def find_taxon_for_species(candidates):
    """Try to find an iNaturalist taxon with research grade observations from candidates."""
    for cand in candidates:
        try:
            data = inat_get("taxa", {"q": cand, "per_page": 5})
            results = data.get("results", [])
            for t in results:
                tname = t.get("name", "").strip().lower()
                matched_term = t.get("matched_term", "").strip().lower()
                cand_l = cand.lower()
                if tname == cand_l or matched_term == cand_l:
                    obs_cnt = t.get("observations_count", 0)
                    if obs_cnt > 0:
                        return t["id"], cand, obs_cnt
        except Exception as e:
            print(f"    [!] Error querying iNat for '{cand}': {e}")
            continue
    return None, None, 0

def fetch_observations(taxon_id, place_id=None, max_photos=3):
    params = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "photo_license": "cc-by,cc-by-nc,cc0",
        "photos": "true",
        "order_by": "votes",
        "per_page": 10,
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
            medium_url = p.get("url", "").replace("square", "medium")
            if not medium_url:
                continue
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

def download_and_convert_webp(url):
    resp = requests.get(url, headers=HEADERS_INAT, timeout=30)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if w > WEBP_WIDTH:
        new_h = int(h * (WEBP_WIDTH / w))
        img = img.resize((WEBP_WIDTH, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=WEBP_QUALITY)
    return buf.getvalue()

def main():
    parser = argparse.ArgumentParser(description="Fetch crustacean photos from iNaturalist")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not download/upload")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of species to process")
    args = parser.parse_args()

    print("=" * 80)
    print(f"🦐 FETCH INATURALIST PHOTOS CHO BỘ SƯU TẬP [{COLLECTION}]")
    print(f"   • Dry run: {args.dry_run}")
    print(f"   • Giới hạn: {args.limit if args.limit > 0 else 'Toàn bộ'}")
    print("=" * 80)

    # 1. Lấy danh sách loài giáp xác chưa có ảnh
    species_list = supa_get(
        "species",
        {
            "collection_id": f"eq.{COLLECTION}",
            "order": "species_index",
            "select": "id,species_index,scientific_name,vn_name,photo_url,worms_accepted_name",
        }
    )

    targets = [s for s in species_list if not s.get("photo_url") or not s["photo_url"].strip()]
    print(f"✓ Tổng số loài trong {COLLECTION}: {len(species_list)}")
    print(f"✓ Số loài chưa có ảnh: {len(targets)}")

    if args.limit > 0:
        targets = targets[:args.limit]
        print(f"✓ Giới hạn xử lý: {len(targets)} loài")

    success_count = 0
    not_found_count = 0

    for i, sp in enumerate(targets, 1):
        sid = sp["id"]
        sci = sp["scientific_name"]
        vn = sp.get("vn_name", "")
        worms_acc = sp.get("worms_accepted_name")

        candidates = generate_search_candidates(sci, worms_acc)
        print(f"\n[{i}/{len(targets)}] {sid}: {vn} ({sci})")
        print(f"   -> Ứng viên tìm kiếm: {candidates}")

        taxon_id, matched_name, obs_cnt = find_taxon_for_species(candidates)
        if not taxon_id:
            print(f"   ❌ Không tìm thấy loài trên iNaturalist")
            not_found_count += 1
            continue

        print(f"   ✅ Khớp: '{matched_name}' (Taxon ID: {taxon_id}, {obs_cnt} quan sát)")

        # Tìm ảnh ưu tiên Việt Nam trước, toàn cầu sau
        photos = fetch_observations(taxon_id, place_id=VIETNAM_PLACE_ID, max_photos=MAX_PHOTOS_PER_SPECIES)
        if not photos:
            photos = fetch_observations(taxon_id, place_id=None, max_photos=MAX_PHOTOS_PER_SPECIES)

        if not photos:
            print(f"   ⚠️ Có quan sát nhưng không có ảnh giấy phép mở (CC-BY, CC-BY-NC, CC0)")
            not_found_count += 1
            continue

        print(f"   📸 Tìm thấy {len(photos)} ảnh CC hợp lệ:")
        for p in photos:
            print(f"      - ID {p['photo_id']} bởi {p['photographer']} ({p['license']})")

        if args.dry_run:
            success_count += 1
            continue

        # Tải, nén và upload lên Supabase Storage
        uploaded_photos = []
        for p_idx, p in enumerate(photos, 1):
            try:
                storage_path = f"{COLLECTION}/{sid}/{p['photo_id']}.webp"
                webp_bytes = download_and_convert_webp(p["photo_url"])
                supa_upload(storage_path, webp_bytes)
                public_url = supa_public_url(storage_path)

                photo_record = {
                    "id": str(uuid.uuid4()),
                    "species_id": sid,
                    "storage_path": storage_path,
                    "source": "inaturalist",
                    "photographer": p["photographer"],
                    "license": p["license"],
                    "source_url": p["obs_url"],
                    "inat_photo_id": p["photo_id"],
                    "is_primary": (p_idx == 1),
                    "sort_order": p_idx,
                }
                supa_post("species_photos", photo_record)
                uploaded_photos.append(public_url)
                print(f"      ✓ Đã lưu ảnh {p_idx} vào Storage & DB")
            except Exception as e:
                print(f"      [!] Lỗi xử lý ảnh {p['photo_id']}: {e}")

        # Cập nhật photo_url cho species nếu có ảnh đầu tiên
        if uploaded_photos:
            try:
                supa_patch(f"species?id=eq.{sid}", {"photo_url": uploaded_photos[0]})
                print(f"   ⭐ Cập nhật photo_url đại diện thành công!")
                success_count += 1
            except Exception as e:
                print(f"   [!] Lỗi cập nhật species.photo_url: {e}")

    print("\n" + "=" * 80)
    print(f"📊 TỔNG KẾT CHIẾN DỊCH TẢI ẢNH GIÁP XÁC:")
    print(f"   • Đã xử lý: {len(targets)} loài")
    print(f"   • Bổ sung ảnh thành công: {success_count} loài")
    print(f"   • Không tìm thấy ảnh CC: {not_found_count} loài")
    print("=" * 80)

if __name__ == "__main__":
    main()
