"""
translate_tap6_size_specimen.py
-------------------------------
Dịch và chuẩn hóa 2 trường Kích thước tiếng Anh (en_size) và Mẫu vật tiếng Anh (en_specimen)
từ tiếng Việt sang cho toàn bộ 263 loài của Tập VI (Atlas cá rạn san hô Việt Nam, RIMF 2017).
Đồng thời làm sạch các lỗi OCR còn sót lại trong trường mẫu vật tiếng Việt (vn_specimen).
"""
import os
import sys
import json
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

def load_dotenv():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base, '.env')
    env = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip("'\"")
    return env

env = load_dotenv()
SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

def translate_size(vn_size):
    if not vn_size:
        return ''
    t = vn_size.strip()
    # Thay dấu phẩy thập phân thành dấu chấm: 57,0 -> 57.0
    t = re.sub(r'(\d+),(\d+)', r'\1.\2', t)
    # Dịch thuật ngữ
    t = re.sub(r'\bkích thước lớn nhất được phát hiện\b', 'maximum recorded length', t, flags=re.IGNORECASE)
    t = re.sub(r'\bkích thước lớn nhất\b', 'maximum length', t, flags=re.IGNORECASE)
    t = re.sub(r'\bkích thước mẫu\s*:\s*', 'Specimen size: ', t, flags=re.IGNORECASE)
    
    # Capitalize chữ cái đầu nếu bắt đầu bằng 'maximum'
    if t.startswith('maximum '):
        t = 'M' + t[1:]
    return t

def clean_and_translate_specimen(vn_spec):
    if not vn_spec:
        return 'Không rõ', 'Unknown'
    raw = vn_spec.strip()

    # Trường hợp ảnh lưu trữ / không có mẫu
    if 'Chưa có mẫu vật' in raw or 'chưa có mẫu vật' in raw:
        if 'Viện Hải dương' in raw and 'ảnh' in raw.lower():
            return (
                'Viện Hải dương học. Ảnh lưu trữ tại Viện Nghiên cứu Hải sản.',
                'Institute of Oceanography (IO); photograph archived at RIMF.'
            )
        return (
            'Chưa có mẫu vật (ảnh lưu trữ tại Viện Nghiên cứu Hải sản).',
            'No physical specimen deposited (photograph archived at RIMF).'
        )

    # Trường hợp không rõ
    if raw.lower() in ['không rõ', 'không ro', 'chưa rõ']:
        return 'Không rõ', 'Unknown'

    # Nhận diện các viện
    has_rimf = any(k in raw for k in ['Hải sản', 'Hai san', 'Hải sån', 'Viện Nghiên'])
    has_imer = any(k in raw for k in ['Tài nguyên và Môi trường', 'Tai nguyen va', 'tài nguyên và Môi'])
    has_io = any(k in raw for k in ['Hải dương học', 'Hai duong hoc', 'Viện Hải dương'])

    vn_parts = []
    en_parts = []

    if has_rimf:
        vn_parts.append('Viện Nghiên cứu Hải sản')
        en_parts.append('Research Institute for Marine Fisheries (RIMF)')
    if has_imer:
        vn_parts.append('Viện Tài nguyên và Môi trường biển')
        en_parts.append('Institute of Marine Environment and Resources (IMER)')
    if has_io:
        vn_parts.append('Viện Hải dương học')
        en_parts.append('Institute of Oceanography (IO)')

    if vn_parts:
        return ', '.join(vn_parts) + '.', ', '.join(en_parts) + '.'

    return raw, raw

def main():
    # 1. Fetch current Tap 6 species from Supabase
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&limit=500&order=species_index"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    with urllib.request.urlopen(req) as resp:
        tap6_species = json.loads(resp.read().decode('utf-8'))

    print(f"📊 Tìm thấy {len(tap6_species)} loài Tập VI trên Supabase.")

    payloads = []
    for s in tap6_species:
        old_vn_sz = (s.get('vn_size') or '').strip()
        old_en_sz = (s.get('en_size') or '').strip()
        old_vn_sp = (s.get('vn_specimen') or '').strip()
        old_en_sp = (s.get('en_specimen') or '').strip()

        new_en_sz = translate_size(old_vn_sz)
        clean_vn_sp, new_en_sp = clean_and_translate_specimen(old_vn_sp)

        has_change = False
        row = dict(s)

        if new_en_sz != old_en_sz:
            row['en_size'] = new_en_sz
            has_change = True

        if clean_vn_sp != old_vn_sp:
            row['vn_specimen'] = clean_vn_sp
            has_change = True

        if new_en_sp != old_en_sp:
            row['en_specimen'] = new_en_sp
            has_change = True

        if has_change:
            payloads.append(row)

    print(f"🚀 Cần cập nhật {len(payloads)} loài trên Tập VI...")

    # 2. Batch update to Supabase
    batch_size = 50
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    success = 0
    for i in range(0, len(payloads), batch_size):
        chunk = payloads[i:i + batch_size]
        r = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species",
            data=json.dumps(chunk, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(r, timeout=20) as res:
                if res.status in (200, 201):
                    success += len(chunk)
                    print(f"  ✓ Đã cập nhật batch {i + 1} - {min(i + batch_size, len(payloads))} ({len(chunk)} loài)")
        except Exception as e:
            print(f"  ✗ Lỗi batch {i + 1}: {e}")

    print(f"\n✅ Hoàn tất cập nhật {success} / {len(payloads)} loài lên Supabase!")

if __name__ == '__main__':
    main()
