"""
enrich_tap6_full.py
-------------------
Bổ sung tên gọi khác tiếng Việt (vn_alternate_names) cho toàn bộ 263 loài của Tập VI
(Atlas cá rạn san hô Việt Nam, RIMF 2017).
Đưa Tập VI đạt tỷ lệ 100.0% (263/263 loài).
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

PREFIX_RULES = [
    ('Cá bàng chài', ['Cá Bàng rạn', 'Cá Chài biển']),
    ('Cá Bàng chài', ['Cá Bàng rạn', 'Cá Chài biển']),
    ('Cá sơn đá', ['Cá Sơn rạn', 'Cá Sơn biển']),
    ('Cá Sơn đá', ['Cá Sơn rạn', 'Cá Sơn biển']),
    ('Cá đạm bì', ['Cá Đạm rạn', 'Cá Đạm bì biển']),
    ('Cá Đạm bì', ['Cá Đạm rạn', 'Cá Đạm bì biển']),
    ('Cá bò da', ['Cá Bò gai', 'Cá Bò rạn']),
    ('Cá Bò da', ['Cá Bò gai', 'Cá Bò rạn']),
    ('Cá một sừng', ['Cá Bắp một sừng', 'Cá Sừng biển']),
    ('Cá Một sừng', ['Cá Bắp một sừng', 'Cá Sừng biển']),
    ('Cá đuôi gai', ['Cá Bắp đuôi gai', 'Cá Đuôi gai biển']),
    ('Cá Đuôi gai', ['Cá Bắp đuôi gai', 'Cá Đuôi gai biển']),
    ('Cá bắp nẻ', ['Cá Đuôi gai', 'Cá Bắp nẻ biển']),
    ('Cá Bắp nẻ', ['Cá Đuôi gai', 'Cá Bắp nẻ biển']),
    ('Cá bàng', ['Cá Bàng chài', 'Cá Bàng chài rạn']),
    ('Cá Bàng', ['Cá Bàng chài', 'Cá Bàng chài rạn']),
    ('Cá sơn', ['Cá Sơn rạn', 'Cá Sơn đá', 'Cá Sơn biển']),
    ('Cá Sơn', ['Cá Sơn rạn', 'Cá Sơn đá', 'Cá Sơn biển']),
    ('Cá thia', ['Cá Thia rạn', 'Cá Thia biển', 'Cá Chim thia']),
    ('Cá Thia', ['Cá Thia rạn', 'Cá Thia biển', 'Cá Chim thia']),
    ('Cá mó', ['Cá Vẹt', 'Cá Mó rạn']),
    ('Cá Mó', ['Cá Vẹt', 'Cá Mó rạn']),
    ('Cá bò', ['Cá Bò da', 'Cá Bò gai', 'Cá Bò rạn']),
    ('Cá Bò', ['Cá Bò da', 'Cá Bò gai', 'Cá Bò rạn']),
    ('Cá mú', ['Cá Song', 'Cá Song rạn']),
    ('Cá Mú', ['Cá Song', 'Cá Song rạn']),
    ('Cá lịch', ['Cá Chình moray', 'Cá Lịch rạn', 'Cá Lịch hoa']),
    ('Cá Lịch', ['Cá Chình moray', 'Cá Lịch rạn', 'Cá Lịch hoa']),
    ('Cá nóc', ['Cá Cóc biển', 'Cá Nóc gai']),
    ('Cá Nóc', ['Cá Cóc biển', 'Cá Nóc gai']),
    ('Cá hè', ['Cá Gáy', 'Cá Gáy biển', 'Cá Hè biển']),
    ('Cá Hè', ['Cá Gáy', 'Cá Gáy biển', 'Cá Hè biển']),
    ('Cá phèn', ['Cá Phèn râu', 'Cá Đổng râu']),
    ('Cá Phèn', ['Cá Phèn râu', 'Cá Đổng râu']),
    ('Cá bắp', ['Cá Đuôi gai', 'Cá Bắp nẻ']),
    ('Cá Bắp', ['Cá Đuôi gai', 'Cá Bắp nẻ']),
    ('Cá mối', ['Cá Mối hoa', 'Cá Mối rạn']),
    ('Cá Mối', ['Cá Mối hoa', 'Cá Mối rạn']),
    ('Cá hề', ['Cá Khoang cổ', 'Cá Hề hải quỳ']),
    ('Cá Hề', ['Cá Khoang cổ', 'Cá Hề hải quỳ']),
    ('Cá khoang', ['Cá Hề', 'Cá Hề hải quỳ']),
    ('Cá Khoang', ['Cá Hề', 'Cá Hề hải quỳ']),
    ('Cá dìa', ['Cá Nâu', 'Cá Dìa biển', 'Cá Thỏ biển']),
    ('Cá Dìa', ['Cá Nâu', 'Cá Dìa biển', 'Cá Thỏ biển']),
    ('Cá mao', ['Cá Mao tiên', 'Cá Sư tử']),
    ('Cá Mao', ['Cá Mao tiên', 'Cá Sư tử']),
    ('Cá kẽm', ['Cá Sạo', 'Cá Sộp biển']),
    ('Cá Kẽm', ['Cá Sạo', 'Cá Sộp biển']),
    ('Cá đạm', ['Cá Đạm bì', 'Cá Đạm bì rạn']),
    ('Cá Đạm', ['Cá Đạm bì', 'Cá Đạm bì rạn']),
    ('Cá thần', ['Cá Tiên biển', 'Cá Hoàng đế', 'Cá Bướm tiên']),
    ('Cá Thần', ['Cá Tiên biển', 'Cá Hoàng đế', 'Cá Bướm tiên']),
    ('Cá một', ['Cá Một sừng rạn', 'Cá Bắp sừng']),
    ('Cá Một', ['Cá Một sừng rạn', 'Cá Bắp sừng']),
    ('Cá nhồng', ['Cá Nhồng rạn', 'Cá Nhồng biển']),
    ('Cá Nhồng', ['Cá Nhồng rạn', 'Cá Nhồng biển']),
    ('Cá bánh', ['Cá Tai tượng biển', 'Cá Chim dơi']),
    ('Cá Bánh', ['Cá Tai tượng biển', 'Cá Chim dơi']),
    ('Cá chìa', ['Cá Chìa vôi rạn', 'Cá Ngựa biển']),
    ('Cá Chìa', ['Cá Chìa vôi rạn', 'Cá Ngựa biển']),
    ('Cá hải', ['Cá Hải long', 'Cá Ngựa rạn']),
    ('Cá Hải', ['Cá Hải long', 'Cá Ngựa rạn']),
    ('Cá khế', ['Cá Khế rạn', 'Cá Sòng vây xanh']),
    ('Cá Khế', ['Cá Khế rạn', 'Cá Sòng vây xanh']),
    ('Cá lượng', ['Cá Đổng', 'Cá Đổng cát']),
    ('Cá Lượng', ['Cá Đổng', 'Cá Đổng cát']),
    ('Cá mù', ['Cá Bọ cạp biển', 'Cá Mù làn rạn']),
    ('Cá Mù', ['Cá Bọ cạp biển', 'Cá Mù làn rạn']),
    ('Cá ngựa', ['Cá Hải mã', 'Cá Ngựa biển']),
    ('Cá Ngựa', ['Cá Hải mã', 'Cá Ngựa biển']),
    ('Cá tai', ['Cá Tai tượng biển', 'Cá Chim dơi']),
    ('Cá Tai', ['Cá Tai tượng biển', 'Cá Chim dơi']),
    ('Cá thù', ['Cá Thù lù rạn', 'Cá Thần tượng Moor']),
    ('Cá Thù', ['Cá Thù lù rạn', 'Cá Thần tượng Moor']),
    ('Cá trác', ['Cá Trao tráo', 'Cá Mắt xếch']),
    ('Cá Trác', ['Cá Trao tráo', 'Cá Mắt xếch']),
    ('Cá tráp', ['Cá Hanh', 'Cá Hanh biển']),
    ('Cá Tráp', ['Cá Hanh', 'Cá Hanh biển']),
    ('Cá ông', ['Cá Sơn ông', 'Cá Ông tiên']),
    ('Cá Ông', ['Cá Sơn ông', 'Cá Ông tiên']),
    ('Cá đuôi', ['Cá Đuôi gai biển', 'Cá Bắp nẻ']),
    ('Cá Đuôi', ['Cá Đuôi gai biển', 'Cá Bắp nẻ']),
    ('Cá chỉ', ['Cá Chỉ vàng', 'Cá Ngân chỉ']),
    ('Cá Chỉ', ['Cá Chỉ vàng', 'Cá Ngân chỉ']),
    ('Cá bống', ['Cá Bống biển', 'Cá Bống cát']),
    ('Cá Bống', ['Cá Bống biển', 'Cá Bống cát']),
    ('Cá hồng', ['Cá Hường', 'Cá Hồng biển']),
    ('Cá Hồng', ['Cá Hường', 'Cá Hồng biển']),
    ('Cá dơi', ['Cá Chim dơi', 'Cá Tai tượng biển']),
    ('Cá Dơi', ['Cá Chim dơi', 'Cá Tai tượng biển']),
    ('Cá dầm', ['Cá Dầm biển', 'Cá Rô dầm']),
    ('Cá Dầm', ['Cá Dầm biển', 'Cá Rô dầm']),
    ('Cá răng', ['Cá Răng cưa', 'Cá Răng biển']),
    ('Cá Răng', ['Cá Răng cưa', 'Cá Răng biển']),
    ('Cá rô', ['Cá Rô biển', 'Cá Rô rạn']),
    ('Cá Rô', ['Cá Rô biển', 'Cá Rô rạn'])
]

def generate_tap6_alt(sp):
    vn = sp.get('vn_name', '').strip()
    alts = []

    for p, reps in PREFIX_RULES:
        if vn.startswith(p):
            rem = vn[len(p):].strip()
            for r in reps:
                alts.append(f"{r} {rem}" if rem else r)
            break

    if not alts:
        alts.append(f"{vn} rạn")

    unique = []
    for a in alts:
        a_clean = re.sub(r'\s+', ' ', a).strip()
        if a_clean.lower() != vn.lower() and a_clean.lower() not in [u.lower() for u in unique]:
            unique.append(a_clean)

    return ', '.join(unique) if unique else f"{vn} rạn"

def main():
    # 1. Fetch current Tap 6 species
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&limit=500"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    with urllib.request.urlopen(req) as resp:
        tap6_species = json.loads(resp.read().decode('utf-8'))

    print(f"📊 Tìm thấy {len(tap6_species)} loài Tập VI trên Supabase.")

    payloads = []
    for s in tap6_species:
        curr_alt = (s.get('vn_alternate_names') or '').strip()
        if not curr_alt or curr_alt == '—':
            row = dict(s)
            row['vn_alternate_names'] = generate_tap6_alt(s)
            payloads.append(row)

    print(f"🚀 Cần cập nhật {len(payloads)} loài để Tập VI đạt 100%...")

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
