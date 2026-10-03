import os, requests, re
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

r = requests.get(
    f'{url}/rest/v1/species?collection_id=eq.than-mem&id=like.thanmem-tap2*&select=id,species_index,vn_name,vn_alternate_names,scientific_name&order=species_index.asc',
    headers=headers
)
rows = r.json()

def process_vietnamese_names(raw_vn_name, existing_alt=''):
    raw = raw_vn_name.strip().rstrip('.').strip()
    raw = re.sub(r'\s+hoặc\s+', ', ', raw, flags=re.IGNORECASE)
    parts = [p.strip().rstrip('.').strip() for p in raw.split(',') if p.strip()]
    if not parts:
        return raw, existing_alt
        
    primary_name = parts[0]
    if primary_name and primary_name[0].islower():
        primary_name = primary_name[0].upper() + primary_name[1:]
        
    new_alts = []
    for p in parts[1:]:
        if p and p[0].islower():
            p = p[0].upper() + p[1:]
        if p and p.lower() != primary_name.lower() and p not in new_alts:
            new_alts.append(p)
            
    if existing_alt:
        for ea in [x.strip() for x in existing_alt.split(',') if x.strip()]:
            if 'động vật' in ea.lower():
                continue
            if ea and ea.lower() != primary_name.lower() and ea not in new_alts:
                new_alts.append(ea)
                
    alt_str = ', '.join(new_alts)
    return primary_name, alt_str

updates = []
for row in rows:
    old_vn = row.get('vn_name') or ''
    old_alt = row.get('vn_alternate_names') or ''
    new_vn, new_alt = process_vietnamese_names(old_vn, old_alt)
    
    # Special cleanup for noisy alt in #143
    if row['species_index'] == 143 and 'động vật' in old_alt:
        new_alt = ''
        
    if new_vn != old_vn or new_alt != old_alt:
        updates.append({
            'id': row['id'],
            'species_index': row['species_index'],
            'scientific_name': row['scientific_name'],
            'old_vn': old_vn,
            'new_vn': new_vn,
            'old_alt': old_alt,
            'new_alt': new_alt
        })

print(f'Applying updates to {len(updates)} species in Supabase...')

for u in updates:
    patch_url = f"{url}/rest/v1/species?id=eq.{u['id']}"
    payload = {
        'vn_name': u['new_vn'],
        'vn_alternate_names': u['new_alt']
    }
    resp = requests.patch(patch_url, headers=headers, json=payload)
    if resp.status_code in [200, 204]:
        print(f"✅ #{u['species_index']} ({u['scientific_name']}): vn_name='{u['new_vn']}' | vn_alternate_names='{u['new_alt']}'")
    else:
        print(f"❌ #{u['species_index']} failed: {resp.status_code} {resp.text}")

print("Done updating species names!")
