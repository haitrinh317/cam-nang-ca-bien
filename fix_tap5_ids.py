import urllib.request
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

env = {}
for line in open('.env'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        env[k] = v

URL = env.get('VITE_SUPABASE_URL', env.get('SUPABASE_URL'))
KEY = env.get('SUPABASE_SERVICE_KEY', env.get('VITE_SUPABASE_ANON_KEY'))

def fetch_invalid_records():
    url = f"{URL}/rest/v1/species?volume=eq.5&species_index=eq.0"
    req = urllib.request.Request(url, headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}'})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def delete_invalid_records():
    url = f"{URL}/rest/v1/species?volume=eq.5&species_index=eq.0"
    req = urllib.request.Request(url, headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}'}, method='DELETE')
    with urllib.request.urlopen(req) as res:
        return res.status

def insert_records(records):
    url = f"{URL}/rest/v1/species"
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    data = json.dumps(records, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as res:
        return res.status

def main():
    records = fetch_invalid_records()
    print(f"Fetched {len(records)} invalid records.")
    
    if not records:
        print("No invalid records found.")
        return
        
    for r in records:
        old_id = r['id']
        # The id should be just a number like "86" or 86
        r['species_index'] = int(old_id)
        r['id'] = f"tap5-species-{old_id}"
        
    status = delete_invalid_records()
    print(f"Deleted invalid records. Status: {status}")
    
    status = insert_records(records)
    print(f"Inserted corrected records. Status: {status}")

if __name__ == '__main__':
    main()
