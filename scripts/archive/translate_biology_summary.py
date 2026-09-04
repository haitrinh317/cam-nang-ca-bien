"""
translate_biology_summary.py
----------------------------
Dịch thông tin tóm tắt sinh học (FishBase: biologySummary, ecologyNotes, reproductionNotes)
sang tiếng Việt với văn phong khoa học chuẩn mực thông qua Gemini AI,
sau đó cập nhật trường 'biology' vào CSDL Supabase.

Cách chạy:
  # 1. Chạy thử nghiệm xem trước (Preview) 3 loài tiêu biểu, KHÔNG ghi vào Supabase:
  python3 scripts/translate_biology_summary.py --dry-run --limit 3

  # 2. Dịch và lưu vào Supabase cho một loài cụ thể:
  python3 scripts/translate_biology_summary.py --id tap1-species-2

  # 3. Dịch và lưu cho toàn bộ một Tập cụ thể (ví dụ Tập 1):
  python3 scripts/translate_biology_summary.py --volume 1

  # 4. Dịch toàn bộ các loài chưa có bản dịch tiếng Việt:
  python3 scripts/translate_biology_summary.py --all
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env", file=sys.stderr)
    sys.exit(1)

if not GEMINI_API_KEY:
    print("[ERROR] Thiếu GEMINI_API_KEY trong .env", file=sys.stderr)
    sys.exit(1)

SYSTEM_PROMPT = """Bạn là chuyên gia hàng đầu về Ngư loại học (Ichthyology) và Sinh học biển tại Việt Nam (Viện Hải dương học / Viện Nghiên cứu Hải sản).
Nhiệm vụ của bạn là dịch các đoạn văn bản mô tả sinh học, sinh thái của loài cá biển từ cơ sở dữ liệu FishBase sang tiếng Việt.

YÊU CẦU DỊCH THUẬT:
1. Văn phong khoa học hàn lâm, chuẩn mực, trong sáng, gãy gọn và dễ hiểu theo đúng chuẩn mực tài liệu sinh học Việt Nam.
2. Dịch chuẩn xác các thuật ngữ ngư học và hải dương học:
   - 'continental shelf': thềm lục địa
   - 'insular shelf': thềm quanh đảo
   - 'demersal': tầng đáy (hoặc cá tầng đáy)
   - 'pelagic': tầng nổi / biển khơi
   - 'benthopelagic': tầng trung - đáy
   - 'bathydemersal': đáy sâu
   - 'reef-associated': sống quanh rạn san hô / liên kết rạn san hô
   - 'intertidal': vùng gian triều / bãi triều
   - 'subtidal': vùng dưới triều
   - 'lagoon': đầm phá / vụng san hô kín
   - 'outer reef slope': sườn ngoài rạn san hô
   - 'drop-offs': bờ dốc đứng dưới biển
   - 'estuary / estuarine': cửa sông / vùng nước lợ cửa sông
   - 'oviparous': đẻ trứng
   - 'viviparous': đẻ con
   - 'ovoviviparous': noãn thai sinh
   - 'carnivorous / carnivore': ăn thịt
   - 'herbivorous / herbivore': ăn thực vật
   - 'planktivorous / planktivore': ăn sinh vật phù du
   - 'corallivorous / corallivore': ăn san hô
   - 'feeds on...': thức ăn chủ yếu gồm... / chuyên ăn...
   - 'solitary': sống đơn độc
   - 'schooling': sống theo đàn / kết đàn
   - 'juveniles': cá con / cá non
   - 'adults': cá trưởng thành
   - 'inhabits / found in': phân bố tại / sinh sống ở
   - 'nocturnal': hoạt động về đêm
   - 'diurnal': hoạt động ban ngày
   - 'cryptic': ngụy trang / ẩn nấp
