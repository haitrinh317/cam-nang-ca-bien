#!/usr/bin/env python3
"""
Đồng bộ WoRMS Taxonomy hiện đại (Class, Order, Family, Genus) cho toàn bộ 1,767 loài Cá biển (ca-bien)
Lưu trữ vào trường biology.wormsTaxonomy trong Supabase, bảo toàn dữ liệu sinh học hiện có.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

ENV_FILE = '.env'
CACHE_FILE = '_offline/data/worms_fish_taxonomy_cache.json'

ORDER_VN_DICT = {
    'Perciformes': 'Bộ Cá Vược',
    'Gobiiformes': 'Bộ Cá Bống',
    'Carangiformes': 'Bộ Cá Khế',
    'Acanthuriformes': 'Bộ Cá Đuôi Gai & Cá Bướm',
    'Blenniiformes': 'Bộ Cá Mào Gà',
    'Callionymiformes': 'Bộ Cá Đàn Lia',
    'Apogoniformes': 'Bộ Cá Sơn',
    'Kurtiformes': 'Bộ Cá Sơn & Đồng Minh',
    'Centrarchiformes': 'Bộ Cá Căng & Thái Dương',
    'Labriformes': 'Bộ Cá Bàng Chài',
    'Scombriformes': 'Bộ Cá Thu Ngừ',
    'Uranoscopiformes': 'Bộ Cá Sao',
    'Syngnathiformes': 'Bộ Cá Chìa Vôi & Cá Ngựa',
    'Pleuronectiformes': 'Bộ Cá Bơn',
    'Tetraodontiformes': 'Bộ Cá Nóc',
    'Scorpaeniformes': 'Bộ Cá Mù Làn',
    'Anguilliformes': 'Bộ Cá Chình',
    'Clupeiformes': 'Bộ Cá Trích',
    'Beloniformes': 'Bộ Cá Nhái (Cá Kìm)',
    'Mugiliformes': 'Bộ Cá Đối',
    'Siluriformes': 'Bộ Cá Nheo (Cá Úc, Cá Ngát)',
    'Aulopiformes': 'Bộ Cá Mối Biển',
    'Myctophiformes': 'Bộ Cá Đèn Biển',
    'Batrachoidiformes': 'Bộ Cá Cóc Biển',
    'Lophiiformes': 'Bộ Cá Vảy Chân (Cá Lưỡi Chân)',
    'Beryciformes': 'Bộ Cá Băng Nhi',
    'Holocentriformes': 'Bộ Cá Sơn Đá',
    'Ophidiiformes': 'Bộ Cá Búi Lạc',
    'Atheriniformes': 'Bộ Cá Hàng Bạc',
    'Gadiformes': 'Bộ Cá Tuyết',
    'Elopiformes': 'Bộ Cá Cháo Lớn',
    'Albuliformes': 'Bộ Cá Mòi Đường',
    'Lampriformes': 'Bộ Cá Mặt Trăng Lampris',
    'Polymixiiformes': 'Bộ Cá Râu Răng Gai',
    'Synbranchiformes': 'Bộ Cá Lươn',
    # Chondrichthyes (Cá Sụn)
    'Carcharhiniformes': 'Bộ Cá Mập Mắt Trắng',
    'Orectolobiformes': 'Bộ Cá Nhám Râu',
    'Lamniformes': 'Bộ Cá Mập Chuột',
    'Heterodontiformes': 'Bộ Cá Nhám Mang',
    'Hexanchiformes': 'Bộ Cá Mập Sáu Mang',
    'Squaliformes': 'Bộ Cá Nhám Góc',
    'Squatiniformes': 'Bộ Cá Nhám Dẹt',
    'Pristiophoriformes': 'Bộ Cá Nhám Cưa',
    'Myliobatiformes': 'Bộ Cá Đuối Đại Bàng & Đuối Gai Độc',
    'Rajiformes': 'Bộ Cá Đuối Bút',
    'Rhinopristiformes': 'Bộ Cá Giống & Cá Đuối Cưa',
    'Torpediniformes': 'Bộ Cá Đuối Điện',
    # Ovalentaria & Eupercaria incertae sedis
    'Ovalentaria incertae sedis': 'Bộ Cá Thia (Ovalentaria)',
    'Eupercaria incertae sedis': 'Bộ Cá Vược Thật (Eupercaria)',
    'Teleostei incertae sedis': 'Bộ Cá Xương Thật (Chưa xếp bộ)',
    'Cichliformes': 'Bộ Cá Rô Phi & Cá Thia',
    'Amphioxiformes': 'Bộ Cá Lưỡng Tiêm',
}

CLASS_VN_DICT = {
    'Teleostei': 'Lớp Cá Xương Thật',
    'Actinopterygii': 'Lớp Cá Vây Tia',
    'Elasmobranchii': 'Lớp Cá Sụn Mang Tấm',
    'Holocephali': 'Lớp Cá Toàn Đầu',
    'Leptocardii': 'Lớp Cá Lưỡng Tiêm',
    'Chondrichthyes': 'Lớp Cá Sụn',
    'Osteichthyes': 'Lớp Cá Xương',
}


def load_env():
    supabase_url = ''
    supabase_key = ''
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    if k == 'NEXT_PUBLIC_SUPABASE_URL':
                        supabase_url = v.strip('\"\'')
                    elif k == 'SUPABASE_SERVICE_ROLE_KEY':
                        supabase_key = v.strip('\"\'')
    if not supabase_url or not supabase_key:
        print('Lỗi: Không tìm thấy NEXT_PUBLIC_SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env')
        sys.exit(1)
    return supabase_url, supabase_key


def fetch_all_ca_bien_species(supabase_url, supabase_key):
    print('Đang tải danh sách 1,767 loài cá biển từ Supabase...')
    all_rows = []
    for start in range(0, 3000, 1000):
        url = f'{supabase_url}/rest/v1/species?collection_id=eq.ca-bien&select=id,species_index,volume,scientific_name,tax_class_latin,tax_order_latin,tax_family_latin,tax_family_vn,worms_id,worms_accepted_name,worms_status,biology&order=species_index.asc'
        req = urllib.request.Request(url, headers={
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Range': f'{start}-{start+999}'
        })
        try:
            with urllib.request.urlopen(req) as resp:
                rows = json.loads(resp.read().decode('utf-8'))
                all_rows.extend(rows)
                if len(rows) < 1000:
                    break
        except Exception as e:
            print(f'Lỗi tải range {start}-{start+999}: {e}')
            break
    print(f'-> Đã tải thành công {len(all_rows)} loài cá biển.')
    return all_rows


def fetch_worms_records_batch(aphia_ids):
    """
    Fetch batch WoRMS records using AphiaRecordsByAphiaIDs (50 IDs per request)
    """
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f'Đã nạp {len(cache)} bản ghi từ cache {CACHE_FILE}')
        except Exception:
            cache = {}

    missing_ids = [aid for aid in aphia_ids if str(aid) not in cache and aid]
    print(f'Tổng AphiaIDs cần kiểm tra: {len(aphia_ids)} | Đã có trong cache: {len(cache)} | Cần tải từ WoRMS: {len(missing_ids)}')

    if missing_ids:
        batch_size = 50
        for i in range(0, len(missing_ids), batch_size):
            batch = missing_ids[i:i+batch_size]
            params = '&'.join([f'aphiaids[]={aid}' for aid in batch])
            url = f'https://www.marinespecies.org/rest/AphiaRecordsByAphiaIDs?{params}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Cam Nang Sinh Vat Bien VN - Academic Sync)'})
            retries = 3
            success = False
            while retries > 0 and not success:
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        records = json.loads(resp.read().decode('utf-8'))
                        for rec in records:
                            if rec and rec.get('AphiaID'):
                                cache[str(rec['AphiaID'])] = rec
                        success = True
                        print(f'  [Batch {i//batch_size + 1}/{(len(missing_ids)+batch_size-1)//batch_size}] Tải thành công {len(records)} records (AphiaID {batch[0]}..{batch[-1]})')
                except Exception as e:
                    retries -= 1
                    print(f'  Lỗi tải batch {i//batch_size + 1} ({e}), thử lại sau 3s... (còn {retries} lần)')
                    time.sleep(3)
            time.sleep(1.2)  # tôn trọng rate limit WoRMS

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f'-> Đã lưu toàn bộ {len(cache)} bản ghi vào cache {CACHE_FILE}')

    return cache


def prepare_worms_taxonomy_payload(sp, worms_cache):
    aid = sp.get('worms_id')
    rec = worms_cache.get(str(aid)) if aid else None

    # Fallback to species fields if WoRMS record is empty
    cls_lat = (rec.get('class') if rec else None) or sp.get('tax_class_latin') or 'Teleostei'
    ord_lat = (rec.get('order') if rec else None) or sp.get('tax_order_latin') or 'Perciformes'
    fam_lat = (rec.get('family') if rec else None) or sp.get('tax_family_latin') or ''
    gen_lat = (rec.get('genus') if rec else None) or (sp.get('scientific_name', '').split()[0] if sp.get('scientific_name') else '')

    cls_vn = CLASS_VN_DICT.get(cls_lat, f'Lớp {cls_lat}')
    ord_vn = ORDER_VN_DICT.get(ord_lat, f'Bộ {ord_lat}')
    
    # Family Vietnamese: if same as book family, keep book vn name; else format 'Họ ...'
    book_fam_lat = (sp.get('tax_family_latin') or '').strip().lower()
    if fam_lat and fam_lat.lower() == book_fam_lat and sp.get('tax_family_vn'):
        fam_vn = sp.get('tax_family_vn')
    else:
        fam_vn = sp.get('tax_family_vn') or f'Họ {fam_lat}'
    if not fam_vn.startswith('Họ ') and not fam_vn.startswith('Họ cá ') and not fam_vn.startswith('Họ Cá '):
        fam_vn = f'Họ {fam_vn}'

    worms_tax = {
        'class': cls_lat,
        'classVn': cls_vn,
        'order': ord_lat,
        'orderVn': ord_vn,
        'family': fam_lat,
        'familyVn': fam_vn,
        'genus': gen_lat,
        'genusVn': f'Chi {gen_lat}',
        'aphiaId': aid,
        'status': rec.get('status') if rec else (sp.get('worms_status') or 'valid'),
        'validName': rec.get('valid_name') if rec else (sp.get('worms_accepted_name') or sp.get('scientific_name')),
    }

    biology = sp.get('biology') or {}
    # Shallow copy / deep clone
    new_biology = dict(biology)
    new_biology['wormsTaxonomy'] = worms_tax

    return {
        'id': sp['id'],
        'biology': new_biology
    }


def patch_species_batch(supabase_url, supabase_key, updates):
    print(f'Bắt đầu cập nhật {len(updates)} loài vào Supabase qua đa luồng (20 workers)...')
    success_count = 0
    fail_count = 0

    def patch_one(item):
        sp_id = item['id']
        url = f"{supabase_url}/rest/v1/species?id=eq.{sp_id}"
        payload = json.dumps({'biology': item['biology']}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            method='PATCH'
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 204):
                    return True, sp_id, None
                return False, sp_id, f"HTTP {resp.status}"
        except Exception as e:
            return False, sp_id, str(e)

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(patch_one, item): item for item in updates}
        done = 0
        for fut in as_completed(futures):
            done += 1
            ok, sp_id, err = fut.result()
            if ok:
                success_count += 1
            else:
                fail_count += 1
                print(f"  [!] Lỗi cập nhật {sp_id}: {err}")
            if done % 200 == 0 or done == len(updates):
                print(f"  Tiến độ: {done}/{len(updates)} ({done*100//len(updates)}%) - Thành công: {success_count}, Thất bại: {fail_count}")

    duration = time.time() - start_time
    print(f"\n-> HOÀN TẤT CẬP NHẬT TRONG {duration:.1f} GIÂY!")
    print(f"   Thành công: {success_count}/{len(updates)}")
    print(f"   Thất bại:   {fail_count}")


def main():
    supabase_url, supabase_key = load_env()
    species_list = fetch_all_ca_bien_species(supabase_url, supabase_key)
    if not species_list:
        print('Không có loài nào để xử lý!')
        return

    # Collect unique AphiaIDs
    aphia_ids = []
    seen = set()
    for sp in species_list:
        aid = sp.get('worms_id')
        if aid and aid not in seen:
            seen.add(aid)
            aphia_ids.append(aid)

    print(f'Tìm thấy {len(aphia_ids)} AphiaIDs duy nhất trên tổng số {len(species_list)} loài.')
    worms_cache = fetch_worms_records_batch(aphia_ids)

    # Prepare updates
    updates = []
    orders_counter = {}
    for sp in species_list:
        up = prepare_worms_taxonomy_payload(sp, worms_cache)
        wt = up['biology']['wormsTaxonomy']
        ord_name = wt['order']
        orders_counter[ord_name] = orders_counter.get(ord_name, 0) + 1
        updates.append(up)

    print('\n--- THỐNG KÊ CÁC BỘ HIỆN ĐẠI (WoRMS 2026) CHO 1,767 LOÀI CÁ BIỂN ---')
    sorted_orders = sorted(orders_counter.items(), key=lambda x: x[1], reverse=True)
    for ord_name, count in sorted_orders[:20]:
        vn = ORDER_VN_DICT.get(ord_name, ord_name)
        print(f"  {ord_name:<25} ({vn:<32}): {count} loài")
    print(f"  Tổng cộng: {len(sorted_orders)} Bộ hiện đại (so với 48 bộ truyền thống của sách cũ)")

    # Execute Supabase updates
    patch_species_batch(supabase_url, supabase_key, updates)


if __name__ == '__main__':
    main()
