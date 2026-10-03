#!/usr/bin/env python3
"""
scripts/sync_sealifebase.py
----------------------------
Đồng bộ và làm giàu dữ liệu sinh học, sinh thái, kích thước, tập tính và mô tả song ngữ Việt - Anh
cho TOÀN BỘ các nhóm sinh vật biển ngoài cá (Non-Fish Marine Organisms) từ hệ sinh thái SeaLifeBase v25.04:
  - bo-sat-bien: Bò sát biển (Rắn biển, Rùa biển, Cá sấu hoa cà)
  - than-mem: Động vật thân mềm (Ốc, Sò, Mực, Bạch tuộc...)
  - san-ho: San hô & Thích ty bào (San hô tám ngăn, san hô cứng, hải quỳ...)
  - giap-xac: Giáp xác biển (Tôm, Cua, Ghẹ, Tôm hùm, Tôm tít...)
  - sinh-vat-doc: Động vật độc biển (Sứa lửa, Ốc cối, Bạch tuộc đốm xanh, Rắn biển, Cầu gai...)

Cơ chế đối chiếu 4 tầng:
  1. Bảng đối chiếu thủ công (Manual Override / Special historic names)
  2. Tên khoa học gốc trong sách OCR (scientific_name)
  3. Danh pháp hợp lệ chuẩn WoRMS (worms_accepted_name)
  4. Bảng đồng danh phân loại toàn cầu của SeaLifeBase (synonyms.parquet - 143,000+ tên)

Tự động dịch thuật học thuật chuyên ngành sang tiếng Việt bằng Gemini AI:
  - Giáp xác học (Carcinology)
  - Bò sát học biển (Marine Herpetology)
  - Thân mềm học (Malacology)
  - San hô & Thích ty bào học (Cnidariology)
  - Độc tố học sinh vật biển (Marine Toxicology)

Cơ chế Deep Merge an toàn tuyệt đối:
  - Bảo toàn 100% hồ sơ Sách Đỏ VAST 2024 (vnRedList) và các dữ liệu đã có.
  - Làm giàu các chỉ số định lượng: maxLength, maxWeight, depth, trophicLevel, vulnerability, dangerous.
  - Làm giàu các khối ghi chú song ngữ: biologySummaryVn, ecologyNotesVn, reproductionNotesVn.
  - Đồng bộ mã định danh quốc tế song hành: external_ids.sealifebase & external_ids.gbif.
  - Đồng bộ depth_range và max_size ở cấp độ bảng species.

Cách dùng:
  # 1. Chạy thử xem trước nhóm bò sát biển (không ghi DB):
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --collection bo-sat-bien --dry-run

  # 2. Đồng bộ thật cho nhóm bò sát biển:
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --collection bo-sat-bien

  # 3. Đồng bộ cho 1 loài cụ thể:
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --id ruabien-species-1

  # 4. Chạy cho toàn bộ các nhóm sinh vật biển ngoài cá:
  uv run --with duckdb,requests,python-dotenv python3 scripts/sync_sealifebase.py --collection all-non-fish
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
    # Giáp xác
    'Lysiosquillina tredecimdentata': 92615,
    # Rắn biển
    'Hydrophis annandalei': 83964,
    'Hydrophis anomalus': 83976,
    'Hydrophis jerdonii': 83963,
    'Hydrophis viperina': 83975,
    'Hydrophis brookii': 83936,
    'Hydrophis pachycercos': 153049,
    'Hydrophis platura': 67462,
    'Microcephalophis gracilis': 83972,
    # Rùa biển & Cá sấu
    'Chelonia mydas': 67018,
    'Caretta caretta': 67017,
    'Eretmochelys imbricata': 67019,
    'Lepidochelys olivacea': 67020,
    'Dermochelys coriacea': 67021,
    'Crocodylus porosus': 67466,
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

# ─── HỆ THỐNG PROMPT CHUYÊN NGÀNH HỌC THUẬT (SYSTEM PROMPTS) ──────────────────

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
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân, chỉ dịch trung thực và mượt mà nội dung nguồn."""

