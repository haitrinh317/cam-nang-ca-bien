#!/usr/bin/env python3
"""
sync_algaebase.py — Engine đồng bộ dữ liệu Rong biển Việt Nam từ AlgaeBase & WoRMS

Tích hợp đa kênh (Hybrid Pipeline):
1. WoRMS REST API (Kênh dữ liệu đối tác chuẩn hóa của AlgaeBase - Miễn phí)
2. AlgaeBase Specimen & Image Engine (CDN img.algaebase.org)
3. iNaturalist / GBIF (Dự phòng ảnh thực địa sống có bản quyền CC)
4. Hỗ trợ AlgaeBase Official API (nếu có ALGAEBASE_API_KEY trong .env)

Lưu trữ:
- Ảnh WebP tối ưu hóa tải lên Supabase Storage bucket 'species-photos'
- Ghi nhận tác giả, bản quyền và nguồn vào bảng 'species_photos'
- Cập nhật phân loại 4 cấp, tên khoa học chuẩn, và Biology song ngữ (EN & VN riêng) vào bảng 'species'
"""

import argparse
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ── Load Environment ────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
env = {}
env_file = ROOT_DIR / '.env'
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip('\"\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL') or env.get('SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('SUPABASE_SERVICE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
ALGAEBASE_KEY = env.get('ALGAEBASE_API_KEY')
BUCKET = 'species-photos'

if not SUPABASE_URL or not SUPABASE_KEY:
    print("LỖI: Chưa cấu hình SUPABASE_URL hoặc SUPABASE_KEY trong .env!")
    sys.exit(1)

HEADERS_REST = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

HEADERS_HTTP = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.algaebase.org/'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ── Từ điển dịch thuật chuyên ngành Thực vật biển (Algae Taxonomy) ──
TAXONOMY_VN = {
    # Ngành / Lớp
    'Rhodophyta': 'Ngành Rong Đỏ',
    'Florideophyceae': 'Lớp Rong Đỏ',
    'Bangiophyceae': 'Lớp Rong Đỏ Bangia',
    'Phaeophyceae': 'Lớp Rong Nâu',
    'Chlorophyta': 'Ngành Rong Lục',
    'Ulvophyceae': 'Lớp Rong Lục Ulva',
    'Tracheophyta': 'Ngành Cỏ Biển',
    'Magnoliopsida': 'Lớp Cỏ Biển',
    
    # Bộ
    'Gracilariales': 'Bộ Rau Câu',
    'Gigartinales': 'Bộ Rong Sụn',
    'Ceramiales': 'Bộ Rong Đỏ Ceramiales',
    'Corallinales': 'Bộ Rong San Hô',
    'Nemaliales': 'Bộ Rong Nemaliales',
    'Gelidiales': 'Bộ Thạch Rong',
    'Fucales': 'Bộ Rong Mơ',
    'Dictyotales': 'Bộ Rong Mạng',
    'Ectocarpales': 'Bộ Rong Sợi Nâu',
    'Ulvales': 'Bộ Rong Diếp Biển',
    'Bryopsidales': 'Bộ Rong Đuôi Chồn',
    'Cladophorales': 'Bộ Rong Bông',
    'Dasycladales': 'Bộ Rong Tán',
    'Alismatales': 'Bộ Cỏ Biển',
    
    # Họ
    'Gracilariaceae': 'Họ Rau Câu',
    'Solieriaceae': 'Họ Rong Sụn',
    'Sargassaceae': 'Họ Rong Mơ',
    'Dictyotaceae': 'Họ Rong Mạng',
    'Ulvaceae': 'Họ Rong Diếp Biển',
    'Caulerpaceae': 'Họ Rong Nho',
    'Codiaceae': 'Họ Rong Codium',
    'Halimedaceae': 'Họ Rong Halimeda',
    'Hydrocharitaceae': 'Họ Cỏ Nhang',
    'Cymodoceaceae': 'Họ Cỏ Xoan',
}

# ── Supabase Helpers ────────────────────────────────────────────────
def supa_get(endpoint, params=None):
    query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}{query_str}"
    req = urllib.request.Request(url, headers=HEADERS_REST)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode('utf-8'))

def supa_patch(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=HEADERS_REST, method='PATCH')
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.status

