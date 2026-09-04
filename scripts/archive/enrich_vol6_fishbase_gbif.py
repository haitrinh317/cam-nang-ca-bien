"""
enrich_vol6_fishbase_gbif.py
-----------------------------
Đồng bộ dữ liệu Sinh học (Biology), Hình thái EN (Morphology EN), Sinh thái EN (Ecology EN),
Giá trị kinh tế EN (Economic Value EN), và IUCN Status từ FishBase + GBIF cho Tập 6 (Atlas cá rạn san hô).

Nguồn:
- FishBase v25.04 (Local Parquet)
- GBIF API (https://api.gbif.org/v1)

Chạy:
  uv run --with duckdb python scripts/enrich_vol6_fishbase_gbif.py
"""

import json
import os
import sys
import ssl
import time
import urllib.request
import urllib.parse
import urllib.error
import duckdb

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
CACHE_DIR = os.path.join(BASE, "data", "fishbase_cache")
GBIF_BASE = "https://api.gbif.org/v1"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env")
    sys.exit(1)

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

USEFUL_TYPES = ("diagnosis", "description", "biology", "habitat")

# ─── GBIF helpers ─────────────────────────────────────────────────────────────

def gbif_get(path: str):
    url = f"{GBIF_BASE}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes-SyncBot/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def get_gbif_data(sci_name: str):
    """Lấy IUCN status và descriptions từ GBIF theo tên khoa học"""
    parts = sci_name.strip().split()
    if len(parts) < 2:
        return None, None
    canonical = f"{parts[0]} {parts[1]}"
    match_data = gbif_get(f"species/match?name={urllib.parse.quote(canonical)}&kingdom=Animalia")
    if not match_data or match_data.get("matchType") == "NONE":
        return None, None

    key = match_data.get("speciesKey") or match_data.get("usageKey")
    iucn = match_data.get("iucnRedListCategory")

    description = None
    if key:
        desc_data = gbif_get(f"species/{key}/descriptions")
        if desc_data and desc_data.get("results"):
            for pref_type in USEFUL_TYPES:
                for r in desc_data["results"]:
                    if r.get("type", "").lower() == pref_type and r.get("language", "").lower() in ("eng", "en", ""):
                        txt = r.get("description", "").strip()
                        if txt and len(txt) > 60:
                            description = txt[:2000]
                            break
                if description:
                    break
    return iucn, description

# ─── FishBase Lookups ─────────────────────────────────────────────────────────

def build_fishbase_lookups():
    print("[1] Đọc dữ liệu FishBase Parquet...")
    con = duckdb.connect()
    sp_path = os.path.join(CACHE_DIR, "species.parquet")
    eco_path = os.path.join(CACHE_DIR, "ecology.parquet")
    rep_path = os.path.join(CACHE_DIR, "reproduc.parquet")

    # Species
    sp_rows = con.execute(f"""
        SELECT SpecCode, Genus, Species, FBname, Length, LTypeMaxM, Weight,
               DepthRangeShallow, DepthRangeDeep,
               LongevityWild, Vulnerability, Importance,
               PriceCateg, UsedforAquaculture, Dangerous, Comments
        FROM '{sp_path}'
    """).fetchall()
    cols_sp = [c[0] for c in con.description]
    sp_map = {int(r[0]): dict(zip(cols_sp, r)) for r in sp_rows if r[0] is not None}

    # Ecology
    eco_rows = con.execute(f"""
        SELECT SpecCode, FeedingType, DietTroph,
               Neritic, Estuaries, Mangroves, CoralReefs,
               Benthic, SoftBottom, Mud, Rocky, Rubble,
               AddRems
        FROM '{eco_path}'
    """).fetchall()
    cols_eco = [c[0] for c in con.description]
    eco_map = {}
    for r in eco_rows:
        if r[0] is not None and int(r[0]) not in eco_map:
            eco_map[int(r[0])] = dict(zip(cols_eco, r))

    # Reproduc
    rep_rows = con.execute(f"""
        SELECT SpecCode, ReproMode, Fertilization,
               SpawnAgg, Spawning, RepGuild1, RepGuild2,
               ParentalCare, AddInfos
        FROM '{rep_path}'
    """).fetchall()
    cols_rep = [c[0] for c in con.description]
    rep_map = {}
    for r in rep_rows:
        if r[0] is not None and int(r[0]) not in rep_map:
            rep_map[int(r[0])] = dict(zip(cols_rep, r))

    # Name Index (genus + species -> SpecCode)
    name_index = {}
    for sc, row in sp_map.items():
        g = (row.get("Genus") or "").strip().lower()
        s = (row.get("Species") or "").strip().lower()
        if g and s:
            name_index[f"{g} {s}"] = sc

    con.close()
    print(f"  ✓ Đã nạp {len(sp_map):,} loài FishBase, {len(eco_map):,} ecology records, {len(rep_map):,} reproduc records")
    return sp_map, eco_map, rep_map, name_index

