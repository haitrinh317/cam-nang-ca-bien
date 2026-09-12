#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/pilot_merge_snake_1.py
------------------------------
Thử nghiệm hợp nhất dữ liệu cho loài Rắn biển #1 (Aipysurus eydouxii):
- Gộp tài liệu dẫn (Sách Rắn biển 2016 + Sách Độc biển 2021 + trích dẫn gốc)
- Nạp khối độc tố học lâm sàng (toxicology: cơ chế, triệu chứng, phác đồ sơ cứu)
- Bổ sung tên gọi khác, kích thước song ngữ
- Thêm ảnh thực địa từ sách Độc biển vào thư viện ảnh species_photos
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

# 1. Fetch ranbien-species-1 & sinhvatdoc-species-25
req_r1 = urllib.request.Request(f'{url}/rest/v1/species?id=eq.ranbien-species-1', headers=headers)
with urllib.request.urlopen(req_r1) as r:
    r1 = json.loads(r.read().decode())[0]

req_s25 = urllib.request.Request(f'{url}/rest/v1/species?id=eq.sinhvatdoc-species-25', headers=headers)
with urllib.request.urlopen(req_s25) as r:
    s25 = json.loads(r.read().decode())[0]

print("=== TRƯỚC KHI MERGE ===")
print(f"Species: {r1['scientific_name']} ({r1['vn_name']})")
print("r1 vn_literature:", r1.get('vn_literature'))
print("r1 biology keys:", list((r1.get('biology') or {}).keys()))

# 2. Build Merged Fields
BOOK_RANBIEN_VI = "Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng, Phan Kim Hồng, Võ Văn Quang, John C. Murphy, 2016. Rắn biển Việt Nam. Viện Hải dương học Nha Trang, WAR, IOC VN."
BOOK_RANBIEN_EN = "Cao Van Nguyen et al., 2016. Sea Snakes in Vietnam. Institute of Oceanography Nha Trang, WAR, IOC VN."

BOOK_SINHVATDOC_VI = "PGS.TS. Đào Việt Hà (Chủ biên), 2021. Động vật độc biển Việt Nam. NXB Khoa học Tự nhiên và Công nghệ."
BOOK_SINHVATDOC_EN = "Dao Viet Ha (Editor-in-Chief), 2021. Marine Toxic Animals of Vietnam. Publishing House for Science and Technology."

# Literature VI
existing_r1_lit = r1.get('vn_literature') or ''
lit_parts = [BOOK_RANBIEN_VI, BOOK_SINHVATDOC_VI]
if existing_r1_lit and existing_r1_lit != BOOK_RANBIEN_VI:
    lit_parts.append(existing_r1_lit)
merged_vn_literature = "; ".join(lit_parts)

# Literature EN
merged_en_literature = f"{BOOK_RANBIEN_EN}; {BOOK_SINHVATDOC_EN}"

# Biology merge (add toxicology)
merged_biology = dict(r1.get('biology') or {})
s25_bio = s25.get('biology') or {}
if 'toxicology' in s25_bio:
    merged_biology['toxicology'] = s25_bio['toxicology']

# Alternate names
existing_alt = [x.strip() for x in (r1.get('vn_alternate_names') or '').split(',') if x.strip()]
s25_alt = [x.strip() for x in (s25.get('vn_alternate_names') or '').split(',') if x.strip()]
all_alt = []
seen = set()
for name in existing_alt + s25_alt:
    low = name.lower()
    if low not in seen and low != r1['vn_name'].lower():
        seen.add(low)
        all_alt.append(name)
merged_alt_names = ", ".join(all_alt)

# Sizes
merged_vn_size = r1.get('vn_size') or s25.get('vn_size') or ''
merged_en_size = r1.get('en_size') or s25.get('en_size') or ''

# 3. Update ranbien-species-1 in Supabase
update_payload = {
    'vn_literature': merged_vn_literature,
    'en_literature': merged_en_literature,
    'biology': merged_biology,
    'vn_alternate_names': merged_alt_names,
    'vn_size': merged_vn_size,
    'en_size': merged_en_size,
    'updated_at': datetime.now(timezone.utc).isoformat()
}

req_update = urllib.request.Request(
    f'{url}/rest/v1/species?id=eq.ranbien-species-1',
    data=json.dumps(update_payload).encode('utf-8'),
    headers=headers,
    method='PATCH'
)
with urllib.request.urlopen(req_update) as r:
    updated_r1 = json.loads(r.read().decode())[0]

# 4. Add photo from sinhvatdoc to species_photos for ranbien-species-1
check_photo_req = urllib.request.Request(
    f'{url}/rest/v1/species_photos?species_id=eq.ranbien-species-1&storage_path=like.*sinh-vat-doc*',
    headers=headers
)
with urllib.request.urlopen(check_photo_req) as r:
    existing_photos = json.loads(r.read().decode())

photo_added = False
if not existing_photos:
    new_photo = {
        'species_id': 'ranbien-species-1',
        'storage_path': 'sinh-vat-doc/sinhvatdoc-species-25/01.webp',
        'source': 'book_scan',
        'photographer': 'Cao Văn Nguyện',
        'license': 'educational',
        'source_url': 'https://cam-nang-ca-bien.vercel.app/sinh-vat-doc',
        'is_primary': False,
        'sort_order': 1,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    insert_photo_req = urllib.request.Request(
        f'{url}/rest/v1/species_photos',
        data=json.dumps(new_photo).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(insert_photo_req) as r:
        photo_added = True

print("\n=== SAU KHI MERGE ===")
print("vn_literature:\n", updated_r1.get('vn_literature'))
print("\nbiology has toxicology:", 'toxicology' in updated_r1.get('biology', {}))
print("toxicology danger_level:", updated_r1.get('biology', {}).get('toxicology', {}).get('danger_level_vn'))
print("vn_alternate_names:", updated_r1.get('vn_alternate_names'))
print("vn_size:", updated_r1.get('vn_size'))
print("Photo from sinh-vat-doc added?:", photo_added or "Đã có từ trước")
