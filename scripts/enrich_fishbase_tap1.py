"""
scripts/enrich_fishbase_tap1.py
--------------------------------
Enrich dữ liệu sinh học FishBase cho Danh mục Cá biển Tập 1 (Lớp Cá sụn Chondrichthyes).
Khắc phục triệt để lỗi lệch danh pháp nhờ cơ chế đối chiếu 3 tầng:
  1. Bảng đối chiếu đồng danh thủ công (Manual Synonyms)
  2. Tên khoa học gốc (scientific_name)
  3. Danh pháp hợp lệ WoRMS (worms_accepted_name)

Tự động dịch thuật các đoạn mô tả sinh thái/sinh học sang tiếng Việt chuẩn mực
thông qua Gemini AI (gemini-3.6-flash).

Cách chạy:
  # Chạy thử 3 loài (không ghi DB):
  uv run --with duckdb python scripts/enrich_fishbase_tap1.py --dry-run --limit 3

  # Chạy 1 loài cụ thể:
  uv run --with duckdb python scripts/enrich_fishbase_tap1.py --id tap1-species-50

  # Chạy toàn bộ Tập 1:
  uv run --with duckdb python scripts/enrich_fishbase_tap1.py
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
import duckdb

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. Cấu hình Môi trường ──────────────────────────────────────────────────
def load_env():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SPECIES_FILE = os.path.join(BASE_DIR, 'data', 'species.json')
CACHE_DIR = os.path.join(BASE_DIR, 'data', 'fishbase_cache')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env", file=sys.stderr)
    sys.exit(1)

# ── 2. Dữ liệu FishBase Parquet ─────────────────────────────────────────────
PARQUET_SPECIES = os.path.join(CACHE_DIR, 'species.parquet')
PARQUET_ECOLOGY = os.path.join(CACHE_DIR, 'ecology.parquet')
PARQUET_REPRODUC = os.path.join(CACHE_DIR, 'reproduc.parquet')

# Manual map cho các loài có danh pháp đồng danh phức tạp
MANUAL_OVERRIDE = {
    'Negogaleus longicaudatus': 57442, # Paragaleus longicaudatus (Slender weasel shark)
}

# ── 3. Gemini Models & System Prompt ─────────────────────────────────────────
GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

SYSTEM_PROMPT = """Bạn là chuyên gia hàng đầu về Ngư loại học (Ichthyology) và Sinh học biển tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, sinh sản của các loài cá biển (đặc biệt là Lớp Cá sụn: cá mập, cá nhám, cá đuối, cá đao) từ cơ sở dữ liệu FishBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu sinh học biển Việt Nam.
2. Dịch chuẩn xác các thuật ngữ ngư học:
   - 'continental shelf': thềm lục địa
   - 'insular shelf': thềm quanh đảo
   - 'demersal': tầng đáy (cá tầng đáy)
   - 'pelagic': tầng nổi / biển khơi
   - 'coastal-pelagic': tầng nổi ven bờ
   - 'benthopelagic': tầng trung - đáy
   - 'bathydemersal': đáy sâu
   - 'reef-associated': liên kết rạn san hô / sống quanh rạn san hô
   - 'intertidal': vùng gian triều / bãi triều
   - 'subtidal': vùng dưới triều
   - 'lagoon': đầm phá / vụng san hô kín
   - 'estuary / estuarine': cửa sông / vùng nước lợ cửa sông
   - 'oviparous': đẻ trứng
   - 'viviparous': đẻ con (thai sinh)
   - 'ovoviviparous': noãn thai sinh
   - 'yolk-sac placenta': nhau thai túi noãn hoàng
   - 'litter': lứa đẻ / lứa con
   - 'pups': cá con / con non (đối với cá mập, cá đuối)
   - 'parturition': sinh sản / đẻ con
   - 'filter-feeding': ăn lọc
   - 'carnivorous': ăn thịt
   - 'feeds on...': thức ăn chủ yếu gồm...
   - 'inshore / offshore': ven bờ / ngoài khơi
