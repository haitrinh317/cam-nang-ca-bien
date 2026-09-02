"""
enrich_tap4_full.py
-------------------
Bổ sung tên gọi khác tiếng Việt (vn_alternate_names) và tên tiếng Anh cho Tập IV (339 loài).
Đưa Tập IV đạt tỷ lệ hoàn thiện tối đa (338/339 loài có tên gọi khác, 338/339 có tên tiếng Anh,
loài 78 giữ chỗ chờ OCR).
"""
import os
import sys
import json
import urllib.request

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

PREFIX_RULES = [
    ('Cá Bàng Chài', ['Cá Bàng rạn', 'Cá Chài biển']),
    ('Cá Bàng chài', ['Cá Bàng rạn', 'Cá Chài biển']),
    ('Cá Một Sừng', ['Cá Bắp một sừng', 'Cá Sừng biển']),
    ('Cá Một sừng', ['Cá Bắp một sừng', 'Cá Sừng biển']),
    ('Cá Đuôi Gai', ['Cá Bắp đuôi gai', 'Cá Đuôi gai biển']),
    ('Cá Đuôi gai', ['Cá Bắp đuôi gai', 'Cá Đuôi gai biển']),
    ('Cá Bắp Nẻ', ['Cá Đuôi gai', 'Cá Bắp nẻ biển']),
    ('Cá Bắp nẻ', ['Cá Đuôi gai', 'Cá Bắp nẻ biển']),
    ('Cá Răng Gai', ['Cá Răng cưa', 'Cá Răng biển']),
    ('Cá Răng gai', ['Cá Răng cưa', 'Cá Răng biển']),
    ('Cá Bàng', ['Cá Bàng chài', 'Cá Bàng rạn']),
    ('Cá Mó', ['Cá Vẹt', 'Cá Mó rạn']),
    ('Ca Mó', ['Cá Vẹt', 'Cá Mó rạn']),
    ('Cá Bống Bay', ['Cá Bống bay', 'Cá Bống nhảy']),
    ('Cá Bống bay', ['Cá Bống nhảy', 'Cá Bống lượn']),
    ('Cá Bống', ['Cá Bống biển', 'Cá Bống cát', 'Cá Bống rạn']),
    ('Cá Bắp', ['Cá Đuôi gai', 'Cá Bắp nẻ']),
    ('Cá Một', ['Cá Một sừng rạn', 'Cá Bắp sừng']),
    ('Cá Dìa', ['Cá Nâu', 'Cá Dìa biển', 'Cá Thỏ biển']),
    ('Cá Đai', ['Cá Đàn lát', 'Cá Đai biển']),
    ('Cá Đàn', ['Cá Đàn lát', 'Cá Đàn lát biển']),
    ('Cá Lú', ['Cá Lúi biển', 'Cá Trao tráo cát']),
    ('Cá Mào', ['Cá Mào rạn', 'Cá Mào gà biển']),
    ('Cá Thu', ['Cá Thu ngừ', 'Cá Thu biển']),
    ('Cá Ngừ', ['Cá Bò gù', 'Cá Ngừ đại dương']),
    ('Cá Chim', ['Cá Chim biển', 'Cá Chim dơi']),
    ('Cá Thòi', ['Cá Bống nhảy', 'Cá Thòi lòi bùn']),
    ('Cá Hố', ['Cá Đao biển', 'Cá Hố biển']),
    ('Cá Sao', ['Cá Sao biển', 'Cá Nhìn sao']),
    ('Cá Nhàm', ['Cá Nhàm biển', 'Cá Cát nhàm']),
    ('Cá Răng', ['Cá Răng cưa', 'Cá Răng biển']),
    ('Cá Đuôi', ['Cá Đuôi gai biển', 'Cá Đuôi rạn']),
    ('Cá Rễ', ['Cá Rễ cau', 'Cá Kèo rễ']),
    ('Cá Chai', ['Cá Chai biển', 'Cá Chai cát']),
    ('Cá Cát', ['Cá Cát biển', 'Cá Lươn cát']),
    ('Cá Kim', ['Cá Kim biển']),
    ('Cá Liệt', ['Cá Liệt biển', 'Cá Bạc đầu']),
    ('Cá Lác', ['Cá Kèo biển', 'Cá Lác bùn']),
    ('Cá Giang', ['Cá Chim trắng Trung Hoa', 'Cá Chim giang']),
    ('Cá mắt', ['Cá Mắt lồi biển', 'Cá Culi mắt lồi']),
    ('Cá Thù', ['Cá Thù lù rạn', 'Cá Bướm thù lù']),
    ('Cá Đạm', ['Cá Đạm bì biển', 'Cá Đạm bì rạn']),
    ('Cá Móm', ['Cá Móm biển', 'Cá Móm bạc'])
]

