"""
Enrich the final 20 species in Supabase with FishBase biology using both original and WoRMS accepted names.
"""
import os
import json
import urllib.request
import urllib.parse
import duckdb

# Read .env
env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"\'')

supabase_url = env.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

with open('scratch/missing_bio_20.json', 'r', encoding='utf-8') as f:
    missing_items = json.load(f)

print(f"Bắt đầu tìm kiếm FishBase Biology cho {len(missing_items)} loài...")

conn = duckdb.connect()

SPECIES_PARQUET = 'data/fishbase_cache/species.parquet'
ECOLOGY_PARQUET = 'data/fishbase_cache/ecology.parquet'
REPRODUC_PARQUET = 'data/fishbase_cache/reproduc.parquet'

headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def query_fishbase(name):
    if not name:
        return None
    parts = name.strip().split()
    if len(parts) < 2:
        return None
    genus, species = parts[0], parts[1]
    
    # 1. Look in species.parquet
    row = conn.execute(f"""
        SELECT SpecCode, Genus, Species, FBname, Length, LTypeMaxM, Weight, DepthRangeShallow, DepthRangeDeep,
               Vulnerability, Importance, PriceCateg, UsedforAquaculture, Dangerous, Comments
        FROM '{SPECIES_PARQUET}'
        WHERE LOWER(Genus) = LOWER(?) AND LOWER(Species) = LOWER(?)
    """, [genus, species]).fetchone()
    
    if not row:
        return None
        
    spec_code = row[0]
    
    # 2. Look in ecology.parquet
    eco_row = conn.execute(f"""
        SELECT FeedingType, AddRems
        FROM '{ECOLOGY_PARQUET}'
        WHERE SpecCode = ?
    """, [spec_code]).fetchone()
    
    # 3. Look in reproduc.parquet
    rep_row = conn.execute(f"""
        SELECT ReproMode, Fertilization, Spawning, AddInfos
        FROM '{REPRODUC_PARQUET}'
        WHERE SpecCode = ?
    """, [spec_code]).fetchone()
    
    ltype = f" {row[5]}" if row[5] else " TL"
    bio = {
        'fbSpecCode': spec_code,
        'source': 'FishBase v25.04',
        'fbName': row[3] or '',
        'maxLength': f"{row[4]} cm{ltype}" if row[4] else None,
        'maxWeight': f"{row[6]} g" if row[6] else None,
        'depth': f"{row[7]} - {row[8]} m" if (row[7] or row[8]) else None,
        'vulnerability': float(row[9]) if row[9] is not None else None,
        'importance': row[10] or None,
        'priceCategory': row[11] or None,
        'aquaculture': row[12] or None,
        'dangerous': row[13] or None,
        'biologySummary': row[14] or None,
        'feedingType': eco_row[0] if eco_row and eco_row[0] else None,
        'ecologyNotes': eco_row[1] if eco_row and eco_row[1] else None,
        'reproduction': rep_row[0] if rep_row and rep_row[0] else None,
        'reproductionNotes': rep_row[3] if rep_row and rep_row[3] else None
    }
    # Clean None values
    return {k: v for k, v in bio.items() if v is not None}

updated_count = 0
for it in missing_items:
    sp_id = it['id']
    name = it['name']
    accepted = it.get('accepted')
    
    bio = query_fishbase(name) or query_fishbase(accepted)
    if not bio:
        print(f"  [--] Không tìm thấy FishBase cho {sp_id:18s} ({name} / {accepted})")
        continue
        
    patch_url = f"{supabase_url}/rest/v1/species?id=eq.{sp_id}"
    req = urllib.request.Request(patch_url, data=json.dumps({'biology': bio}).encode('utf-8'), headers=headers, method='PATCH')
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 204):
                updated_count += 1
                print(f"  [OK] Cập nhật thành công Biology {sp_id:18s} -> {bio.get('fbName') or name} (SpecCode: {bio.get('fbSpecCode')})")
    except Exception as e:
        print(f"  [ERR] Lỗi cập nhật {sp_id}: {e}")

print(f"\n=======================================================")
print(f"KẾT QUẢ BỔ SUNG BIOLOGY:")
print(f"  - Thành công: {updated_count} / {len(missing_items)} loài")
print(f"=======================================================")