3. Giữ nguyên danh pháp khoa học La-tinh (in nghiêng nếu có thể).
4. Câu văn mạch lạc, tránh dịch cứng nhắc từng từ kiểu máy dịch thô.
5. Chỉ trả về một JSON duy nhất theo đúng cấu trúc yêu cầu, không kèm markdown hay lời dẫn."""

# ── 4. Helpers Xử lý Dữ liệu ────────────────────────────────────────────────
def clean_val(val):
    if val is None:
        return None
    s = str(val).strip()
    if s in ("None", "nan", "NaT", "NA", "<NA>", "", "-999", "-9999"):
        return None
    return s

def flag_val(val):
    try:
        return int(val) == -1
    except (TypeError, ValueError):
        return False

def load_fishbase_maps():
    """Nạp dữ liệu FishBase từ Parquet vào bộ nhớ."""
    print("  [FishBase] Nạp dữ liệu Parquet từ cache...", flush=True)
    con = duckdb.connect()

    # species table
    sp_rows = con.execute(f"""
        SELECT SpecCode, Genus, Species, FBname, Length, LTypeMaxM, Weight,
               DepthRangeShallow, DepthRangeDeep, LongevityWild, Vulnerability,
               Importance, PriceCateg, UsedforAquaculture, Dangerous, Comments
        FROM '{PARQUET_SPECIES}'
    """).fetchall()
    cols_sp = [c[0] for c in con.description]
    species_map = {int(r[0]): dict(zip(cols_sp, r)) for r in sp_rows if r[0] is not None}

    # ecology table
    eco_rows = con.execute(f"""
        SELECT SpecCode, FeedingType, DietTroph,
               Neritic, Estuaries, Mangroves, CoralReefs,
               Benthic, SoftBottom, Mud, Rocky, Rubble, AddRems
        FROM '{PARQUET_ECOLOGY}'
    """).fetchall()
    cols_eco = [c[0] for c in con.description]
    ecology_map = {}
    for r in eco_rows:
        if r[0] is not None and int(r[0]) not in ecology_map:
            ecology_map[int(r[0])] = dict(zip(cols_eco, r))

    # reproduc table
    rep_rows = con.execute(f"""
        SELECT SpecCode, ReproMode, Fertilization,
               SpawnAgg, Spawning, ParentalCare, AddInfos
        FROM '{PARQUET_REPRODUC}'
    """).fetchall()
    cols_rep = [c[0] for c in con.description]
    reproduc_map = {}
    for r in rep_rows:
        if r[0] is not None and int(r[0]) not in reproduc_map:
            reproduc_map[int(r[0])] = dict(zip(cols_rep, r))

    con.close()

    # Build name index
    name_index = {}
    for sc, r in species_map.items():
        g = (r.get("Genus") or "").strip().lower()
        s = (r.get("Species") or "").strip().lower()
        if g and s:
            name_index[f"{g} {s}"] = sc

    print(f"  [FishBase] Đã nạp {len(species_map):,} loài, index: {len(name_index):,} tên.", flush=True)
    return species_map, ecology_map, reproduc_map, name_index

def find_spec_code(sci_name, worms_accepted, name_index):
    """Khớp tên khoa học -> SpecCode theo 3 cấp."""
    if sci_name in MANUAL_OVERRIDE:
        return MANUAL_OVERRIDE[sci_name]

    # 1. Thử sci_name gốc
    if sci_name:
        parts = sci_name.strip().lower().split()
        if len(parts) >= 2:
            key = f"{parts[0]} {parts[1]}"
            if key in name_index:
                return name_index[key]

    # 2. Thử worms_accepted_name
    if worms_accepted:
        parts = worms_accepted.strip().lower().split()
        if len(parts) >= 2:
            key = f"{parts[0]} {parts[1]}"
            if key in name_index:
                return name_index[key]

    return None

def build_fishbase_biology(spec_code, sp_map, eco_map, rep_map):
    """Trích xuất dict biology hoàn chỉnh từ 3 bảng FishBase."""
    bio = {"fbSpecCode": spec_code, "source": "FishBase v25.04"}

    sp = sp_map.get(spec_code, {})
    if sp:
        fb_name = clean_val(sp.get("FBname"))
        if fb_name:
            bio["fbName"] = fb_name

        max_len = clean_val(sp.get("Length"))
        len_type = clean_val(sp.get("LTypeMaxM")) or "TL"
        if max_len:
            try:
                bio["maxLength"] = f"{float(max_len):.1f} cm {len_type}"
            except ValueError:
                bio["maxLength"] = f"{max_len} cm {len_type}"

        max_wt = clean_val(sp.get("Weight"))
        if max_wt:
            try:
                bio["maxWeight"] = f"{float(max_wt):,.0f} g"
            except ValueError:
                bio["maxWeight"] = f"{max_wt} g"

        lon = clean_val(sp.get("LongevityWild"))
        if lon:
            bio["longevity"] = f"{lon} năm"

        d_min = clean_val(sp.get("DepthRangeShallow"))
        d_max = clean_val(sp.get("DepthRangeDeep"))
        if d_min and d_max:
            bio["depth"] = f"{d_min} - {d_max} m"
        elif d_max:
            bio["depth"] = f"đến {d_max} m"

        vuln = clean_val(sp.get("Vulnerability"))
        if vuln:
            try:
                bio["vulnerability"] = float(vuln)
            except ValueError:
                pass

        imp = clean_val(sp.get("Importance"))
        if imp:
            bio["importance"] = imp

        price = clean_val(sp.get("PriceCateg"))
        if price:
            bio["priceCategory"] = price

        aqua = clean_val(sp.get("UsedforAquaculture"))
        if aqua and aqua.lower() not in ("no", "none"):
            bio["aquaculture"] = aqua

        danger = clean_val(sp.get("Dangerous"))
        if danger:
            bio["dangerous"] = danger

        comments = clean_val(sp.get("Comments"))
        if comments:
            bio["biologySummary"] = comments

    eco = eco_map.get(spec_code, {})
    if eco:
        ft = clean_val(eco.get("FeedingType"))
        if ft:
            bio["feedingType"] = ft

        troph = clean_val(eco.get("DietTroph"))
        if troph:
            try:
                bio["trophicLevel"] = round(float(troph), 2)
            except ValueError:
                pass

        habitats = []
        if flag_val(eco.get("Neritic")):    habitats.append("Neritic")
        if flag_val(eco.get("Estuaries")):  habitats.append("Estuaries")
        if flag_val(eco.get("Mangroves")):  habitats.append("Mangroves")
        if flag_val(eco.get("CoralReefs")): habitats.append("Coral reefs")
        if flag_val(eco.get("Benthic")):    habitats.append("Benthic")
        if flag_val(eco.get("SoftBottom")): habitats.append("Soft bottom")
        if flag_val(eco.get("Mud")):        habitats.append("Mud")
        if flag_val(eco.get("Rocky")):      habitats.append("Rocky")
        if flag_val(eco.get("Rubble")):     habitats.append("Rubble")
        if habitats:
            bio["habitat"] = ", ".join(habitats)

        eco_notes = clean_val(eco.get("AddRems"))
        if eco_notes:
            bio["ecologyNotes"] = eco_notes

    rep = rep_map.get(spec_code, {})
    if rep:
        mode = clean_val(rep.get("ReproMode"))
        fert = clean_val(rep.get("Fertilization"))
        parts = []
        if mode:
            parts.append(mode)
        if fert:
            parts.append(f"{fert} fertilization")
        if parts:
            bio["reproduction"] = ", ".join(parts)

        spawn = clean_val(rep.get("Spawning"))
        if spawn:
            bio["spawning"] = spawn

        if flag_val(rep.get("SpawnAgg")) or str(rep.get("SpawnAgg")) == "-1":
            bio["spawnAggregation"] = True

        care = clean_val(rep.get("ParentalCare"))
        if care and care.lower() != "none":
            bio["parentalCare"] = care

        add_rep = clean_val(rep.get("AddInfos"))
        if add_rep:
            bio["reproductionNotes"] = add_rep

    return bio

# ── 5. Dịch Thuật Gemini AI ──────────────────────────────────────────────────
def translate_biology_fields(vn_name, sci_name, bio):
    """Dịch biologySummary, ecologyNotes, reproductionNotes sang tiếng Việt."""
    targets = {}
    if bio.get("biologySummary"):
        targets["biologySummary"] = bio["biologySummary"]
    if bio.get("ecologyNotes"):
        targets["ecologyNotes"] = bio["ecologyNotes"]
    if bio.get("reproductionNotes"):
        targets["reproductionNotes"] = bio["reproductionNotes"]

    if not targets:
        return {}

    user_text = f"""Loài sinh vật biển: {vn_name} ({sci_name})
