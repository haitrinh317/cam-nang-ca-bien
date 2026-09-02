"""
fix_tap6_size.py
----------------
Chuẩn hóa trường kích thước (vn_size) cho toàn bộ 263 loài Tập VI:
1. Bổ sung kích thước cho 15 loài bị khuyết (lấy từ OCR thô và FishBase).
2. Cắt bỏ rác OCR (tên loài kế tiếp, số trang, tọa độ bản đồ, chữ Nơi lưu trữ mẫu vật).
3. Chuẩn hóa định dạng khoảng trắng và dấu cách (cm, TL).
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

RESTORE_MAP = {
    'tap6-species-7': '51,5 cm; kích thước lớn nhất 70,0 cm TL (Myers, R.F., 1991).',
    'tap6-species-9': '41,0 cm; kích thước lớn nhất 62,0 cm TL (Bacchet, P., et al., 2006).',
    'tap6-species-12': 'Kích thước lớn nhất 40,0 cm TL (Lieske, E. and R. Myers, 1994).',
    'tap6-species-27': '15,0 cm; kích thước lớn nhất 30,0 cm TL (Fischer, W., et al., 1990).',
    'tap6-species-30': '15,0 cm; kích thước lớn nhất 26,0 cm TL (Sommer, C., et al., 1996).',
    'tap6-species-40': '8,2 cm; kích thước lớn nhất 17,0 cm (Lourie, S.A., et al., 2006).',
    'tap6-species-51': '20,5 cm; kích thước lớn nhất 65,0 cm TL (Kulbicki, M., et al., 2005).',
    'tap6-species-55': '20,5 cm; kích thước lớn nhất 50,0 cm TL (Heemstra, P.C., et al., 2011).',
    'tap6-species-59': '21,0 cm; kích thước lớn nhất 61,0 cm TL (Sommer, C., et al., 1996).',
    'tap6-species-65': 'Kích thước lớn nhất 125,0 cm TL (Heemstra, P.C. and J.E. Randall, 1993).',
    'tap6-species-68': 'Kích thước lớn nhất 7,5 cm TL (Allen, G.R. and M.V. Erdmann, 2012).',
    'tap6-species-77': '6,0 cm; kích thước lớn nhất 9,0 cm TL (Randall, J.E., et al., 1990).',
    'tap6-species-79': 'Kích thước lớn nhất 8,0 cm TL (Kuiter, R.H. and T. Tonozuka, 2001).',
    'tap6-species-85': '6,0 cm; kích thước lớn nhất 10,0 cm TL (Allen, G.R., et al., 2003).',
    'tap6-species-87': '6,0 cm; kích thước lớn nhất 10,0 cm TL (Bacchet, P., et al., 2006).'
}

def clean_size(v):
    if not v:
        return v
    t = v.strip()

    # 1. Cắt bỏ rác sau dấu ngoặc kết thúc trích dẫn khoa học
    parts = re.split(r'(\([A-Z][^)]*?\d{4}[^)]*?\)\.?)', t)
    if len(parts) >= 3:
        cleaned = ''
        for i in range(1, len(parts), 2):
            cleaned += parts[i-1] + parts[i]
            rem = ''.join(parts[i+1:]).strip()
            # nếu phần còn lại có một số đo thứ 2 hợp lệ thì giữ
            if not re.search(r'\b\d+[,.]\d+\s*cm\b', rem, re.I):
                break
            else:
                if re.match(r'^\s*;\s*\d+[,.]\d+\s*cm\b', rem, re.I):
                    continue
                else:
                    break
        t = cleaned.strip()

    # 2. Xóa bỏ số trang, từ khóa OCR thừa
    t = re.sub(r'\s*\d+\s*---\s*$', '', t)
    t = re.sub(r'\s*VIỆT\s*NAM.*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*N[oơ]i\s*l[ưu]+\s*tr[ũữư]*\s*m[ẫẩ]u\s*v[ậa]t.*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*trường\s*biển.*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*Danh\s*mục\s*các\s*loài.*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*[A-Z][a-z]+\s+[a-z]+(?:\s+[A-Z][a-z]+)?,?\s+\d{4}\.?\s*$', '', t)

    # 3. Chuẩn hóa định dạng khoảng trắng
    t = re.sub(r'(\d)\s*cm\b', r'\1 cm', t, flags=re.IGNORECASE)
    t = re.sub(r';\s*', '; ', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    if t and not t.endswith('.'):
        t += '.'
    return t

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
        sp_id = s['id']
        old_v = (s.get('vn_size') or '').strip()

        if sp_id in RESTORE_MAP:
            new_v = RESTORE_MAP[sp_id]
        else:
            new_v = clean_size(old_v)

        if new_v != old_v:
            row = dict(s)
            row['vn_size'] = new_v
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

    print(f"\n✅ Hoàn tất cập nhật kích thước {success} / {len(payloads)} loài lên Supabase!")

if __name__ == '__main__':
    main()
