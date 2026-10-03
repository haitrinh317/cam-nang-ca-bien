"""
scripts/sync_iucn_status.py
----------------------------
Đồng bộ chỉ số Sách Đỏ Quốc Tế (IUCN Red List status & IUCN Taxon ID) 
từ IUCN / GBIF cho toàn bộ loài sinh vật biển trong database Supabase.

Nguồn dữ liệu:
  1. GBIF Official IUCN Red List Checklist & Category Endpoint:
     - https://api.gbif.org/v1/species/match?name={scientific_name}
     - https://api.gbif.org/v1/species/{usageKey}/iucnRedListCategory
  2. Bóc tách dữ liệu có sẵn trong OCR của các bộ sưu tập đặc thù (VD: ran-bien).

Trường cập nhật trong species.biology (JSONB):
  - iucnStatus  : 'CR' | 'EN' | 'VU' | 'NT' | 'LC' | 'DD' | 'EW' | 'EX'
  - iucnTaxonId : Taxon ID chính thức trên IUCN Red List (để tạo link trực tiếp)

Cách dùng:
  python3 scripts/sync_iucn_status.py --dry-run
  python3 scripts/sync_iucn_status.py --collection ran-bien
  python3 scripts/sync_iucn_status.py --collection giap-xac
  python3 scripts/sync_iucn_status.py
"""

import os
import sys
import re
import json
import time
import argparse
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Lỗi: Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env!", flush=True)
    sys.exit(1)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

VALID_IUCN_CODES = {'CR', 'EN', 'VU', 'NT', 'LC', 'DD', 'EW', 'EX'}

VN_OCR_IUCN_MAP = {
    'ít liên quan': 'LC',
    'ít quan tâm': 'LC',
    'thiếu dữ liệu': 'DD',
    'thiếu dẫn liệu': 'DD',
    'sắp nguy cấp': 'VU',
    'sẽ nguy cấp': 'VU',
    'bị tổn thương': 'VU',
    'nguy cấp': 'EN',
    'cực kỳ nguy cấp': 'CR',
    'tuyệt chủng ngoài tự nhiên': 'EW',
    'tuyệt chủng': 'EX',
    'gần bị đe dọa': 'NT'
}

def extract_iucn_from_ocr(vn_status: str | None) -> str | None:
    """Bóc tách mã IUCN từ trường văn bản vn_status OCR (ví dụ bộ sưu tập rắn biển)"""
    if not vn_status:
        return None
    m = re.search(r'IUCN:\s*([^\.,;\n]+)', vn_status, re.IGNORECASE)
    if not m:
        return None
    raw_status = m.group(1).strip().lower()
    for phrase, code in VN_OCR_IUCN_MAP.items():
        if phrase in raw_status:
            return code
    return None

def fetch_single_species_iucn(session: requests.Session, scientific_name: str, accepted_name: str | None = None) -> tuple[str | None, str | None]:
    """
    Tra cứu GBIF API để lấy IUCN status và iucnTaxonID.
    Trả về: (code, iucnTaxonID)
    """
    clean_sci = " ".join(scientific_name.strip().split()[:2])
    clean_acc = " ".join(accepted_name.strip().split()[:2]) if accepted_name else None

    names_to_try = [clean_sci]
    if clean_acc and clean_acc != clean_sci:
        names_to_try.append(clean_acc)

    for name in names_to_try:
        try:
            r = session.get(
                'https://api.gbif.org/v1/species/match',
                params={'name': name},
                timeout=5
            )
            if r.status_code != 200:
                continue
            data = r.json()
            usage_key = data.get('usageKey') or data.get('speciesKey')
            if not usage_key:
                continue

            r2 = session.get(
                f'https://api.gbif.org/v1/species/{usage_key}/iucnRedListCategory',
                timeout=5
            )
            if r2.status_code != 200:
                continue
            iucn_data = r2.json()
            code = (iucn_data.get('code') or '').upper().strip()
            taxon_id = iucn_data.get('iucnTaxonID')
            if taxon_id:
                taxon_id = str(taxon_id).split('_')[0]

            if code in VALID_IUCN_CODES:
                return code, taxon_id
        except Exception:
            continue
        
    return None, None

def process_species_item(sp: dict, session: requests.Session, dry_run: bool) -> dict:
    sp_id = sp['id']
    sci_name = sp.get('scientific_name', '')
    accepted_name = sp.get('worms_accepted_name')
    vn_status = sp.get('vn_status')
    bio = sp.get('biology') or {}
    if isinstance(bio, str):
        try: bio = json.loads(bio)
        except: bio = {}

    existing_iucn = bio.get('iucnStatus')
    existing_taxon_id = bio.get('iucnTaxonId')

    # 1. Tra cứu GBIF
    gbif_code, gbif_taxon_id = fetch_single_species_iucn(session, sci_name, accepted_name)
    # 2. Bóc tách OCR dự phòng
    ocr_code = extract_iucn_from_ocr(vn_status)

    final_code = gbif_code or ocr_code
    final_taxon_id = gbif_taxon_id

    result = {
        'id': sp_id,
        'scientific_name': sci_name,
        'code': final_code,
        'taxon_id': final_taxon_id,
        'source': 'GBIF' if gbif_code else ('OCR' if ocr_code else None),
        'updated': False,
        'error': None
    }

    if final_code:
        is_changed = (final_code != existing_iucn) or (final_taxon_id and final_taxon_id != existing_taxon_id)
        if is_changed:
            if not dry_run:
                bio['iucnStatus'] = final_code
                if final_taxon_id:
                    bio['iucnTaxonId'] = final_taxon_id
                
                patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
                try:
                    resp = session.patch(patch_url, json={"biology": bio}, headers=HEADERS, timeout=8)
                    if resp.status_code in (200, 204):
                        result['updated'] = True
                    else:
                        result['error'] = f"PATCH HTTP {resp.status_code}"
                except Exception as pe:
                    result['error'] = str(pe)
            else:
                result['updated'] = True

    return result

