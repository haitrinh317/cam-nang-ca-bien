import os
import sys
import json
import urllib.request
from collections import defaultdict

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

# Paginate to fetch all species
all_sp = []
offset = 0
limit = 1000
while True:
    h = headers.copy()
    h['Range'] = f'{offset}-{offset + limit - 1}'
    req = urllib.request.Request(
        f'{url}/rest/v1/species?select=id,collection_id,species_index,scientific_name,vn_name,worms_id,deleted_at',
        headers=h
    )
    with urllib.request.urlopen(req) as r:
        batch = json.loads(r.read().decode())
        all_sp.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

print(f"Tổng số bản ghi tải về: {len(all_sp)} (chỉ xét deleted_at IS NULL)")
active_sp = [s for s in all_sp if not s.get('deleted_at')]
print(f"Số bản ghi active: {len(active_sp)}")

by_worms = defaultdict(list)
for sp in active_sp:
    wid = sp.get('worms_id')
    if wid:
        by_worms[wid].append(sp)

cross_col = {}
for wid, items in by_worms.items():
    cols = {x['collection_id'] for x in items}
    if len(cols) > 1:
        cross_col[wid] = items

print(f"\nTổng số taxa trùng chéo giữa các collection khác nhau: {len(cross_col)} taxa\n")
for wid, items in sorted(cross_col.items(), key=lambda x: len(x[1]), reverse=True):
    cols_str = " <===> ".join([f"[{x['collection_id']}] #{x['species_index']}: {x['scientific_name']} ({x['vn_name']})" for x in items])
    print(f"• WoRMS {wid}: {cols_str}")