def _clean(val):
    if val is None:
        return None
    s = str(val).strip()
    if s in ("None", "nan", "NaT", "NA", "<NA>", "", "-999", "-9999"):
        return None
    return s

def _flag(val):
    try:
        return int(val) == -1
    except (TypeError, ValueError):
        return False

def build_biology(spec_code: int, sp_map: dict, eco_map: dict, rep_map: dict) -> dict:
    bio = {"fbSpecCode": spec_code, "source": "FishBase v25.04"}
    sp = sp_map.get(spec_code, {})
    if sp:
        bio["fbName"] = _clean(sp.get("FBname"))
        max_len = _clean(sp.get("Length"))
        len_type = _clean(sp.get("LTypeMaxM")) or "TL"
        if max_len:
            bio["maxLength"] = f"{max_len} cm {len_type}"
        max_wt = _clean(sp.get("Weight"))
        if max_wt:
            bio["maxWeight"] = f"{float(max_wt):,.0f} g"
        lon = _clean(sp.get("LongevityWild"))
        if lon:
            bio["longevity"] = f"{lon} năm"
        d_min = _clean(sp.get("DepthRangeShallow"))
        d_max = _clean(sp.get("DepthRangeDeep"))
        if d_min and d_max:
            bio["depth"] = f"{d_min} - {d_max} m"
        elif d_max:
            bio["depth"] = f"đến {d_max} m"
        vuln = _clean(sp.get("Vulnerability"))
        if vuln:
            bio["vulnerability"] = float(vuln)
        imp = _clean(sp.get("Importance"))
        if imp:
            bio["importance"] = imp
        price = _clean(sp.get("PriceCateg"))
        if price:
            bio["priceCategory"] = price
        aqua = _clean(sp.get("UsedforAquaculture"))
        if aqua and aqua.lower() not in ("no", "none"):
            bio["aquaculture"] = aqua
        danger = _clean(sp.get("Dangerous"))
        if danger:
            bio["dangerous"] = danger
        comments = _clean(sp.get("Comments"))
        if comments:
            bio["biologySummary"] = comments

    eco = eco_map.get(spec_code, {})
    if eco:
        ft = _clean(eco.get("FeedingType"))
        if ft:
            bio["feedingType"] = ft
        troph = _clean(eco.get("DietTroph"))
        if troph:
            try:
                bio["trophicLevel"] = round(float(troph), 2)
            except ValueError:
                pass
        habitats = []
        if _flag(eco.get("Neritic")):    habitats.append("Neritic")
        if _flag(eco.get("Estuaries")):  habitats.append("Estuaries")
        if _flag(eco.get("Mangroves")):  habitats.append("Mangroves")
        if _flag(eco.get("CoralReefs")): habitats.append("Coral reefs")
        if _flag(eco.get("Benthic")):    habitats.append("Benthic")
        if _flag(eco.get("SoftBottom")): habitats.append("Soft bottom")
        if _flag(eco.get("Mud")):        habitats.append("Mud")
        if _flag(eco.get("Rocky")):      habitats.append("Rocky")
        if _flag(eco.get("Rubble")):     habitats.append("Rubble")
        if habitats:
            bio["habitat"] = ", ".join(habitats)
        eco_notes = _clean(eco.get("AddRems"))
        if eco_notes:
            bio["ecologyNotes"] = eco_notes

    rep = rep_map.get(spec_code, {})
    if rep:
        mode = _clean(rep.get("ReproMode"))
        fert = _clean(rep.get("Fertilization"))
        parts = []
        if mode: parts.append(mode)
        if fert: parts.append(f"{fert} fertilization")
        if parts: bio["reproduction"] = ", ".join(parts)
        spawn = _clean(rep.get("Spawning"))
        if spawn: bio["spawning"] = spawn
        if _flag(rep.get("SpawnAgg")) or str(rep.get("SpawnAgg")) == "-1":
            bio["spawnAggregation"] = True
        care = _clean(rep.get("ParentalCare"))
        if care and care.lower() != "none":
            bio["parentalCare"] = care
        add_rep = _clean(rep.get("AddInfos"))
        if add_rep: bio["reproductionNotes"] = add_rep

    return bio

