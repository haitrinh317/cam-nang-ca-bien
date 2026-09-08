#!/usr/bin/env python3
"""
scripts/sync_sealifebase.py
----------------------------
Đồng bộ và làm giàu dữ liệu sinh học, sinh thái, kích thước, tập tính và mô tả song ngữ Việt - Anh
cho bộ sưu tập Giáp xác biển ('giap-xac') từ hệ sinh thái SeaLifeBase v25.04.

Cơ chế đối chiếu 4 tầng:
  1. Bảng đối chiếu thủ công (Manual Override / Local endemic species)
  2. Tên khoa học gốc trong sách OCR (scientific_name)
  3. Danh pháp hợp lệ chuẩn WoRMS (worms_accepted_name)
  4. Bảng đồng danh phân loại toàn cầu của SeaLifeBase (synonyms.parquet - 143,000+ tên)

Tự động dịch thuật học thuật Giáp xác học (Carcinology) sang tiếng Việt bằng Gemini AI:
  - biologySummaryVn, ecologyNotesVn, reproductionNotesVn

Cách dùng:
  # 1. Chạy thử xem trước 3 loài (không ghi DB):
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --dry-run --limit 3

  # 2. Chạy cho 1 loài cụ thể:
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --id giapxac-species-1

  # 3. Chạy đồng bộ toàn bộ 132 loài Giáp xác biển:
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py
"""

import os
import sys
import json
import re
import ssl
import time
import argparse
import urllib.request
from pathlib import Path
import duckdb
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "sealifebase_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load environment
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

HF_BASE_URL = "https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/slb/v25.04/parquet"

TABLES = [
    "species.parquet",
    "ecology.parquet",
    "reproduc.parquet",
    "comnames.parquet",
    "synonyms.parquet"
]

# Manual override mapping cho các loài phân loại lịch sử đặc biệt
MANUAL_OVERRIDE = {
    'Lysiosquillina tredecimdentata': 92615,  # Giáp xác: giống cũ Lysiosquilla
    'Hydrophis annandalei': 83964,   # Rắn biển: Kolpophis annandalei
    'Hydrophis anomalus': 83976,     # Rắn biển: Thalassophis anomalus
    'Hydrophis jerdonii': 83963,     # Rắn biển: Kerilia jerdoni
    'Hydrophis viperina': 83975,     # Rắn biển: Praescutata viperina / Hydrophis viperinus
    'Hydrophis brookii': 83936,      # Rắn biển: Hydrophis brooki
    'Hydrophis pachycercos': 153049, # Rắn biển: Hydrophis pachyceros
    'Hydrophis platura': 67462,      # Rắn biển: Hydrophis platurus
    'Microcephalophis gracilis': 83972, # Rắn biển: Hydrophis gracilis
}

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Gemini models
GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

SYSTEM_PROMPT_CRUSTACEA = """Bạn là chuyên gia hàng đầu về Giáp xác học (Carcinology) và Sinh học biển tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, sinh sản của các loài giáp xác biển (tôm, cua, ghẹ, tôm hùm, tôm tít, ốc mượn hồn) từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu sinh học biển và động vật chí Việt Nam.
2. Dịch chuẩn xác các thuật ngữ giáp xác & sinh thái biển:
   - 'carapace length' (CL): chiều dài giáp đầu ngực
   - 'total length' (TL): chiều dài toàn thân
   - 'benthopelagic': tầng sát đáy và tầng nổi
   - 'benthic': tầng đáy
   - 'demersal': sát đáy
   - 'reef-associated': liên kết rạn san hô
   - 'intertidal': vùng gian triều / bãi triều
   - 'subtidal': vùng dưới triều
   - 'continental shelf': thềm lục địa
   - 'substrate': giá thể / nền đáy
   - 'soft bottoms': đáy mềm (bùn, cát bùn)
   - 'burrower': tập tính đào hang
   - 'nocturnal': hoạt động về đêm
   - 'scavenger': ăn xác thối / mùn bã
   - 'predator': ăn thịt / bắt mồi
   - 'ovigerous female': con cái mang trứng / ôm trứng
3. Giữ nguyên tên khoa học (in nghiêng nếu có thể) và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân, chỉ dịch trung thực và mượt mà nội dung nguồn."""

