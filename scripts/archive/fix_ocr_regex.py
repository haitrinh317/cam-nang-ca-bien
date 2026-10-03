"""
fix_ocr_regex.py
----------------
Sửa lỗi chính tả OCR (tiếng Việt) cho Tập 6 bằng Regex/Thay thế chuỗi.
Cách này cực nhanh và không tốn phí API, áp dụng cho các lỗi phổ biến.
"""

import os
import sys
import json
import urllib.request
import re

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

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env")
    sys.exit(1)

FIELDS_TO_CHECK = [
    'morphology_vn',
    'ecology_vn',
    'vn_distribution',
    'economic_value_vn',
    'vn_size',
    'vn_specimen'
]

# Danh sách các từ cần thay thế (Tìm kiếm, Thay thế)
REPLACEMENTS = [
    (r'\bcomad\b', 'cơ thể'),
    (r'\bvorca\b', 'với các'),
    (r'\bCơ oe thể\b', 'Cơ thể'),
    (r'\bCơ oẽ thể\b', 'Cơ thể'),
    (r'\bCơ oê thể\b', 'Cơ thể'),
    (r'\bmầu\b', 'màu'),
    (r'\bmôm\b', 'mõm'),
    (r'\bmôm trắng\b', 'mõm trắng'),
    (r'\bở ở độ độ sâu\b', 'ở độ sâu'),
    (r'\bở ở độ sâu\b', 'ở độ sâu'),
    (r'\bViên Nghiên cứu\b', 'Viện Nghiên cứu'),
    (r'\biguyen\b', 'nguyên'),
    (r'\bMôi iguyen trường\b', 'Môi trường'),
    (r'\bHải Vẫn\b', 'Hải Vân'),
    (r'\btrung bỉnh\b', 'trung bình'),
    (r'\bđổng\b', 'đồng'),
    (r'\bđổng đều\b', 'đồng đều'),
    (r'\bVẩy\b', 'Vảy'),
    (r'\bvẩy\b', 'vảy'),
    (r'\btiếu\b', 'tiêu'),  # e.g. tiêu bản
    (r'\bchiểu dài\b', 'chiều dài'),
]

def apply_regex(text):
    if not text:
        return text
    new_text = text
    for pattern, repl in REPLACEMENTS:
        # Thay thế có phân biệt hoa thường dựa vào pattern, nhưng cẩn thận chữ cái đầu câu.
        # Ở đây ta dùng regex đơn giản
        new_text = re.sub(pattern, repl, new_text)
    
    # Xóa khoảng trắng kép
    new_text = re.sub(r'\s{2,}', ' ', new_text)
    return new_text.strip()

def main():
    print("=" * 60)
    print("BẮT ĐẦU RÀ SOÁT LỖI OCR BẰNG REGEX (Tập 6)")
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

    print(f"Tìm thấy {len(species_list)} loài. Tiến hành xử lý...\n")

    updated_count = 0
    for idx, sp in enumerate(species_list, 1):
        sp_id = sp['id']
        sci_name = sp['scientific_name']

        patch_data = {}
        for f in FIELDS_TO_CHECK:
            orig = sp.get(f)
            if orig and orig.strip():
                orig_clean = orig.strip()
                corr = apply_regex(orig_clean)
                if corr != orig_clean:
                    patch_data[f] = corr

        if not patch_data:
            continue
        
        print(f"[{idx:3d}/{len(species_list)}] {sci_name:30s} -> Sửa {len(patch_data)} trường")
        
        # Cập nhật Supabase
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

    print("\n" + "=" * 60)
    print(f"HOÀN TẤT: Đã sửa bằng Regex cho {updated_count}/{len(species_list)} loài.")
    print("=" * 60)

if __name__ == "__main__":
    main()
