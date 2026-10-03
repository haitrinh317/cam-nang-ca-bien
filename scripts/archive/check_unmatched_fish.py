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

queries = ['Torquigener', 'gloveri', 'suezensis', 'Synanceja', 'Pterois', 'Scorpaena', 'Dasyatis']

for q in queries:
    req = urllib.request.Request(
        f'{url}/rest/v1/species?collection_id=eq.ca-bien&scientific_name=ilike.*{q}*&select=id,volume,species_index,scientific_name,vn_name',
        headers=headers
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode())
    print(f"Query '{q}' in ca-bien ({len(res)} results):")
    for row in res[:5]:
        print(f"  • Vol {row['volume']} #{row['species_index']}: {row['scientific_name']} ({row['vn_name']})")
