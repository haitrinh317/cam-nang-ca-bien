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

SUPABASE_URL = "https://cjxqogvtzrvnlsssnfob.supabase.co"
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHFvZ3Z0enJ2bmxzc3NuZm9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzOTUxNjIsImV4cCI6MjEwMDk3MTE2Mn0.HBi2zicdL9O7uMJD6r8IYPXI7ztHcv-5PsTdBwa65_I"
)

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


def flatten(sp: dict) -> dict:
    """Convert nested species.json record → flat Supabase row"""
    tax   = sp.get("taxonomy", {}) or {}
    specs = sp.get("specs", {}) or {}
    vn    = specs.get("vn", {}) if isinstance(specs, dict) else {}
    en    = specs.get("en", {}) if isinstance(specs, dict) else {}

    order_latin = ""
    if isinstance(tax.get("order"), dict):
        order_latin = tax["order"].get("latin", "")
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
        "species_index": sp.get("speciesIndex", 0),
        "vn_name":       sp.get("vnName", ""),
        "scientific_name": sp.get("scientificName", ""),
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
    }

    # Null → empty string for text fields
    for k, v in row.items():
        if v is None:
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

    rows = [flatten(r) for r in records]

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
