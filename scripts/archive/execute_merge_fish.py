#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/execute_merge_fish.py
-----------------------------
Thực thi Giai đoạn 2: Hợp nhất tri thức Đa Nguồn cho nhóm Cá biển độc giữa:
- Bộ sách "Danh mục Cá biển Việt Nam" (Tập I, III, V) & "Atlas Cá rạn san hô Việt Nam" (Tập VI)
- Chuyên khảo "Động vật độc biển Việt Nam" (PGS.TS. Đào Việt Hà, 2021)

Xử lý:
1. 17 loài cá độc trùng khớp 1-1 (16 loài cá nóc + 1 loài cá hồng Lutjanus bohar)
2. Chuẩn hóa tài liệu dẫn cho 8 taxa cá độc còn lại (cấp Chi & ghi nhận mới)
3. Tích hợp độc tố học lâm sàng (Tetrodotoxin, Ciguatoxin, triệu chứng, sơ cứu) vào ca-bien
4. Bổ sung ảnh thực địa vào thư viện species_photos của cá biển
5. Đồng bộ 2 chiều sang sinh-vat-doc và ghi audit_log
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

BOOK_TITLES_VI = {
    1: "GS. Nguyễn Khắc Hường, 1992. Danh mục Cá biển Việt Nam — Tập I: Cá Nhám, Cá Đuối, Cá Trích, Cá Chình. NXB Nông nghiệp.",
    2: "GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi, 1994. Danh mục Cá biển Việt Nam — Tập II. NXB Nông nghiệp.",
    3: "GS. Nguyễn Khắc Hường, 2000. Danh mục Cá biển Việt Nam — Tập III: Cá Hồng, Cá Mú, Cá Đù, Cá Mối. NXB Nông nghiệp.",
    4: "TS. Nguyễn Nhật Thi, 2004. Danh mục Cá biển Việt Nam — Tập IV: Cá Bướm, Cá Thiên nga, Cá Tai tượng. NXB Nông nghiệp.",
    5: "TS. Nguyễn Nhật Thi, 2007. Danh mục Cá biển Việt Nam — Tập V: Cá Bống, Cá Bơn, Cá Nóc, Cá Cóc biển. NXB Nông nghiệp.",
    6: "TS. Đỗ Thị Cát Tường, 2020. Atlas Cá rạn san hô Việt Nam (Tập VI). NXB Khoa học Tự nhiên và Công nghệ."
}

