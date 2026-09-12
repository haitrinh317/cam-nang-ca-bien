#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/execute_merge_snakes.py
-------------------------------
Thực thi hợp nhất toàn diện dữ liệu cho 27 loài Rắn biển Việt Nam:
1. Gộp tài liệu dẫn (Sách Rắn biển 2016 + Sách Độc biển 2021 + trích dẫn phân loại gốc)
2. Nạp dữ liệu độc học lâm sàng (toxicology: cơ chế, triệu chứng, phác đồ sơ cứu)
3. Hợp nhất tên gọi khác (vn_alternate_names), kích thước song ngữ
4. Đồng bộ ảnh thực địa từ sách Độc biển vào thư viện ảnh species_photos của Rắn biển
5. Đồng bộ ngược thông tin hợp nhất sang 23 bản ghi sinhvatdoc để đảm bảo tính nhất quán
6. Ghi nhật ký vào bảng audit_log
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    for f in ['.env.local', '.env']:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

BOOK_RANBIEN_VI = "Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng, Phan Kim Hồng, Võ Văn Quang, John C. Murphy, 2016. Rắn biển Việt Nam. Viện Hải dương học Nha Trang, WAR, IOC VN."
BOOK_RANBIEN_EN = "Cao Van Nguyen et al., 2016. Sea Snakes in Vietnam. Institute of Oceanography Nha Trang, WAR, IOC VN."

BOOK_SINHVATDOC_VI = "PGS.TS. Đào Việt Hà (Chủ biên), 2021. Động vật độc biển Việt Nam. NXB Khoa học Tự nhiên và Công nghệ."
BOOK_SINHVATDOC_EN = "Dao Viet Ha (Editor-in-Chief), 2021. Marine Toxic Animals of Vietnam. Publishing House for Science and Technology."

def merge_literatures(*lit_strings):
    items = []
    seen = set()
    for s in lit_strings:
        if not s:
            continue
        for raw_item in s.split(';'):
            clean = raw_item.strip()
            if not clean:
                continue
            norm = clean.rstrip('.').lower()
            if norm not in seen:
                seen.add(norm)
                items.append(clean)
    return "; ".join(items)

