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
    'Content-Type': 'application/json'
}

# Fetch all ran-bien species
req_rb = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.ran-bien&select=*&order=species_index', headers=headers)
with urllib.request.urlopen(req_rb) as r:
    rb_list = json.loads(r.read().decode())

# Fetch all sinh-vat-doc species (only 25-47)
req_svd = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.sinh-vat-doc&species_index=gte.25&species_index=lte.47&select=*&order=species_index', headers=headers)
with urllib.request.urlopen(req_svd) as r:
    svd_list = json.loads(r.read().decode())

print(f"Loaded {len(rb_list)} ran-bien species and {len(svd_list)} sinh-vat-doc snake species.")

# Map SVD snakes by worms_id
svd_by_worms = {s['worms_id']: s for s in svd_list if s.get('worms_id')}

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

plan = []
for rb in rb_list:
    wid = rb.get('worms_id')
    svd = svd_by_worms.get(wid)
    
    # 1. Literature
    orig_rb_lit = rb.get('vn_literature') or ''
    if svd:
        merged_vn_lit = merge_literatures(BOOK_RANBIEN_VI, BOOK_SINHVATDOC_VI, orig_rb_lit)
        merged_en_lit = f"{BOOK_RANBIEN_EN}; {BOOK_SINHVATDOC_EN}"
    else:
        merged_vn_lit = merge_literatures(BOOK_RANBIEN_VI, orig_rb_lit)
        merged_en_lit = BOOK_RANBIEN_EN
        
    # 2. Biology & Toxicology
    merged_bio = dict(rb.get('biology') or {})
    if svd and 'toxicology' in (svd.get('biology') or {}):
        merged_bio['toxicology'] = svd['biology']['toxicology']
        
    # 3. Alternate names
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
    
    # 4. Sizes
    merged_vn_size = rb.get('vn_size') or (svd.get('vn_size') if svd else '') or ''
    merged_en_size = rb.get('en_size') or (svd.get('en_size') if svd else '') or ''
    
    # 5. SVD photo path
    svd_photo_path = f"sinh-vat-doc/{svd['id']}/01.webp" if svd else None
    
    plan.append({
        'rb_id': rb['id'],
        'rb_index': rb['species_index'],
        'scientific_name': rb['scientific_name'],
        'vn_name': rb['vn_name'],
        'has_svd_match': svd is not None,
        'svd_id': svd['id'] if svd else None,
        'svd_index': svd['species_index'] if svd else None,
        'svd_vn_name': svd['vn_name'] if svd else None,
        'merged_vn_lit': merged_vn_lit,
        'merged_en_lit': merged_en_lit,
        'has_toxicology': 'toxicology' in merged_bio,
        'merged_alt': merged_alt,
        'merged_vn_size': merged_vn_size,
        'svd_photo_path': svd_photo_path,
        'merged_bio': merged_bio
    })

print("\n=== BẢNG TỔNG KẾT KẾ HOẠCH MERGE CHO 27 LOÀI RẮN BIỂN ===")
for p in plan:
    status = f"MATCH SVD #{p['svd_index']}" if p['has_svd_match'] else "SÁCH RẮN DUY NHẤT (NO SVD)"
    print(f"#{p['rb_index']:2d} | {p['rb_id']:18s} | {p['scientific_name']:28s} | {status:28s} | Độc học: {str(p['has_toxicology']):5s} | Tên khác: {p['merged_alt'][:30]}")