SYSTEM_PROMPT_HERPETOLOGY = """Bạn là chuyên gia hàng đầu về Bò sát học biển (Marine Herpetology) và Bảo tồn Sinh vật biển tại Viện Hải dương học Nha Trang & VAST.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, tập tính làm tổ, di cư và sinh sản của các loài Bò sát biển (Rùa biển, Rắn biển, Cá sấu hoa cà) từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu Bò sát chí và Sách Đỏ Việt Nam.
2. Dịch chuẩn xác các thuật ngữ bò sát học biển:
   - 'carapace length' / 'straight carapace length' (SCL): chiều dài mai theo đường thẳng
   - 'curved carapace length' (CCL): chiều dài mai theo đường cong
   - 'plastron': yếm rùa
   - 'prefrontal scales': vảy trước trán
   - 'clutch size' / 'eggs per clutch': số trứng mỗi lứa / ổ trứng
   - 'nesting beach': bãi cát đẻ trứng / bãi làm tổ
   - 'nesting cycle': chu kỳ sinh sản / chu kỳ đẻ trứng
   - 'renesting interval': khoảng cách giữa các lần đẻ trứng trong mùa
   - 'arribada': hiện tượng rùa biển lên bãi đẻ trứng đồng loạt
   - 'incubation period': thời gian ấp trứng
   - 'temperature-dependent sex determination' (TSD): cơ chế xác định giới tính theo nhiệt độ tổ trứng
   - 'hatchlings': rùa con mới nở
   - 'spongivore': chuyên ăn bọt biển (hải miên)
   - 'gelatinivore': chuyên ăn sinh vật thân mềm trôi nổi và sứa biển
   - 'herbivore': ăn thực vật / cỏ biển
   - 'pelagic dive pattern': kiểu lặn sâu đại dương
   - 'paddle-shaped tail': đuôi dẹp như mái chèo
   - 'ovoviviparous' / 'viviparous': trứng thai / đẻ con
   - 'oviparous': đẻ trứng
   - 'venomous': có nọc độc
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân, dịch mạch lạc và trung thực."""

SYSTEM_PROMPT_MALACOLOGY = """Bạn là chuyên gia hàng đầu về Thân mềm học (Malacology) và Thủy sinh học biển tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, vỏ ốc, sinh sản và tập tính của các loài Thân mềm biển (Ốc, Sò, Điệp, Nghêu, Mực, Bạch tuộc) từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu Thân mềm học Việt Nam.
2. Dịch chuẩn xác các thuật ngữ thân mềm học:
   - 'shell length' (SL): chiều dài vỏ
   - 'body whorl': tầng thân vỏ
   - 'spire': tháp vỏ
   - 'aperture': miệng vỏ
   - 'operculum': nắp vỏ
   - 'radula': dải răng giũa
   - 'siphon': ống hút nước / ống xiphon
   - 'mantle': màng áo
   - 'benthic': tầng đáy
   - 'intertidal': vùng gian triều / bãi triều
   - 'epifauna': sinh vật sống bám trên bề mặt đáy
   - 'infauna': sinh vật sống vùi mình trong đáy bùn cát
   - 'filter feeder': động vật lọc nước ăn sinh vật phù du
   - 'carnivorous snail': ốc ăn thịt
   - 'conotoxin': độc tố peptide conotoxin (ốc cối)
   - 'egg capsules': bao nang trứng
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân."""