SYSTEM_PROMPT_HERPETOLOGY = """Bạn là chuyên gia hàng đầu về Bò sát học biển (Marine Herpetology) và Sinh học biển tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, sinh sản, độc tố học của các loài rắn biển từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu sinh học biển và cẩm nang Rắn biển Việt Nam.
2. Dịch chuẩn xác các thuật ngữ bò sát & sinh thái biển:
   - 'total length' (TL): chiều dài toàn thân
   - 'snout-vent length' (SVL): chiều dài từ mõm đến hậu môn
   - 'tail length': chiều dài đuôi
   - 'paddle-shaped tail': đuôi dẹp như mái chèo
   - 'benthopelagic': tầng sát đáy và tầng nổi
   - 'pelagic': tầng mặt / khơi
   - 'reef-associated': liên kết rạn san hô
   - 'ovoviviparous' / 'viviparous': trứng thai / đẻ con
   - 'oviparous': đẻ trứng
   - 'venomous': có nọc độc
   - 'neurotoxin': độc tố thần kinh
   - 'lethal dose' (LD50): liều gây tử vong 50%
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân, chỉ dịch trung thực và mượt mà nội dung nguồn."""

CURRENT_COLLECTION = "giap-xac"
SYSTEM_PROMPT = SYSTEM_PROMPT_CRUSTACEA


