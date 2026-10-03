#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/sync_fishbase_ca_bien.py
---------------------------------
Đồng bộ và làm giàu dữ liệu sinh học, sinh thái, kích thước, tập tính và mô tả song ngữ Việt - Anh
cho 547 loài Cá Biển (collection 'ca-bien') từ hệ sinh thái FishBase v25.04 & GBIF API.

Cơ chế đối chiếu 3 tầng:
  1. Tên khoa học gốc trong sách OCR (scientific_name)
  2. Danh pháp hợp lệ chuẩn WoRMS (worms_accepted_name)
  3. Bảng đồng danh phân loại của FishBase (synonyms.parquet)

Dịch thuật học thuật Ngư loại học (Ichthyology) sang tiếng Việt bằng Gemini AI.
Bảo toàn 100% wormsTaxonomy và vnRedList qua cơ chế Deep Merge.
"""

import os
import sys
import json
import re
import ssl
import time
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
import duckdb
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "fishbase_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

HF_BASE_URL = "https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/fb/v25.04/parquet"

TABLES = [
    "species.parquet",
    "ecology.parquet",
    "reproduc.parquet",
    "synonyms.parquet"
]

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

SYSTEM_PROMPT_ICHTHYOLOGY = """Bạn là chuyên gia hàng đầu về Ngư loại học (Ichthyology) và Sinh thái học biển tại Viện Hải dương học.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, kích thước, môi trường sống, tập tính săn mồi, bầy đàn và sinh sản của các loài Cá biển từ cơ sở dữ liệu FishBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, khúc chiết, chuẩn mực sách chuyên khảo sinh học biển Việt Nam.
2. Dịch chuẩn xác các thuật ngữ ngư loại học:
   - 'benthic': tầng đáy
   - 'pelagic': tầng khơi
   - 'demersal': tầng sát đáy / cá đáy
   - 'benthopelagic': tầng trung gian đáy - khơi
   - 'reef-associated': sống gắn liền với rạn san hô
   - 'intertidal': vùng gian triều
   - 'estuarine': vùng cửa sông / nước lợ
   - 'carnivore' / 'piscivore': ăn thịt / chuyên ăn cá con
   - 'planktivore': chuyên ăn sinh vật phù du
   - 'herbivore': ăn rong tảo / thực vật biển
   - 'schooling': sống kết thành đàn lớn
   - 'solitary': sống đơn độc
   - 'oviparous' / 'viviparous': đẻ trứng / đẻ con
   - 'ciguatera': ngộ độc độc tố ciguatera
   - 'standard length' (SL): chiều dài chuẩn
   - 'total length' (TL): chiều dài tổng cộng
   - 'fork length' (FL): chiều dài chẽ đuôi
