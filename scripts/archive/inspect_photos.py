import os
import sys
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    for f in ['.env.local', '.env']:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

req = urllib.request.Request(f'{url}/rest/v1/species_photos?select=*&species_id=like.ranbien-species-*', headers=headers)
with urllib.request.urlopen(req) as r:
    rb_photos = json.loads(r.read().decode())

req2 = urllib.request.Request(f'{url}/rest/v1/species_photos?select=*&species_id=like.sinhvatdoc-species-*', headers=headers)
with urllib.request.urlopen(req2) as r:
    svd_photos = json.loads(r.read().decode())

print(f"Ranbien photos total: {len(rb_photos)}")
print(f"Sinhvatdoc photos total: {len(svd_photos)}")

svd_snake_photos = [p for p in svd_photos if p['species_id'].startswith('sinhvatdoc-species-') and 25 <= int(p['species_id'].split('-')[-1]) <= 47]
print(f"Sinhvatdoc snake photos (#25-#47): {len(svd_snake_photos)}")

if rb_photos:
    print("\nSample RB photo:")
    print(json.dumps(rb_photos[0], ensure_ascii=False, indent=2))
if svd_snake_photos:
    print("\nSample SVD photo:")
    print(json.dumps(svd_snake_photos[0], ensure_ascii=False, indent=2))