# ─── Main Pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ENRICHMENT GIAI ĐOẠN B CHO TẬP 6 (Atlas cá rạn san hô Việt Nam)")
    print("=" * 70)

    sp_map, eco_map, rep_map, name_index = build_fishbase_lookups()

    # 1. Fetch species from Vol 6 Supabase
    print("\n[2] Lấy danh sách 263 loài Tập 6 từ Supabase...")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&select=*&order=species_index",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    )
    species_list = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(f"  ✓ Lấy được {len(species_list)} loài từ Supabase")

    # 2. Enrich each species
    matched_fb = 0
    matched_gbif = 0
    updated_count = 0

    print("\n[3] Bắt đầu xử lý từng loài...")
    for idx, sp in enumerate(species_list, 1):
        sp_id = sp["id"]
        sci_name = sp["scientific_name"]
        parts = sci_name.strip().split()
        key = f"{parts[0].lower()} {parts[1].lower()}" if len(parts) >= 2 else ""

        spec_code = name_index.get(key)
        bio = {}
        if spec_code:
            bio = build_biology(spec_code, sp_map, eco_map, rep_map)
            matched_fb += 1

        # Query GBIF for IUCN status and description
        iucn_status, gbif_desc = get_gbif_data(sci_name)
        if iucn_status or gbif_desc:
            matched_gbif += 1
            if iucn_status:
                bio["iucnStatus"] = iucn_status
            if gbif_desc:
                bio["morphDescription"] = gbif_desc

        # Build fields to patch
        patch_data = {}
        if bio:
            patch_data["biology"] = bio

        # Build morphology_en if currently empty and available from GBIF/FishBase
        if not sp.get("morphology_en"):
            desc = bio.get("morphDescription") or bio.get("biologySummary")
            if desc:
                patch_data["morphology_en"] = desc

        # Build ecology_en if currently empty and available from FishBase
        if not sp.get("ecology_en"):
            eco_parts = []
            if bio.get("habitat"):
                eco_parts.append(f"Habitat: {bio['habitat']}")
            if bio.get("feedingType"):
                eco_parts.append(f"Feeding: {bio['feedingType']}")
            if bio.get("depth"):
                eco_parts.append(f"Depth range: {bio['depth']}")
            if bio.get("ecologyNotes"):
                eco_parts.append(bio["ecologyNotes"])
            if eco_parts:
                patch_data["ecology_en"] = ". ".join(eco_parts)

        # Build economic_value_en if currently empty and available from FishBase
        if not sp.get("economic_value_en"):
            econ_parts = []
            if bio.get("importance"):
                econ_parts.append(f"Commercial importance: {bio['importance']}")
            if bio.get("priceCategory"):
                econ_parts.append(f"Price category: {bio['priceCategory']}")
            if bio.get("aquaculture"):
                econ_parts.append(f"Aquaculture: {bio['aquaculture']}")
            if bio.get("vulnerability"):
                econ_parts.append(f"Vulnerability index: {bio['vulnerability']}/100")
            if econ_parts:
                patch_data["economic_value_en"] = ". ".join(econ_parts)

        # Build en_common_name if currently empty
        if not sp.get("en_common_name") and bio.get("fbName"):
            patch_data["en_common_name"] = bio["fbName"]

        if patch_data:
            # PATCH to Supabase
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            payload = json.dumps(patch_data, ensure_ascii=False).encode('utf-8')
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            patch_req = urllib.request.Request(patch_url, data=payload, headers=headers, method="PATCH")
            try:
                urllib.request.urlopen(patch_req)
                updated_count += 1
                status_str = f"FB✓ (Code: {spec_code})" if spec_code else "FB✗"
                if iucn_status: status_str += f" | IUCN: {iucn_status}"
                print(f"  [{idx:3d}/{len(species_list)}] {sci_name:35s} -> {status_str}")
            except Exception as e:
                print(f"  [{idx:3d}/{len(species_list)}] {sci_name:35s} -> Lỗi PATCH: {e}")
        else:
            print(f"  [{idx:3d}/{len(species_list)}] {sci_name:35s} -> Không tìm thấy thêm dữ liệu")

        time.sleep(0.1) # Be respectful to GBIF API

    print("\n" + "=" * 70)
    print(f"HOÀN TẤT ENRICHMENT TẬP 6:")
    print(f"  - Tổng số loài xử lý : {len(species_list)}")
    print(f"  - Khớp FishBase      : {matched_fb}/{len(species_list)} ({matched_fb/len(species_list)*100:.1f}%)")
    print(f"  - Khớp GBIF          : {matched_gbif}/{len(species_list)} ({matched_gbif/len(species_list)*100:.1f}%)")
    print(f"  - Số loài cập nhật   : {updated_count}/{len(species_list)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
