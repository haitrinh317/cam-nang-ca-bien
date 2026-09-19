#!/usr/bin/env python3
"""
upload_dvpd_photos.py
Tải 103 ảnh vi thể WebP lên Supabase Storage bucket 'species-photos'
và đồng bộ metadata vào bảng species_photos.
"""

import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
BUCKET = 'species-photos'

INPUT_JSON = 'scratch/dvpd_atlat_enriched_worms.json'
WEBP_DIR = 'scratch/dvpd_webp'
OUTPUT_JSON = 'scratch/dvpd_atlat_with_photos.json'

def upload_file_to_storage(local_path, storage_path):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'image/webp',
        'x-upsert': 'true'
    }
    with open(local_path, 'rb') as f:
        data = f.read()
        
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
    except urllib.error.HTTPError as e:
        print(f"  [!] Lỗi upload HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"  [!] Lỗi upload {storage_path}: {e}")
    return None

def main():
    print(f"[*] Đọc danh sách loài từ {INPUT_JSON}...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    uploaded_count = 0
    total_sp = len(species_list)

    for idx, sp in enumerate(species_list, 1):
        sp_id = sp['id']
        sci_name = sp['scientific_name']
        images = sp.get('images', [])
        
        photo_records = []
        primary_url = None

        if images:
            for s_idx, img_fname in enumerate(images, 1):
                base_name = os.path.splitext(img_fname)[0]
                webp_file = os.path.join(WEBP_DIR, f"{base_name}.webp")
                
                if os.path.exists(webp_file):
                    storage_path = f"dong-vat-phu-du/{sp_id}/{base_name}.webp"
                    pub_url = upload_file_to_storage(webp_file, storage_path)
                    
                    if pub_url:
                        uploaded_count += 1
                        if not primary_url:
                            primary_url = pub_url
                            
                        # Tạo caption học thuật
                        spec_info = f" (Mẫu {', '.join(sp['specimens'])})" if sp.get('specimens') else ""
                        cap_info = sp['captions'][s_idx-1] if len(sp.get('captions', [])) >= s_idx else f"Tiêu bản {sci_name}{spec_info}"
                        
                        photo_records.append({
                            'species_id': sp_id,
                            'photo_url': pub_url,
                            'caption': cap_info,
                            'source': 'Atlat Động vật phù du 2016–2019 (VNMN)',
                            'photographer': 'TS. Trương Sĩ Hải Trình & CS / Bảo tàng Thiên nhiên Việt Nam (VNMN)',
                            'license': 'VNMN Academic Research',
                            'is_primary': (s_idx == 1),
                            'sort_order': s_idx
                        })
                        print(f"[{idx}/{total_sp}] ✓ Đã tải ảnh ({s_idx}/{len(images)}) cho {sci_name}")
                else:
                    print(f"[{idx}/{total_sp}] ⚠ Không tìm thấy {webp_file}")
                    
        sp['photo_url'] = primary_url
        sp['photos'] = photo_records

    # Lưu kết quả
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(species_list, f, ensure_ascii=False, indent=2)

    print("\n" + "="*50)
    print(f"=== TỔNG KẾT UPLOAD ẢNH VI THỂ ===")
    print(f"• Tổng số ảnh đã tải lên Storage: {uploaded_count}/103")
    print(f"• File enriched lưu tại: {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
