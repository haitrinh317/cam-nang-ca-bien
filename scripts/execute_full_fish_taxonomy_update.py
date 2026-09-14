import os, requests, json, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: missing env variables")
    sys.exit(1)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

with open('scratch/full_fish_taxonomy_updates.json') as f:
    updates = json.load(f)

print(f"Total species to update taxonomy: {len(updates)}")

def patch_species(item):
    sp_id, payload = item
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
    try:
        resp = requests.patch(url, headers=HEADERS, json=payload, timeout=10)
        return sp_id, resp.status_code == 204 or resp.status_code == 200, resp.text
    except Exception as e:
        return sp_id, False, str(e)

success_count = 0
failed_count = 0

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(patch_species, item): item[0] for item in updates.items()}
    for f in as_completed(futures):
        sp_id, ok, msg = f.result()
        if ok:
            success_count += 1
            if success_count % 100 == 0:
                print(f"Progress: {success_count} / {len(updates)} updated...")
        else:
            failed_count += 1
            print(f"Failed {sp_id}: {msg}")

print(f"\n=== TAXONOMY UPDATE COMPLETE ===")
print(f"Success: {success_count}")
print(f"Failed: {failed_count}")