Dưới đây là các đoạn văn bản tiếng Anh cần dịch sang tiếng Việt khoa học chuẩn mực:
{json.dumps(targets, ensure_ascii=False, indent=2)}

Trả về JSON có dạng:
{{
  "biologySummaryVn": "...",
  "ecologyNotesVn": "...",
  "reproductionNotesVn": "..."
}}
(Chỉ trả về các trường có trong văn bản gốc)."""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_text}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    data_bytes = json.dumps(payload).encode('utf-8')

    for model_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    resp_json = json.loads(resp.read().decode('utf-8'))
                    raw_text = resp_json['candidates'][0]['content']['parts'][0]['text'].strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    parsed = json.loads(raw_text.strip())
                    return parsed
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_sec = (attempt + 1) * 10
                    print(f" [Rate-limit 429, chờ {wait_sec}s]...", end=" ", flush=True)
                    time.sleep(wait_sec)
                    continue
                elif e.code in (500, 503):
                    time.sleep(5)
                    continue
                break
            except Exception as ex:
                time.sleep(2)
                continue

    return {}

# ── 6. Cập nhật Supabase & Local ─────────────────────────────────────────────
def patch_supabase_species(species_id, biology, en_common_name=None):
    """Cập nhật trực tiếp vào Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{species_id}"
    patch_body = {"biology": biology}
    if en_common_name:
        patch_body["en_common_name"] = en_common_name

    payload = json.dumps(patch_body, ensure_ascii=False).encode("utf-8")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"  [ERROR] Lỗi PATCH Supabase cho loài {species_id}: {e}", file=sys.stderr)
        return False