SYSTEM_PROMPT_CNIDARIA = """Bạn là chuyên gia hàng đầu về San hô & Thích ty bào học (Cnidariology) tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái rạn, cấu trúc tập đoàn và sinh sản của các loài San hô và Thích ty bào biển (San hô tám ngăn Octocorallia, San hô cứng Scleractinia, Hải quỳ, Thủy tức, Sứa biển) từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo chuyên khảo San hô Việt Nam.
2. Dịch chuẩn xác các thuật ngữ san hô học:
   - 'colony': tập đoàn san hô
   - 'polyp': cá thể san hô / polyp
   - 'sclerites': trâm xương / gai xương
   - 'coenenchyme': mô liên kết thịt san hô
   - 'zooxanthellae': tảo cộng sinh đơn bào
   - 'tentacles': xúc tu
   - 'nematocysts' / 'cnidocytes': nang thích ty / tế bào thích ty
   - 'broadcast spawner': thụ tinh ngoài giải phóng giao tử hàng loạt
   - 'brooder': ấp thụ tinh trong cá thể mẹ
   - 'branching' / 'encrusting' / 'massive': dạng phân nhánh / dạng phủ bám / dạng khối
   - 'reef-building' (hermatypic): san hô tạo rạn
   - 'deep-water octocoral': san hô tám ngăn vùng nước sâu
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
4. KHÔNG thêm bớt ý kiến cá nhân."""

SYSTEM_PROMPT_TOXICOLOGY = """Bạn là chuyên gia hàng đầu về Độc tố học Sinh vật biển (Marine Toxicology) và Sinh học biển tại Viện Hải dương học Nha Trang.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả độc tố, sinh thái học, cơ chế tác động và tập tính săn mồi của các loài động vật biển có độc từ SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học y sinh học biển chuẩn mực, khúc chiết, chuẩn hóa y tế.
2. Dịch chuẩn xác các thuật ngữ độc tố học:
   - 'venomous': có nọc độc tiếp xúc/chích/cắn
   - 'poisonous': độc khi ăn phải ngộ độc thực phẩm
   - 'neurotoxin': độc tố thần kinh
   - 'myotoxin': độc tố cơ
   - 'tetrodotoxin' (TTX): độc tố tetrodotoxin
   - 'saxitoxin' (STX): độc tố saxitoxin
   - 'conotoxin': độc tố peptide ốc cối
   - 'envenomation': sự nhiễm độc nọc
   - 'lethal dose' (LD50): liều gây tử vong 50%
3. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234)."""

SYSTEM_PROMPT_MAMMALIA = """Bạn là chuyên gia hàng đầu về Thú biển học (Marine Mammalogy / Cetology & Sirenology) và Sinh học đại dương tại Viện Hải dương học.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái, kích thước, khối lượng, độ sâu lặn, thức ăn, tập tính bầy đàn và sinh sản của các loài Thú biển (Bò biển Dugong, Cá voi tấm sừng hàm, Cá nhà táng, Cá voi có mỏ và Cá heo) từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, gãy gọn, chính xác theo đúng tài liệu sinh học thú biển và động vật chí Việt Nam.
2. Tuân thủ tuyệt đối: Cơ quan là "Viện Hải dương học" (không bao giờ viết thêm chữ Nha Trang đằng sau).
3. Dịch chuẩn xác các thuật ngữ thú biển học:
   - 'total length' (TL): chiều dài toàn thân
   - 'body weight' / 'body mass': khối lượng cơ thể
   - 'baleen plates': tấm sừng hàm
   - 'blowhole': lỗ thở
   - 'flukes': thùy đuôi
   - 'dorsal fin': vây lưng
   - 'pectoral flippers' / 'pectoral fins': vây ngực / chi chèo
   - 'bubble-net feeding': kỹ thuật săn mồi bằng lưới bong bóng khí
   - 'lunge feeding': săn mồi lao đớp mở rộng miệng
   - 'breaching': cú nhảy nhào lộn vọt khỏi mặt nước
   - 'echolocation': định vị bằng sóng âm
   - 'pods': đàn / bầy
   - 'pelagic': vùng biển khơi
   - 'demersal': vùng biển tầng đáy
   - 'coastal / inshore': vùng ven bờ
   - 'gestation period': thời gian mang thai
   - 'lactation': thời kỳ nuôi con bằng sữa mẹ
   - 'calving': sinh con non
   - 'herbivorous': ăn thực vật (cỏ biển)
   - 'carnivorous': ăn thịt (cá, mực, giáp xác)
4. Giữ nguyên tên khoa học và các trích dẫn tài liệu như (Ref. 1234).
5. KHÔNG thêm bớt ý kiến cá nhân, dịch mạch lạc và trung thực."""

