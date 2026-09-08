#!/usr/bin/env python3
"""
test_sealifebase.py
-------------------
Kiểm tra tính khả thi và chất lượng dữ liệu khi đồng bộ từ SeaLifeBase (v25.04)
cho 132 loài Giáp xác biển (collection 'giap-xac') của Cẩm nang Sinh vật Biển Việt Nam.

Quy trình:
1. Tải các bảng Parquet SeaLifeBase v25.04 về data/sealifebase_cache/ (nếu chưa có).
2. Phân tích cấu trúc schema của SeaLifeBase (species, ecology, reproduc, comnames).
3. Lấy 132 loài giáp xác từ Supabase.
4. Đối soát 3 tầng: Tên khoa học gốc -> WoRMS Accepted Name -> Synonyms.
5. Đo lường tỷ lệ khớp (match rate) và độ phong phú của dữ liệu sinh học trích xuất được.
"""

import os
import sys
import json
import ssl
import urllib.request
from pathlib import Path
import duckdb
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "sealifebase_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load Supabase env
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

HF_BASE_URL = "https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/slb/v25.04/parquet"

TABLES = [
    "species.parquet",
    "ecology.parquet",
    "reproduc.parquet",
    "comnames.parquet",
    "synonyms.parquet"
]

# SSL context
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def download_tables():
    print("=" * 70)
    print("📥 1. KIỂM TRA & TẢI SEALIFEBASE V25.04 PARQUET")
    print("=" * 70)
    for tbl in TABLES:
        dest = CACHE_DIR / tbl
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  ✓ {tbl}: Đã có trong cache ({dest.stat().st_size / (1024*1024):.2f} MB)")
            continue
        url = f"{HF_BASE_URL}/{tbl}"
        print(f"  ⬇ Đang tải {tbl} từ HuggingFace...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=_ssl_ctx) as response, open(dest, 'wb') as out_f:
            data = response.read()
            out_f.write(data)
        print(f"  ✓ {tbl}: Tải thành công ({len(data) / (1024*1024):.2f} MB)")


def inspect_schema():
    print("\n" + "=" * 70)
    print("🔍 2. KHẢO SÁT SCHEMA SEALIFEBASE (DUCKDB)")
    print("=" * 70)
    con = duckdb.connect()
    
    # 1. Species table
    sp_path = (CACHE_DIR / "species.parquet").as_posix()
    con.execute(f"CREATE VIEW slb_species AS SELECT * FROM read_parquet('{sp_path}')")
    sp_count = con.execute("SELECT count(*) FROM slb_species").fetchone()[0]
    cols = [col[0] for col in con.execute("DESCRIBE slb_species").fetchall()]
    print(f"  • Bảng `species`: {sp_count:,} bản ghi, {len(cols)} cột.")
    key_sp_cols = [c for c in ['SpecCode', 'Genus', 'Species', 'FBname', 'Length', 'LTypeMax', 'CommonLength', 'Weight', 'DepthRangeShallow', 'DepthRangeDeep', 'DemersPelag', 'Dangerous', 'Vulnerability', 'Comments'] if c in cols]
    print(f"    Các cột sinh học cốt lõi: {', '.join(key_sp_cols)}")

    # 2. Ecology table
    eco_path = (CACHE_DIR / "ecology.parquet").as_posix()
    con.execute(f"CREATE VIEW slb_ecology AS SELECT * FROM read_parquet('{eco_path}')")
    eco_count = con.execute("SELECT count(*) FROM slb_ecology").fetchone()[0]
    eco_cols = [col[0] for col in con.execute("DESCRIBE slb_ecology").fetchall()]
    print(f"  • Bảng `ecology`: {eco_count:,} bản ghi, {len(eco_cols)} cột.")
    key_eco_cols = [c for c in ['SpecCode', 'FoodTroph', 'FoodTrophT', 'Herbivory2', 'FeedingType', 'DietTroph', 'EcolCom'] if c in eco_cols]
    print(f"    Các cột sinh thái cốt lõi: {', '.join(key_eco_cols)}")

    # 3. Reproduc table
    rep_path = (CACHE_DIR / "reproduc.parquet").as_posix()
    con.execute(f"CREATE VIEW slb_reproduc AS SELECT * FROM read_parquet('{rep_path}')")
    rep_count = con.execute("SELECT count(*) FROM slb_reproduc").fetchone()[0]
    rep_cols = [col[0] for col in con.execute("DESCRIBE slb_reproduc").fetchall()]
    print(f"  • Bảng `reproduc`: {rep_count:,} bản ghi, {len(rep_cols)} cột.")
    key_rep_cols = [c for c in ['SpecCode', 'RepMode', 'Fertilization', 'MatingType', 'Spawning', 'ParentalCare', 'AddInfos'] if c in rep_cols]
    print(f"    Các cột sinh sản cốt lõi: {', '.join(key_rep_cols)}")

    # 4. Comnames table
    com_path = (CACHE_DIR / "comnames.parquet").as_posix()
    con.execute(f"CREATE VIEW slb_comnames AS SELECT * FROM read_parquet('{com_path}')")
    com_count = con.execute("SELECT count(*) FROM slb_comnames").fetchone()[0]
    print(f"  • Bảng `comnames`: {com_count:,} tên thường gọi đa ngôn ngữ.")

    # 5. Synonyms table
    syn_path = (CACHE_DIR / "synonyms.parquet").as_posix()
    con.execute(f"CREATE VIEW slb_synonyms AS SELECT * FROM read_parquet('{syn_path}')")
    syn_count = con.execute("SELECT count(*) FROM slb_synonyms").fetchone()[0]
    print(f"  • Bảng `synonyms`: {syn_count:,} tên đồng danh phân loại.")

    return con


def fetch_giapxac_from_supabase():
    print("\n" + "=" * 70)
    print("🦐 3. LẤY DANH SÁCH LOÀI GIÁP XÁC TỪ SUPABASE")
    print("=" * 70)
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.giap-xac&select=id,scientific_name,vn_name,worms_accepted_name,synonyms,biology&order=id.asc"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    species = resp.json()
    print(f"  ✓ Lấy thành công {len(species)} loài giáp xác từ Supabase.")
    return species


def match_sealifebase(con, species_list):
    print("\n" + "=" * 70)
    print("🔬 4. ĐỐI SOÁT & ĐÁNH GIÁ CHẤT LƯỢNG KHỚP NỐI")
    print("=" * 70)

    matched_exact = 0
    matched_worms = 0
    matched_synonym = 0
    not_found = []
    matched_samples = []

    for sp in species_list:
        orig_sci = (sp.get('scientific_name') or '').strip()
        worms_sci = (sp.get('worms_accepted_name') or '').strip()
        synonyms = sp.get('synonyms') or []
        sp_id = sp.get('id')
        vn_name = sp.get('vn_name')

        # Helper parse genus + species (xóa phân giống trong ngoặc đơn)
        def split_sci(name):
            if not name:
                return None, None
            import re
            cleaned = re.sub(r'\(.*?\)', '', name).strip()
            parts = cleaned.split()
            if len(parts) >= 2:
                genus = parts[0].strip('()[]{}.,')
                epithet = parts[1].strip('()[]{}.,').lower()
                if genus.isalpha() and epithet.isalpha():
                    return genus.capitalize(), epithet
            return None, None

        hit = None
        method = None

        # Level 1: Match with original scientific_name
        g, e = split_sci(orig_sci)
        if g and e:
            res = con.execute("""
                SELECT s.SpecCode, s.FBname, s.Length, s.LTypeMaxM, s.Weight,
                       s.DepthRangeShallow, s.DepthRangeDeep, s.DemersPelag,
                       s.Dangerous, s.Vulnerability, s.Comments,
                       e.FoodTroph, e.FeedingType, e.FoodRemark,
                       r.ReproMode, r.Fertilization, r.Spawning, r.AddInfos
                FROM slb_species s
                LEFT JOIN slb_ecology e ON s.SpecCode = e.SpecCode
                LEFT JOIN slb_reproduc r ON s.SpecCode = r.SpecCode
                WHERE lower(s.Genus) = lower(?) AND lower(s.Species) = lower(?)
                LIMIT 1
            """, [g, e]).fetchone()
            if res:
                hit = res
                method = "1. Tên gốc sách OCR"
                matched_exact += 1

        # Level 2: Match with worms_accepted_name
        if not hit and worms_sci:
            wg, we = split_sci(worms_sci)
            if wg and we:
                res = con.execute("""
                    SELECT s.SpecCode, s.FBname, s.Length, s.LTypeMaxM, s.Weight,
                           s.DepthRangeShallow, s.DepthRangeDeep, s.DemersPelag,
                           s.Dangerous, s.Vulnerability, s.Comments,
                           e.FoodTroph, e.FeedingType, e.FoodRemark,
                           r.ReproMode, r.Fertilization, r.Spawning, r.AddInfos
                    FROM slb_species s
                    LEFT JOIN slb_ecology e ON s.SpecCode = e.SpecCode
                    LEFT JOIN slb_reproduc r ON s.SpecCode = r.SpecCode
                    WHERE lower(s.Genus) = lower(?) AND lower(s.Species) = lower(?)
                    LIMIT 1
                """, [wg, we]).fetchone()
                if res:
                    hit = res
                    method = f"2. Tên WoRMS hợp lệ ({worms_sci})"
                    matched_worms += 1

        # Level 3: Match with synonyms from OCR book
        if not hit and synonyms:
            for syn in synonyms:
                sg, se = split_sci(syn)
                if sg and se:
                    res = con.execute("""
                        SELECT s.SpecCode, s.FBname, s.Length, s.LTypeMaxM, s.Weight,
                               s.DepthRangeShallow, s.DepthRangeDeep, s.DemersPelag,
                               s.Dangerous, s.Vulnerability, s.Comments,
                               e.FoodTroph, e.FeedingType, e.FoodRemark,
                               r.ReproMode, r.Fertilization, r.Spawning, r.AddInfos
                        FROM slb_species s
                        LEFT JOIN slb_ecology e ON s.SpecCode = e.SpecCode
                        LEFT JOIN slb_reproduc r ON s.SpecCode = r.SpecCode
                        WHERE lower(s.Genus) = lower(?) AND lower(s.Species) = lower(?)
                        LIMIT 1
                    """, [sg, se]).fetchone()
                    if res:
                        hit = res
                        method = f"3. Tên đồng danh sách ({syn})"
                        matched_synonym += 1
                        break

        # Level 4: Match with SeaLifeBase synonyms table
        if not hit:
            candidates = [orig_sci, worms_sci] + (synonyms if isinstance(synonyms, list) else [])
            for cand in candidates:
                cg, ce = split_sci(cand)
                if cg and ce:
                    sres = con.execute("""
                        SELECT SpecCode FROM slb_synonyms
                        WHERE lower(SynGenus) = lower(?) AND lower(SynSpecies) = lower(?)
                        LIMIT 1
                    """, [cg, ce]).fetchone()
                    if sres and sres[0]:
                        target_code = sres[0]
                        res = con.execute("""
                            SELECT s.SpecCode, s.FBname, s.Length, s.LTypeMaxM, s.Weight,
                                   s.DepthRangeShallow, s.DepthRangeDeep, s.DemersPelag,
                                   s.Dangerous, s.Vulnerability, s.Comments,
                                   e.FoodTroph, e.FeedingType, e.FoodRemark,
                                   r.ReproMode, r.Fertilization, r.Spawning, r.AddInfos
                            FROM slb_species s
                            LEFT JOIN slb_ecology e ON s.SpecCode = e.SpecCode
                            LEFT JOIN slb_reproduc r ON s.SpecCode = r.SpecCode
                            WHERE s.SpecCode = ?
                            LIMIT 1
                        """, [target_code]).fetchone()
                        if res:
                            hit = res
                            method = f"4. Bảng đồng danh SeaLifeBase ({cg} {ce})"
                            matched_synonym += 1
                            break

        if hit:
            spec_code, fb_name, length, l_type, weight, depth_min, depth_max, dem_pel, dangerous, vuln, comments, troph, feed_type, food_rem, rep_mode, fert, spawn, rep_info = hit
            
            # Fetch English common name if fb_name is null
            en_name = fb_name
            if not en_name:
                cres = con.execute("""
                    SELECT ComName FROM slb_comnames
                    WHERE SpecCode = ? AND (Language = 'English' OR Language = 'eng')
                    LIMIT 1
                """, [spec_code]).fetchone()
                if cres:
                    en_name = cres[0]

            matched_samples.append({
                "species_id": sp_id,
                "vn_name": vn_name,
                "sci_name": orig_sci,
                "method": method,
                "spec_code": spec_code,
                "en_name": en_name,
                "length": f"{length} cm {l_type or ''}".strip() if length else None,
                "depth": f"{depth_min} - {depth_max} m" if (depth_min is not None or depth_max is not None) else None,
                "habitat": dem_pel,
                "trophic_level": troph,
                "feeding_type": feed_type,
                "vulnerability": vuln,
                "comments": (comments or '')[:120] + '...' if comments and len(comments) > 120 else comments,
                "reproduction": rep_mode or fert,
            })
        else:
            not_found.append({
                "species_id": sp_id,
                "vn_name": vn_name,
                "sci_name": orig_sci,
                "worms_sci": worms_sci
            })

    total_matched = matched_exact + matched_worms + matched_synonym
    total_sp = len(species_list)
    pct = (total_matched / total_sp) * 100 if total_sp else 0

    print(f"\n📊 KẾT QUẢ ĐỐI SOÁT TỔNG THỂ:")
    print(f"  • Tổng số loài giáp xác: {total_sp} loài")
    print(f"  • Khớp thành công:        {total_matched}/{total_sp} loài ({pct:.1f}%)")
    print(f"    - Tầng 1 (Tên gốc):     {matched_exact} loài")
    print(f"    - Tầng 2 (WoRMS valid): {matched_worms} loài")
    print(f"    - Tầng 3 (Đồng danh):   {matched_synonym} loài")
    print(f"  • Chưa tìm thấy:          {len(not_found)}/{total_sp} loài ({100-pct:.1f}%)")

    print("\n" + "=" * 70)
    print("🌟 5. MẪU DỮ LIỆU ĐIỂN HÌNH TRÍCH XUẤT TỪ SEALIFEBASE:")
    print("=" * 70)
    for sample in matched_samples[:8]:
        print(f"🦐 [{sample['species_id']}] {sample['vn_name']} ({sample['sci_name']})")
        print(f"   ├─ Khớp theo: {sample['method']}")
        print(f"   ├─ SeaLifeBase SpecCode: {sample['spec_code']} | Tên EN: {sample['en_name'] or 'Chưa có'}")
        print(f"   ├─ Kích thước tối đa: {sample['length'] or 'N/A'}")
        print(f"   ├─ Độ sâu: {sample['depth'] or 'N/A'} | Sinh cảnh: {sample['habitat'] or 'N/A'}")
        print(f"   ├─ Bậc dinh dưỡng (Trophic): {sample['trophic_level'] or 'N/A'} | Kiểu ăn: {sample['feeding_type'] or 'N/A'}")
        print(f"   ├─ Độ tổn thương sinh thái: {sample['vulnerability'] or 'N/A'}")
        print(f"   └─ Mô tả: {sample['comments'] or 'N/A'}")
        print()

    if not_found:
        print(f"\n📋 Một số loài chưa có trên SeaLifeBase ({min(len(not_found), 10)} loài đầu):")
        for nf in not_found[:10]:
            print(f"   • [{nf['species_id']}] {nf['vn_name']} - {nf['sci_name']} (WoRMS: {nf['worms_sci'] or 'N/A'})")

    return total_matched, len(not_found), matched_samples


if __name__ == '__main__':
    download_tables()
    con = inspect_schema()
    species_list = fetch_giapxac_from_supabase()
    match_sealifebase(con, species_list)