# ── 7. Main Runner ───────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Enrich FishBase biology cho Danh mục Cá biển Tập 1")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử nghiệm, không ghi Supabase")
    parser.add_argument("--limit", type=int, default=0, help="Giới hạn số loài xử lý")
    parser.add_argument("--id", type=str, default="", help="Chỉ chạy một loài cụ thể")
    parser.add_argument("--missing-vn", action="store_true", help="Dịch bổ sung cho các loài thiếu biologySummaryVn")
    args = parser.parse_args()

    print("=" * 70)
    print("ENRICH THÔNG TIN FISHBASE — DANH MỤC CÁ BIỂN TẬP 1")
    print("=" * 70)

    # 1. Nạp FishBase maps
    sp_map, eco_map, rep_map, name_index = load_fishbase_maps()

    # 2. Lấy dữ liệu Tập 1 từ Supabase
    print("\n[1] Lấy danh sách loài Tập 1 từ Supabase...", end=" ", flush=True)
    query_url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.1&select=id,scientific_name,vn_name,en_common_name,biology,worms_accepted_name"
    if args.id:
        query_url += f"&id=eq.{args.id}"
    query_url += "&order=species_index.asc"

    req = urllib.request.Request(query_url, headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'})
    with urllib.request.urlopen(req) as resp:
        species_list = json.loads(resp.read().decode('utf-8'))
    print(f"Đã lấy {len(species_list)} loài.")

    # Lọc loài cần xử lý
    if args.id:
        targets = species_list
    elif args.missing_vn:
        targets = [s for s in species_list if (s.get('biology') or {}).get('biologySummary') and not (s.get('biology') or {}).get('biologySummaryVn')]
    else:
        targets = [s for s in species_list if not (s.get('biology') or {}).get('fbSpecCode')]

    if args.limit > 0:
        targets = targets[:args.limit]

    print(f"[2] Số loài cần enrich FishBase: {len(targets)}")
    print("-" * 70)

    # Nạp file local backup
    local_species = []
    if os.path.exists(SPECIES_FILE):
        with open(SPECIES_FILE, 'r', encoding='utf-8') as f:
            local_species = json.load(f)
    local_map = {s.get("id"): s for s in local_species}

    success_count = 0
    skip_count = 0

    for i, sp in enumerate(targets, 1):
        sp_id = sp["id"]
        vn_name = sp.get("vn_name") or ""
        sci_name = sp.get("scientific_name") or ""
        worms_name = sp.get("worms_accepted_name") or ""
        current_bio = sp.get("biology") or {}

        # Khớp SpecCode
        spec_code = find_spec_code(sci_name, worms_name, name_index)

        if not spec_code:
            print(f"[{i}/{len(targets)}] {sp_id:16s} | {vn_name} ({sci_name}) -> KHÔNG TÌM THẤY TRÊN FISHBASE")
            skip_count += 1
            continue

        # Trích xuất dữ liệu FishBase
        fb_bio = build_fishbase_biology(spec_code, sp_map, eco_map, rep_map)

        # Hợp nhất với biology hiện có (bảo tồn gbifKey, iucnStatus...)
        merged_bio = dict(current_bio)
        for k, v in fb_bio.items():
            if v is not None:
                merged_bio[k] = v

        fb_name = merged_bio.get("fbName") or ""
        max_len = merged_bio.get("maxLength") or "-"
        depth = merged_bio.get("depth") or "-"

        print(f"[{i}/{len(targets)}] {sp_id:16s} | {vn_name} ({sci_name})")
        print(f"   -> Match #{spec_code} | FB Name: {fb_name} | Max: {max_len} | Depth: {depth}")

        # Dịch thuật mô tả sinh học bằng Gemini AI
        print(f"   -> Dịch thuật sinh học sang tiếng Việt...", end=" ", flush=True)
        translations = translate_biology_fields(vn_name, sci_name, merged_bio)
        for tk, tv in translations.items():
            if tv:
                merged_bio[tk] = tv
        print(f"Xong ({len(translations)} trường dịch).")

        if merged_bio.get("biologySummaryVn"):
            snip = merged_bio['biologySummaryVn'][:90]
            print(f"   [VN]: {snip}...")

        # Cập nhật en_common_name nếu cần
        new_en_name = None
        if not sp.get("en_common_name") and fb_name:
            new_en_name = fb_name

        # Ghi vào Supabase
        if not args.dry_run:
            ok = patch_supabase_species(sp_id, merged_bio, new_en_name)
            if ok:
                print(f"   ✓ Đã cập nhật Supabase thành công.")
                success_count += 1
            else:
                print(f"   ✗ Cập nhật Supabase thất bại.")
        else:
            print(f"   [DRY-RUN] Bỏ qua ghi CSDL.")
            success_count += 1

        # Cập nhật local map
        if sp_id in local_map:
            local_sp = local_map[sp_id]
            local_sp["biology"] = merged_bio
            if new_en_name and not local_sp.get("en_common_name"):
                local_sp["en_common_name"] = new_en_name

        time.sleep(0.5) # Tránh rate-limit AI

    # Ghi lại file local backup
    if not args.dry_run and local_species and success_count > 0:
        with open(SPECIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(local_species, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Đã đồng bộ {success_count} loài vào file local {SPECIES_FILE}")

    print("\n" + "=" * 70)
    print(f"TỔNG KẾT ENRICH FISHBASE TẬP 1:")
    print(f"  - Thành công: {success_count} loài")
    print(f"  - Bỏ qua    : {skip_count} loài (không nằm trong FishBase)")
    print("=" * 70)

if __name__ == "__main__":
    main()
