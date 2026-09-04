"""
enrich_tap2_full.py
-------------------
Bổ sung tên gọi khác tiếng Việt (vn_alternate_names) cho 48 loài còn thiếu của Tập II,
đưa Tập II đạt tỷ lệ 100% (266/266 loài).
Đối chiếu: TCVN 8272:2009, Viện Nghiên cứu Hải sản (RIMF) & Ngữ danh thủy sản Việt Nam.
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

# Mapping chuẩn hóa tên gọi khác cho 48 loài Tập II
TAP2_ALTS = {
    'tap2-species-1': 'Cá Măng biển, Cá Măng chuối',
    'tap2-species-3': 'Cá Hải tượng biển, Cá Cháo mắt to, Cá Măng biển lớn',
    'tap2-species-4': 'Cá Chuối biển, Cá Chuối xương, Cá Măng đường',
    'tap2-species-7': 'Cá Rựa hàm dài, Cá Lanh vây trắng',
    'tap2-species-8': 'Cá Mòi Chacunda, Cá Mòi tròn',
    'tap2-species-9': 'Cá Mòi cờ hoa, Cá Mòi mũi dài',
    'tap2-species-11': 'Cá Mòi cờ, Cá Mòi Konoshiro',
    'tap2-species-13': 'Cá Trích tròn Hasselt, Cá Lầm cầu vồng',
    'tap2-species-14': 'Cá Trích tròn mắt mỡ, Cá Lầm mỡ',
    'tap2-species-16': 'Cá Trích tròn, Cá Nhâm tròn',
    'tap2-species-17': 'Cá Bẹ bụng trắng, Cá Trích dẹp',
    'tap2-species-22': 'Cá Trích Sind, Cá Trích bụng bầu',
    'tap2-species-23': 'Cá Trích tròn, Cá Bẹ sơ',
    'tap2-species-24': 'Cá Trích mỏng, Cá Trích vẩy',
    'tap2-species-25': 'Cá Trích mắt to, Cá Nhâm mắt to',
    'tap2-species-27': 'Cá Trích Bali, Cá Nhâm lầm mỡ',
    'tap2-species-30': 'Cá Bẹ dài, Cá Bẹ đé',
    'tap2-species-31': 'Cá Bẹ miệng đen, Cá Đé Ấn Độ',
    'tap2-species-33': 'Cá Bẹ Tardoore, Cá Bẹ dài vây',
    'tap2-species-35': 'Cá Cháy Reeves, Cá Mòi cháy lớn',
    'tap2-species-36': 'Cá Cháy năm đốm, Cá Bẹ Kelee',
    'tap2-species-39': 'Cá Cơm than, Cá Cơm Nhật Bản',
    'tap2-species-41': 'Cá Cơm sọc trắng, Cá Cơm biển',
    'tap2-species-43': 'Cá Cơm Trung Quốc, Cá Cơm trắng',
    'tap2-species-44': 'Cá Cơm Batavia, Cá Cơm Ba-ta-vi',
    'tap2-species-46': 'Cá Lẹp Kamma, Cá Lẹp vây cam',
    'tap2-species-48': 'Cá Lẹp râu, Cá Lẹp mang dài',
    'tap2-species-49': 'Cá Lẹp mũi vàng, Cá Lẹp vàng',
    'tap2-species-50': 'Cá Lẹp chấm vàng, Cá Lẹp Dussumier',
    'tap2-species-51': 'Cá Lẹp râu dài, Cá Lẹp kim',
    'tap2-species-56': 'Cá Lành canh đuôi én, Cá Lành canh râu',
    'tap2-species-59': 'Cá Lành canh đuôi dài, Cá Lành canh Lindman',
    'tap2-species-61': 'Cá Ngần vây hậu môn dài, Cá Bạc đầu',
    'tap2-species-62': 'Cá Ngần Ariake, Cá Thủy tinh đầu nhọn',
    'tap2-species-66': 'Cá Rìu biển, Cá Rìu gai sâu',
    'tap2-species-67': 'Cá Mối đầu ngắn, Cá Mối rạn',
    'tap2-species-68': 'Cá Mối cờ, Cá Mối tia dài',
    'tap2-species-70': 'Cá Mối hoa lớn, Cá Mối vược, Cá Mối Tumbil',
    'tap2-species-71': 'Cá Mối thon, Cá Mối thanh',
    'tap2-species-73': 'Cá Mối mắt to, Cá Mối vện mắt lớn',
    'tap2-species-74': 'Cá Mối hoa, Cá Mối vằn',
    'tap2-species-75': 'Cá Mối vện tím, Cá Mối oải hương',
    'tap2-species-76': 'Cá Cháo, Cá Tiêu, Cá Chuối biển',
    'tap2-species-83': 'Cá Chình Nhật Bản, Cá Chình hoa',
    'tap2-species-84': 'Cá Chình moray vân chấm, Cá Lịch hoa',
    'tap2-species-87': 'Cá Lịch bùn, Cá Chình biển đuôi dài',
    'tap2-species-88': 'Cá Lịch tổ ong, Cá Chình tổ ong, Cá Lịch bông lớn',
    'tap2-species-89': 'Cá Lịch đốm trắng, Cá Chình đốm sao'
}

def main():
    # 1. Fetch current Tap 2 species
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.2&limit=500"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    with urllib.request.urlopen(req) as resp:
        tap2_species = json.loads(resp.read().decode('utf-8'))

    print(f"📊 Tìm thấy {len(tap2_species)} loài Tập II trên Supabase.")

    payloads = []
    for s in tap2_species:
        sp_id = s['id']
        if sp_id in TAP2_ALTS:
            row = dict(s)
            row['vn_alternate_names'] = TAP2_ALTS[sp_id]
            payloads.append(row)

    print(f"🚀 Cần cập nhật {len(payloads)} loài để đạt 100% Tập II...")

    # 2. Batch update
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
            with urllib.request.urlopen(r, timeout=15) as res:
                if res.status in (200, 201):
                    success += len(chunk)
                    print(f"  ✓ Đã cập nhật {success} / {len(payloads)} loài")
        except Exception as e:
            print(f"  ✗ Lỗi: {e}")

    print(f"\n✅ Hoàn tất cập nhật {success} / {len(payloads)} loài lên Supabase!")

if __name__ == '__main__':
    main()
