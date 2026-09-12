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

# Inspect Arothron hispidus in ca-bien and sinh-vat-doc
req_cb5 = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.5&species_index=eq.245', headers=headers)
with urllib.request.urlopen(req_cb5) as r:
    cb5 = json.loads(r.read().decode())[0]

req_cb6 = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&species_index=eq.259', headers=headers)
with urllib.request.urlopen(req_cb6) as r:
    cb6 = json.loads(r.read().decode())[0]

req_svd = urllib.request.Request(f'{url}/rest/v1/species?collection_id=eq.sinh-vat-doc&species_index=eq.59', headers=headers)
with urllib.request.urlopen(req_svd) as r:
    svd = json.loads(r.read().decode())[0]

print("=== SO SÁNH Arothron hispidus (Cá nóc chuột vân bụng) ===")
print("CB5 ID:", cb5['id'], "| vn_literature:", cb5.get('vn_literature'))
print("CB6 ID:", cb6['id'], "| vn_literature:", cb6.get('vn_literature'))
print("SVD ID:", svd['id'], "| vn_literature:", svd.get('vn_literature'))
print("\nCB5 vn_morphology length:", len(cb5.get('vn_morphology') or ''))
print("CB6 vn_diagnosis length:", len(cb6.get('vn_diagnosis') or ''))
print("SVD vn_morphology length:", len(svd.get('vn_morphology') or ''))
print("\nSVD toxicology keys:", list((svd.get('biology', {}).get('toxicology') or {}).keys()))
print("CB5 has toxicology?:", 'toxicology' in (cb5.get('biology') or {}))
print("CB6 has toxicology?:", 'toxicology' in (cb6.get('biology') or {}))
