"""
build_database.py — Gom dữ liệu OCR từ tất cả các tập vào species.json
và taxonomy_tree.json cho web app.

Nguồn dữ liệu:
  - data/parsed/tap1_from_html.json   (list)
  - data/parsed/tap2_from_html.json   (list)
  - data/parsed/tap3_parsed_details.json  (dict, keys = "1".."518")
  - data/parsed/tap4_parsed_details.json  (list)
  - data/parsed/tap5_parsed_details.json  (list)

Schema đầu ra (species.json) — khớp với species.html:
{
  id, volume, speciesIndex, vnName, scientificName, authorship,
  taxonomy: { order: {vn, latin}, family: {vn, latin}, genus: {vn, latin} },
  specs: {
    vn: { alternateNames, size, distribution, specimen, status, literature },
    en: { commonName, size, distribution, specimen, status, literature }
  },
  synonyms: [...],   // list of strings
  status              // "common" | "uncommon" | ...
}
"""
import json
import os
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
PARSED = os.path.join(DATA, "parsed")

OUTPUT_SPECIES = os.path.join(DATA, "species.json")
OUTPUT_TAXONOMY = os.path.join(DATA, "taxonomy_tree.json")


def clean(val):
    if not val:
        return ""
    if isinstance(val, list):
        return val
    v = str(val).strip()
    if v.upper() == "NULL":
        return ""
    return v


# ── Tap 3 normalizer ──────────────────────────────────────────────
def load_tap3():
    path = os.path.join(PARSED, "tap3_parsed_details.json")
    if not os.path.exists(path):
        return []
    raw = json.load(open(path, encoding="utf-8"))
    # raw is dict with string keys "1".."518"
    results = []
    for key in sorted(raw.keys(), key=lambda k: int(k)):
        sp = raw[key]
        vn_specs = sp.get("specs_vn", {})
        en_specs = sp.get("specs_en", {})
        tax_raw = sp.get("taxonomy", {})

        obj = {
            "id": f"tap3-species-{key}",
            "volume": 3,
            "speciesIndex": int(key),
            "vnName": clean(sp.get("vn_name", "")),
            "scientificName": clean(sp.get("sci_name", "")),
            "authorship": clean(sp.get("authorship", "")),
            "status": clean(sp.get("status_class", "")).replace("status-", "") or "unknown",
            "taxonomy": {
                "order": {
                    "vn": clean(tax_raw.get("order_vn", "")),
                    "latin": clean(tax_raw.get("order_lat", ""))
                },
                "family": {
                    "vn": clean(tax_raw.get("family_vn", "")),
                    "latin": clean(tax_raw.get("family_lat", ""))
                },
                "genus": {
                    "vn": clean(tax_raw.get("genus_vn", "")),
                    "latin": clean(tax_raw.get("genus_lat", ""))
                }
            },
            "specs": {
                "vn": {
                    "alternateNames": clean(vn_specs.get("Tên gọi khác", "")),
                    "size": clean(vn_specs.get("Kích thước", "")),
                    # ponytail: hai phiên bản key song song — fallback cả hai
                    "distribution": clean(vn_specs.get("Phân bố địa lý") or vn_specs.get("Phân bố", "")),
                    "specimen": clean(vn_specs.get("Nơi lưu trữ mẫu", "")),
                    "status": clean(vn_specs.get("Tình trạng mẫu vật") or vn_specs.get("Tình trạng", "")),
                    "literature": clean(vn_specs.get("Tài liệu dẫn", ""))
                },
                "en": {
                    "commonName": clean(en_specs.get("Common Name", "")),
                    "size": clean(en_specs.get("Size Specifications") or en_specs.get("Size", "")),
                    "distribution": clean(en_specs.get("Geographical Distribution") or en_specs.get("Distribution", "")),
                    "specimen": clean(en_specs.get("Specimen Conservation") or en_specs.get("Conservation", "")),
                    "status": clean(en_specs.get("Status", "")),
                    "literature": clean(en_specs.get("Literature Citations") or en_specs.get("Literature", ""))
                }
            },
            "synonyms": sp.get("synonyms", []) if isinstance(sp.get("synonyms"), list) else []
        }
        if obj["vnName"] and obj["scientificName"]:
            results.append(obj)
    return results