3. Giữ nguyên tên khoa học in nghiêng hoặc chữ La-tinh và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân."""

def translate_gemini(text: str) -> str:
    """Dịch đoạn văn bản sang tiếng Việt chuẩn Ngư loại học bằng Gemini AI"""
    if not text or not text.strip() or not GEMINI_API_KEY:
        return ""
    
    clean_text = text.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Dịch đoạn mô tả ngư học sau sang tiếng Việt chuẩn xác, tự nhiên, khoa học:\n\n{clean_text}"}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT_ICHTHYOLOGY}]},
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
    }
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode("utf-8"))
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return ans
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
    return ""

def download_file(filename: str) -> Path:
    local_path = CACHE_DIR / filename
    if local_path.exists() and local_path.stat().st_size > 10000:
        return local_path
    
    url = f"{HF_BASE_URL}/{filename}"
    print(f"  [Tải Parquet] {filename} từ HuggingFace...", end=" ", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=_SSL_CTX, timeout=120) as resp:
        with open(local_path, "wb") as f:
            f.write(resp.read())
    size_mb = local_path.stat().st_size / 1024 / 1024
    print(f"✓ ({size_mb:.1f} MB)")
    return local_path

def init_duckdb():
    print("⏳ Đang chuẩn bị các bảng cơ sở dữ liệu FishBase v25.04...")
    for f in TABLES:
        download_file(f)
    
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW species AS SELECT * FROM '{CACHE_DIR}/species.parquet'")
    con.execute(f"CREATE OR REPLACE VIEW ecology AS SELECT * FROM '{CACHE_DIR}/ecology.parquet'")
    con.execute(f"CREATE OR REPLACE VIEW reproduc AS SELECT * FROM '{CACHE_DIR}/reproduc.parquet'")
    con.execute(f"CREATE OR REPLACE VIEW synonyms AS SELECT * FROM '{CACHE_DIR}/synonyms.parquet'")
    print("✓ Đã nạp thành công DuckDB in-memory.")
    return con

def get_species_code(con, sci_name: str, worms_accepted: str = None) -> tuple:
    """Đối chiếu 3 tầng tìm SpecCode FishBase"""
    def clean(n):
        return re.sub(r'\s+', ' ', (n or '')).strip().lower()
    
    orig = clean(sci_name)
    parts = orig.split()
    if len(parts) >= 2:
        g, s = parts[0], parts[1]
        res = con.execute("SELECT SpecCode FROM species WHERE lower(Genus) = ? AND lower(Species) = ? LIMIT 1", [g, s]).fetchone()
        if res:
            return res[0], "1. Tên gốc sách OCR"
    
    if worms_accepted:
        w_clean = clean(worms_accepted)
        w_parts = w_clean.split()
        if len(w_parts) >= 2:
            wg, ws = w_parts[0], w_parts[1]
            res = con.execute("SELECT SpecCode FROM species WHERE lower(Genus) = ? AND lower(Species) = ? LIMIT 1", [wg, ws]).fetchone()
            if res:
                return res[0], f"2. WoRMS Accepted Name ({worms_accepted})"
    
    for name_to_check in [orig, clean(worms_accepted)]:
        if not name_to_check:
            continue
        p = name_to_check.split()
        if len(p) >= 2:
            res = con.execute("SELECT SpecCode FROM synonyms WHERE lower(SynGenus) = ? AND lower(SynSpecies) = ? AND SpecCode IS NOT NULL LIMIT 1", [p[0], p[1]]).fetchone()
            if res:
                return res[0], f"3. Bảng đồng danh FishBase ({name_to_check})"
    
    return None, None

def extract_biology(con, spec_code: int, sp_info: dict, translate: bool = True) -> dict:
    """Trích xuất 15+ thông số sinh học từ DuckDB FishBase"""
    sp_row = con.execute("SELECT * FROM species WHERE SpecCode = ?", [spec_code]).fetchone()
    cols_sp = [desc[0] for desc in con.description]
    sp_dict = dict(zip(cols_sp, sp_row)) if sp_row else {}
    
    eco_row = con.execute("SELECT * FROM ecology WHERE SpecCode = ?", [spec_code]).fetchone()
    cols_eco = [desc[0] for desc in con.description]
    eco_dict = dict(zip(cols_eco, eco_row)) if eco_row else {}
    
    rep_row = con.execute("SELECT * FROM reproduc WHERE SpecCode = ?", [spec_code]).fetchone()
    cols_rep = [desc[0] for desc in con.description]
    rep_dict = dict(zip(cols_rep, rep_row)) if rep_row else {}
    
    bio = {}
    bio["source"] = "FishBase v25.04"
    bio["fbSpecCode"] = spec_code
    
    fb_name = sp_dict.get("FBname")
    if fb_name and str(fb_name).strip():
        bio["fbName"] = str(fb_name).strip()
    
    length = sp_dict.get("Length")
    l_type = sp_dict.get("LTypeMaxM") or "TL"
    if length and str(length) != "nan" and float(length) > 0:
        bio["maxLength"] = f"{float(length):.1f} cm {l_type}"
    
    weight = sp_dict.get("Weight")
    if weight and str(weight) != "nan" and float(weight) > 0:
        w_val = float(weight)
        bio["maxWeight"] = f"{w_val:.1f} g" if w_val < 1000 else f"{w_val/1000:.2f} kg"
    
    d_shallow = sp_dict.get("DepthRangeShallow")
    d_deep = sp_dict.get("DepthRangeDeep")
    if d_shallow is not None and str(d_shallow) != "nan" and d_deep is not None and str(d_deep) != "nan":
        bio["depth"] = f"{int(float(d_shallow))} - {int(float(d_deep))} m"
    elif d_deep is not None and str(d_deep) != "nan":
        bio["depth"] = f"lên đến {int(float(d_deep))} m"
    
    habitats = []
    if sp_dict.get("DemersPelag"):
        habitats.append(str(sp_dict.get("DemersPelag")))
    if eco_dict.get("Neritic"):
        habitats.append("Vùng thềm lục địa")
    if eco_dict.get("CoralReefs"):
        habitats.append("Rạn san hô")
    if eco_dict.get("SoftBottom"):
        habitats.append("Đáy mềm / Bùn cát")
    if habitats:
        bio["habitat"] = ", ".join(dict.fromkeys(habitats))
    
    feed_type = eco_dict.get("FeedingType")
    if feed_type and str(feed_type).strip():
        bio["feedingType"] = str(feed_type).strip()
    
    trophic = eco_dict.get("DietTroph")
    if trophic and str(trophic) != "nan" and float(trophic) > 0:
        bio["trophicLevel"] = round(float(trophic), 2)
    
    rep_mode = rep_dict.get("ReproMode")
    if rep_mode and str(rep_mode).strip():
        bio["reproduction"] = str(rep_mode).strip()
    
    spawning = rep_dict.get("Spawning")
    if spawning and str(spawning).strip():
        bio["spawning"] = str(spawning).strip()
    
    care = rep_dict.get("ParentalCare")
    if care and str(care).strip() and str(care).lower() != "none":
        bio["parentalCare"] = str(care).strip()
    
    dangerous = sp_dict.get("Dangerous")
    if dangerous and str(dangerous).strip():
        bio["dangerous"] = str(dangerous).strip()
    
    vuln = sp_dict.get("Vulnerability")
    if vuln and str(vuln) != "nan":
        bio["vulnerability"] = round(float(vuln), 2)
    
    longevity = sp_dict.get("LongevityWild")
    if longevity and str(longevity) != "nan" and float(longevity) > 0:
        bio["longevity"] = f"{float(longevity):.1f} năm"
    
    imp = sp_dict.get("Importance")
    if imp and str(imp).strip():
        bio["importance"] = str(imp).strip()
    
    aqua = sp_dict.get("Aquaculture")
    if aqua and str(aqua).strip():
        bio["aquaculture"] = str(aqua).strip()
    
    comments = sp_dict.get("Comments")
    if comments and str(comments).strip():
        bio["biologySummary"] = str(comments).strip()
        if translate:
            bio["biologySummaryVn"] = translate_gemini(bio["biologySummary"])
    
    add_infos = eco_dict.get("AddInfos")
    if add_infos and str(add_infos).strip():
        bio["ecologyNotes"] = str(add_infos).strip()
        if translate:
            bio["ecologyNotesVn"] = translate_gemini(bio["ecologyNotes"])
    
    return bio

def deep_merge(target: dict, source: dict) -> dict:
    result = dict(target)
    for k, v in source.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

def main():
    parser = argparse.ArgumentParser(description="Đồng bộ dữ liệu FishBase v25.04 cho Cá biển")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử không ghi vào Supabase")
    parser.add_argument("--limit", type=int, default=0, help="Giới hạn số loài")
    parser.add_argument("--no-translate", action="store_true", help="Bỏ qua dịch Gemini")
    parser.add_argument("--volume", type=int, default=0, help="Lọc theo tập (1-6)")
    parser.add_argument("--force", action="store_true", help="Đồng bộ cả loài đã có FishBase")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[LỖI] Thiếu credentials Supabase!")
        sys.exit(1)

    con = init_duckdb()

    # Lấy danh sách loài cá biển từ Supabase
    print("⏳ Đang truy vấn danh sách cá biển từ Supabase...")
    PAGE_SIZE = 1000
    all_species = []
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&select=id,species_index,volume,vn_name,scientific_name,worms_accepted_name,en_common_name,biology&order=volume,species_index&limit={PAGE_SIZE}&offset={offset}"
        req = urllib.request.Request(url, headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'})
        with urllib.request.urlopen(req) as resp:
            batch = json.loads(resp.read().decode('utf-8'))
            all_species.extend(batch)
            if len(batch) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

    print(f"✓ Đã nạp {len(all_species)} loài cá biển.")

    targets = []
    for sp in all_species:
        if args.volume and sp.get("volume") != args.volume:
            continue
        bio = sp.get("biology") or {}
        if not args.force and (bio.get("fbSpecCode") or bio.get("source") == "FishBase v25.04"):
            continue
        targets.append(sp)

    if args.limit:
        targets = targets[:args.limit]

    print(f"🎯 Số loài cần đồng bộ FishBase: {len(targets)} loài" + (f" (Tập {args.volume})" if args.volume else ""))
    print("=" * 80)

    matched_count = 0
    updated_count = 0
    not_found_count = 0

    for i, sp in enumerate(targets, 1):
        sp_id = sp["id"]
        vn_name = sp.get("vn_name", "")
        sci_name = sp.get("scientific_name", "")
        worms_name = sp.get("worms_accepted_name")

        spec_code, match_type = get_species_code(con, sci_name, worms_name)

        if not spec_code:
            not_found_count += 1
            print(f"[{i}/{len(targets)}] ⚠️ Không tìm thấy trên FishBase: [{sp_id}] {vn_name} ({sci_name})")
            continue

        matched_count += 1
        print(f"[{i}/{len(targets)}] 🔍 Khớp [{sp_id}] {vn_name} -> SpecCode {spec_code} ({match_type})")

        fb_bio = extract_biology(con, spec_code, sp, translate=not args.no_translate)

        # Chuẩn bị payload PATCH Supabase
        current_bio = sp.get("biology") or {}
        merged_bio = deep_merge(current_bio, fb_bio)

        payload = {"biology": merged_bio}
        if not sp.get("en_common_name") and fb_bio.get("fbName"):
            payload["en_common_name"] = fb_bio["fbName"]

        if args.dry_run:
            print(f"  [DRY-RUN] Dài: {fb_bio.get('maxLength')} | Sâu: {fb_bio.get('depth')} | FB: {fb_bio.get('fbName')}")
            continue

        # Ghi thật vào Supabase
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        req = urllib.request.Request(
            patch_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            data=json.dumps(payload).encode("utf-8"),
            method="PATCH"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 204):
                    updated_count += 1
                    print(f"  ✓ Đã cập nhật Supabase [{sp_id}] (Dài: {fb_bio.get('maxLength', '-')}, Sâu: {fb_bio.get('depth', '-')})")
        except Exception as e:
            print(f"  ❌ Lỗi khi cập nhật Supabase [{sp_id}]: {e}")

    print("\n" + "=" * 80)
    print(f"📊 TỔNG KẾT ĐỒNG BỘ FISHBASE:")
    print(f"  • Tổng loài xử lý  : {len(targets)}")
    print(f"  • Khớp thành công  : {matched_count}")
    print(f"  • Cập nhật Supabase: {updated_count}")
    print(f"  • Không tìm thấy   : {not_found_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
