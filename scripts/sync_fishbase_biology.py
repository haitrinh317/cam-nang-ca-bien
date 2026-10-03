"""
sync_fishbase_biology.py
------------------------
Bổ sung trường 'biology' vào species.json từ FishBase Parquet (HuggingFace).

Nguồn dữ liệu:
  FishBase v25.04 — https://huggingface.co/datasets/cboettig/fishbase
  (CC-BY-NC 4.0 — ghi credit "Data from FishBase (www.fishbase.org)")

Trường bổ sung (biology):
  habitat, depth, maxLength, maxWeight, longevity,
  feedingType, trophicLevel, reproduction, spawning,
  vulnerability, iucnStatus (placeholder), dangerous, importance, aquaculture
  fbName, fbSpecCode

Cách chạy:
  python scripts/sync_fishbase_biology.py           # chỉ loài chưa có biology
  python scripts/sync_fishbase_biology.py --force   # ghi đè tất cả
  python scripts/sync_fishbase_biology.py --no-download  # dùng cache Parquet cũ
"""

import json
import os
import sys
import ssl
import time
import argparse
import tempfile
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

# ─── Config ──────────────────────────────────────────────────────────────────

SPECIES_FILE  = "data/species.json"
CACHE_DIR     = "data/fishbase_cache"          # lưu Parquet tải về
HF_BASE       = ("https://huggingface.co/datasets/cboettig/fishbase"
                 "/resolve/main/data/fb/v25.04/parquet")

TABLES = {
    "species":  "species.parquet",    # 5 MB
    "ecology":  "ecology.parquet",    # 1.4 MB
    "reproduc": "reproduc.parquet",   # 0.5 MB
}

# SSL context bỏ qua verify (proxy/intranet)
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