# ── Tap 4 & Tap 5 normalizer (same schema) ────────────────────────
def load_tap4_or_5(filename, volume):
    path = os.path.join(PARSED, filename)
    if not os.path.exists(path):
        return []
    raw = json.load(open(path, encoding="utf-8"))
    results = []
    for sp in raw:
        # Extract speciesIndex
        idx = sp.get("speciesIndex") or sp.get("stt") or 0

        # Taxonomy — already in { order: {vn, latin}, ... } format
        tax_raw = sp.get("taxonomy", {})
        tax = {}
        for rank in ("order", "family", "genus"):
            r = tax_raw.get(rank, {})
            if isinstance(r, dict):
                tax[rank] = {"vn": clean(r.get("vn", "")), "latin": clean(r.get("latin", ""))}
            else:
                tax[rank] = {"vn": "", "latin": ""}

        # Specs — already in { vn: {...}, en: {...} } format
        specs_raw = sp.get("specs", {})
        vn_raw = specs_raw.get("vn", {}) if isinstance(specs_raw, dict) else {}
        en_raw = specs_raw.get("en", {}) if isinstance(specs_raw, dict) else {}

        specs = {
            "vn": {
                "alternateNames": clean(vn_raw.get("alternateNames", "")),
                "size": clean(vn_raw.get("size", "")),
                "distribution": clean(vn_raw.get("distribution", "")),
                "specimen": clean(vn_raw.get("specimen", "")),
                "status": clean(vn_raw.get("status", "")),
                "literature": clean(vn_raw.get("literature", ""))
            },
            "en": {
                "commonName": clean(en_raw.get("commonName", en_raw.get("common_name", ""))),
                "size": clean(en_raw.get("size", "")),
                "distribution": clean(en_raw.get("distribution", "")),
                "specimen": clean(en_raw.get("specimen", en_raw.get("conservation", ""))),
                "status": clean(en_raw.get("status", "")),
                "literature": clean(en_raw.get("literature", ""))
            }
        }

        syns = sp.get("synonyms", [])
        if not isinstance(syns, list):
            syns = [syns] if syns else []

        obj = {
            "id": sp.get("id", f"tap{volume}-species-{idx}"),
            "volume": volume,
            "speciesIndex": int(idx),
            "vnName": clean(sp.get("vnName", "")),
            "scientificName": clean(sp.get("scientificName", "")),
            "authorship": clean(sp.get("authorship", "")),
            "status": clean(sp.get("status", "unknown")),
            "taxonomy": tax,
            "specs": specs,
            "synonyms": syns
        }
        if obj["vnName"] and obj["scientificName"]:
            results.append(obj)
    return results


# ── Taxonomy tree builder ──────────────────────────────────────────
def build_taxonomy_tree(all_species):
    """
    Xây dựng cây: Lớp > Bộ > Họ > Giống > Loài
    Vì dữ liệu không có Lớp, gộp tất cả vào Lớp Cá Xương.
    """
    tree = {}  # order_vn -> { family_vn -> { genus_vn -> [species] } }

    for sp in all_species:
        tax = sp.get("taxonomy", {})
        order_vn = tax.get("order", {}).get("vn", "") or "Chưa phân loại"
        order_lat = tax.get("order", {}).get("latin", "")
        family_vn = tax.get("family", {}).get("vn", "") or "Chưa phân loại"
        family_lat = tax.get("family", {}).get("latin", "")
        genus_vn = tax.get("genus", {}).get("vn", "") or "Chưa phân loại"
        genus_lat = tax.get("genus", {}).get("latin", "")

        order_key = f"{order_vn}|{order_lat}"
        family_key = f"{family_vn}|{family_lat}"
        genus_key = f"{genus_vn}|{genus_lat}"

        if order_key not in tree:
            tree[order_key] = {}
        if family_key not in tree[order_key]:
            tree[order_key][family_key] = {}
        if genus_key not in tree[order_key][family_key]:
            tree[order_key][family_key][genus_key] = []

        tree[order_key][family_key][genus_key].append({
            "id": sp["id"],
            "vnName": sp["vnName"],
            "scientificName": sp["scientificName"]
        })

    # Convert to nested list format for browse.html
    result = []
    # Wrap everything in a single "Lớp Cá Xương" node
    class_node = {
        "vn": "Cá Xương",
        "latin": "Osteichthyes",
        "children": []
    }

    for order_key in sorted(tree.keys()):
        parts = order_key.split("|", 1)
        order_node = {"vn": parts[0], "latin": parts[1] if len(parts) > 1 else "", "children": []}

        for family_key in sorted(tree[order_key].keys()):
            fparts = family_key.split("|", 1)
            family_node = {"vn": fparts[0], "latin": fparts[1] if len(fparts) > 1 else "", "children": []}

            for genus_key in sorted(tree[order_key][family_key].keys()):
                gparts = genus_key.split("|", 1)
                genus_node = {
                    "vn": gparts[0],
                    "latin": gparts[1] if len(gparts) > 1 else "",
                    "species": tree[order_key][family_key][genus_key]
                }
                family_node["children"].append(genus_node)

            order_node["children"].append(family_node)

        class_node["children"].append(order_node)

    result.append(class_node)
    return result


# ── Main ───────────────────────────────────────────────────────────
def build_database():
    all_species = []

    # Load Tap 1 from translated JSON files in data/parsed/
    for vol in [1]:
        path = os.path.join(PARSED, f"tap{vol}_from_html.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                species = json.load(f)
            print(f"Tập {vol} (JSON):  {len(species)} loài")
            all_species.extend(species)
        else:
            print(f"Tập {vol}: file not found, skipping")

    # Load Tap 2
    tap2 = load_tap4_or_5("tap2_parsed_details.json", 2)
    print(f"Tập II:  {len(tap2)} loài")
    all_species.extend(tap2)

    # Load Tap 3
    tap3 = load_tap3()
    print(f"Tập III: {len(tap3)} loài")
    all_species.extend(tap3)

    # Load Tap 4
    tap4 = load_tap4_or_5("tap4_parsed_details.json", 4)
    print(f"Tập IV:  {len(tap4)} loài")
    all_species.extend(tap4)

    # Sort by volume, then speciesIndex
    all_species.sort(key=lambda s: (s["volume"], s["speciesIndex"]))

    # Write species.json
    with open(OUTPUT_SPECIES, "w", encoding="utf-8") as f:
        json.dump(all_species, f, ensure_ascii=False, indent=2)

    # Build and write taxonomy tree
    tree = build_taxonomy_tree(all_species)
    with open(OUTPUT_TAXONOMY, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Tổng cộng: {len(all_species)} loài → {OUTPUT_SPECIES}")
    print(f"✓ Cây phân loại → {OUTPUT_TAXONOMY}")


if __name__ == "__main__":
    build_database()
