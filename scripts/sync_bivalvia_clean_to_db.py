import json, re, os, requests, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

# 1. Fetch current DB records for comparison
print("Fetching current DB records for than-mem tap 2...")
r = requests.get(f"{url}/rest/v1/species?collection_id=eq.than-mem&id=like.thanmem-tap2*&select=id,species_index,vn_name,scientific_name,authorship", headers=headers)
db_records = {sp['species_index']: sp for sp in r.json()}
print(f"Found {len(db_records)} records in DB.")

# 2. Load clean parsed records
with open('/tmp/bivalvia_parsed_143_clean.json', 'r', encoding='utf-8') as f:
    clean_records = json.load(f)

print(f"Loaded {len(clean_records)} parsed records.")

def update_single_species(rec):
    sp_num = rec['species_index']
    sp_id = rec['id']
    existing = db_records.get(sp_num, {})
    
    # Determine final VN name: prefer parsed, fallback to existing DB if valid, else default
    vn_name = rec['vn_name']
    if not vn_name or len(vn_name) < 2:
        existing_vn = existing.get('vn_name', '')
        if existing_vn and 'chưa có' not in existing_vn.lower() and '#' not in existing_vn:
            vn_name = existing_vn
        else:
            vn_name = "Chưa có tên tiếng Việt chính thức"
            
    # Authorship fallback
    authorship = rec['authorship'] or existing.get('authorship', '')
    
    # Scientific name: ensure clean
    sci_clean = rec['scientific_name']
    if authorship and sci_clean.endswith(authorship):
        sci_clean = sci_clean.replace(authorship, '').strip()
    sci_clean = re.sub(r'\s+', ' ', sci_clean).strip(' ,;')

    payload = {
        'scientific_name': sci_clean,
        'authorship': authorship,
        'vn_name': vn_name,
        'vn_size': rec['vn_size'],
        'vn_specimen': rec['vn_specimen'],
        'morphology_vn': rec['morphology_vn'],
        'ecology_vn': rec['ecology_vn'],
        'vn_distribution': rec['vn_distribution'],
        'en_distribution': rec['en_distribution'],
        'economic_value_vn': rec['economic_value_vn'],
        'synonyms': rec['synonyms']
    }
    
    patch_url = f"{url}/rest/v1/species?id=eq.{sp_id}"
    resp = requests.patch(patch_url, headers=headers, json=payload)
    if resp.status_code in [200, 204]:
        return sp_num, True, ""
    else:
        return sp_num, False, resp.text

print("Updating Supabase database for 143 species...")
success_count = 0
failed = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(update_single_species, rec): rec['species_index'] for rec in clean_records}
    for fut in as_completed(futures):
        sp_num, ok, err = fut.result()
        if ok:
            success_count += 1
        else:
            failed.append((sp_num, err))
        if success_count % 25 == 0 or success_count == len(clean_records):
            print(f"Updated [{success_count}/{len(clean_records)}] species in Supabase.")

print(f"\nFINISHED! Successfully updated {success_count}/143 species.")
if failed:
    print(f"Failed species: {failed}")