# ─── Download helpers ─────────────────────────────────────────────────────────

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def download_parquet(table_key: str, force: bool = False) -> str:
    """Tải file Parquet về cache. Trả về đường dẫn local."""
    filename = TABLES[table_key]
    local_path = os.path.join(CACHE_DIR, filename)

    if os.path.exists(local_path) and not force:
        size_mb = os.path.getsize(local_path) / 1024 / 1024
        print(f"  [cache] {filename} ({size_mb:.1f} MB)")
        return local_path

    url = f"{HF_BASE}/{filename}"
    print(f"  [download] {filename} từ HuggingFace...", end=" ", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes-SyncBot/2.0"})
    resp = urllib.request.urlopen(req, context=_SSL_CTX, timeout=120)
    with open(local_path, "wb") as f:
        f.write(resp.read())
    size_mb = os.path.getsize(local_path) / 1024 / 1024
    print(f"{size_mb:.1f} MB ✓")
    return local_path


# ─── Build lookup dicts từ Parquet ───────────────────────────────────────────

def build_lookups(no_download: bool = False) -> tuple[dict, dict, dict]:
    """
    Trả về 3 dict keyed by SpecCode (int):
      species_map, ecology_map, reproduc_map
    """
    import duckdb

    ensure_cache_dir()
    force_dl = not no_download

    sp_path  = download_parquet("species",  force=False)
    eco_path = download_parquet("ecology",  force=False)
    rep_path = download_parquet("reproduc", force=False)

    con = duckdb.connect()

    # ── species ──
    print("  Đọc species table...", end=" ", flush=True)
    rows = con.execute(f"""
        SELECT SpecCode, Genus, Species, FBname, Length, LTypeMaxM, Weight,
               DepthRangeShallow, DepthRangeDeep,
               LongevityWild, Vulnerability, Importance,
               PriceCateg, UsedforAquaculture, Dangerous, Comments
        FROM '{sp_path}'
    """).fetchall()
    cols_sp = [c[0] for c in con.description]
    species_map = {int(r[0]): dict(zip(cols_sp, r)) for r in rows if r[0] is not None}
    print(f"{len(species_map):,} loài")

    # ── ecology ──
    print("  Đọc ecology table...", end=" ", flush=True)
    rows = con.execute(f"""
        SELECT SpecCode, FeedingType, DietTroph,
               Neritic, Estuaries, Mangroves, CoralReefs,
               Benthic, SoftBottom, Mud, Rocky, Rubble,
               AddRems
        FROM '{eco_path}'
    """).fetchall()
    cols_eco = [c[0] for c in con.description]
    ecology_map = {}
    for r in rows:
        if r[0] is None:
            continue
        sc = int(r[0])
        if sc not in ecology_map:       # chỉ lấy record đầu tiên
            ecology_map[sc] = dict(zip(cols_eco, r))
    print(f"{len(ecology_map):,} records")

    # ── reproduc ──
    print("  Đọc reproduc table...", end=" ", flush=True)
    rows = con.execute(f"""
        SELECT SpecCode, ReproMode, Fertilization,
               SpawnAgg, Spawning, RepGuild1, RepGuild2,
               ParentalCare, AddInfos
        FROM '{rep_path}'
    """).fetchall()
    cols_rep = [c[0] for c in con.description]
    reproduc_map = {}
    for r in rows:
        if r[0] is None:
            continue
        sc = int(r[0])
        if sc not in reproduc_map:
            reproduc_map[sc] = dict(zip(cols_rep, r))
    print(f"{len(reproduc_map):,} records")

    con.close()
    return species_map, ecology_map, reproduc_map


# ─── Match tên khoa học → SpecCode ────────────────────────────────────────────

def build_name_index(species_map: dict) -> dict:
    """
    Trả về dict: "genus species" (lower) → SpecCode
    """
    idx = {}
    for sc, row in species_map.items():
        g = (row.get("Genus") or "").strip().lower()
        s = (row.get("Species") or "").strip().lower()
        if g and s:
            idx[f"{g} {s}"] = sc
    return idx


def find_spec_code(sci_name: str, name_index: dict) -> int | None:
    """Khớp tên khoa học → SpecCode. Chỉ dùng genus + epithet."""
    if not sci_name:
        return None
    parts = sci_name.strip().split()
    if len(parts) < 2:
        return None
    key = f"{parts[0].lower()} {parts[1].lower()}"
    return name_index.get(key)


# ─── Build biology dict từ 3 maps ─────────────────────────────────────────────

def _clean(val) -> str | None:
    """Chuyển giá trị NaN/None/pd.NA thành None."""
    if val is None:
        return None
    s = str(val).strip()
    if s in ("None", "nan", "NaT", "NA", "<NA>", "", "-999", "-9999"):
        return None
    return s


def _flag(val) -> bool:
    """FishBase dùng -1 = True, 0 = False cho binary fields."""
    try:
        return int(val) == -1
    except (TypeError, ValueError):
        return False


def build_biology(spec_code: int, sp_map: dict, eco_map: dict, rep_map: dict) -> dict:
    bio: dict = {"fbSpecCode": spec_code, "source": "FishBase v25.04"}

    # ── species fields ──
    sp = sp_map.get(spec_code, {})
    if sp:
        bio["fbName"] = _clean(sp.get("FBname"))

        # Kích thước
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

        # Độ sâu
        d_min = _clean(sp.get("DepthRangeShallow"))
        d_max = _clean(sp.get("DepthRangeDeep"))
        if d_min and d_max:
            bio["depth"] = f"{d_min} - {d_max} m"
        elif d_max:
            bio["depth"] = f"đến {d_max} m"

        # Kinh tế
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

    # ── ecology fields ──
    eco = eco_map.get(spec_code, {})
    if eco:
        # Kiểu ăn & trophic level
        ft = _clean(eco.get("FeedingType"))
        if ft:
            bio["feedingType"] = ft

        troph = _clean(eco.get("DietTroph"))
        if troph:
            try:
                bio["trophicLevel"] = round(float(troph), 2)
            except ValueError:
                pass

        # Habitat tổng hợp
        habitats = []
        if _flag(eco.get("Neritic")):      habitats.append("Neritic")
        if _flag(eco.get("Estuaries")):    habitats.append("Estuaries")
        if _flag(eco.get("Mangroves")):    habitats.append("Mangroves")
        if _flag(eco.get("CoralReefs")):   habitats.append("Coral reefs")
        if _flag(eco.get("Benthic")):      habitats.append("Benthic")
        if _flag(eco.get("SoftBottom")):   habitats.append("Soft bottom")
        if _flag(eco.get("Mud")):          habitats.append("Mud")
        if _flag(eco.get("Rocky")):        habitats.append("Rocky")
        if _flag(eco.get("Rubble")):       habitats.append("Rubble")
        if habitats:
            bio["habitat"] = ", ".join(habitats)

        eco_notes = _clean(eco.get("AddRems"))
        if eco_notes:
            bio["ecologyNotes"] = eco_notes

    # ── reproduction fields ──
    rep = rep_map.get(spec_code, {})
    if rep:
        mode = _clean(rep.get("ReproMode"))
        fert = _clean(rep.get("Fertilization"))
        parts = []
        if mode:
            parts.append(mode)
        if fert:
            parts.append(f"{fert} fertilization")
        if parts:
            bio["reproduction"] = ", ".join(parts)

        spawn = _clean(rep.get("Spawning"))
        if spawn:
            bio["spawning"] = spawn

        if _flag(rep.get("SpawnAgg")) or str(rep.get("SpawnAgg")) == "-1":
            bio["spawnAggregation"] = True

        care = _clean(rep.get("ParentalCare"))
        if care and care.lower() != "none":
            bio["parentalCare"] = care

        add_rep = _clean(rep.get("AddInfos"))
        if add_rep:
            bio["reproductionNotes"] = add_rep

    return bio


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bổ sung biology từ FishBase vào species.json")
    parser.add_argument("--force",       action="store_true",
                        help="Ghi đè cả loài đã có biology")
    parser.add_argument("--no-download", action="store_true",
                        help="Dùng Parquet cache cũ, không tải lại")
    parser.add_argument("--volume",      type=int, default=0,
                        help="Chỉ xử lý tập cụ thể (1-5). Mặc định: tất cả")
    args = parser.parse_args()

    if not os.path.exists(SPECIES_FILE):
        print(f"[ERROR] Không tìm thấy {SPECIES_FILE}")
        sys.exit(1)

    print("=" * 60)
    print("Sync FishBase Biology → species.json")
    print("=" * 60)

    # 1. Tải Parquet về cache
    print("\n[1] Chuẩn bị dữ liệu FishBase:")
    try:
        sp_map, eco_map, rep_map = build_lookups(no_download=args.no_download)
    except ImportError:
        print("[ERROR] Thiếu thư viện duckdb. Chạy: pip install duckdb pandas")
        sys.exit(1)

    name_idx = build_name_index(sp_map)
    print(f"  Name index: {len(name_idx):,} entries")

    # 2. Đọc species.json
    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    # Filter theo volume nếu cần
    targets = species_list
    if args.volume:
        targets = [s for s in species_list if s.get("volume") == args.volume]

    print(f"\n[2] Xử lý {len(targets)} loài" +
          (f" (Tập {args.volume})" if args.volume else ""))
    print("-" * 60)

    matched  = 0
    skipped  = 0
    no_match = 0

    for i, sp in enumerate(targets, 1):
        sp_id    = sp.get("id", "")
        sci_name = sp.get("scientificName", "")

        # Bỏ qua nếu đã có biology và không force
        if not args.force and sp.get("biology"):
            skipped += 1
            continue

        spec_code = find_spec_code(sci_name, name_idx)

        if spec_code is None:
            no_match += 1
            print(f"  [{i}] {sci_name:50s} → no match")
            continue

        bio = build_biology(spec_code, sp_map, eco_map, rep_map)
        sp["biology"] = bio
        matched += 1

        fb_name = bio.get("fbName", "")
        depth   = bio.get("depth", "-")
        habitat_summary = bio.get("habitat", "-")
        print(f"  [{i}] {sci_name:50s} → #{spec_code} | {fb_name} | {depth} | {habitat_summary[:30]}")

        # Auto-save mỗi 50 loài
        if matched % 50 == 0:
            with open(SPECIES_FILE, "w", encoding="utf-8") as f:
                json.dump(species_list, f, ensure_ascii=False, indent=2)
            print(f"  ── Auto-saved ({matched} matched so far) ──")

    # 3. Ghi kết quả cuối
    with open(SPECIES_FILE, "w", encoding="utf-8") as f:
        json.dump(species_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"Hoàn tất!")
    print(f"  Matched & updated : {matched}")
    print(f"  Đã bỏ qua (cached): {skipped}")
    print(f"  Không khớp       : {no_match}")
    print(f"  File đã lưu      : {SPECIES_FILE}")
    print(f"\nCredit: Data from FishBase (www.fishbase.org)")


if __name__ == "__main__":
    main()
