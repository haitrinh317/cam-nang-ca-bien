"""
import_to_supabase.py — Import species.json + fishbase_sync.json vào Supabase
Chạy: python scripts/import_to_supabase.py
"""
import json
import os
import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Config ──
SUPABASE_URL = "https://cjxqogvtzrvnlsssnfob.supabase.co"
# service_role key nếu có, fallback anon key
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHFvZ3Z0enJ2bmxzc3NuZm9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzOTUxNjIsImV4cCI6MjEwMDk3MTE2Mn0.HBi2zicdL9O7uMJD6r8IYPXI7ztHcv-5PsTdBwa65_I"
)

# ── Class mapping (from build_taxonomy_tree.py) ──
SUN_ORDERS = [
    "lamniformes", "squaliformes", "rajiformes", "torpediniformes",
    "pristiophoriformes", "heterodontiformes", "hexanchiformes",
    "orectolobiformes", "carcharhiniformes", "dasyatiformes"
]

def get_class(order_latin):
    if not order_latin:
        return "Lớp Cá Xương", "Osteichthyes"
    ol = order_latin.lower().strip()
    if "amphioxiformes" in ol:
        return "Lớp Cá Lưỡng Tiêm", "Leptocardii"
    if any(o in ol for o in SUN_ORDERS):
        return "Lớp Cá Sụn", "Chondrichthyes"
    return "Lớp Cá Xương", "Osteichthyes"


def flatten_species(sp, worms_lookup):
    """Flatten nested species.json record → Supabase row"""
    tax = sp.get("taxonomy", {})
    specs = sp.get("specs", {})
    vn = specs.get("vn", {}) if isinstance(specs, dict) else {}
    en = specs.get("en", {}) if isinstance(specs, dict) else {}
    
    order_latin = tax.get("order", {}).get("latin", "") if isinstance(tax.get("order"), dict) else ""
    class_vn, class_latin = get_class(order_latin)
    
    species_id = sp.get("id", "")
    worms = worms_lookup.get(species_id, {})
    
    syns = sp.get("synonyms", [])
    if not isinstance(syns, list):
        syns = [syns] if syns else []

    return {
        "id": species_id,
        "volume": sp.get("volume", 0),
        "species_index": sp.get("speciesIndex", 0),
        "vn_name": sp.get("vnName", ""),
        "scientific_name": sp.get("scientificName", ""),
        "authorship": sp.get("authorship", ""),
        "en_common_name": en.get("commonName", ""),
        "vn_alternate_names": vn.get("alternateNames", ""),
        # Taxonomy
        "tax_class_vn": class_vn,
        "tax_class_latin": class_latin,
        "tax_order_vn": tax.get("order", {}).get("vn", "") if isinstance(tax.get("order"), dict) else "",
        "tax_order_latin": order_latin,
        "tax_family_vn": tax.get("family", {}).get("vn", "") if isinstance(tax.get("family"), dict) else "",
        "tax_family_latin": tax.get("family", {}).get("latin", "") if isinstance(tax.get("family"), dict) else "",
        "tax_genus_vn": tax.get("genus", {}).get("vn", "") if isinstance(tax.get("genus"), dict) else "",
        "tax_genus_latin": tax.get("genus", {}).get("latin", "") if isinstance(tax.get("genus"), dict) else "",
        # Specs VN
        "vn_size": vn.get("size", ""),
        "vn_distribution": vn.get("distribution", ""),
        "vn_specimen": vn.get("specimen", ""),
        "vn_status": vn.get("status", ""),
        "vn_literature": vn.get("literature", ""),
        # Specs EN
        "en_size": en.get("size", ""),
        "en_distribution": en.get("distribution", ""),
        "en_specimen": en.get("specimen", ""),
        "en_status": en.get("status", ""),
        "en_literature": en.get("literature", ""),
        # Conservation
        "conservation_status": sp.get("status", "unknown") or "unknown",
        # Synonyms
        "synonyms": json.dumps(syns, ensure_ascii=False),
        # WoRMS
        "worms_status": worms.get("status", ""),
        "worms_accepted_name": worms.get("acceptedName", ""),
        "worms_id": worms.get("wormsId") or None,
    }


def upsert_batch(rows, batch_num):
    """UPSERT a batch of rows via PostgREST"""
    url = f"{SUPABASE_URL}/rest/v1/species"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    
    # Clean None values → empty strings for text fields
    for row in rows:
        for k, v in row.items():
            if v is None and k not in ("worms_id", "worms_synced_at"):
                row[k] = ""
    
    data = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  ✗ Batch {batch_num} lỗi {e.code}: {body[:300]}")
        return e.code


def main():
    # Load data
    species_path = os.path.join(BASE, "data", "species.json")
    fishbase_path = os.path.join(BASE, "data", "fishbase_sync.json")
    
    with open(species_path, "r", encoding="utf-8") as f:
        species_list = json.load(f)
    print(f"Loaded {len(species_list)} species from species.json")
    
    # Build WoRMS lookup (keyed by species id like "tap1-species-11")
    worms_lookup = {}
    if os.path.exists(fishbase_path):
        with open(fishbase_path, "r", encoding="utf-8") as f:
            fishbase = json.load(f)
        if isinstance(fishbase, dict):
            worms_lookup = fishbase
        print(f"Loaded {len(worms_lookup)} WoRMS records from fishbase_sync.json")
    
    # Flatten all + deduplicate by id (keep last)
    raw_rows = [flatten_species(sp, worms_lookup) for sp in species_list]
    seen = {}
    for r in raw_rows:
        seen[r['id']] = r
    rows = list(seen.values())
    print(f"Flattened {len(raw_rows)} rows → {len(rows)} unique")
    
    # Validate conservation_status
    valid_statuses = {"common", "uncommon", "rare", "unknown"}
    for r in rows:
        if r["conservation_status"] not in valid_statuses:
            r["conservation_status"] = "unknown"
    
    # Upsert in batches of 100
    BATCH = 100
    success = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        batch_num = i // BATCH + 1
        status = upsert_batch(batch, batch_num)
        if status in (200, 201):
            success += len(batch)
            vol_counts = {}
            for r in batch:
                v = r["volume"]
                vol_counts[v] = vol_counts.get(v, 0) + 1
            detail = ", ".join(f"T{v}:{c}" for v, c in sorted(vol_counts.items()))
            print(f"  ✓ Batch {batch_num}: {len(batch)} rows ({detail})")
        
    print(f"\n{'='*50}")
    print(f"✓ Import hoàn tất: {success}/{len(rows)} rows")
    
    # Verify
    verify_url = f"{SUPABASE_URL}/rest/v1/species?select=volume,id&limit=1"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    req = urllib.request.Request(verify_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        if data:
            print(f"✓ Verify: bảng species có data (sample: {data[0]['id']})")


if __name__ == "__main__":
    main()