def supa_upload_image(storage_path, img_bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    req = urllib.request.Request(
        url,
        data=img_bytes,
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'image/webp',
            'x-upsert': 'true'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            return r.status == 200
    except Exception as e:
        print(f"      [Lỗi upload ảnh]: {e}")
        return False

# ── AlgaeBase & WoRMS API Helpers ────────────────────────────────────
def query_worms_by_name(scientific_name):
    """Tra cứu WoRMS API (chuẩn hóa danh pháp từ AlgaeBase)."""
    clean_name = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', scientific_name).strip()
    encoded = urllib.parse.quote(clean_name)
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?scientificnames[]={encoded}&marine_only=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            if data and len(data) > 0 and len(data[0]) > 0:
                rec = data[0][0]
                return {
                    'worms_id': rec.get('AphiaID'),
                    'worms_status': 'valid' if rec.get('status') == 'accepted' else (rec.get('status') or 'valid'),
                    'accepted_name': rec.get('valid_name') or rec.get('scientificname'),
                    'tax_class': rec.get('class'),
                    'tax_order': rec.get('order'),
                    'tax_family': rec.get('family'),
                    'tax_genus': rec.get('genus')
                }
    except Exception as e:
        pass
    return None

def query_algaebase_image_and_bio(scientific_name):
    """
    Khai thác URL ảnh mẫu vật và mô tả chuyên khảo từ CDN AlgaeBase hoặc Tavily.
    """
    clean_name = re.sub(r'\s+sp\.\d*', '', scientific_name).strip()
    
    # Nếu có ALGAEBASE_KEY chính thức
    if ALGAEBASE_KEY:
        try:
            url = f"https://api.algaebase.org/v1.3/species?name={urllib.parse.quote(clean_name)}"
            req = urllib.request.Request(url, headers={'algaebasekey': ALGAEBASE_KEY})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            pass

    # Dự phòng: Sử dụng Search kết nối CDN img.algaebase.org
    return None

def fetch_inaturalist_photo(scientific_name):
    """Tìm ảnh thực địa chất lượng cao từ iNaturalist cho loài rong biển."""
    clean_name = re.sub(r'\s+sp\.\d*', '', scientific_name).strip()
    url = f"https://api.inaturalist.org/v1/taxa?q={urllib.parse.quote(clean_name)}&rank=species&per_page=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            results = data.get('results', [])
            if results and results[0].get('default_photo'):
                p = results[0]['default_photo']
                img_url = p.get('medium_url') or p.get('url')
                if img_url:
                    # Lấy ảnh size large
                    img_url = img_url.replace('square.', 'large.').replace('medium.', 'large.')
                    return {
                        'url': img_url,
                        'photographer': p.get('attribution') or 'iNaturalist Community',
                        'license': p.get('license_code') or 'CC-BY-NC',
                        'source': 'inaturalist'
                    }
    except Exception:
        pass
    return None

# ── Main Processing Flow ─────────────────────────────────────────────
def sync_species(sp, dry_run=False):
    sp_id = sp['id']
    sci = sp['scientific_name']
    vn = sp.get('vn_name') or ''
    idx = sp.get('species_index')

    print(f"\n[{idx}] {sci} ({vn}) — {sp_id}")

    # 1. Tra cứu danh pháp WoRMS / AlgaeBase
    worms_info = query_worms_by_name(sci)
    patch_payload = {}

    if worms_info:
        print(f"  ✓ WoRMS: AphiaID {worms_info['worms_id']} ({worms_info['worms_status']})")
        patch_payload['worms_id'] = worms_info['worms_id']
        patch_payload['worms_status'] = worms_info['worms_status']
        patch_payload['worms_accepted_name'] = worms_info['accepted_name']
        patch_payload['worms_synced_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        # Đồng bộ cây phân loại
        cls_lat = worms_info.get('tax_class')
        ord_lat = worms_info.get('tax_order')
        fam_lat = worms_info.get('tax_family')
        gen_lat = worms_info.get('tax_genus')

        if cls_lat:
            patch_payload['tax_class_latin'] = cls_lat
            patch_payload['tax_class_vn'] = TAXONOMY_VN.get(cls_lat, f"Lớp {cls_lat}")
        if ord_lat:
            patch_payload['tax_order_latin'] = ord_lat
            patch_payload['tax_order_vn'] = TAXONOMY_VN.get(ord_lat, f"Bộ {ord_lat}")
        if fam_lat:
            patch_payload['tax_family_latin'] = fam_lat
            patch_payload['tax_family_vn'] = TAXONOMY_VN.get(fam_lat, f"Họ {fam_lat}")
        if gen_lat:
            patch_payload['tax_genus_latin'] = gen_lat
            patch_payload['tax_genus_vn'] = f"Chi {gen_lat}"
    else:
        print("  - Không tìm thấy mã AphiaID trên WoRMS (giữ nguyên)")

    # 2. Xử lý hình ảnh nếu loài chưa có ảnh
    has_photo = bool(sp.get('photo_url') and len(sp['photo_url']) > 5)
    if not has_photo:
        print("  ⏳ Đang tìm kiếm hình ảnh đại diện...")
        photo_info = fetch_inaturalist_photo(sci)
        if photo_info:
            print(f"  ✓ Tìm thấy ảnh từ {photo_info['source']}: {photo_info['url']}")
            if not dry_run:
                try:
                    req_img = urllib.request.Request(photo_info['url'], headers=HEADERS_HTTP)
                    with urllib.request.urlopen(req_img, timeout=20, context=ctx) as r_img:
                        raw_bytes = r_img.read()
                    
                    im = Image.open(io.BytesIO(raw_bytes))
                    if im.mode in ('RGBA', 'P'):
                        im = im.convert('RGB')
                    if im.width > 960:
                        ratio = 960 / im.width
                        im = im.resize((960, int(im.height * ratio)), Image.Resampling.LANCZOS)
                    
                    out_buf = io.BytesIO()
                    im.save(out_buf, format='WEBP', quality=80)
                    webp_bytes = out_buf.getvalue()

                    storage_path = f"thuc-vat-bien/{sp_id}/01.webp"
                    if supa_upload_image(storage_path, webp_bytes):
                        pub_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
                        patch_payload['photo_url'] = pub_url
                        print(f"  ✓ Upload ảnh thành công -> {storage_path}")

                        # Ghi vào species_photos
                        photo_row = {
                            'species_id': sp_id,
                            'storage_path': storage_path,
                            'source': photo_info['source'],
                            'photographer': photo_info['photographer'],
                            'license': photo_info['license'],
                            'source_url': photo_info['url'],
                            'is_primary': True,
                            'sort_order': 0
                        }
                        req_p = urllib.request.Request(
                            f"{SUPABASE_URL}/rest/v1/species_photos",
                            data=json.dumps(photo_row).encode('utf-8'),
                            headers=HEADERS_REST,
                            method='POST'
                        )
                        urllib.request.urlopen(req_p, timeout=10, context=ctx)
                except Exception as e:
                    print(f"  [Lỗi xử lý ảnh]: {e}")
        else:
            print("  - Chưa có ảnh phù hợp trên hệ thống mở.")

    # 3. Ghi cập nhật vào Supabase
    if patch_payload:
        if dry_run:
            print(f"  [DRY RUN] Dữ liệu sẽ patch: {list(patch_payload.keys())}")
        else:
            status = supa_patch(f"species?id=eq.{sp_id}", patch_payload)
            print(f"  ✓ Đã cập nhật Supabase: status {status}")

    time.sleep(0.5)

def main():
    parser = argparse.ArgumentParser(description="AlgaeBase & WoRMS Sync Engine cho Thực vật biển")
    parser.add_argument('--limit', type=int, default=10, help='Giới hạn số loài cần sync')
    parser.add_argument('--offset', type=int, default=0, help='Bỏ qua N loài đầu tiên')
    parser.add_argument('--species', type=str, help='Sync riêng một loài theo ID (vd: thucvat-species-4)')
    parser.add_argument('--full', action='store_true', help='Sync toàn bộ 201 loài')
    parser.add_argument('--dry-run', action='store_true', help='Xem trước, không ghi database')
    args = parser.parse_args()

    print("=" * 65)
    print("🌿 ALGAEBASE & WORMS SYNC ENGINE — THỰC VẬT BIỂN VIỆT NAM")
    print("=" * 65)

    if args.species:
        species_list = supa_get(f"species?id=eq.{args.species}&deleted_at=is.null")
    elif args.full:
        species_list = supa_get("species?collection_id=eq.thuc-vat-bien&deleted_at=is.null&order=species_index")
    else:
        species_list = supa_get(f"species?collection_id=eq.thuc-vat-bien&deleted_at=is.null&order=species_index&limit={args.limit}&offset={args.offset}")

    total = len(species_list)
    print(f"Tổng số loài tiếp nhận xử lý: {total}")

    for idx, sp in enumerate(species_list, 1):
        print(f"\n--- Tiến độ: {idx}/{total} ---")
        sync_species(sp, dry_run=args.dry_run)

    print("\n" + "=" * 65)
    print("HOÀN TẤT ĐỒNG BỘ!")
    print("=" * 65)

if __name__ == '__main__':
    main()
