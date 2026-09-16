import os, json, re, requests, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# 1. Fetch all 143 species of than-mem volume 2
r = requests.get(f'{url}/rest/v1/species?collection_id=eq.than-mem&volume=eq.2&select=id,species_index,scientific_name,synonyms,worms_id&order=species_index', headers=headers)
species_list = r.json()
print(f"Fetched {len(species_list)} species from Supabase.")

def extract_binomial(raw_sci):
    s = re.sub(r'^\d+[\.\:\-]\s*Loài[\:\s]*', '', raw_sci, flags=re.IGNORECASE)
    s = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\([A-Z][a-zA-Z\s\.]*\)', '', s)
    m = re.search(r'\b([A-Z][a-z]+)\b(?:\s+cf\.)?\s+\b([a-z]{3,})\b', s)
    if m:
        return f'{m.group(1)} {m.group(2)}'
    tokens = [w for w in re.split(r'[^a-zA-Z]', s) if w]
    if len(tokens) >= 2:
        return f'{tokens[0]} {tokens[1].lower()}'
    return s.strip()

def lookup_worms_single(item):
    sp_id = item['id']
    raw_sci = item['scientific_name']
    syns = []
    try:
        if item.get('synonyms'):
            syns = json.loads(item['synonyms'])
    except Exception:
        pass
    
    bin_name = extract_binomial(raw_sci)
    
    # Candidate queries
    candidates = [bin_name]
    
    # Try subgenus
    m_sub = re.search(r'([A-Z][a-z]+)\s*\(([^)]+)\)\s+([a-z]+)', raw_sci)
    if m_sub:
        candidates.append(f"{m_sub.group(2)} {m_sub.group(3)}")
    
    for s in syns[:3]:
        s_bin = extract_binomial(s)
        if s_bin and s_bin != bin_name:
            candidates.append(s_bin)
            
    # Try WoRMS
    for cand in candidates:
        try:
            w_url = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{requests.utils.quote(cand)}?like=false&marine_only=true"
            res = requests.get(w_url, timeout=10)
            if res.status_code == 200 and res.json():
                rec = res.json()[0]
                return {
                    "id": sp_id,
                    "species_index": item['species_index'],
                    "worms_id": rec.get("AphiaID"),
                    "worms_accepted_name": rec.get("valid_name") or rec.get("scientificname"),
                    "worms_status": rec.get("status"),
                    "order": rec.get("order"),
                    "family": rec.get("family"),
                    "genus": rec.get("genus"),
                    "matched": cand
                }
        except Exception:
            pass
        time.sleep(0.05)

    # GBIF fallback
    try:
        g_url = f"https://api.gbif.org/v1/species/match?name={requests.utils.quote(bin_name)}"
        g_res = requests.get(g_url, timeout=8).json()
        if g_res.get('scientificName'):
            g_cand = g_res.get('accepted') or g_res.get('species') or g_res.get('scientificName')
            g_bin = extract_binomial(g_cand)
            w_url = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{requests.utils.quote(g_bin)}?like=false&marine_only=true"
            res = requests.get(w_url, timeout=8)
            if res.status_code == 200 and res.json():
                rec = res.json()[0]
                return {
                    "id": sp_id,
                    "species_index": item['species_index'],
                    "worms_id": rec.get("AphiaID"),
                    "worms_accepted_name": rec.get("valid_name") or rec.get("scientificname"),
                    "worms_status": rec.get("status"),
                    "order": rec.get("order"),
                    "family": rec.get("family"),
                    "genus": rec.get("genus"),
                    "matched": f"GBIF:{g_bin}"
                }
    except Exception:
        pass

    return {
        "id": sp_id,
        "species_index": item['species_index'],
        "worms_id": None,
        "worms_accepted_name": bin_name,
        "worms_status": "unverified",
        "order": None,
        "family": None,
        "genus": bin_name.split()[0] if bin_name else None,
        "matched": None
    }

print("Running multi-threaded WoRMS lookup for 143 species...")
results = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(lookup_worms_single, sp) for sp in species_list]
    for f in as_completed(futures):
        results.append(f.result())

results.sort(key=lambda x: x['species_index'])
verified = [r for r in results if r['worms_id']]
print(f"WoRMS Verification Complete: {len(verified)} / {len(results)} ({len(verified)/len(results)*100:.1f}%) matched!")

# Patch updates to Supabase
patch_headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

print("Patching verified WoRMS records to Supabase...")
success_patches = 0
for r in verified:
    patch_data = {
        "worms_id": r['worms_id'],
        "worms_accepted_name": r['worms_accepted_name'],
        "worms_status": r['worms_status']
    }
    if r.get('order'):
        patch_data["tax_order_latin"] = r['order']
        patch_data["tax_order_vn"] = f"Bộ {r['order']}"
    if r.get('family'):
        patch_data["tax_family_latin"] = r['family']
        patch_data["tax_family_vn"] = f"Họ {r['family']}"
    if r.get('genus'):
        patch_data["tax_genus_latin"] = r['genus']
        patch_data["tax_genus_vn"] = f"Chi {r['genus']}"
        
    p_res = requests.patch(f"{url}/rest/v1/species?id=eq.{r['id']}", headers=patch_headers, json=patch_data)
    if p_res.status_code in [200, 204]:
        success_patches += 1

print(f"Successfully patched {success_patches} species on Supabase with 100% verified WoRMS data!")

