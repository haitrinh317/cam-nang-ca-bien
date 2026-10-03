#!/usr/bin/env python3
"""
sync_dvpd_worms.py
Xác thực danh pháp quốc tế qua WoRMS (World of Copepods Database)
cho 101 loài Giáp xác chân chèo (Copepoda) trong file staging.
"""

import json
import urllib.request
import urllib.parse
import time
import os
import re

INPUT_JSON = 'scratch/dvpd_atlat_raw_102.json'
CACHE_JSON = 'scratch/dvpd_worms_cache.json'
OUTPUT_JSON = 'scratch/dvpd_atlat_enriched_worms.json'

def load_cache():
    if os.path.exists(CACHE_JSON):
        try:
            with open(CACHE_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_JSON, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

NAME_OVERRIDES = {
    'Labidocera kröyeri': 'Labidocera kroyeri',
    'Pareucalanus attenuates': 'Pareucalanus attenuatus',
    'Pareucalanus elongata': 'Paraeuchaeta elongata',
}

def query_worms(name):
    query_name = NAME_OVERRIDES.get(name, name)
    clean_name = re.sub(r'\(.*?\)', '', query_name)
    clean_name = re.sub(r'[–-].*', '', clean_name).strip()
    encoded = urllib.parse.quote(clean_name)
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{encoded}?like=false&marine_only=true"
    
    headers = {
        'User-Agent': 'Antigravity-Copepoda-Sync/1.0 (haitrinh082@gmail.com)',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and isinstance(data, list):
                # Ưu tiên lấy record có status 'accepted'
                for r in data:
                    if r.get('status', '').lower() == 'accepted':
                        return r
                return data[0]
    except urllib.error.HTTPError as e:
        if e.code == 204:
            return None  # No content (not found)
        print(f"  [!] HTTP Error {e.code} cho '{name}': {e}")
    except Exception as e:
        print(f"  [!] Lỗi kết nối WoRMS cho '{name}': {e}")
    return None

def main():
    print(f"[*] Đọc danh sách loài từ {INPUT_JSON}...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    cache = load_cache()
    print(f"[*] Đã nạp {len(cache)} kết quả từ cache WoRMS.")

    enriched_list = []
    total = len(species_list)

    for idx, sp in enumerate(species_list, 1):
        sci_name = sp['scientific_name']
        print(f"[{idx}/{total}] Đang xác thực: {sci_name}...", end=" ", flush=True)

        if sci_name in cache:
            rec = cache[sci_name]
            print(f"(cache: {rec.get('status') if rec else 'not_found'})")
        else:
            rec = query_worms(sci_name)
            cache[sci_name] = rec
            save_cache(cache)
            if rec:
                print(f"✓ {rec.get('status')} -> {rec.get('valid_name')}")
            else:
                print("✗ Not found")
            time.sleep(0.8)  # Tránh vượt quá rate limit WoRMS

        # Điền thông tin vào loài
        sp_enriched = dict(sp)
        if rec:
            status = rec.get('status', '').lower()
            sp_enriched['worms_id'] = rec.get('valid_AphiaID') or rec.get('AphiaID')
            sp_enriched['worms_status'] = 'accepted' if status == 'accepted' else ('synonym' if 'unaccepted' in status or 'synonym' in status else status)
            sp_enriched['worms_accepted_name'] = rec.get('valid_name') or rec.get('scientificname')
            sp_enriched['worms_lsid'] = rec.get('lsid')
            sp_enriched['taxonomy_order'] = rec.get('order') or 'Calanoida'
            sp_enriched['taxonomy_family'] = rec.get('family') or ''
            sp_enriched['taxonomy_genus'] = rec.get('genus') or sp['taxonomy_genus']
            
            # Nếu tên trong Atlat là synonym, ghi nhận vào synonyms
            if rec.get('valid_name') and rec.get('valid_name').lower() != sci_name.lower():
                sp_enriched['synonyms'] = [sci_name]
        else:
            sp_enriched['worms_id'] = None
            sp_enriched['worms_status'] = 'not_found'
            sp_enriched['worms_accepted_name'] = sci_name
            sp_enriched['worms_lsid'] = None
            sp_enriched['taxonomy_order'] = 'Calanoida'  # Default order cho Copepoda nổi
            sp_enriched['taxonomy_family'] = ''

        enriched_list.append(sp_enriched)

    # Lưu kết quả enriched
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(enriched_list, f, ensure_ascii=False, indent=2)

    # Thống kê
    accepted_cnt = sum(1 for s in enriched_list if s.get('worms_status') == 'accepted')
    synonym_cnt = sum(1 for s in enriched_list if s.get('worms_status') == 'synonym')
    not_found_cnt = sum(1 for s in enriched_list if s.get('worms_status') == 'not_found')

    print("\n" + "="*50)
    print("=== TỔNG HỢP XÁC THỰC WORMS ===")
    print(f"• Tổng số loài xử lý: {total}")
    print(f"• Accepted (Hợp lệ): {accepted_cnt} ({accepted_cnt*100/total:.1f}%)")
    print(f"• Synonym (Đồng danh chuyển đổi): {synonym_cnt} ({synonym_cnt*100/total:.1f}%)")
    print(f"• Not Found: {not_found_cnt} ({not_found_cnt*100/total:.1f}%)")
    print(f"[✓] Đã xuất kết quả sang {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
