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

# 1. Fetch all sinh-vat-doc species
req_svd = urllib.request.Request(
    f'{url}/rest/v1/species?collection_id=eq.sinh-vat-doc&select=*&order=species_index',
    headers=headers
)
with urllib.request.urlopen(req_svd) as r:
    svd_all = json.loads(r.read().decode())

# Filter fish in SVD: Class Actinopterygii or Elasmobranchii, or indices 21-24 and 56-76
fish_classes = {'Actinopterygii', 'Elasmobranchii', 'Chondrichthyes', 'Teleostei'}
svd_fish = [
    s for s in svd_all 
    if (s.get('tax_class_latin') in fish_classes) or (21 <= s['species_index'] <= 24) or (56 <= s['species_index'] <= 76)
]

print(f"Tổng số loài/taxa Cá độc trong sinh-vat-doc: {len(svd_fish)}")
for f in svd_fish:
    print(f"  #{f['species_index']:2d}: {f['scientific_name']:28s} | {f['vn_name']:25s} | WoRMS: {f.get('worms_id')} ({f.get('worms_accepted_name')})")

# 2. Fetch all ca-bien species (paginate to get all 1764)
all_cabien = []
offset = 0
limit = 1000
while True:
    h = headers.copy()
    h['Range'] = f'{offset}-{offset + limit - 1}'
    req_cb = urllib.request.Request(
        f'{url}/rest/v1/species?collection_id=eq.ca-bien&select=id,volume,species_index,scientific_name,vn_name,worms_id,worms_accepted_name,vn_literature,biology,deleted_at',
        headers=h
    )
    with urllib.request.urlopen(req_cb) as r:
        batch = json.loads(r.read().decode())
        all_cabien.extend([b for b in batch if not b.get('deleted_at')])
        if len(batch) < limit:
            break
        offset += limit

print(f"\nTổng số loài cá biển active trong CSDL: {len(all_cabien)}")

# 3. Match SVD fish against ca-bien
# Indexes for ca-bien:
cb_by_worms = {}
cb_by_name = {}
cb_by_accepted = {}

for cb in all_cabien:
    wid = cb.get('worms_id')
    if wid:
        cb_by_worms.setdefault(wid, []).append(cb)
    sn = cb['scientific_name'].strip().lower()
    cb_by_name.setdefault(sn, []).append(cb)
    wan = (cb.get('worms_accepted_name') or '').strip().lower()
    if wan:
        cb_by_accepted.setdefault(wan, []).append(cb)

matches = []
unmatched = []

for sf in svd_fish:
    wid = sf.get('worms_id')
    sn = sf['scientific_name'].strip().lower()
    wan = (sf.get('worms_accepted_name') or '').strip().lower()
    
    cb_matches = []
    m_type = None
    
    # Priority 1: Exact scientific name match
    if sn in cb_by_name:
        cb_matches = cb_by_name[sn]
        m_type = 'scientific_name'
    # Priority 2: WoRMS accepted name
    elif wan and wan in cb_by_accepted:
        cb_matches = cb_by_accepted[wan]
        m_type = 'worms_accepted_name'
    # Priority 3: WoRMS ID (careful: check genus match to avoid bad synonyms)
    elif wid and wid in cb_by_worms:
        # verify genus
        sf_genus = sn.split()[0]
        valid_candidates = [c for c in cb_by_worms[wid] if c['scientific_name'].strip().lower().startswith(sf_genus)]
        if valid_candidates:
            cb_matches = valid_candidates
            m_type = 'worms_id'

    if cb_matches:
        matches.append((sf, cb_matches, m_type))
    else:
        unmatched.append(sf)

print(f"\n=== KẾT QUẢ ĐỐI SOÁT CÁ BIỂN ĐỘC ===")
print(f"Số loài KHỚP trong ca-bien: {len(matches)} / {len(svd_fish)}")
print(f"Số loài CHƯA KHỚP trong ca-bien: {len(unmatched)} / {len(svd_fish)}")

print("\n--- CHI TIẾT CÁC LOÀI KHỚP ---")
for sf, cb_list, m_type in matches:
    cb_desc = ", ".join([f"Tập {c['volume']} #{c['species_index']}: {c['scientific_name']} ({c['vn_name']})" for c in cb_list])
    print(f"SVD #{sf['species_index']:2d} ({sf['scientific_name']} | {sf['vn_name']})")
    print(f"   <===> {cb_desc} [via {m_type}]")

if unmatched:
    print("\n--- CHI TIẾT CÁC LOÀI CHƯA KHỚP TRONG CA-BIEN ---")
    for sf in unmatched:
        print(f"SVD #{sf['species_index']:2d} ({sf['scientific_name']} | {sf['vn_name']})")