def main():
    print("=== BẮT ĐẦU HỢP NHẤT DỮ LIỆU RẮN BIỂN (PHASE 1) ===")
    
    # 1. Fetch data
    req_rb = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.ran-bien&select=*&order=species_index', headers=headers)
    with urllib.request.urlopen(req_rb) as r:
        rb_list = json.loads(r.read().decode())

    req_svd = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.sinh-vat-doc&species_index=gte.25&species_index=lte.47&select=*&order=species_index', headers=headers)
    with urllib.request.urlopen(req_svd) as r:
        svd_list = json.loads(r.read().decode())

    svd_by_worms = {s['worms_id']: s for s in svd_list if s.get('worms_id')}
    print(f"Đã tải {len(rb_list)} loài Rắn biển và {len(svd_list)} loài Độc biển tương ứng.")

    now_iso = datetime.now(timezone.utc).isoformat()
    updated_rb_count = 0
    updated_svd_count = 0
    photos_added = 0

    for rb in rb_list:
        wid = rb.get('worms_id')
        svd = svd_by_worms.get(wid)
        sp_id = rb['id']
        
        # Merge Literature
        orig_rb_lit = rb.get('vn_literature') or ''
        if svd:
            merged_vn_lit = merge_literatures(BOOK_RANBIEN_VI, BOOK_SINHVATDOC_VI, orig_rb_lit)
            merged_en_lit = f"{BOOK_RANBIEN_EN}; {BOOK_SINHVATDOC_EN}"
        else:
            merged_vn_lit = merge_literatures(BOOK_RANBIEN_VI, orig_rb_lit)
            merged_en_lit = BOOK_RANBIEN_EN
            
        # Merge Biology (Toxicology)
        merged_bio = dict(rb.get('biology') or {})
        if svd and 'toxicology' in (svd.get('biology') or {}):
            merged_bio['toxicology'] = svd['biology']['toxicology']
            
        # Merge Alternate Names
        existing_alt = [x.strip() for x in (rb.get('vn_alternate_names') or '').split(',') if x.strip()]
        svd_alt = [x.strip() for x in ((svd.get('vn_alternate_names') or '') if svd else '').split(',') if x.strip()]
        if svd and svd.get('vn_name'):
            svd_alt.append(svd['vn_name'].strip())
            
        all_alt = []
        seen_alt = set()
        for name in existing_alt + svd_alt:
            low = name.lower()
            if low not in seen_alt and low != rb['vn_name'].lower():
                seen_alt.add(low)
                all_alt.append(name)
        merged_alt = ", ".join(all_alt)
        
        # Merge Sizes
        merged_vn_size = rb.get('vn_size') or (svd.get('vn_size') if svd else '') or ''
        merged_en_size = rb.get('en_size') or (svd.get('en_size') if svd else '') or ''
        
        # Patch RB
        rb_payload = {
            'vn_literature': merged_vn_lit,
            'en_literature': merged_en_lit,
            'biology': merged_bio,
            'vn_alternate_names': merged_alt,
            'vn_size': merged_vn_size,
            'en_size': merged_en_size,
            'updated_at': now_iso
        }
        req_patch_rb = urllib.request.Request(
            f'{url}/rest/v1/species?id=eq.{sp_id}',
            data=json.dumps(rb_payload).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        with urllib.request.urlopen(req_patch_rb) as r:
            pass
        updated_rb_count += 1
        
        # If matched SVD: also sync merged fields to SVD row & add photo to RB
        if svd:
            svd_id = svd['id']
            svd_payload = {
                'vn_literature': merged_vn_lit,
                'en_literature': merged_en_lit,
                'biology': merged_bio,
                'vn_alternate_names': merged_alt,
                'vn_size': merged_vn_size,
                'en_size': merged_en_size,
                'updated_at': now_iso
            }
            req_patch_svd = urllib.request.Request(
                f'{url}/rest/v1/species?id=eq.{svd_id}',
                data=json.dumps(svd_payload).encode('utf-8'),
                headers=headers,
                method='PATCH'
            )
            with urllib.request.urlopen(req_patch_svd) as r:
                pass
            updated_svd_count += 1
            
            # Check and link photo from SVD into RB species_photos
            svd_storage_path = f"sinh-vat-doc/{svd_id}/01.webp"
            check_photo_req = urllib.request.Request(
                f'{url}/rest/v1/species_photos?species_id=eq.{sp_id}&storage_path=like.*{svd_id}*',
                headers=headers
            )
            with urllib.request.urlopen(check_photo_req) as r:
                existing_p = json.loads(r.read().decode())
                
            if not existing_p:
                new_photo = {
                    'species_id': sp_id,
                    'storage_path': svd_storage_path,
                    'source': 'book_scan',
                    'photographer': svd.get('biology', {}).get('toxicology', {}).get('photographer') or 'Cao Văn Nguyện',
                    'license': 'educational',
                    'source_url': 'https://cam-nang-ca-bien.vercel.app/sinh-vat-doc',
                    'is_primary': False,
                    'sort_order': 1,
                    'created_at': now_iso
                }
                insert_photo_req = urllib.request.Request(
                    f'{url}/rest/v1/species_photos',
                    data=json.dumps(new_photo).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                try:
                    with urllib.request.urlopen(insert_photo_req) as r:
                        photos_added += 1
                except Exception as ex:
                    print(f"  ✗ Lỗi thêm ảnh cho {sp_id}: {ex}")

        print(f"  ✓ Đã merge: #{rb['species_index']:2d} {rb['scientific_name']} ({rb['vn_name']}) {'[+ SVD]' if svd else '[RB only]'}")

    # 3. Create Audit Log
    audit_payload = {
        'user_email': 'haitrinh082@gmail.com',
        'action': 'merge_species',
        'details': f'Hợp nhất tri thức 23 loài rắn biển trùng lặp giữa Sách Rắn biển (2016) và Sách Động vật độc biển (2021): chuẩn hóa Tài liệu dẫn đa nguồn, tích hợp độc tố học lâm sàng (toxicology), tên gọi khác và ảnh thực địa.'
    }
    audit_req = urllib.request.Request(
        f'{url}/rest/v1/audit_log',
        data=json.dumps(audit_payload).encode('utf-8'),
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Prefer': 'return=minimal'},
        method='POST'
    )
    with urllib.request.urlopen(audit_req) as r:
        pass

    print(f"\n✅ HOÀN TẤT GIAI ĐOẠN 1:")
    print(f"  • Cập nhật bản ghi Rắn biển: {updated_rb_count}/27 loài")
    print(f"  • Đồng bộ bản ghi Độc biển tương ứng: {updated_svd_count}/23 loài")
    print(f"  • Bổ sung ảnh thực địa vào thư viện Rắn biển: {photos_added} ảnh")
    print(f"  • Đã ghi nhật ký audit_log.")

if __name__ == '__main__':
    main()
