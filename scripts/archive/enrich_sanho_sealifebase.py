#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_sanho_sealifebase.py
----------------------------
Làm giàu dữ liệu sinh học, độ sâu, kích thước và tên tiếng Anh cho 42 loài San hô (collection san-ho)
từ SeaLifeBase v25.04 offline cache (DuckDB).
"""

import os, sys, json, urllib.request
import duckdb

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

con = duckdb.connect()

# 1. Fetch species from Supabase
url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.san-ho&select=id,species_index,scientific_name,en_common_name,biology&order=species_index.asc"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req) as resp:
    species_list = json.loads(resp.read().decode('utf-8'))

print(f"Tổng số loài san-ho cần enrich: {len(species_list)}")

enriched_count = 0
photos_found = {}

for s in species_list:
    sp_id = s['id']
    sp_idx = s['species_index']
    sc = s['scientific_name']
    
    if ' ' not in sc or sp_idx == 30:
        continue
        
    g, sp = sc.split(' ', 1)
    
    # 1. Query species.parquet
    r = con.execute('SELECT SpecCode, Genus, Species, FBname, Length, DepthRangeShallow, DepthRangeDeep, Comments FROM read_parquet("data/sealifebase_cache/species.parquet") WHERE LOWER(Genus)=? AND LOWER(Species)=?', [g.lower(), sp.lower()]).fetchall()
    
    # Fallback to Sinularia if Sclerophytum
    if not r and g.lower() == 'sclerophytum':
        r = con.execute('SELECT SpecCode, Genus, Species, FBname, Length, DepthRangeShallow, DepthRangeDeep, Comments FROM read_parquet("data/sealifebase_cache/species.parquet") WHERE LOWER(Genus)=\'sinularia\' AND LOWER(Species)=?', [sp.lower()]).fetchall()
        
    # Fallback to synonyms.parquet
    if not r:
        rs = con.execute('SELECT SpecCode, SynGenus, SynSpecies FROM read_parquet("data/sealifebase_cache/synonyms.parquet") WHERE LOWER(SynGenus)=? AND LOWER(SynSpecies)=?', [g.lower(), sp.lower()]).fetchall()
        if rs:
            spec_code = rs[0][0]
            r = con.execute('SELECT SpecCode, Genus, Species, FBname, Length, DepthRangeShallow, DepthRangeDeep, Comments FROM read_parquet("data/sealifebase_cache/species.parquet") WHERE SpecCode=?', [spec_code]).fetchall()

    if not r:
        continue
        
    row = r[0]
    spec_code = row[0]
    matched_genus = row[1]
    matched_species = row[2]
    fb_name = row[3]
    length = row[4]
    depth_shallow = row[5]
    depth_deep = row[6]
    comments = row[7]
    
    # Check English common names from comnames.parquet
    en_names = con.execute('SELECT ComName FROM read_parquet("data/sealifebase_cache/comnames.parquet") WHERE SpecCode=? AND LOWER(Language)=\'english\'', [spec_code]).fetchall()
    best_en_name = fb_name
    if not best_en_name and en_names:
        best_en_name = en_names[0][0]
        
    # Check ecology.parquet
    eco_r = con.execute('SELECT Herbivory2, FeedingType, Benthic FROM read_parquet("data/sealifebase_cache/ecology.parquet") WHERE SpecCode=?', [spec_code]).fetchall()
    ecology_data = {}
    if eco_r:
        ecology_data = {
            "herbivory": eco_r[0][0],
            "feedingType": eco_r[0][1],
            "benthicEnvironment": eco_r[0][2]
        }
        
    # Check pictures in picturesmain.parquet
    pics = con.execute('SELECT PicName, AuthName, Remark FROM read_parquet("data/sealifebase_cache/picturesmain.parquet") WHERE SpecCode=?', [spec_code]).fetchall()
    if pics:
        photos_found[sp_id] = pics
        
    # Build biology jsonb
    existing_biology = s.get('biology') or {}
    new_biology = {
        **existing_biology,
        "specCode": spec_code,
        "matchedTaxon": f"{matched_genus} {matched_species}",
        "max_length_cm": length,
        "depth_range_shallow_m": depth_shallow,
        "depth_range_deep_m": depth_deep,
        "biologySummary": comments,
        "ecology": ecology_data
    }
    
    # Remove nulls
    new_biology = {k: v for k, v in new_biology.items() if v is not None}
    
    payload = {
        'biology': new_biology
    }
    if best_en_name and not s.get('en_common_name'):
        payload['en_common_name'] = best_en_name
        
    patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
    patch_req = urllib.request.Request(patch_url, data=json.dumps(payload).encode('utf-8'), headers=HEADERS, method='PATCH')
    try:
        with urllib.request.urlopen(patch_req) as patch_resp:
            enriched_count += 1
            en_str = f" | EN Name: '{best_en_name}'" if best_en_name else ""
            depth_str = f" | Depth: {depth_shallow}-{depth_deep}m" if depth_shallow or depth_deep else ""
            pics_str = f" | Photos: {len(pics)}" if pics else ""
            print(f"✅ [#{sp_idx:2d}] {sc} -> SpecCode {spec_code}{en_str}{depth_str}{pics_str}")
    except Exception as e:
        print(f"❌ Error patching {sp_id}: {e}")

print("\n==========================================")
print(f"🎉 Hoàn tất enrich SeaLifeBase cho {enriched_count} loài san hô!")
print(f"📸 Tìm thấy ảnh khoa học SeaLifeBase cho {len(photos_found)} loài.")
print("==========================================")

# Save photos found list for Phase 4
with open('/Users/macbook2016/.gemini/antigravity-ide/brain/0c721b9c-d53e-418b-a401-d01c07e77efd/scratch/sanho_slb_photos.json', 'w', encoding='utf-8') as f:
    json.dump({k: [{'picName': p[0], 'authName': p[1], 'remark': p[2]} for p in v] for k, v in photos_found.items()}, f, ensure_ascii=False, indent=2)