def download_tables_if_needed():
    for tbl in TABLES:
        dest = CACHE_DIR / tbl
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        url = f"{HF_BASE_URL}/{tbl}"
        print(f"  ⬇ Đang tải bảng {tbl} từ SeaLifeBase v25.04...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=_ssl_ctx) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        print(f"  ✓ {tbl} đã tải xong.")


def init_duckdb():
    con = duckdb.connect()
    for tbl in ["species", "ecology", "reproduc", "comnames", "synonyms"]:
        p = (CACHE_DIR / f"{tbl}.parquet").as_posix()
        con.execute(f"CREATE VIEW slb_{tbl} AS SELECT * FROM read_parquet('{p}')")
    return con


def call_gemini(prompt: str) -> str:
    """Gọi Gemini API qua danh sách model fallback."""
    if not GEMINI_API_KEY:
        return ""

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return text
        except Exception as e:
            continue
    return ""


def clean_sci_name(name: str):
    if not name:
        return None, None
    cleaned = re.sub(r'\(.*?\)', '', name).strip()
    parts = cleaned.split()
    if len(parts) >= 2:
        g = parts[0].strip('()[]{}.,')
        e = parts[1].strip('()[]{}.,').lower()
        if g.isalpha() and e.isalpha():
            return g.capitalize(), e
    return None, None


def query_sealifebase(con, sp: dict):
    orig_sci = (sp.get('scientific_name') or '').strip()
    worms_sci = (sp.get('worms_accepted_name') or '').strip()
    synonyms = sp.get('synonyms') or []

    # Check Manual Override
    if orig_sci in MANUAL_OVERRIDE:
        spec_code = MANUAL_OVERRIDE[orig_sci]
        res = con.execute("SELECT * FROM slb_species WHERE SpecCode = ?", [spec_code]).fetchone()
        if res:
            return extract_record(con, spec_code, "0. Bảng đối chiếu thủ công")

    # Level 1: Original scientific name
    g, e = clean_sci_name(orig_sci)
    if g and e:
        row = con.execute("SELECT SpecCode FROM slb_species WHERE lower(Genus)=lower(?) AND lower(Species)=lower(?) LIMIT 1", [g, e]).fetchone()
        if row:
            return extract_record(con, row[0], "1. Tên gốc sách OCR")

    # Level 2: WoRMS accepted name
    if worms_sci:
        wg, we = clean_sci_name(worms_sci)
        if wg and we:
            row = con.execute("SELECT SpecCode FROM slb_species WHERE lower(Genus)=lower(?) AND lower(Species)=lower(?) LIMIT 1", [wg, we]).fetchone()
            if row:
                return extract_record(con, row[0], f"2. Tên WoRMS hợp lệ ({worms_sci})")

    # Level 3: Synonyms from OCR book
    if synonyms:
        for syn in synonyms:
            sg, se = clean_sci_name(syn)
            if sg and se:
                row = con.execute("SELECT SpecCode FROM slb_species WHERE lower(Genus)=lower(?) AND lower(Species)=lower(?) LIMIT 1", [sg, se]).fetchone()
                if row:
                    return extract_record(con, row[0], f"3. Tên đồng danh sách ({syn})")

    # Level 4: SeaLifeBase synonyms table
    cands = [orig_sci, worms_sci] + (synonyms if isinstance(synonyms, list) else [])
    for c in cands:
        cg, ce = clean_sci_name(c)
        if cg and ce:
            sres = con.execute("SELECT SpecCode FROM slb_synonyms WHERE lower(SynGenus)=lower(?) AND lower(SynSpecies)=lower(?) LIMIT 1", [cg, ce]).fetchone()
            if sres and sres[0]:
                return extract_record(con, sres[0], f"4. Bảng đồng danh SeaLifeBase ({cg} {ce})")

    return None


def extract_record(con, spec_code: int, match_method: str):
    s = con.execute("""
        SELECT SpecCode, Genus, Species, FBname, Length, LTypeMaxM, CommonLength, Weight,
               DepthRangeShallow, DepthRangeDeep, DemersPelag, Dangerous, Vulnerability, Comments
        FROM slb_species WHERE SpecCode = ?
    """, [spec_code]).fetchone()

    if not s:
        return None

    e = con.execute("""
        SELECT FoodTroph, DietTroph, FeedingType, FoodRemark, DietRemark
        FROM slb_ecology WHERE SpecCode = ?
    """, [spec_code]).fetchone()

    r = con.execute("""
        SELECT ReproMode, Fertilization, Spawning, AddInfos
        FROM slb_reproduc WHERE SpecCode = ?
    """, [spec_code]).fetchone()

    # English common name
    en_name = s[3]
    if not en_name:
        c = con.execute("""
            SELECT ComName FROM slb_comnames
            WHERE SpecCode = ? AND (Language = 'English' OR Language = 'eng')
            ORDER BY PreferredName DESC LIMIT 1
        """, [spec_code]).fetchone()
        if c:
            en_name = c[0]

    # Format fields
    length_val = None
    if s[4]:
        l_type = s[5] or "TL"
        length_val = f"{s[4]} cm {l_type}"

    depth_val = None
    if s[8] is not None or s[9] is not None:
        min_d = s[8] if s[8] is not None else "?"
        max_d = s[9] if s[9] is not None else "?"
        depth_val = f"{min_d} - {max_d} m"

    troph = e[0] if (e and e[0] is not None) else (e[1] if (e and e[1] is not None) else None)
    feed_type = e[2] if (e and e[2]) else None
    ecol_notes = e[3] if (e and e[3]) else (e[4] if (e and e[4]) else None)

    rep_mode = r[0] if (r and r[0]) else (r[1] if (r and r[1]) else None)
    rep_notes = r[3] if (r and r[3]) else None

    return {
        "specCode": spec_code,
        "fbName": en_name,
        "source": "SeaLifeBase v25.04",
        "matchMethod": match_method,
        "maxLength": length_val,
        "depth": depth_val,
        "habitat": s[10],
        "feedingType": feed_type,
        "trophicLevel": float(troph) if troph is not None else None,
        "reproduction": rep_mode,
        "vulnerability": float(s[12]) if s[12] is not None else None,
        "dangerous": s[11],
        "biologySummary": s[13],
        "ecologyNotes": ecol_notes,
        "reproductionNotes": rep_notes
    }


def enrich_species(sp: dict, bio_raw: dict, translate: bool = True):
    bio = dict(bio_raw)
    
    # Translate summaries if requested
    if translate and GEMINI_API_KEY:
        to_trans = []
        if bio.get("biologySummary"):
            to_trans.append(f"MÔ TẢ SINH HỌC:\n{bio['biologySummary']}")
        if bio.get("ecologyNotes"):
            to_trans.append(f"GHI CHÚ SINH THÁI:\n{bio['ecologyNotes']}")
        if bio.get("reproductionNotes"):
            to_trans.append(f"ĐẶC ĐIỂM SINH SẢN:\n{bio['reproductionNotes']}")

        if to_trans:
            prompt = (
                f"Hãy dịch các đoạn thông tin sinh học sau đây của loài giáp xác {sp.get('vn_name')} "
                f"({sp.get('scientific_name')}) sang tiếng Việt học thuật chuẩn mực.\n\n"
                + "\n\n---\n\n".join(to_trans)
                + "\n\nTrả về bản dịch theo cấu trúc JSON gồm các khóa: 'biologySummaryVn', 'ecologyNotesVn', 'reproductionNotesVn' (nếu không có trường nào thì để null)."
            )
            res_text = call_gemini(prompt)
            if res_text:
                try:
                    # Clean markdown fence if present
                    clean_json = re.sub(r'^```json\s*|\s*```$', '', res_text.strip(), flags=re.MULTILINE)
                    trans_data = json.loads(clean_json)
                    if trans_data.get("biologySummaryVn"):
                        bio["biologySummaryVn"] = trans_data["biologySummaryVn"]
                    if trans_data.get("ecologyNotesVn"):
                        bio["ecologyNotesVn"] = trans_data["ecologyNotesVn"]
                    if trans_data.get("reproductionNotesVn"):
                        bio["reproductionNotesVn"] = trans_data["reproductionNotesVn"]
                except Exception:
                    pass

    return bio


def main():
    global SYSTEM_PROMPT
    parser = argparse.ArgumentParser(description="Đồng bộ dữ liệu SeaLifeBase v25.04 cho sinh vật biển (Giáp xác, Rắn biển...)")
    parser.add_argument("--collection", type=str, default="giap-xac", help="Mã collection (mặc định: giap-xac, hỗ trợ ran-bien)")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước kết quả, không ghi vào CSDL Supabase")
    parser.add_argument("--id", type=str, help="Chạy cho một loài cụ thể theo id (vd: ranbien-species-1)")
    parser.add_argument("--limit", type=int, help="Giới hạn số loài cần xử lý")
    parser.add_argument("--no-translate", action="store_true", help="Bỏ qua bước dịch AI Gemini")
    parser.add_argument("--force", action="store_true", help="Ghi đè cả loài đã có trường biology")
    args = parser.parse_args()

    col = args.collection
    if col == "ran-bien":
        SYSTEM_PROMPT = SYSTEM_PROMPT_HERPETOLOGY
        col_name = "RẮN BIỂN VIỆT NAM"
        col_icon = "🐍"
    else:
        SYSTEM_PROMPT = SYSTEM_PROMPT_CRUSTACEA
        col_name = "GIÁP XÁC BIỂN"
        col_icon = "🦐"

    print("=" * 75)
    print(f"{col_icon} SEALIFEBASE SYNC — CẨM NANG SINH VẬT BIỂN VIỆT NAM ({col_name})")
    print("=" * 75)

    download_tables_if_needed()
    con = init_duckdb()

    # Lấy danh sách loài từ Supabase
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.{col}&order=species_index.asc"
    if args.id:
        url += f"&id=eq.{args.id}"
    resp = requests.get(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}, timeout=30)
    resp.raise_for_status()
    species_list = resp.json()

    print(f"✓ Đã nạp {len(species_list)} loài từ CSDL Supabase ({col}).")
    if args.limit:
        species_list = species_list[:args.limit]
        print(f"  → Giới hạn xử lý: {len(species_list)} loài.")

    success_count = 0
    skip_count = 0
    not_found_count = 0

    for idx, sp in enumerate(species_list, 1):
        sp_id = sp["id"]
        vn_name = sp.get("vn_name") or "Chưa rõ"
        sci_name = sp.get("scientific_name") or ""
        curr_bio = sp.get("biology")

        if curr_bio and not args.force and not args.id:
            print(f"[{idx}/{len(species_list)}] ⏩ Bỏ qua {sp_id}: {vn_name} (Đã có biology)")
            skip_count += 1
            continue

        raw_bio = query_sealifebase(con, sp)
        if not raw_bio:
            print(f"[{idx}/{len(species_list)}] ⚠️ Không tìm thấy trên SeaLifeBase: [{sp_id}] {vn_name} ({sci_name})")
            not_found_count += 1
            continue

        print(f"[{idx}/{len(species_list)}] 🔍 Khớp [{sp_id}] {vn_name} -> SpecCode {raw_bio['specCode']} ({raw_bio['matchMethod']})")
        
        # Enrich & Translate
        final_bio = enrich_species(sp, raw_bio, translate=not args.no_translate)

        # Prepare update payload
        update_data = {"biology": final_bio}
        if raw_bio.get("fbName") and not sp.get("en_common_name"):
            update_data["en_common_name"] = raw_bio["fbName"]

        if args.dry_run:
            print(f"  [DRY-RUN] Dữ liệu sinh học trích xuất:")
            print(f"    • Kích thước: {final_bio.get('maxLength')} | Độ sâu: {final_bio.get('depth')} | Sinh cảnh: {final_bio.get('habitat')}")
            print(f"    • Trophic: {final_bio.get('trophicLevel')} | Tên EN: {raw_bio.get('fbName')}")
            if final_bio.get('biologySummaryVn'):
                print(f"    • Mô tả VN: {final_bio.get('biologySummaryVn')[:150]}...")
        else:
            # Ghi vào Supabase
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            presp = requests.patch(patch_url, headers=HEADERS_SUPA, json=update_data, timeout=30)
            if presp.status_code in [200, 204]:
                print(f"  ✓ Đã cập nhật thành công vào Supabase [{sp_id}].")
                success_count += 1
            else:
                print(f"  ❌ Lỗi cập nhật Supabase [{sp_id}]: {presp.text}")

        # Nghỉ nhẹ giữa các lần gọi Gemini nếu dịch
        if not args.no_translate and GEMINI_API_KEY and not args.dry_run:
            time.sleep(0.5)

    print("\n" + "=" * 75)
    print("📊 TỔNG KẾT ĐỒNG BỘ SEALIFEBASE:")
    print(f"  • Tổng loài xử lý: {len(species_list)}")
    print(f"  • Cập nhật thành công: {success_count}")
    print(f"  • Bỏ qua (đã có):   {skip_count}")
    print(f"  • Không tìm thấy:    {not_found_count}")
    print("=" * 75)


if __name__ == '__main__':
    main()
