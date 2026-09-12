#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/upload_sinhvatdoc_all.py
Upload toàn bộ 76 loài Động vật độc biển Việt Nam và 77 ảnh mẫu vật lên Supabase (SSOT).
"""

import os
import io
import json
import uuid
import urllib.request
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
)

BUCKET = "species-photos"
IMG_DIR = BASE_DIR / "Documents/sinh-vat-doc/sach-sinh-vat-bien-doc/Sách Cô Hà/List hình/List hình"
JSON_PATH = BASE_DIR / "scratch/sinhvatdoc_parsed.json"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def supa_upload(storage_path: str, file_bytes: bytes) -> bool:
    """Tải file lên Supabase Storage bucket."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/webp",
        "x-upsert": "true",
    }
    req = urllib.request.Request(url, headers=headers, data=file_bytes, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"  [ERROR] Upload {storage_path}: {e}")
        return False

def supa_patch_species(species_id: str, public_url: str) -> bool:
    """Cập nhật photo_url vào bảng species."""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{species_id}"
    headers = {**HEADERS_SUPA, "Prefer": "return=minimal"}
    data = json.dumps({"photo_url": public_url}).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, data=data, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"  [ERROR] Patch species {species_id}: {e}")
        return False

def supa_insert_photo_record(species_id: str, storage_path: str, photographer: str, is_primary: bool, sort_order: int) -> bool:
    """Ghi bản ghi vào bảng species_photos."""
    url = f"{SUPABASE_URL}/rest/v1/species_photos"
    headers = {**HEADERS_SUPA, "Prefer": "return=minimal"}
    record = {
        "id": str(uuid.uuid4()),
        "species_id": species_id,
        "storage_path": storage_path,
        "source": "book_scan",
        "photographer": photographer,
        "license": "educational",
        "source_url": "https://cam-nang-ca-bien.vercel.app/sinh-vat-doc",
        "is_primary": is_primary,
        "sort_order": sort_order,
    }
    data = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 201, 204)
    except Exception as e:
        print(f"  [ERROR] Insert photo record {species_id}: {e}")
        return False

def optimize_image_to_webp(img_path: Path, max_dim: int = 1200, quality: int = 85) -> bytes:
    """Đọc ảnh, chuẩn hóa màu, resize và nén sang WebP."""
    with Image.open(img_path) as im:
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        elif im.mode != "RGB":
            im = im.convert("RGB")
            
        w, h = im.size
        if max(w, h) > max_dim:
            if w >= h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        buf = io.BytesIO()
        im.save(buf, format="WEBP", quality=quality, method=6)
        return buf.getvalue()

def main():
    print("==================================================")
    print(" BẮT ĐẦU NẠP 76 LOÀI VÀ 77 ẢNH ĐỘNG VẬT ĐỘC BIỂN ")
    print("==================================================")
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        species_rows = json.load(f)
        
    print(f"Loaded {len(species_rows)} species from {JSON_PATH.name}")
    
    # Bước 1: Upsert toàn bộ 76 loài vào bảng species
    print("\n--- BƯỚC 1: UPSERT 76 LOÀI VÀO BẢNG SPECIES ---")
    url_upsert = f"{SUPABASE_URL}/rest/v1/species"
    headers_upsert = {
        **HEADERS_SUPA,
        "Prefer": "resolution=merge-duplicates",
    }
    
    # Upsert theo batch 20 loài
    batch_size = 20
    for i in range(0, len(species_rows), batch_size):
        batch = species_rows[i:i + batch_size]
        data_batch = json.dumps(batch).encode("utf-8")
        req_batch = urllib.request.Request(url_upsert, headers=headers_upsert, data=data_batch, method="POST")
        with urllib.request.urlopen(req_batch) as resp:
            print(f"  ✓ Upsert batch {i+1} - {min(i+batch_size, len(species_rows))}: status {resp.status}")
            
    print("--> 100% 76 loài đã nạp thành công vào Supabase!")
    
    # Bước 2: Xử lý và upload ảnh lên Storage + Ghi nhận species_photos
    print("\n--- BƯỚC 2: TỐI ƯU WEBP & UPLOAD SUPABASE STORAGE ---")
    uploaded_photos = 0
    
    for s in species_rows:
        species_id = s["id"]
        vn_name = s["vn_name"]
        photographer = s["biology"].get("photographer", "Viện Hải dương học")
        img_files = s["biology"].get("image_files", [])
        
        if not img_files:
            print(f"  ⚠ {species_id} ({vn_name}): Không có file ảnh")
            continue
            
        for photo_idx, filename in enumerate(img_files, 1):
            img_path = IMG_DIR / filename
            if not img_path.exists():
                print(f"  [MISSING] File not found: {img_path}")
                continue
                
            storage_path = f"sinh-vat-doc/{species_id}/{photo_idx:02d}.webp"
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
            
            # Nén WebP
            webp_bytes = optimize_image_to_webp(img_path)
            
            # Upload Storage
            if supa_upload(storage_path, webp_bytes):
                uploaded_photos += 1
                is_primary = (photo_idx == 1)
                
                # Insert photo record
                supa_insert_photo_record(
                    species_id=species_id,
                    storage_path=storage_path,
                    photographer=photographer,
                    is_primary=is_primary,
                    sort_order=photo_idx - 1,
                )
                
                # Patch species photo_url for primary photo
                if is_primary:
                    supa_patch_species(species_id, public_url)
                    
        print(f"  ✓ [{species_id}] {vn_name} ({photographer}) -> {len(img_files)} ảnh uploaded.")
        
    print(f"\n==================================================")
    print(f" HOÀN TẤT: 76 loài & {uploaded_photos} ảnh mẫu vật WebP")
    print(f"==================================================")

if __name__ == "__main__":
    main()