def main():
    parser = argparse.ArgumentParser(description="Đồng bộ IUCN Red List status vào database")
    parser.add_argument('--collection', type=str, default=None, help="Chỉ xử lý collection cụ thể")
    parser.add_argument('--limit', type=int, default=None, help="Giới hạn số loài xử lý")
    parser.add_argument('--force', action='store_true', help="Quét lại cả loài đã có iucnStatus")
    parser.add_argument('--dry-run', action='store_true', help="Chạy thử nghiệm không ghi vào DB")
    parser.add_argument('--workers', type=int, default=6, help="Số luồng đồng thời (mặc định 6)")
    args = parser.parse_args()

    print("══════════════════════════════════════════════════════════════════════", flush=True)
    print("  ĐỒNG BỘ IUCN RED LIST STATUS VÀO SUPABASE DATABASE", flush=True)
    print("══════════════════════════════════════════════════════════════════════", flush=True)
    if args.dry_run:
        print("  ⚠️  CHẾ ĐỘ CHẠY THỬ (DRY-RUN) — Không ghi đè Supabase", flush=True)
    if args.collection:
        print(f"  🎯 Bộ sưu tập: {args.collection}", flush=True)
    print(f"  ⚡ Luồng xử lý (Concurrency): {args.workers}", flush=True)
    print(flush=True)

    main_session = requests.Session()
    main_session.headers.update({'User-Agent': 'VietnamMarineBiodiversity/2.0'})

    limit_batch = 1000
    offset = 0
    all_species = []

    while True:
        url = f"{SUPABASE_URL}/rest/v1/species?select=id,collection_id,scientific_name,worms_accepted_name,vn_status,biology&order=id.asc&limit={limit_batch}&offset={offset}"
        if args.collection:
            url += f"&collection_id=eq.{args.collection}"
        
        try:
            r = main_session.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                print(f"❌ Lỗi HTTP {r.status_code}: {r.text}", flush=True)
                sys.exit(1)
            batch = r.json()
            if not batch:
                break
            all_species.extend(batch)
            offset += len(batch)
            if len(batch) < limit_batch:
                break
        except Exception as e:
            print(f"❌ Lỗi tải dữ liệu Supabase: {e}", flush=True)
            sys.exit(1)

    print(f"📦 Đã tải {len(all_species)} loài từ Supabase.", flush=True)

    to_process = []
    for sp in all_species:
        bio = sp.get('biology') or {}
        if isinstance(bio, str):
            try: bio = json.loads(bio)
            except: bio = {}
        
        has_iucn = bool(bio.get('iucnStatus'))
        if not has_iucn or args.force:
            to_process.append(sp)

    print(f"🔍 Số loài cần kiểm tra/bổ sung IUCN: {len(to_process)}", flush=True)
    if args.limit:
        to_process = to_process[:args.limit]
        print(f"⚡ Giới hạn xử lý: {args.limit} loài", flush=True)

    print("-" * 70, flush=True)

    updated_count = 0
    found_count = 0
    not_found_count = 0
    completed = 0
    total = len(to_process)

    def worker_task(species_item):
        s = requests.Session()
        s.headers.update({'User-Agent': 'VietnamMarineBiodiversity/2.0'})
        return process_species_item(species_item, s, args.dry_run)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(worker_task, sp): sp for sp in to_process}
        for future in as_completed(futures):
            completed += 1
            res = future.result()
            if res['code']:
                found_count += 1
                if res['updated']:
                    updated_count += 1
                sis_str = f" (SIS #{res['taxon_id']})" if res['taxon_id'] else ""
                print(f"[{completed}/{total}] ✅ {res['id']} | {res['scientific_name']} -> IUCN: {res['code']}{sis_str} [{res['source']}]", flush=True)
            else:
                not_found_count += 1
                if completed % 25 == 0 or completed == total:
                    print(f"[{completed}/{total}] ℹ️ Đang quét... ({found_count} tìm thấy, {not_found_count} chưa có / NE)", flush=True)

    elapsed = time.time() - start_time
    print("══════════════════════════════════════════════════════════════════════", flush=True)
    print(f"🎉 HOÀN TẤT ĐỒNG BỘ IUCN RED LIST TRONG {elapsed:.1f} GIÂY:", flush=True)
    print(f"  • Tổng loài đã quét: {total}", flush=True)
    print(f"  • Tìm thấy thông tin IUCN: {found_count} loài", flush=True)
    print(f"  • Chưa có trong IUCN / Chưa đánh giá (NE): {not_found_count} loài", flush=True)
    print(f"  • {'Dự kiến cập nhật' if args.dry_run else 'Đã cập nhật vào Supabase'}: {updated_count} loài", flush=True)
    print("══════════════════════════════════════════════════════════════════════", flush=True)

if __name__ == '__main__':
    main()
