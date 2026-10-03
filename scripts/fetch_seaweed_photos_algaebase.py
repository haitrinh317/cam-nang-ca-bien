#!/usr/bin/env python3
"""
fetch_seaweed_photos_algaebase.py — Tự Động Bổ Sung Ảnh Cho Các Loài Rong Biển Còn Thiếu (v2 Tối Ưu)

Nguồn dữ liệu ưu tiên:
1. GBIF (Global Biodiversity Information Facility) — Mẫu tiêu bản đại thể & ảnh thực địa từ các viện bảo tàng
2. Wikimedia Commons / Wikipedia — Tranh tiêu bản kinh điển & ảnh thực địa CC
3. iNaturalist API — Tra cứu theo tên đồng nghĩa / tên danh pháp hợp lệ WoRMS

Tối ưu hóa:
- socket.setdefaulttimeout(10) chống nghẽn mạng
- Tự động thay thế 'original.jpg' thành 'large.jpg' để tải nhanh hơn gấp 10 lần
- Chuyển đổi WebP (960px max width, quality 80)
- Tải lên Supabase Storage bucket 'species-photos/thuc-vat-bien/{id}/01.webp'
- Ghi vào bảng 'species_photos' với tác giả, giấy phép, nguồn
- Cập nhật 'species.photo_url'
"""

import io
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

socket.setdefaulttimeout(12)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent

# 1. Đọc môi trường
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
BUCKET = 'species-photos'

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

def supa_get(endpoint, params=None):
    query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}{query_str}"
    req = urllib.request.Request(url, headers=HEADERS_REST)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return json.loads(r.read().decode('utf-8'))

def supa_patch(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=HEADERS_REST, method='PATCH')
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
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
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            return r.status == 200
    except Exception as e:
        print(f"      [Lỗi upload ảnh]: {e}", flush=True)
        return False

# ── 2. Các hàm tìm kiếm ảnh đa nguồn ─────────────────────────────────

def search_gbif(scientific_name):
    """Tìm kiếm ảnh tiêu bản hoặc ảnh thực địa từ GBIF."""
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={urllib.parse.quote(scientific_name)}&mediaType=StillImage&limit=5"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            for occ in data.get('results', []):
                for m in occ.get('media', []):
                    if m.get('type') == 'StillImage' and m.get('identifier'):
                        img_url = m['identifier']
                        # Tránh các trang xem ảnh API phức tạp hoặc server treo
                        if any(bad in img_url for bad in ('quod.lib.umich.edu', 'oxalis.br.fgov.be', 'symbiota.org', 'editedimages.s3-accelerate.amazonaws.com')):
                            continue
                        if any(img_url.lower().endswith(ext) or ext in img_url.lower() for ext in ('.jpg', '.jpeg', '.png', '.webp')):
                            # Tối ưu kích thước nếu là iNaturalist S3
                            img_url = img_url.replace('/original.', '/large.')
                            return {
                                'url': img_url,
                                'photographer': m.get('rightsHolder') or occ.get('publisher') or occ.get('institutionCode') or 'GBIF Herbarium Collection',
                                'license': m.get('license') or 'CC-BY',
                                'source': 'gbif'
                            }
    except Exception:
        pass
    return None

def search_inaturalist(scientific_name):
    """Tìm ảnh thực địa từ iNaturalist."""
    url = f"https://api.inaturalist.org/v1/taxa?q={urllib.parse.quote(scientific_name)}&per_page=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            results = data.get('results', [])
            if results and results[0].get('default_photo'):
                p = results[0]['default_photo']
                img_url = p.get('medium_url') or p.get('url')
                if img_url:
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

