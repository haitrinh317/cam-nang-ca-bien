#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_sanho_worms.py
-------------------
Xác thực danh pháp quốc tế WoRMS cho 42 loài San hô tám ngăn (collection san-ho)
và taxonomy chuẩn hóa từ WoRMS.
"""

import os, sys, time, json, urllib.request, urllib.parse
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

env_file = '.env.local' if os.path.exists('.env.local') else '.env'
env = {}
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k] = v.strip('\"').strip('\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json'
}

def query_worms(name):
    # Query WoRMS match API
    encoded = urllib.parse.quote(name)
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?scientificnames[]={encoded}&marine_only=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'VietnameseMarineSpecies/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0 and len(data[0]) > 0:
                return data[0][0]
    except urllib.error.HTTPError as e:
        if e.code == 204:
            return None
        print(f"    WoRMS HTTP {e.code} for {name}")
    except Exception as e:
        print(f"    WoRMS error for {name}: {e}")
    return None

def get_aphia_record(aphia_id):
    url = f"https://www.marinespecies.org/rest/AphiaRecordByAphiaID/{aphia_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'VietnameseMarineSpecies/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"    Error fetching AphiaID {aphia_id}: {e}")
    return None

def main():
    print("=== BẮT ĐẦU ĐỒNG BỘ WORMS CHO COLLECTION SAN-HO ===")
    
    # 1. Fetch all san-ho species
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.san-ho&order=species_index.asc"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        species_list = json.loads(resp.read().decode('utf-8'))
        
    print(f"Tổng số loài san-ho: {len(species_list)}")
    
    now_iso = datetime.now(timezone.utc).isoformat()
    success_count = 0
    synonym_count = 0
    valid_count = 0
    not_found_count = 0
    
    for s in species_list:
        sp_id = s['id']
        sp_idx = s['species_index']
        sc_name = s['scientific_name']
        
        if sp_idx == 30 or '[KHUYẾT' in s['vn_name']:
            print(f"[{sp_idx:2d}/42] Skip khuyết trang: {sp_id}")
            continue
            
        print(f"[{sp_idx:2d}/42] Đang tra WoRMS cho: {sc_name}...", end=" ", flush=True)
        
        # Primary query
        record = query_worms(sc_name)
        time.sleep(1.0)
        
        # If not found and starts with Sclerophytum, try Sinularia
        if not record and sc_name.startswith("Sclerophytum "):
            alt_name = sc_name.replace("Sclerophytum ", "Sinularia ")
            print(f"(thử {alt_name})...", end=" ", flush=True)
            record = query_worms(alt_name)
            time.sleep(1.0)
            
        if not record:
            print("❌ NOT FOUND")
            not_found_count += 1
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            payload = {
                'worms_status': 'not_found',
                'worms_synced_at': now_iso
            }
            req = urllib.request.Request(patch_url, data=json.dumps(payload).encode('utf-8'), headers=HEADERS, method='PATCH')
            try:
                with urllib.request.urlopen(req) as resp: pass
            except: pass
            continue
            
        aphia_id = record.get('AphiaID')
        status = record.get('status', '').lower()
        valid_name = record.get('valid_name', sc_name)
        valid_aphia_id = record.get('valid_AphiaID', aphia_id)
        lsid = record.get('lsid', f"urn:lsid:marinespecies.org:taxname:{aphia_id}")
        
        # If unaccepted / synonym
        worms_status = 'valid'
        if status in ['unaccepted', 'synonym', 'alternative representation']:
            worms_status = 'synonym'
            synonym_count += 1
            # If valid record exists, get details
            if valid_aphia_id and valid_aphia_id != aphia_id:
                valid_rec = get_aphia_record(valid_aphia_id)
                time.sleep(1.0)
                if valid_rec:
                    valid_name = valid_rec.get('scientificname', valid_name)
                    record = valid_rec # use valid record for taxonomy
            print(f"🔄 SYNONYM -> {valid_name} (AphiaID {valid_aphia_id})")
        else:
            valid_count += 1
            print(f"✅ VALID (AphiaID {aphia_id})")
            
        # Taxonomy from WoRMS
        order_latin = record.get('order', s.get('tax_order_latin') or 'Alcyonacea')
        family_latin = record.get('family', s.get('tax_family_latin') or 'Alcyoniidae')
        genus_latin = record.get('genus', s.get('tax_genus_latin') or sc_name.split()[0])
        class_latin = record.get('class', 'Anthozoa')
        
        payload = {
            'worms_id': valid_aphia_id or aphia_id,
            'worms_status': worms_status,
            'worms_accepted_name': valid_name,
            'worms_synced_at': now_iso,
            'tax_order_latin': order_latin,
            'tax_family_latin': family_latin,
            'tax_genus_latin': genus_latin,
            'tax_class_latin': f"{class_latin} (Octocorallia)"
        }
        
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        req = urllib.request.Request(patch_url, data=json.dumps(payload).encode('utf-8'), headers=HEADERS, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                success_count += 1
        except Exception as e:
            print(f"    Lỗi PATCH Supabase cho {sp_id}: {e}")
            
    print("\n==========================================")
    print(f"🎉 HOÀN THÀNH WORMS SYNC!")
    print(f"• Tổng số loài xử lý: {success_count}/41 (loài 30 khuyết)")
    print(f"• Valid (Tên hợp lệ): {valid_count}")
    print(f"• Synonym (Đồng danh cập nhật): {synonym_count}")
    print(f"• Not found: {not_found_count}")
    print("==========================================")

if __name__ == '__main__':
    main()
