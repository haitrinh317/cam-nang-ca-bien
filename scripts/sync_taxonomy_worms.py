import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import time

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://cjxqogvtzrvnlsssnfob.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

WORMS_BASE = "https://www.marinespecies.org/rest"
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def get_species():
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.thuc-vat-bien&select=id,worms_id,scientific_name"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def get_classification(aphia_id):
    url = f"{WORMS_BASE}/AphiaClassificationByAphiaID/{aphia_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes-SyncBot/1.0 (+research)"})
    try:
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return None

def extract_taxonomy(node, taxonomy):
    if not node:
        return
    rank = node.get("rank")
    name = node.get("scientificname")
    if rank == "Class":
        taxonomy["tax_class_latin"] = name
    elif rank == "Order":
        taxonomy["tax_order_latin"] = name
    elif rank == "Family":
        taxonomy["tax_family_latin"] = name
    elif rank == "Genus":
        taxonomy["tax_genus_latin"] = name
    
    if "child" in node and node["child"]:
        extract_taxonomy(node["child"], taxonomy)

def update_supabase(sp_id, taxonomy):
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = json.dumps(taxonomy, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return resp.status

def main():
    species = get_species()
    print(f"Got {len(species)} species.")
    
    for i, sp in enumerate(species, 1):
        sp_id = sp["id"]
        worms_id = sp["worms_id"]
        print(f"[{i}/{len(species)}] {sp['scientific_name']}:", end=" ", flush=True)
        
        if not worms_id:
            print("No WoRMS ID, skipping.")
            continue
            
        tree = get_classification(worms_id)
        if not tree:
            print("Failed to fetch classification.")
            continue
            
        taxonomy = {
            "tax_class_latin": "",
            "tax_order_latin": "",
            "tax_family_latin": "",
            "tax_genus_latin": ""
        }
        extract_taxonomy(tree, taxonomy)
        
        # We don't have VN translations for seaweeds, so clear them to be safe
        taxonomy["tax_class_vn"] = ""
        taxonomy["tax_order_vn"] = ""
        taxonomy["tax_family_vn"] = ""
        taxonomy["tax_genus_vn"] = ""
        
        update_supabase(sp_id, taxonomy)
        print(f"Updated: {taxonomy['tax_class_latin']} > {taxonomy['tax_order_latin']} > {taxonomy['tax_family_latin']} > {taxonomy['tax_genus_latin']}")
        
        time.sleep(0.2)

if __name__ == "__main__":
    main()