3. TUYỆT ĐỐI KHÔNG dịch theo kiểu thô từng từ (word-by-word) của máy dịch tự động thông thường. Câu văn phải mạch lạc, uyển chuyển, đúng văn phạm tiếng Việt.
4. Giữ nguyên danh pháp khoa học La-tinh (ví dụ Acropora, Porites, Copepoda...).
5. Chỉ trả về một JSON duy nhất với các trường tương ứng đã dịch, KHÔNG kèm giải thích hay markdown code blocks ngoài JSON.
"""

# Ưu tiên các model flash có quota hoạt động
MODELS = [
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3-flash-preview",
]

def normalize_translated_keys(raw: dict) -> dict:
    """Chuẩn hóa mọi dạng key về định dạng chuẩn lưu CSDL: biologySummaryVn, reproductionNotesVn..."""
    res = {}
    for k, v in raw.items():
        if not v:
            continue
        val_str = str(v).strip()
        if not val_str:
            continue
        if k in ('biologySummary', 'biologySummaryVn'):
            res['biologySummaryVn'] = val_str
        elif k in ('ecologyNotes', 'ecologyNotesVn'):
            res['ecologyNotesVn'] = val_str
        elif k in ('reproductionNotes', 'reproductionNotesVn'):
            res['reproductionNotesVn'] = val_str
        elif k in ('morphDescription', 'morphDescriptionVn'):
            res['morphDescriptionVn'] = val_str
        else:
            res[k] = val_str
    return res

def translate_biology_fields(sci_name: str, vn_name: str, bio_dict: dict) -> dict:
    """Gọi Gemini để dịch các trường văn bản trong biology sang tiếng Việt."""
    targets = {}
    if bio_dict.get('biologySummary'):
        targets['biologySummary'] = bio_dict['biologySummary']
    if bio_dict.get('ecologyNotes') and bio_dict['ecologyNotes'] != bio_dict.get('biologySummary'):
        targets['ecologyNotes'] = bio_dict['ecologyNotes']
    if bio_dict.get('reproductionNotes'):
        targets['reproductionNotes'] = bio_dict['reproductionNotes']
    if bio_dict.get('morphDescription'):
        targets['morphDescription'] = bio_dict['morphDescription']

    if not targets:
        return {}

    user_text = f"""Loài cá: {vn_name} ({sci_name})
Dưới đây là các đoạn văn bản tiếng Anh cần dịch sang tiếng Việt khoa học:
{json.dumps(targets, ensure_ascii=False, indent=2)}

