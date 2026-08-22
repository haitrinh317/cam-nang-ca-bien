"""
upsert_species.py — Nhận species records (JSON từ stdin hoặc file),
flatten sang flat schema và UPSERT thẳng vào Supabase.

Dùng: python scripts/upsert_species.py --file output.json
      cat output.json | python scripts/upsert_species.py
"""
import json
import sys
import os
import urllib.request
import urllib.error
import argparse

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Load .env ──
def _load_dotenv():
    env_path = os.path.join(BASE, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_dotenv()

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('✗ Missing SUPABASE_SERVICE_ROLE_KEY or SUPABASE_URL in .env', file=sys.stderr)
    sys.exit(1)


SUN_ORDERS = [
    "lamniformes","squaliformes","rajiformes","torpediniformes",
    "pristiophoriformes","heterodontiformes","hexanchiformes",
    "orectolobiformes","carcharhiniformes","dasyatiformes"
]

def get_class(order_latin: str):
    if not order_latin:
        return "Lớp Cá Xương", "Osteichthyes"
    ol = order_latin.lower().strip()
    if "amphioxiformes" in ol:
        return "Lớp Cá Lưỡng Tiêm", "Leptocardii"
    if any(o in ol for o in SUN_ORDERS):
        return "Lớp Cá Sụn", "Chondrichthyes"
    return "Lớp Cá Xương", "Osteichthyes"


def is_flat(sp: dict) -> bool:
    """Return True if record is already in flat Supabase schema (new OCR output).
    Flat records have direct flat keys like vn_name, tax_order_latin, etc.
    Nested records have taxonomy.* or specs.* dicts.
    """
    return (
        "taxonomy" not in sp and
        "specs" not in sp and
        ("vn_name" in sp or "scientific_name" in sp)
    )


def normalize_flat(sp: dict) -> dict:
    """Light normalization for already-flat records from ocr-sinhvat-bien."""
    syns = sp.get("synonyms", [])
    if not isinstance(syns, list):
        syns = [syns] if syns else []

    cs = sp.get("conservation_status", "unknown") or "unknown"
    if cs not in ("common", "uncommon", "rare", "unknown"):
        cs = "unknown"

    row = dict(sp)  # copy
    row["synonyms"] = json.dumps(syns, ensure_ascii=False)
    row["conservation_status"] = cs
    row.setdefault("collection_id", "ca-bien")

    # Infer tax_class for ca-bien if missing
    if row.get("collection_id") == "ca-bien" and not row.get("tax_class_vn"):
        class_vn, class_latin = get_class(row.get("tax_order_latin", ""))
        row["tax_class_vn"] = class_vn
        row["tax_class_latin"] = class_latin

    # Null → empty string for text fields, keep worms_id/biology as None
    for k, v in row.items():
        if v is None and k not in ("worms_id", "biology"):
            row[k] = ""

    return row


def flatten(sp: dict) -> dict:
    """Convert nested species.json record → flat Supabase row"""
    tax   = sp.get("taxonomy", {}) or {}
    specs = sp.get("specs", {}) or {}
    vn    = specs.get("vn", {}) if isinstance(specs, dict) else {}
    en    = specs.get("en", {}) if isinstance(specs, dict) else {}

    collection_id = sp.get("collection_id", "ca-bien")
    
    class_vn = t(tax.get("class", {}), "vn") if isinstance(tax.get("class"), dict) else ""
    class_latin = t(tax.get("class", {}), "latin") if isinstance(tax.get("class"), dict) else ""

    order_latin = ""
    if isinstance(tax.get("order"), dict):
        order_latin = tax["order"].get("latin", "")
        
    if not class_vn and not class_latin and collection_id == "ca-bien":
        class_vn, class_latin = get_class(order_latin)

    syns = sp.get("synonyms", [])
    if not isinstance(syns, list):
        syns = [syns] if syns else []

    cs = sp.get("status", "unknown") or "unknown"
    if cs not in ("common", "uncommon", "rare", "unknown"):
        cs = "unknown"

    def t(d, k): return d.get(k, "") if isinstance(d, dict) else ""

    row = {
        "id":            sp.get("id", ""),
        "volume":        sp.get("volume", 0),
        "species_index": sp.get("speciesIndex", 0) or sp.get("species_index", 0),
        "vn_name":       sp.get("vnName", "") or sp.get("vn_name", ""),
        "scientific_name": sp.get("scientificName", "") or sp.get("scientific_name", ""),
        "authorship":    sp.get("authorship", ""),
        "en_common_name": t(en, "commonName"),
        "vn_alternate_names": t(vn, "alternateNames"),
        # Taxonomy
        "tax_class_vn":    class_vn,
        "tax_class_latin": class_latin,
        "tax_order_vn":    t(tax.get("order", {}), "vn"),
        "tax_order_latin": order_latin,
        "tax_family_vn":   t(tax.get("family", {}), "vn") if isinstance(tax.get("family"), dict) else "",
        "tax_family_latin":t(tax.get("family", {}), "latin") if isinstance(tax.get("family"), dict) else "",
        "tax_genus_vn":    t(tax.get("genus", {}), "vn") if isinstance(tax.get("genus"), dict) else "",
        "tax_genus_latin": t(tax.get("genus", {}), "latin") if isinstance(tax.get("genus"), dict) else "",
        # Specs VN
        "vn_size":        t(vn, "size"),
        "vn_distribution":t(vn, "distribution"),
        "vn_specimen":    t(vn, "specimen"),
        "vn_status":      t(vn, "status"),
        "vn_literature":  t(vn, "literature"),
        # Specs EN
        "en_size":        t(en, "size"),
        "en_distribution":t(en, "distribution"),
        "en_specimen":    t(en, "specimen"),
        "en_status":      t(en, "status"),
        "en_literature":  t(en, "literature"),
        # Conservation
        "conservation_status": cs,
        "synonyms": json.dumps(syns, ensure_ascii=False),
        "worms_status": sp.get("worms_status", ""),
        "worms_accepted_name": sp.get("worms_accepted_name", ""),
        "worms_id": sp.get("worms_id", None),
        # Morphology — seaweed: from OCR, fish: from FishBase enrichment
        "morphology_vn": t(vn, "morphology") if t(vn, "morphology") else sp.get("morphology_vn", ""),
        "morphology_en": t(en, "morphology") if t(en, "morphology") else sp.get("morphology_en", ""),
        # Photo metadata — shared across all collections
        "photo_place": sp.get("photo_place", "") or sp.get("photoPlace", ""),
        "photo_depth": sp.get("photo_depth", "") or sp.get("photoDepth", ""),
        "photo_date": sp.get("photo_date", "") or sp.get("photoDate", ""),
        # Biology — FishBase + GBIF enrichment (JSONB, nullable)
        # "biology": sp.get("biology") or None,
        # Collection (default: ca-bien)
        "collection_id": sp.get("collection_id", "ca-bien"),
    }

    # Null → empty string for text fields, but keep worms_id and biology as None
    for k, v in row.items():
        if v is None and k not in ("worms_id", "biology", "collection_id"):
            row[k] = ""

    return row


def upsert(rows: list) -> int:
    url = f"{SUPABASE_URL}/rest/v1/species"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    data = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  ✗ HTTP {e.code}: {body[:300]}", file=sys.stderr)
        return e.code


def main():
    parser = argparse.ArgumentParser(description="Upsert species records to Supabase")
    parser.add_argument("--file", "-f", help="JSON file (list of species records). Default: stdin")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = json.load(sys.stdin)

    if isinstance(records, dict):
        records = [records]   # single record

    # Auto-detect flat vs nested schema
    flat_count = sum(1 for r in records if is_flat(r))
    nested_count = len(records) - flat_count
    if flat_count and nested_count:
        print(f"  ℹ Mixed: {flat_count} flat + {nested_count} nested records")
    elif flat_count:
        print(f"  ℹ Flat schema detected ({flat_count} records) — direct upsert")
    else:
        print(f"  ℹ Nested schema detected ({nested_count} records) — flattening...")

    rows = [normalize_flat(r) if is_flat(r) else flatten(r) for r in records]


    # Deduplicate by id
    seen = {}
    for r in rows:
        seen[r["id"]] = r
    rows = list(seen.values())

    print(f"Upserting {len(rows)} records to Supabase...")
    status = upsert(rows)

    if status in (200, 201):
        print(f"✅ Done: {len(rows)} records upserted")
        for r in rows:
            print(f"  • {r['id']} — {r['vn_name']} ({r['scientific_name']})")
    else:
        print(f"✗ Failed: HTTP {status}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