SYSTEM_PROMPT_GENERAL = """Bạn là chuyên gia Sinh học biển tại Viện Hải dương học.
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái và sinh sản của sinh vật biển từ cơ sở dữ liệu SeaLifeBase sang tiếng Việt khoa học chuẩn mực, gãy gọn, trung thực với dữ liệu gốc."""


def get_system_prompt_for_species(sp: dict, col: str) -> str:
    """Chọn System Prompt phù hợp nhất theo từng phân ngành học thuật."""
    tax_class = (sp.get('tax_class_latin') or '').lower()
    tax_phylum = (sp.get('tax_phylum_latin') or '').lower()
    tax_order = (sp.get('tax_order_latin') or '').lower()
    sp_id = sp.get('id', '')

    # 0. Thú biển (Mammalia: Bò biển, Cá voi, Cá heo)
    if col == 'thu-bien' or tax_class == 'mammalia' or sp_id.startswith('thubien-'):
        return SYSTEM_PROMPT_MAMMALIA

    # 1. Bò sát biển (Reptilia: Rùa biển, Rắn biển, Cá sấu)
    if col == 'bo-sat-bien' or tax_class == 'reptilia' or sp_id.startswith(('ruabien-', 'ranbien-', 'casau-')):
        return SYSTEM_PROMPT_HERPETOLOGY

    # 2. Thân mềm (Mollusca: Ốc, Sò, Mực, Bạch tuộc)
    if col == 'than-mem' or tax_phylum == 'mollusca' or tax_class in ('gastropoda', 'bivalvia', 'cephalopoda') or sp_id.startswith('thanmem-'):
        return SYSTEM_PROMPT_MALACOLOGY

    # 3. San hô & Thích ty bào (Cnidaria)
    if col == 'san-ho' or tax_phylum == 'cnidaria' or tax_class in ('anthozoa', 'hydrozoa', 'scyphozoa') or sp_id.startswith('sanho-'):
        return SYSTEM_PROMPT_CNIDARIA

    # 4. Giáp xác (Crustacea)
    if col == 'giap-xac' or sp_id.startswith('giapxac-') or 'malacostraca' in tax_class or tax_order in ('decapoda', 'stomatopoda'):
        return SYSTEM_PROMPT_CRUSTACEA

    # 5. Sinh vật độc
    if col == 'sinh-vat-doc' or sp_id.startswith('doc-'):
        if tax_class == 'reptilia':
            return SYSTEM_PROMPT_HERPETOLOGY
        if tax_phylum == 'mollusca':
            return SYSTEM_PROMPT_MALACOLOGY
        if tax_phylum == 'cnidaria':
            return SYSTEM_PROMPT_CNIDARIA
        return SYSTEM_PROMPT_TOXICOLOGY

    return SYSTEM_PROMPT_GENERAL


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


def call_gemini(prompt: str, system_prompt: str) -> str:
    """Gọi Gemini API qua danh sách model fallback với system prompt chuyên ngành."""
    if not GEMINI_API_KEY:
        return ""

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
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
        except Exception:
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