Trả về JSON có dạng:
{{
  "biologySummaryVn": "...",
  "ecologyNotesVn": "...",
  "reproductionNotesVn": "...",
  "morphDescriptionVn": "..."
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

    for outer in range(3):
        for model_name in MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
            
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                        parsed = json.loads(raw_text.strip())
                        return normalize_translated_keys(parsed)
                except urllib.error.HTTPError as e:
                    if e.code in (429, 503):
                        break
                    else:
                        break
                except (TimeoutError, urllib.error.URLError):
                    break
                except Exception:
                    time.sleep(1)
        if outer < 2:
            time.sleep(15)

    return {}

def patch_species_biology(species_id: str, biology: dict) -> bool:
    """PATCH cập nhật trường biology vào Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{species_id}"
    payload = json.dumps({"biology": biology}, ensure_ascii=False).encode("utf-8")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception as e:
        print(f"  [ERROR] Lỗi PATCH Supabase cho loài {species_id}: {e}", file=sys.stderr)
        return False

def fetch_species_batch(limit: int = 1000, offset: int = 0, volume: int = None, species_id: str = None) -> list:
    """Lấy danh sách loài từ Supabase có chứa dữ liệu biology."""
    query_parts = ["select=id,volume,vn_name,scientific_name,biology", "biology=not.is.null"]
    if volume:
        query_parts.append(f"volume=eq.{volume}")
    if species_id:
        query_parts.append(f"id=eq.{species_id}")
    query_parts.append(f"limit={limit}")
    query_parts.append(f"offset={offset}")
    query_parts.append("order=volume.asc,id.asc")

    url = f"{SUPABASE_URL}/rest/v1/species?{'&'.join(query_parts)}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description="Dịch Biology Summary sang tiếng Việt khoa học")
    parser.add_argument("--dry-run", action="store_true", help="Chạy thử nghiệm hiển thị kết quả, không ghi vào CSDL")
    parser.add_argument("--limit", type=int, default=0, help="Giới hạn số lượng loài cần xử lý")
    parser.add_argument("--volume", type=int, default=None, help="Chỉ xử lý trong Tập nhất định (1 - 6)")
    parser.add_argument("--id", type=str, default=None, help="Xử lý một loài theo ID cụ thể")
    parser.add_argument("--force", action="store_true", help="Dịch lại cả các loài đã có biologySummaryVn")
    args = parser.parse_args()

    print(f"=== BẮT ĐẦU CHƯƠNG TRÌNH DỊCH KHOA HỌC BIOLOGY SUMMARY ===")
    print(f"Chế độ: {'DRY-RUN (Chỉ xem trước, không ghi DB)' if args.dry_run else 'LƯU VÀO SUPABASE'}")
    if args.volume:
        print(f"Tập: {args.volume}")
    if args.id:
        print(f"ID loài: {args.id}")

    # Lấy dữ liệu
    all_targets = []
    if args.id:
        items = fetch_species_batch(limit=1, species_id=args.id)
        all_targets.extend(items)
    else:
        offset = 0
        batch_size = 1000
        while True:
            items = fetch_species_batch(limit=batch_size, offset=offset, volume=args.volume)
            if not items:
                break
            for item in items:
                bio = item.get('biology')
                if not isinstance(bio, dict):
                    continue
                has_en = bio.get('biologySummary') or bio.get('ecologyNotes') or bio.get('reproductionNotes')
                if not has_en:
                    continue
                # Bỏ qua nếu đã có bản dịch và không bật force
                if not args.force and bio.get('biologySummaryVn'):
                    continue
                all_targets.append(item)
            if len(items) < batch_size:
                break
            offset += batch_size

    if args.limit > 0:
        all_targets = all_targets[:args.limit]

    print(f"Tổng số loài cần dịch: {len(all_targets)}\n")

    success_count = 0
    for idx, sp in enumerate(all_targets, 1):
        sp_id = sp['id']
        vn_name = sp.get('vn_name', '')
        sci_name = sp.get('scientific_name', '')
        vol = sp.get('volume', '')
        bio = sp.get('biology', {})

        print(f"[{idx}/{len(all_targets)}] (Tập {vol}) {sp_id}: {vn_name} ({sci_name})")
        
        retry_count = 0
        translated = {}
        while not translated and retry_count < 5:
            translated = translate_biology_fields(sci_name, vn_name, bio)
            if not translated:
                retry_count += 1
                wait_sec = 15 * retry_count
                print(f"  ⚠️ Chạm rate limit (thử lại {retry_count}/5 sau {wait_sec}s)...", flush=True)
                time.sleep(wait_sec)

        if not translated:
            print(f"  ✗ Bỏ qua loài {sp_id} sau 5 lần thử.")
            continue

        if args.dry_run:
            if 'biologySummary' in bio and 'biologySummaryVn' in translated:
                print(f"  [VN - Tóm tắt]: {translated['biologySummaryVn'][:120]}...")
            if 'reproductionNotes' in bio and 'reproductionNotesVn' in translated:
                print(f"  [VN - Sinh sản]: {translated['reproductionNotesVn'][:120]}...")
            success_count += 1
            print("-" * 50)
        else:
            bio.update(translated)
            if patch_species_biology(sp_id, bio):
                success_count += 1
                summary_snip = translated.get('biologySummaryVn', '')[:60]
                print(f"  ✓ Đã lưu DB [{success_count}/{len(all_targets)}]: \"{summary_snip}...\"")
            else:
                print(f"  ✗ Lưu thất bại: {sp_id}")

        time.sleep(0.5)

    print(f"\n=== HOÀN THÀNH: {success_count}/{len(all_targets)} loài ===")

if __name__ == '__main__':
    main()
