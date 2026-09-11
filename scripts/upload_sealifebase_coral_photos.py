#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_sealifebase_coral_photos.py
-----------------------------------
Tải ảnh khoa học từ SeaLifeBase (mirror sealifebase.se), nén WebP
và upload lên Supabase Storage bucket `species-photos`, ghi metadata vào `species_photos`.
"""

import os, sys, json, io, uuid, urllib.request
import requests
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

env_file = '.env.local' if os.path.exists('.env.local') else '.env'
env = {}
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k] = v.strip('\"').strip('\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
BUCKET = "species-photos"

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}'
}

def download_and_convert_webp(url, max_width=640, quality=75):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")
    w, h = im.size
    if w > max_width:
        new_h = int(h * (max_width / w))
        im = im.resize((max_width, new_h), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="WEBP", quality=quality)
    return buf.getvalue()

def upload_supabase_storage(path, file_bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"
    headers = {
        'apikey': KEY,
        'Authorization': f'Bearer {KEY}',
        'Content-Type': 'image/webp',
        'x-upsert': 'true'
    }
    resp = requests.post(url, headers=headers, data=file_bytes, timeout=30)
    resp.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"

def main():
    json_path = '/Users/macbook2016/.gemini/antigravity-ide/brain/0c721b9c-d53e-418b-a401-d01c07e77efd/scratch/sanho_slb_photos.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        slb_data = json.load(f)
        
    print(f"=== BẮT ĐẦU TẢI ẢNH KHOA HỌC SEALIFEBASE ===")
    total_uploaded = 0
    
    for sp_id, photos in slb_data.items():
        selected = [p for p in photos if p['picName'].endswith('.jpg')][:2]
        if not selected:
            selected = photos[:2]
            
        print(f"\nLoài {sp_id}: {len(selected)} ảnh...")
        first_url = None
        
        for idx, p in enumerate(selected):
            pic_name = p['picName']
            auth_name = p['authName'] or "SeaLifeBase"
            remark = p.get('remark') or "SeaLifeBase Scientific Mirror"
            
            img_url = f"https://www.sealifebase.se/images/species/{pic_name}"
            print(f"  • Đang tải: {img_url}...", end=" ", flush=True)
            
            try:
                webp_bytes = download_and_convert_webp(img_url)
                photo_uuid = str(uuid.uuid4())
                storage_path = f"san-ho/{sp_id}/{idx+1:02d}.webp"
                public_url = upload_supabase_storage(storage_path, webp_bytes)
                
                if idx == 0:
                    first_url = public_url
                    
                photo_record = {
                    "id": photo_uuid,
                    "species_id": sp_id,
                    "storage_path": storage_path,
                    "source": "sealifebase",
                    "photographer": auth_name,
                    "license": "cc-by",
                    "source_url": img_url,
                    "is_primary": (idx == 0),
                    "sort_order": idx
                }
                
                insert_url = f"{SUPABASE_URL}/rest/v1/species_photos"
                resp = requests.post(insert_url, headers={**HEADERS, 'Content-Type': 'application/json'}, json=photo_record)
                resp.raise_for_status()
                
                print(f"✅ WebP ({len(webp_bytes)//1024} KB) -> Storage")
                total_uploaded += 1
            except Exception as e:
                print(f"❌ Lỗi: {e}")
                
        if first_url:
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            requests.patch(patch_url, headers={**HEADERS, 'Content-Type': 'application/json'}, json={"photo_url": first_url})
            print(f"  ⭐ Đã gán ảnh đại diện cho {sp_id}!")

    print(f"\n🎉 Hoàn thành upload {total_uploaded} ảnh SeaLifeBase lên Supabase Storage!")

if __name__ == '__main__':
    main()