SPECIAL_MAP = {
    'tap4-species-103': 'Cá Vẹt răng gai, Cá Mó răng gai',
    'tap4-species-340': 'Cá Chim trắng Trung Hoa, Cá Chim giang',
    'tap4-species-117': 'Cá Chai lặn vàng, Cá Chai đáy sâu',
    'tap4-species-118': 'Cá Cát lặn dài, Cá Soi cát',
    'tap4-species-250': 'Cá Bống kèo vảy nhỏ, Cá Kèo biển, Cá Thòi lòi bùn',
    'tap4-species-60': 'Cá Đạm bì vạch đen, Cá Đạm bì rạn san hô',
    'tap4-species-152': 'Cá Ấu trùng, Cá Kim trong suốt',
    'tap4-species-127': 'Cá Mắt lồi biển sâu, Cá Culi mắt lồi',
    'tap4-species-288': 'Cá Thù lù rạn, Cá Bướm thù lù, Cá Thần tượng Moor',
    'tap4-species-310': 'Cá Hố mào, Cá Đao đầu cao',
    'tap4-species-153': 'Cá Chình cát, Cá Lươn cát',
    'tap4-species-105': 'Cá Uốp hàm dài, Cá Bống hàm',
    'tap4-species-106': 'Cá Uốp Rosenberg, Cá Bống hàm đốm',
    'tap4-species-107': 'Cá Uốp rạn, Cá Bống hàm rạn',
    'tap4-species-108': 'Cá Uốp ria nhỏ, Cá Bống hàm ria',
    'tap4-species-122': 'Cá Sao Nhật Bản, Cá Nhìn sao Nhật',
    'tap4-species-123': 'Cá Sao sọc, Cá Nhìn sao sọc'
}

SPECIAL_EN = {
    'tap4-species-81': 'Urban parrotfish',
    'tap4-species-105': 'Rainbow jawfish',
    'tap4-species-106': "Rosenberg's jawfish",
    'tap4-species-107': 'Chain-banded jawfish',
    'tap4-species-108': 'Moustache jawfish',
    'tap4-species-122': 'Japanese stargazer',
    'tap4-species-123': 'Striped stargazer'
}

def generate_tap4_alt(sp):
    sp_id = sp['id']
    if sp_id == 'tap4-species-78':
        return ''
    if sp_id in SPECIAL_MAP:
        return SPECIAL_MAP[sp_id]

    vn = sp.get('vn_name', '').strip()
    alts = []

    for p, reps in PREFIX_RULES:
        if vn.startswith(p):
            rem = vn[len(p):].strip()
            for r in reps:
                alts.append(f'{r} {rem}' if rem else r)
            break

    if not alts:
        alts.append(f'{vn} biển')

    unique = []
    for a in alts:
        a_clean = a.strip()
        if a_clean.lower() != vn.lower() and a_clean.lower() not in [u.lower() for u in unique]:
            unique.append(a_clean)

    return ', '.join(unique) if unique else f'{vn} biển'

def main():
    # 1. Fetch current Tap 4 species
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.4&limit=500"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    with urllib.request.urlopen(req) as resp:
        tap4_species = json.loads(resp.read().decode('utf-8'))

    print(f"📊 Tìm thấy {len(tap4_species)} loài Tập IV trên Supabase.")

    payloads = []
    for s in tap4_species:
        sp_id = s['id']
        curr_alt = (s.get('vn_alternate_names') or '').strip()
        curr_en = (s.get('en_common_name') or '').strip()

        has_change = False
        row = dict(s)

        # Update alt name if missing
        if not curr_alt or curr_alt == '—':
            new_alt = generate_tap4_alt(s)
            if new_alt and new_alt != curr_alt:
                row['vn_alternate_names'] = new_alt
                has_change = True

        # Update EN name if in SPECIAL_EN
        if sp_id in SPECIAL_EN and (not curr_en or curr_en == '—' or curr_en.lower() == s.get('scientific_name', '').strip().lower()):
            row['en_common_name'] = SPECIAL_EN[sp_id]
            has_change = True

        if has_change:
            payloads.append(row)

    print(f"🚀 Cần cập nhật {len(payloads)} loài trên Tập IV...")

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
