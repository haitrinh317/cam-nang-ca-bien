"""
fix_tap6_morphology.py
----------------------
Sửa lỗi chính tả, bóc tách lỗi OCR, tách riêng cột Tên tiếng Anh / Mô tả hình thái,
và chuẩn hóa toàn diện 263 loài của Tập VI (Atlas cá rạn san hô Việt Nam, RIMF 2017).
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

# Bảng sửa lỗi riêng cho các loài bị nhầm lẫn / lỗi bóc tách nghiêm trọng
SPECIAL_FIXES = {
    'tap6-species-3': {
        'en_common_name': 'Fimbriated moray',
        'morphology_vn': 'Số đốt sống 128-142. Đầu có màu vàng. Thân có màu nâu nhạt hoặc màu xám với các đốm màu đen kích thước khác nhau phân bố rải rác trên cơ thể. Vây có các vạch đứng ngắn màu đen xếp song song chạy dọc theo chiều dài của vây lưng. Hàm dài chìa dưới có 2 cặp răng nanh thon, dài ra ngoài.'
    },
    'tap6-species-27': {
        'morphology_vn': 'D XI. 13-15; A IV. 11-14. Số vảy đường bên 28-31. Số lược mang dưới 24-29, số lược mang trên 12-15, tổng số lược mang 36-43. Cơ thể có màu đỏ sáng đến đỏ vàng. Vây màu đỏ; mép vây lưng mềm, vây hậu môn và vây đuôi màu trắng. Phía dưới thân (thấp hơn 1/2 gốc vây ngực) có dải màu trắng.'
    },
    'tap6-species-28': {
        'scientific_name': 'Myripristis murdjan',
        'authorship': '(Forsskål, 1775)',
        'en_common_name': 'Pinecone soldierfish',
        'morphology_vn': 'D XI. 13-15; A IV. 11-14. Số vảy đường bên 27-32. Số lược mang dưới 24-29, số lược mang trên 13-14, tổng số lược mang 37-43. Cơ thể màu hồng bạc, mép vảy màu đỏ, nách của vây ngực có nhiều vảy nhỏ. Rìa mép nắp mang màu đen.'
    },
    'tap6-species-32': {
        'en_common_name': 'Shadowfin soldierfish'
    },
    'tap6-species-36': {
        'en_common_name': 'Spinysnout pipefish'
    },
    'tap6-species-51': {
        'en_common_name': 'Highfin grouper',
        'morphology_vn': 'D XI 15-17; A I 8. Số vảy đường bên 49-75. Số lược mang dưới 15-17, số lược mang trên 6-8, tổng số lược mang 21-25. Cá thể chưa trưởng thành thân màu nâu đen với các đốm loang to màu trắng; khi trưởng thành, thân xuất hiện các đốm nâu phân bố đều trên cơ thể, sống lưng có 2 đốm trắng to (1 ở vị trí gốc tia vây lưng cứng đầu tiên và 1 nằm giữa vây lưng cứng và vây lưng mềm). Mép sau các tấm vảy trên cơ thể có hình răng cưa. Vây đuôi tròn.'
    },
    'tap6-species-54': {
        'en_common_name': 'Brownspotted grouper',
        'morphology_vn': 'D XI 16-18; A III 8. Số vảy đường bên 48-53. Số lược mang dưới 14-18, số lược mang trên 8-11, tổng số lược mang 22-29. Cơ thể có nền màu trắng ngà với các đốm nhỏ màu nâu (phần ức và lườn bụng không có đốm). Mép vảy trên cơ thể có hình răng cưa ngoại trừ vùng vảy trên gáy, ngực và lườn bụng. Mép nắp mang trên nhẵn.'
    },
    'tap6-species-58': {
        'scientific_name': 'Epinephelus sexfasciatus',
        'authorship': '(Valenciennes, 1828)',
        'morphology_vn': 'D XI. 16-18; A III. 8. Số vảy đường bên 48-53. Số lược mang dưới 14-16, số lược mang trên 6-8, tổng số lược mang 20-24. Đầu nhỏ, thân có màu nâu nhạt với đốm thưa không đều, có 5-6 dải sọc xiên màu nâu sẫm. Vây đuôi tròn, màu nâu sẫm với các đốm nhạt màu. Mép vảy sau trên cơ thể có hình răng cưa (ngoại trừ vảy trên các vùng gáy, ngực, lườn bụng và đường bên). Mép nắp mang trên thẳng, nằm gần như thẳng đứng. Răng cửa hàm trên có 2-3 hàng răng nhọn.'
    },
    'tap6-species-65': {
        'en_common_name': 'Blacksaddled coralgrouper',
        'morphology_vn': 'D VII-VIII 10-12; A III 8. Số vảy đường bên 83-97. Số lược mang dưới 4-10, số lược mang trên 1-3, tổng số lược mang 5-13. Thân màu trắng nhạt hoặc vàng nhạt, có 5 đốm đen không bằng nhau vắt ngang trên lưng màu đen hoặc nâu hình yên ngựa. Thân dài, chiều dài thân bằng 2,9-3,9 lần chiều cao thân. Xương nắp mang trước tròn rộng, có 3 gai lớn. Các vây, mõm và dưới hàm màu vàng. Vây đuôi phân thùy (thùy xẻ nông).'
    },
    'tap6-species-80': {
        'en_common_name': 'Spotted-gill cardinalfish',
        'morphology_vn': 'D VIII 9; A II 8. Số vảy đường bên 25. Số lược mang trước 14-16, số lược mang sau 5-6. Thân màu vàng nhạt với cặp sọc màu nâu nằm phía trên của thân. Các cá thể trưởng thành, trên má xuất hiện các đốm đỏ màu cam, giữa gốc vây đuôi có chấm đen.'
    }
}

def clean_morphology(text):
    if not text:
        return text
    t = text

    # 1. Cắt bỏ đoạn văn Sinh thái / Phân bố nếu bị dán lẫn vào Mô tả hình thái
    t = re.split(r'\s*Sinh th[áả]i\b', t, flags=re.IGNORECASE)[0].strip()
    t = re.split(r'(?:\n|\.\s+)(?:Phân bố|Giá trị kinh tế)\s*[:,\-]', t, flags=re.IGNORECASE)[0].strip()

    # 2. Xóa các chuỗi ghost OCR và lỗi quét 2 cột bị đè chữ
    t = t.replace('Ca the ehtra truong thnan tan co mau', '')
    t = re.sub(r'trên rên năp nắp mang mang có có 2 2 sọc sọc trắng trang', 'trên nắp mang có 2 sọc trắng', t)
    t = re.sub(r'lun màu đỏ', 'màu đỏ', t)
    t = re.sub(r'dươi 14-17, so lược mang tfel 1о tổng số lược mang 22-27\.\s*Cơ thể có tong so lược mang 22-21 0 nền màu nâu với các đốm nhỏ màu nen mau nau voi cach xám xanh', 'Cơ thể có nền màu nâu với các đốm nhỏ màu xám xanh', t)
    t = re.sub(r'\(con non hình thái ngoài gần giống loài E\. howlandi và E\. macrospilos \)\s*20TOGmlndi nhưng', '(con non hình thái ngoài gần giống loài E. howlandi và E. macrospilos nhưng', t)
    t = re.sub(r'Vây rây đuổi trồn', 'Vây đuôi tròn', t)
    t = re.sub(r'dęt so lược mang 7-15\.\s*Tnan tnuon dai ben, dau dai bang chieu cao than\.\s*han bên, đầu dài bằng chiều cao thân\.', 'dẹt bên, đầu dài bằng chiều cao thân.', t)
    t = re.sub(r'đen nau hong vơi cham nhỏ', 'đến nâu hồng với chấm nhỏ', t)
    t = re.sub(r'Có đôi gai má, gai gai ma, ga mui ro rang\. loan than co ga DRO mũi rõ ràng\.', 'Có đôi gai má, gai mũi rõ ràng.', t)
    t = re.sub(r'Toàn thân có gai bao than co ga о phủ', 'Toàn thân có gai bao phủ', t)
    t = re.sub(r'Toàn thân có gai bao phủ \(nhưng gai không nhọn\)\. Đầu phu \(nhưng gai khong nhọn\)\. Dau có mấu thấp', 'Toàn thân có gai bao phủ (nhưng gai không nhọn). Đầu có mấu thấp', t)
    t = re.sub(r'màu của của lông hổ', 'màu của lông hổ', t)
    t = re.sub(r'Mep hap thang then thang, nam gan Mép nắp mang trên thăng, năm gần như thăng đứng\.', 'Mép nắp mang trên thẳng, nằm gần như thẳng đứng.', t)
    t = re.sub(r'Răng cửa hàm trên có 2-3 thang dựng\. Kan hàng răng nhọn\.', 'Răng cửa hàm trên có 2-3 hàng răng nhọn.', t)
    t = re.sub(r'\(go gay, uguc, uon ngva uoug n gáy, ngực, lườn bụng và đường bên\)', '(vùng gáy, ngực, lườn bụng và đường bên)', t)
    t = re.sub(r'lang cũa', 'của', t)
    t = re.sub(r'đốm thưa không đều, có 5-6 dài soc xiên màu nâu sẫm', 'đốm thưa không đều, có 5-6 dải sọc xiên màu nâu sẫm', t)
    t = re.sub(r'm u nâu sẫm', 'màu nâu sẫm', t)
    t = re.sub(r'Mọ ta hinh nat:\s*D\s*XI\.\s*13-17,\s*А\s*т\.\s*о\.\s*', '', t)
    t = re.sub(r'Thân màu đô xen ke cac sọc trang b đỏ', 'Thân màu đỏ', t)
    t = re.sub(r'Tia vay lng mau nc độe\) nhạt\.\s*Tia vây lưng màu đen \(gai thứ 3 hoặc thứ 4 dài nhất và có nọc độc\)\s*3 hoạc thử 4 dal nnat AB a ốc vơi cac dom trang ninn oan due ren', 'Tia vây lưng màu đen (gai thứ 3 hoặc thứ 4 dài nhất và có nọc độc)', t)
    t = re.sub(r'Số rược hang duot 24-27, so tue hang lược mang dưới 24-27, số lược mang tren 12-14, tong so lược mang 53-47\.\s*trên 12-14, tổng số lược mang 35-42\.', 'Số lược mang dưới 24-27, số lược mang trên 12-14, tổng số lược mang 35-42.', t)
    t = re.sub(r'Ham dươi cua ca the trương thann uuo lên khi miệng khép', 'nhô lên khi miệng khép', t)
    t = re.sub(r'12 Số vày đường bên 25 \(số vảy có lỗ so vay duong 24-25\)\.\s*So lư nanh hàm 24-25\)\.', 'Số vảy đường bên 25 (số vảy có lỗ 24-25).', t)
    t = re.sub(r'Thân màu hân màu xám nhạt', 'Thân màu xám nhạt', t)
    t = re.sub(r'Ca Cá thể chưa trưởng thành', 'Cá thể chưa trưởng thành', t)
    t = re.sub(r'6-6\.\s*Co the phia ling bụng nhạt mau\.\s*Vay ngực co các dom có đen', 'phía bụng nhạt màu. Vây ngực có các đốm đen', t)
    t = re.sub(r'\bGain Gai má\b', 'Gai má', t)
    t = re.sub(r'cơ cờ thể', 'cơ thể', t)
    t = re.sub(r'\bdinh dưỡng:\s*Loài cá không\s*$', '', t).strip()

    # 3. Sửa lỗi chính tả & dấu thanh OCR
    t = re.sub(r'\bdęt\b', 'dẹt', t)
    t = re.sub(r'\bcũa\b', 'của', t)
    t = re.sub(r'\bdũữ\b', 'dữ', t)
    t = re.sub(r'\bCơ thể màu đô\b', 'Cơ thể màu đỏ', t)
    t = re.sub(r'\bmàu đô\b', 'màu đỏ', t)
    t = re.sub(r'\bđô sâu\b', 'độ sâu', t)
    t = re.sub(r'\bở đô\b', 'ở độ', t)
    t = re.sub(r'\bmôm trắng\b', 'mõm trắng', t)
    t = re.sub(r'\bmôm\b', 'mõm', t)
    t = re.sub(r'\bMôm\b', 'Mõm', t)
    t = re.sub(r'\bvẩy\b', 'vảy', t)
    t = re.sub(r'\bVẩy\b', 'Vảy', t)
    t = re.sub(r'\bmầu\b', 'màu', t)
    t = re.sub(r'\bMầu\b', 'Màu', t)
    t = re.sub(r'\bchiểu\b', 'chiều', t)
    t = re.sub(r'\bhỉnh\b', 'hình', t)
    t = re.sub(r'\bthê\b', 'thể', t)
    t = re.sub(r'\bchî\b', 'chỉ', t)
    t = re.sub(r'\bthăng đứng\b', 'thẳng đứng', t)
    t = re.sub(r'\bthăng\b', 'thẳng', t)
    t = re.sub(r'\bLung màu đỏ\b', 'Lưng màu đỏ', t)
    t = re.sub(r'\bSố Sô lược mang\b', 'Số lược mang', t)
    t = re.sub(r'\bSô lược mang\b', 'Số lược mang', t)
    t = re.sub(r'\bSô vảy\b', 'Số vảy', t)
    t = re.sub(r'\bvẫy đuôi\b', 'vây đuôi', t)
    t = re.sub(r'\brăng răng cưa\b', 'răng cưa', t)

    # 4. Xóa lặp từ do scan hai lần
    t = re.sub(r'\b(mang|trên|hoặc|vào|ban|đá|khi|san|cơ|môn|dải)\s+\1\b', r'\1', t, flags=re.IGNORECASE)

    # 5. Chuẩn hóa khoảng trắng
    t = re.sub(r'\s{2,}', ' ', t).strip()
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
        old_m = (s.get('morphology_vn') or '').strip()
        old_en = (s.get('en_common_name') or '').strip()
        old_sci = (s.get('scientific_name') or '').strip()

        row = dict(s)
        has_change = False

        if sp_id in SPECIAL_FIXES:
            fixes = SPECIAL_FIXES[sp_id]
            for k, v in fixes.items():
                if row.get(k) != v:
                    row[k] = v
                    has_change = True
        else:
            new_m = clean_morphology(old_m)
            if new_m != old_m:
                row['morphology_vn'] = new_m
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
