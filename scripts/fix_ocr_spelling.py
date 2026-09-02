"""
fix_ocr_spelling.py
-------------------
Sử dụng Gemini API để sửa lỗi chính tả OCR (tiếng Việt) cho Tập 6.
Các trường xử lý: morphology_vn, ecology_vn, vn_distribution, economic_value_vn, vn_size, vn_specimen.

Cách chạy:
  python scripts/fix_ocr_spelling.py
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time
import argparse

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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env")
    sys.exit(1)

if not GEMINI_API_KEY:
    print("[ERROR] Thiếu GEMINI_API_KEY trong .env")
    sys.exit(1)

FIELDS_TO_CHECK = [
    'morphology_vn',
    'ecology_vn',
    'vn_distribution',
    'economic_value_vn',
    'vn_size',
    'vn_specimen'
]

def call_gemini(text_dict):
    """
    Gửi dict chứa văn bản tiếng Việt sang Gemini để nhờ sửa lỗi chính tả OCR.
    Trả về dict đã sửa (cùng keys).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = """Bạn là một chuyên gia sinh học biển và hiệu đính tiếng Việt.
Dưới đây là một JSON chứa các đoạn văn bản trích từ một cuốn Atlas cá biển bị lỗi nhận dạng ký tự (OCR).
Ví dụ lỗi OCR phổ biến:
- "comad" -> "cơ thể"
- "vorca" -> "với các"
- "mầu" -> "màu"
- Mất khoảng trắng, sai dấu câu, sai dấu tiếng Việt...
Nhiệm vụ của bạn là SỬA LỖI CHÍNH TẢ của các đoạn văn bản này để nó trở nên mượt mà, đúng ngữ pháp và đúng từ vựng tiếng Việt.
Tuyệt đối giữ nguyên các thuật ngữ khoa học, tên địa danh. KHÔNG ĐƯỢC bịa thêm thông tin, thêm chữ hoặc tự ý tóm tắt.
Chỉ trả về ĐÚNG cấu trúc JSON y hệt đầu vào, không có text dư thừa, không có markdown (như ```json). 
Đầu vào JSON:
""" + json.dumps(text_dict, ensure_ascii=False)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
            # Xóa markdown nếu API vẫn trả về
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            return json.loads(result_text)
    except Exception as e:
        print(f"  [Gemini Error] {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Số lượng loài muốn test (0 = tất cả)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ in ra kết quả, không update DB")
    args = parser.parse_args()

    print("=" * 60)
    print("BẮT ĐẦU RÀ SOÁT LỖI OCR BẰNG GEMINI AI (Tập 6)")
    print("=" * 60)

    # Lấy danh sách loài Tập 6
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&select=id,scientific_name,{','.join(FIELDS_TO_CHECK)}&order=species_index",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    )
    try:
        species_list = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Không lấy được dữ liệu từ Supabase: {e}")
        return

    if args.limit > 0:
        species_list = species_list[:args.limit]

    print(f"Tìm thấy {len(species_list)} loài. Tiến hành xử lý...\n")

    updated_count = 0
    for idx, sp in enumerate(species_list, 1):
        sp_id = sp['id']
        sci_name = sp['scientific_name']

        # Gom những trường có dữ liệu
        to_check = {}
        for f in FIELDS_TO_CHECK:
            if sp.get(f) and sp[f].strip():
                to_check[f] = sp[f].strip()
        
        if not to_check:
            print(f"[{idx:3d}/{len(species_list)}] {sci_name:30s} -> Bỏ qua (không có dữ liệu VN)")
            continue

        print(f"[{idx:3d}/{len(species_list)}] {sci_name:30s} -> Đang gọi Gemini...", end="", flush=True)
        
        max_retries = 3
        corrected = None
        for attempt in range(max_retries):
            corrected = call_gemini(to_check)
            if corrected:
                break
            print(f" ↻ Thử lại ({attempt+1}/{max_retries})...", end="", flush=True)
            time.sleep(10)
            
        if not corrected:
            print(" ✗ Lỗi API (Rate limit hoặc lỗi khác), bỏ qua")
            continue

        # So sánh sự khác biệt
        patch_data = {}
        for f in to_check.keys():
            orig = to_check[f]
            corr = corrected.get(f)
            if corr and corr != orig:
                patch_data[f] = corr

        if not patch_data:
            print(" ✓ OK (Không có lỗi)")
            time.sleep(4.2)
            continue
        
        print(f" ✎ Phát hiện lỗi ở {len(patch_data)} trường:")
        for f, corr in patch_data.items():
            print(f"    - {f}:\n      [Cũ]  {to_check[f][:150]}...\n      [Mới] {corr[:150]}...")
        
        if not args.dry_run:
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            req_patch = urllib.request.Request(
                patch_url,
                data=json.dumps(patch_data).encode('utf-8'),
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="PATCH"
            )
            try:
                urllib.request.urlopen(req_patch)
                updated_count += 1
            except Exception as e:
                print(f"    ✗ Lỗi khi lưu DB: {e}")
        else:
            updated_count += 1 # Cho mục đích đếm dry-run

        time.sleep(4.2) # Tránh rate limit của API (15 RPM free tier)

    print("\n" + "=" * 60)
    mode_str = "DRY-RUN" if args.dry_run else "THỰC TẾ"
    print(f"HOÀN TẤT ({mode_str}): Đã rà soát & cập nhật {updated_count}/{len(species_list)} loài.")
    print("=" * 60)

if __name__ == "__main__":
    main()
