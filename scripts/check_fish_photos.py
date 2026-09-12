import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

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
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

req_p = urllib.request.Request(
    f'{url}/rest/v1/species_photos?species_id=like.sinhvatdoc-species-*',
    headers=headers
)
with urllib.request.urlopen(req_p) as r:
    svd_photos = json.loads(r.read().decode())

print(f"Tổng số ảnh sinh-vat-doc: {len(svd_photos)}")
fish_photos = [p for p in svd_photos if 21 <= int(p['species_id'].split('-')[-1]) <= 24 or 56 <= int(p['species_id'].split('-')[-1]) <= 76]
print(f"Số ảnh của các loài cá độc (SVD #21-#24 & #56-#76): {len(fish_photos)}")
for p in fish_photos[:5]:
    print(f"  • {p['species_id']}: {p['storage_path']} (by {p.get('photographer')})")