def query_gbif_usage_key(scientific_name: str) -> int | None:
    """Tra cứu usageKey định danh quốc tế trên GBIF API."""
    if not scientific_name:
        return None
    try:
        url = f"https://api.gbif.org/v1/species/match?name={urllib.parse.quote(scientific_name)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            if data.get("matchType") in ("EXACT", "FUZZY") and data.get("usageKey"):
                return data["usageKey"]
    except Exception:
        pass
    return None


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
        SELECT FoodTroph, DietTroph, FeedingType, FoodRemark, DietRemark, AddRems
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

    # Weight in kg or g
    weight_val = None
    if s[7] is not None:
        raw_w = float(s[7])
        if raw_w >= 1000:
            weight_val = f"{raw_w / 1000:.1f} kg"
        else:
            weight_val = f"{raw_w:.1f} g"

    depth_val = None
    if s[8] is not None or s[9] is not None:
        min_d = s[8] if s[8] is not None else "0"
        max_d = s[9] if s[9] is not None else "?"
        depth_val = f"{min_d} - {max_d} m"

    troph = e[0] if (e and e[0] is not None) else (e[1] if (e and e[1] is not None) else None)
    feed_type = e[2] if (e and e[2]) else None
    
    # Ghi chú sinh thái học: ưu tiên AddRems, sau đó FoodRemark/DietRemark
    ecol_notes = None
    if e:
        candidates = [e[5], e[3], e[4]]
        for cand in candidates:
            if cand and len(str(cand).strip()) > 10:
                ecol_notes = str(cand).strip()
                break

    rep_mode = r[0] if (r and r[0]) else (r[1] if (r and r[1]) else None)
    rep_notes = r[3] if (r and r[3] and len(str(r[3]).strip()) > 10) else None

    return {
        "specCode": spec_code,
        "fbName": en_name,
        "source": "SeaLifeBase v25.04",
        "matchMethod": match_method,
        "maxLength": length_val,
        "maxWeight": weight_val,
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


def enrich_species(sp: dict, bio_raw: dict, col: str, translate: bool = True):
    bio = dict(bio_raw)
    system_prompt = get_system_prompt_for_species(sp, col)
    
    # Translate summaries if requested
    if translate and GEMINI_API_KEY:
        to_trans = []
        if bio.get("biologySummary"):
            to_trans.append(f"MÔ TẢ SINH HỌC:\n{bio['biologySummary']}")
        if bio.get("ecologyNotes"):
            to_trans.append(f"GHI CHÚ SINH THÁI HỌC & TẬP TÍNH:\n{bio['ecologyNotes']}")
        if bio.get("reproductionNotes"):
            to_trans.append(f"ĐẶC ĐIỂM SINH SẢN & LÀM TỔ:\n{bio['reproductionNotes']}")

        if to_trans:
            prompt = (
                f"Hãy dịch các đoạn thông tin sinh học sau đây của loài {sp.get('vn_name') or ''} "
                f"({sp.get('scientific_name')}) sang tiếng Việt học thuật chuẩn mực của Viện Hải dương học Nha Trang.\n\n"
                + "\n\n---\n\n".join(to_trans)
                + "\n\nTrả về bản dịch theo định dạng JSON gồm các khóa: 'biologySummaryVn', 'ecologyNotesVn', 'reproductionNotesVn' (nếu không có trường nào thì trả về null)."
            )
            res_text = call_gemini(prompt, system_prompt)
            if res_text:
                try:
                    trans_data = json.loads(res_text.strip())
                except Exception:
                    clean_json = re.sub(r'^```(?:json)?\s*|\s*```$', '', res_text.strip(), flags=re.MULTILINE)
                    match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                    trans_data = json.loads(match.group(0)) if match else {}

                if isinstance(trans_data, dict):
                    if trans_data.get("biologySummaryVn"):
                        bio["biologySummaryVn"] = trans_data["biologySummaryVn"]
                    if trans_data.get("ecologyNotesVn"):
                        bio["ecologyNotesVn"] = trans_data["ecologyNotesVn"]
                    if trans_data.get("reproductionNotesVn"):
                        bio["reproductionNotesVn"] = trans_data["reproductionNotesVn"]

    return bio


def deep_merge_biology(curr_bio: dict | None, final_bio: dict) -> dict:
    """
    Cơ chế Deep Merge an toàn:
    Bảo toàn 100% hồ sơ Sách Đỏ VAST 2024 (vnRedList), toxicology và các trường đã có.
    Bổ sung các trường đo lường định lượng và ghi chú chuyên sâu từ SeaLifeBase.
    """
    merged = dict(curr_bio or {})

    # Các khóa cập nhật từ SeaLifeBase
    slb_keys = [
        "specCode", "fbName", "maxLength", "maxWeight", "depth",
        "trophicLevel", "vulnerability", "dangerous", "reproduction",
        "biologySummary", "biologySummaryVn",
        "ecologyNotes", "ecologyNotesVn",
        "reproductionNotes", "reproductionNotesVn"
    ]

    for k in slb_keys:
        val = final_bio.get(k)
        if val is not None:
            # Nếu bản ghi hiện có đã có bản dịch tiếng Việt rất chi tiết, không ghi đè nếu val rỗng
            if k.endswith("Vn") and merged.get(k) and not val:
                continue
            merged[k] = val

    # Habitat / FeedingType: chỉ nạp nếu chưa có
    if final_bio.get("habitat") and not merged.get("habitat"):
        merged["habitat"] = final_bio["habitat"]
    if final_bio.get("feedingType") and not merged.get("feedingType"):
        merged["feedingType"] = final_bio["feedingType"]

    if final_bio.get("matchMethod"):
        merged["matchMethod"] = final_bio["matchMethod"]

    # Đảm bảo source ghi nhận SeaLifeBase v25.04
    curr_source = str(merged.get("source") or "")
    if "SeaLifeBase" not in curr_source:
        if curr_source:
            merged["source"] = f"SeaLifeBase v25.04 & {curr_source}"
        else:
            merged["source"] = "SeaLifeBase v25.04"

    return merged


def process_collection(con, col: str, args):
    COLLECTION_TITLES = {
        "bo-sat-bien": ("BÒ SÁT BIỂN (Rùa, Rắn, Cá sấu)", "🐢"),
        "than-mem": ("ĐỘNG VẬT THÂN MỀM (Ốc, Sò, Mực)", "🐚"),
        "san-ho": ("SAN HÔ & THÍCH TY BÀO", "🪸"),
        "giap-xac": ("GIÁP XÁC BIỂN (Tôm, Cua, Ghẹ)", "🦐"),
        "sinh-vat-doc": ("ĐỘNG VẬT ĐỘC BIỂN (Sứa, Ốc cối, Bạch tuộc đốm xanh...)", "☣️"),
    }

    col_title, col_icon = COLLECTION_TITLES.get(col, (col.upper(), "🌊"))

    print("\n" + "=" * 78)
    print(f"{col_icon} SEALIFEBASE SYNC v2.0 — {col_title} [collection_id='{col}']")
    print("=" * 78)

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
        curr_bio = sp.get("biology") or {}

        # Tiêu chí bỏ qua: Đã có specCode VÀ đã có mô tả sinh học (hoặc bản dịch)
        has_slb_enrichment = bool(curr_bio.get("specCode") and (curr_bio.get("biologySummaryVn") or curr_bio.get("biologySummary")))
        if has_slb_enrichment and not args.force and not args.id:
            print(f"[{idx}/{len(species_list)}] ⏩ Bỏ qua [{sp_id}] {vn_name}: Đã hoàn thiện SeaLifeBase.")
            skip_count += 1
            continue

        raw_bio = query_sealifebase(con, sp)
        if not raw_bio:
            print(f"[{idx}/{len(species_list)}] ⚠️ Không tìm thấy trên SeaLifeBase: [{sp_id}] {vn_name} ({sci_name})")
            not_found_count += 1
            continue

        print(f"[{idx}/{len(species_list)}] 🔍 Khớp [{sp_id}] {vn_name} -> SpecCode {raw_bio['specCode']} ({raw_bio['matchMethod']})")

        # Enrich & Translate với Prompt chuyên ngành phù hợp
        final_bio = enrich_species(sp, raw_bio, col, translate=not args.no_translate)

        # Deep merge bảo toàn dữ liệu hiện có
        merged_bio = deep_merge_biology(curr_bio, final_bio)

        # Tra cứu GBIF usageKey
        gbif_key = query_gbif_usage_key(sci_name)
        if gbif_key:
            merged_bio["gbifKey"] = gbif_key

        # Chuẩn bị payload cập nhật (chỉ gửi các cột thực tế tồn tại trên bảng species)
        update_data = {"biology": merged_bio}

        # Cập nhật tên tiếng Anh nếu loài chưa có
        if not sp.get("en_common_name") and raw_bio.get("fbName"):
            update_data["en_common_name"] = raw_bio["fbName"]

        if args.dry_run:
            print(f"  [DRY-RUN] Dữ liệu sinh học trích xuất:")
            print(f"    • Kích thước: {merged_bio.get('maxLength')} | Cân nặng: {merged_bio.get('maxWeight')} | Độ sâu: {merged_bio.get('depth')}")
            print(f"    • Trophic: {merged_bio.get('trophicLevel')} | Tên EN: {raw_bio.get('fbName')} | GBIF: {gbif_key}")
            print(f"    • Bảo tồn VAST: {'Vẫn giữ nguyên' if merged_bio.get('vnRedList') else 'Không có'}")
            if merged_bio.get('biologySummaryVn'):
                print(f"    • Mô tả sinh học VN: {merged_bio.get('biologySummaryVn')[:120]}...")
            if merged_bio.get('reproductionNotesVn'):
                print(f"    • Ghi chú sinh sản VN: {merged_bio.get('reproductionNotesVn')[:120]}...")
        else:
            # Ghi vào Supabase
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            presp = requests.patch(patch_url, headers=HEADERS_SUPA, json=update_data, timeout=30)
            if presp.status_code in [200, 204]:
                print(f"  ✓ Đã cập nhật thành công vào Supabase [{sp_id}] (SLB: {raw_bio['specCode']}{f', GBIF: {gbif_key}' if gbif_key else ''}).")
                success_count += 1
            else:
                print(f"  ❌ Lỗi cập nhật Supabase [{sp_id}]: {presp.text}")

        # Nghỉ nhẹ giữa các lần gọi Gemini nếu dịch
        if not args.no_translate and GEMINI_API_KEY and not args.dry_run:
            time.sleep(0.5)

    print(f"\n📊 Tổng kết collection [{col}]:")
    print(f"  • Đã xử lý: {len(species_list)} loài")
    print(f"  • Cập nhật thành công: {success_count}")
    print(f"  • Bỏ qua (đã đủ dữ liệu): {skip_count}")
    print(f"  • Không tìm thấy: {not_found_count}")


def main():
    parser = argparse.ArgumentParser(description="Đồng bộ dữ liệu SeaLifeBase v25.04 & GBIF cho TOÀN BỘ các nhóm sinh vật biển ngoài cá")
    parser.add_argument("--collection", type=str, default="giap-xac",
                        help="Mã collection: bo-sat-bien, than-mem, san-ho, giap-xac, sinh-vat-doc, hoặc 'all-non-fish'")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước kết quả, không ghi vào CSDL Supabase")
    parser.add_argument("--id", type=str, help="Chạy cho một loài cụ thể theo id (vd: ruabien-species-1)")
    parser.add_argument("--limit", type=int, help="Giới hạn số loài cần xử lý")
    parser.add_argument("--no-translate", action="store_true", help="Bỏ qua bước dịch AI Gemini")
    parser.add_argument("--force", action="store_true", help="Ghi đè làm mới cả loài đã có đủ dữ liệu SeaLifeBase")
    args = parser.parse_args()

    download_tables_if_needed()
    con = init_duckdb()

    VALID_COLLECTIONS = ["bo-sat-bien", "than-mem", "san-ho", "giap-xac", "sinh-vat-doc", "thu-bien"]

    if args.id:
        # Nếu chỉ định ID cụ thể, tự tìm collection của loài đó
        check_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{args.id}&select=collection_id"
        cresp = requests.get(check_url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}, timeout=15)
        cdata = cresp.json()
        target_col = cdata[0]["collection_id"] if cdata else args.collection
        process_collection(con, target_col, args)
    elif args.collection == "all-non-fish":
        print("\n🚀 BẮT ĐẦU ĐỒNG BỘ TOÀN BỘ 5 NHÓM SINH VẬT BIỂN NGOÀI CÁ TRÊN TOÀN HỆ THỐNG...")
        for col in VALID_COLLECTIONS:
            process_collection(con, col, args)
    else:
        process_collection(con, args.collection, args)

    print("\n🏁 HOÀN TẤT TOÀN BỘ TIẾN TRÌNH ĐỒNG BỘ SEALIFEBASE!")


if __name__ == '__main__':
    main()
