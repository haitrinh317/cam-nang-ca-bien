#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_pilot_cypraeidae_worms.py — Xác thực danh pháp khoa học 74 loài Họ Ốc sứ Cypraeidae
bằng WoRMS REST API (AphiaRecordsByName).
"""

import os
import sys
import json
import time
import requests
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

IN_JSON = 'scratch/pilot_cypraeidae_flat.json'
OUT_JSON = 'scratch/pilot_cypraeidae_worms.json'

WORMS_API = 'https://www.marinespecies.org/rest/AphiaRecordsByName/{name}?like=false&marine_only=true'

def query_worms(sci_name):
    encoded = urllib.parse.quote(sci_name)
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{encoded}?like=false&marine_only=true"
    headers = {'User-Agent': 'VietnameseMarineMolluscs/1.0 (haitrinh082@gmail.com)'}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            records = r.json()
            if records:
                # Pick the first marine record
                rec = records[0]
                return {
                    "worms_id": rec.get('AphiaID'),
                    "worms_accepted_name": rec.get('valid_name') or rec.get('scientificname'),
                    "worms_status": rec.get('status'),
                    "worms_lsid": rec.get('lsid'),
                    "worms_valid_id": rec.get('valid_AphiaID')
                }
        elif r.status_code == 204:
            return {"worms_id": None, "worms_accepted_name": sci_name, "worms_status": "not_found", "worms_lsid": None}
    except Exception as e:
        print(f"    [WoRMS Error] {sci_name}: {e}")
    
    return {"worms_id": None, "worms_accepted_name": sci_name, "worms_status": "error", "worms_lsid": None}

def main():
    with open(IN_JSON, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    print(f"Bắt đầu kiểm tra WoRMS cho {len(species_list)} loài Ốc sứ...")
    
    accepted_count = 0
    synonym_count = 0
    not_found_count = 0

    for idx, sp in enumerate(species_list, start=1):
        sci = sp['scientific_name']
        res = query_worms(sci)
        
        sp['worms_id'] = res['worms_id']
        sp['worms_accepted_name'] = res['worms_accepted_name']
        sp['worms_status'] = res['worms_status']
        sp['worms_lsid'] = res['worms_lsid']

        status = res['worms_status']
        if status == 'accepted':
            accepted_count += 1
            icon = "✅"
        elif status == 'unaccepted' or (res['worms_accepted_name'] and res['worms_accepted_name'] != sci):
            synonym_count += 1
            icon = "🔄"
        else:
            not_found_count += 1
            icon = "❓"

        print(f"  [{idx:02d}/74] {icon} {sci} -> {res['worms_accepted_name']} ({status})")
        time.sleep(0.15)  # Respect rate limit

    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(species_list, f, ensure_ascii=False, indent=2)

    print(f"\nHoàn tất WoRMS validation:")
    print(f"  - Accepted (Hợp lệ giữ nguyên tên): {accepted_count}")
    print(f"  - Synonyms (Đã chuyển chi/đổi tên): {synonym_count}")
    print(f"  - Not found: {not_found_count}")
    print(f"  - File kết quả: {OUT_JSON}")

if __name__ == '__main__':
    main()