BOOK_TITLES_EN = {
    1: "Nguyen Khac Huong, 1992. Check-list of Marine Fishes of Vietnam — Vol. I. Agricultural Publishing House.",
    2: "Nguyen Khac Huong & Nguyen Nhat Thi, 1994. Check-list of Marine Fishes of Vietnam — Vol. II. Agricultural Publishing House.",
    3: "Nguyen Khac Huong, 2000. Check-list of Marine Fishes of Vietnam — Vol. III. Agricultural Publishing House.",
    4: "Nguyen Nhat Thi, 2004. Check-list of Marine Fishes of Vietnam — Vol. IV. Agricultural Publishing House.",
    5: "Nguyen Nhat Thi, 2007. Check-list of Marine Fishes of Vietnam — Vol. V. Agricultural Publishing House.",
    6: "Do Thi Cat Tuong, 2020. Atlas of Coral Reef Fishes of Vietnam (Vol. VI). Publishing House for Science and Technology."
}

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
    print("=== BẮT ĐẦU HỢP NHẤT DỮ LIỆU CÁ BIỂN ĐỘC (GIAI ĐOẠN 2) ===")
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Import matching logic from check_fish_overlap
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from check_fish_overlap import matches, unmatched
    
    print(f"Có {len(matches)} loài cá độc trùng khớp 1-1 và {len(unmatched)} taxa cá độc độc bản.")
    
    updated_cb_count = 0
    updated_svd_count = 0
    photos_added = 0
    
    # --- PHẦN 1: HỢP NHẤT 17 LOÀI CÁ ĐỘC TRÙNG KHỚP 1-1 ---
    for idx, (sf, cb_list, m_type) in enumerate(matches, 1):
        svd_id = sf['id']
        svd_bio = sf.get('biology') or {}
        toxicology_data = svd_bio.get('toxicology')
        
        # 1. Gather all books across all matched ca-bien records + toxic book
        books_vi = []
        books_en = []
        for c in cb_list:
            vol = c.get('volume')
            b_vi = BOOK_TITLES_VI.get(vol, f"Danh mục Cá biển Việt Nam Tập {vol}")
            b_en = BOOK_TITLES_EN.get(vol, f"Check-list of Marine Fishes of Vietnam Vol. {vol}")
            books_vi.append(b_vi)
            books_en.append(b_en)
            
        unique_books_vi = list(dict.fromkeys(books_vi)) + [BOOK_SINHVATDOC_VI]
        unique_books_en = list(dict.fromkeys(books_en)) + [BOOK_SINHVATDOC_EN]
        
        # 2. Gather alternate names
        all_alt_names = []
        seen_alt = set()
        for c in cb_list + [sf]:
            raw_alt = c.get('vn_alternate_names') or ''
            for part in raw_alt.split(','):
                p = part.strip()
                if p and p.lower() not in seen_alt:
                    seen_alt.add(p.lower())
                    all_alt_names.append(p)
            # also include vn_name if different
            vn_n = c.get('vn_name', '').strip()
            if vn_n and vn_n.lower() not in seen_alt:
                seen_alt.add(vn_n.lower())
                all_alt_names.append(vn_n)
                
        # 3. Process each ca-bien record
        for c in cb_list:
            cb_id = c['id']
            cb_orig_lit = c.get('vn_literature') or ''
            
            # Combine books + original historical citations
            merged_vn_lit = merge_literatures(*unique_books_vi, cb_orig_lit)
            merged_en_lit = "; ".join(unique_books_en)
            
            # Alternate names without this species's own primary vn_name
            cb_alt = [name for name in all_alt_names if name.lower() != (c.get('vn_name') or '').lower()]
            merged_alt_str = ", ".join(cb_alt)
            
            # Merge biology with toxicology
            cb_bio = dict(c.get('biology') or {})
            if toxicology_data:
                cb_bio['toxicology'] = toxicology_data
                
            # Update ca-bien record in Supabase
            patch_payload = {
                'vn_literature': merged_vn_lit,
                'en_literature': merged_en_lit,
                'biology': cb_bio,
                'vn_alternate_names': merged_alt_str,
                'updated_at': now_iso
            }
            req_patch = urllib.request.Request(
                f'{url}/rest/v1/species?id=eq.{cb_id}',
                data=json.dumps(patch_payload).encode('utf-8'),
                headers=headers,
                method='PATCH'
            )
            with urllib.request.urlopen(req_patch) as r:
                pass
            updated_cb_count += 1
            
            # 4. Link photo from SVD to this ca-bien record if exists
            svd_photo_path = f"sinh-vat-doc/{svd_id}/01.webp"
            check_photo_req = urllib.request.Request(
                f'{url}/rest/v1/species_photos?species_id=eq.{cb_id}&storage_path=like.*{svd_id}*',
                headers=headers
            )
            with urllib.request.urlopen(check_photo_req) as r:
                existing_p = json.loads(r.read().decode())
                
            if not existing_p:
                photographer = toxicology_data.get('photographer') if toxicology_data else 'Trần Thị Hồng Hoa'
                new_photo = {
                    'species_id': cb_id,
                    'storage_path': svd_photo_path,
                    'source': 'book_scan',
                    'photographer': photographer or 'Trần Thị Hồng Hoa',
                    'license': 'educational',
                    'source_url': 'https://cam-nang-ca-bien.vercel.app/sinh-vat-doc',
                    'is_primary': False,
                    'sort_order': 2,
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
                    print(f"  ✗ Lỗi thêm ảnh cho {cb_id}: {ex}")
                    
        # 5. Synchronize back to SVD record
        svd_alt = [name for name in all_alt_names if name.lower() != (sf.get('vn_name') or '').lower()]
        svd_patch_payload = {
            'vn_literature': merge_literatures(*unique_books_vi, sf.get('vn_literature') or ''),
            'en_literature': "; ".join(unique_books_en),
            'vn_alternate_names': ", ".join(svd_alt),
            'updated_at': now_iso
        }
        req_patch_svd = urllib.request.Request(
            f'{url}/rest/v1/species?id=eq.{svd_id}',
            data=json.dumps(svd_patch_payload).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        with urllib.request.urlopen(req_patch_svd) as r:
            pass
        updated_svd_count += 1
        
        print(f"  ✓ Đã merge #{idx:2d}: SVD #{sf['species_index']:2d} {sf['scientific_name']} ({sf['vn_name']}) -> {len(cb_list)} bản ghi cá biển")

    # --- PHẦN 2: CHUẨN HÓA TÀI LIỆU DẪN CHO 8 TAXA CÁ ĐỘC ĐỘC BẢN ---
    for sf in unmatched:
        svd_id = sf['id']
        cur_lit = sf.get('vn_literature') or ''
        clean_lit = merge_literatures(BOOK_SINHVATDOC_VI, cur_lit)
        req_unmatched = urllib.request.Request(
            f'{url}/rest/v1/species?id=eq.{svd_id}',
            data=json.dumps({'vn_literature': clean_lit, 'en_literature': BOOK_SINHVATDOC_EN, 'updated_at': now_iso}).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        with urllib.request.urlopen(req_unmatched) as r:
            pass
        updated_svd_count += 1
        print(f"  ✓ Chuẩn hóa tài liệu dẫn: SVD #{sf['species_index']:2d} {sf['scientific_name']} ({sf['vn_name']})")

    # --- PHẦN 3: GHI NHẬT KÝ AUDIT LOG ---
    audit_payload = {
        'user_email': 'haitrinh082@gmail.com',
        'action': 'merge_species_fish',
        'details': f'Giai đoạn 2: Hợp nhất tri thức 17 loài cá biển độc trùng lặp giữa Danh mục Cá biển (Tập I, III, V), Atlas Tập VI và Sách Động vật độc biển (2021). Chuẩn hóa tài liệu dẫn đa nguồn, nạp độc tố học lâm sàng (Tetrodotoxin/Ciguatera) và bổ sung {photos_added} ảnh thực địa vào thư viện cá biển.'
    }
    audit_req = urllib.request.Request(
        f'{url}/rest/v1/audit_log',
        data=json.dumps(audit_payload).encode('utf-8'),
        headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Prefer': 'return=minimal'},
        method='POST'
    )
    with urllib.request.urlopen(audit_req) as r:
        pass

    print(f"\n✅ HOÀN TẤT GIAI ĐOẠN 2 (CÁ BIỂN ĐỘC):")
    print(f"  • Cập nhật bản ghi Cá biển (ca-bien): {updated_cb_count} bản ghi (thuộc Tập I, III, V, VI)")
    print(f"  • Đồng bộ và chuẩn hóa bản ghi Độc biển (sinh-vat-doc): {updated_svd_count}/25 taxa")
    print(f"  • Bổ sung ảnh thực địa vào thư viện Cá biển: {photos_added} ảnh")
    print(f"  • Đã ghi nhật ký audit_log.")

if __name__ == '__main__':
    main()
