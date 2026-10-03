#!/usr/bin/env python3
"""
scripts/fix_mola_mola_photos.py
Khắc phục lỗi gắn nhầm ảnh cây thực vật (Liquidambar styraciflua) cho Cá mặt trăng (Mola mola - tap5-species-263).
Tải và thay thế bằng 3 ảnh chụp Research-Grade thực thụ của Mola mola (Taxon ID 49601) trên iNaturalist.
"""

import os
import sys
import uuid
import io
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET = "species-photos"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

SPECIES_ID = "tap5-species-263"
COLLECTION = "ca-bien"

# Danh sách 3 ảnh Research-Grade xuất sắc nhất của Mola mola (Taxon 49601) trên iNaturalist
CURATED_PHOTOS = [
    {
        "photo_id": 33024055,
        "obs_id": 21351835,
        "obs_url": "https://www.inaturalist.org/observations/21351835",
        "url": "https://inaturalist-open-data.s3.amazonaws.com/photos/33024055/large.jpg",
        "photographer": "rfoster",
        "license": "cc-by-nc",
        "is_primary": True,
    },
    {
        "photo_id": 452875560,
        "obs_id": 252963288,
        "obs_url": "https://www.inaturalist.org/observations/252963288",
        "url": "https://inaturalist-open-data.s3.amazonaws.com/photos/452875560/large.jpeg",
        "photographer": "zachfrat",
        "license": "cc-by-nc",
        "is_primary": False,
    },
    {
        "photo_id": 396400934,
        "obs_id": 223698837,
        "obs_url": "https://www.inaturalist.org/observations/223698837",
        "url": "https://inaturalist-open-data.s3.amazonaws.com/photos/396400934/large.jpeg",
        "photographer": "legallais",
        "license": "cc-by-nc",
        "is_primary": False,
    }
]


def convert_to_webp(image_bytes, max_size=800, quality=80):
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Resize nếu lớn hơn max_size
    w, h = img.size
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    
    out = io.BytesIO()
    img.save(out, format="WEBP", quality=quality)
    return out.getvalue()


def supa_upload(path, file_bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/webp",
        "x-upsert": "true",
    }
    resp = requests.post(url, headers=headers, data=file_bytes, timeout=60)
    resp.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"


def main():
    print(f"🌊 Đang xử lý làm sạch và cập nhật ảnh cho loài: {SPECIES_ID} (Cá mặt trăng - Mola mola)")

    # 1. Xóa các bản ghi ảnh cũ bị nhầm trong species_photos
    print("1. Xóa bản ghi ảnh cũ bị nhầm trong CSDL...")
    del_url = f"{SUPABASE_URL}/rest/v1/species_photos?species_id=eq.{SPECIES_ID}"
    del_resp = requests.delete(del_url, headers=HEADERS_SUPA)
    print(f"   Status delete: {del_resp.status_code}")

    # 2. Tải và upload từng ảnh Mola mola chuẩn xác
    primary_url = None
    for idx, item in enumerate(CURATED_PHOTOS):
        print(f"2.{idx+1} Tải ảnh {item['photo_id']} từ {item['url']}...")
        dl_resp = requests.get(item['url'], headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        dl_resp.raise_for_status()
        
        webp_bytes = convert_to_webp(dl_resp.content)
        storage_path = f"{COLLECTION}/{SPECIES_ID}/{idx+1:02d}.webp"
        
        print(f"   Upload lên Storage: {storage_path} ({len(webp_bytes)//1024} KB)...")
        pub_url = supa_upload(storage_path, webp_bytes)
        if item["is_primary"]:
            primary_url = pub_url

        # 3. Ghi vào species_photos
        record = {
            "id": str(uuid.uuid4()),
            "species_id": SPECIES_ID,
            "storage_path": storage_path,
            "source": "inaturalist",
            "photographer": item["photographer"],
            "license": item["license"],
            "source_url": item["obs_url"],
            "inat_photo_id": item["photo_id"],
            "is_primary": item["is_primary"],
            "sort_order": idx,
        }
        post_url = f"{SUPABASE_URL}/rest/v1/species_photos"
        post_resp = requests.post(post_url, headers={**HEADERS_SUPA, "Prefer": "return=representation"}, json=record)
        post_resp.raise_for_status()
        print(f"   ✅ Đã lưu metadata ảnh {idx+1}")

    # 4. Cập nhật photo_url trong bảng species
    if primary_url:
        print(f"4. Cập nhật photo_url cho loài {SPECIES_ID}...")
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{SPECIES_ID}"
        patch_resp = requests.patch(patch_url, headers=HEADERS_SUPA, json={"photo_url": primary_url})
        print(f"   Status patch species: {patch_resp.status_code}")

    print("🎉 Hoàn tất khắc phục! Đã cập nhật 3 ảnh Mola mola chuẩn xác 100%.")

if __name__ == "__main__":
    main()