def search_wikimedia(scientific_name):
    """Tìm ảnh tiêu bản / tranh minh họa khoa học từ Wikimedia Commons."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(scientific_name)}&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json&gsrlimit=3"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                ii = p.get('imageinfo', [])
                if ii and ii[0].get('url'):
                    img_url = ii[0]['url']
                    if any(img_url.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp')):
                        meta = ii[0].get('extmetadata', {})
                        artist = meta.get('Artist', {}).get('value', 'Wikimedia Commons')
                        artist = re.sub(r'<[^>]+>', '', artist).strip()[:60]
                        lic = meta.get('LicenseShortName', {}).get('value', 'CC BY-SA')
                        return {
                            'url': img_url,
                            'photographer': artist or 'Wikimedia Commons',
                            'license': lic or 'Public Domain',
                            'source': 'wikimedia'
                        }
    except Exception:
        pass
    return None

def download_and_process_image(img_url):
    """Tải ảnh, kiểm tra tính hợp lệ và nén WebP 960px chất lượng 80."""
    try:
        # Nếu là iNaturalist original, đổi thành large để tải siêu nhanh
        if '/original.' in img_url:
            img_url = img_url.replace('/original.', '/large.')

        req = urllib.request.Request(img_url, headers=HEADERS_HTTP)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            raw_bytes = r.read()

        im = Image.open(io.BytesIO(raw_bytes))
        if im.mode in ('RGBA', 'P'):
            im = im.convert('RGB')
        if im.width > 960:
            ratio = 960 / im.width
            im = im.resize((960, int(im.height * ratio)), Image.Resampling.LANCZOS)

        out_buf = io.BytesIO()
        im.save(out_buf, format='WEBP', quality=80)
        return out_buf.getvalue()
    except Exception as e:
        return None

# ── 3. Main Loop ──────────────────────────────────────────────────────

def main():
    print("=" * 65, flush=True)
    print("🌿 TIẾN TRÌNH TỰ ĐỘNG BỔ SUNG ẢNH THỰC VẬT BIỂN (ALGAEBASE & HERBARIUM)", flush=True)
    print("=" * 65, flush=True)

    species_list = supa_get("species?collection_id=eq.thuc-vat-bien&deleted_at=is.null&order=species_index")
    missing = [s for s in species_list if not s.get('photo_url') or len(s['photo_url']) <= 5]

    total = len(missing)
    print(f"Tổng số loài chưa có ảnh cần tìm: {total} / {len(species_list)}\n", flush=True)

    success_count = 0

    for idx, sp in enumerate(missing, 1):
        sp_id = sp['id']
        sci = sp['scientific_name']
        vn = sp.get('vn_name') or ''
        s_idx = sp.get('species_index')
        accepted = sp.get('worms_accepted_name')

        print(f"[{idx}/{total}] #{s_idx} {sci} ({vn}) — {sp_id}", flush=True)

        names_to_try = [sci]
        if accepted and accepted != sci:
            names_to_try.append(accepted)

        clean_names = []
        for n in names_to_try:
            cn = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', n).strip()
            if cn not in clean_names:
                clean_names.append(cn)

        photo_info = None

        # 1. Thử GBIF (Mẫu tiêu bản & ảnh viện bảo tàng)
        for name in clean_names:
            photo_info = search_gbif(name)
            if photo_info:
                print(f"  ✓ Tìm thấy ảnh từ GBIF ({photo_info['photographer']}): {photo_info['url'][:80]}...", flush=True)
                break

        # 2. Thử Wikimedia Commons (Tranh tiêu bản & ảnh thực địa mở)
        if not photo_info:
            for name in clean_names:
                photo_info = search_wikimedia(name)
                if photo_info:
                    print(f"  ✓ Tìm thấy ảnh từ Wikimedia ({photo_info['photographer']}): {photo_info['url'][:80]}...", flush=True)
                    break

        # 3. Thử iNaturalist với tên hợp lệ
        if not photo_info:
            for name in clean_names:
                photo_info = search_inaturalist(name)
                if photo_info:
                    print(f"  ✓ Tìm thấy ảnh từ iNaturalist ({photo_info['photographer']}): {photo_info['url'][:80]}...", flush=True)
                    break

        if photo_info:
            webp_bytes = download_and_process_image(photo_info['url'])
            if webp_bytes:
                storage_path = f"thuc-vat-bien/{sp_id}/01.webp"
                if supa_upload_image(storage_path, webp_bytes):
                    pub_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
                    
                    # Cập nhật species
                    supa_patch(f"species?id=eq.{sp_id}", {'photo_url': pub_url})
                    
                    # Lưu vào species_photos
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
                    try:
                        req_p = urllib.request.Request(
                            f"{SUPABASE_URL}/rest/v1/species_photos",
                            data=json.dumps(photo_row).encode('utf-8'),
                            headers=HEADERS_REST,
                            method='POST'
                        )
                        urllib.request.urlopen(req_p, timeout=10, context=ctx)
                    except Exception:
                        pass

                    success_count += 1
                    print(f"  🎉 Đã tải lên Supabase Storage và cập nhật URL thành công!", flush=True)
            else:
                print(f"  [Lỗi]: Không thể tải hoặc định dạng ảnh từ {photo_info['url'][:60]}", flush=True)
        else:
            print("  - Không tìm thấy ảnh tiêu bản / thực địa phù hợp", flush=True)

        time.sleep(0.2)

    print("\n" + "=" * 65, flush=True)
    print(f"HOÀN TẤT! ĐÃ BỔ SUNG THÀNH CÔNG: {success_count} / {total} LOÀI", flush=True)
    print("=" * 65, flush=True)

if __name__ == '__main__':
    main()
