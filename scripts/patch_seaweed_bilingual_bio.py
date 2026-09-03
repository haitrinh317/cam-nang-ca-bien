"""
Patch 3 seaweed species in Supabase with bilingual AlgaeBase data:
- bio.biologySummary = Original English text from AlgaeBase
- bio.biologySummaryVn = Standard academic Vietnamese translation
"""

import json
import urllib.request

env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k.strip()] = v.strip('\"\'')

url = env['NEXT_PUBLIC_SUPABASE_URL']
key = env.get('SUPABASE_SERVICE_ROLE_KEY') or env['NEXT_PUBLIC_SUPABASE_ANON_KEY']
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

DATA = {
    'thucvat-species-1': {
        'fbName': 'Flat Gracilaria / Textor Gracilaria',
        'habitat': 'Đới dưới triều nông (Subtidal), bám đá hoặc rạn san hô',
        'depth': '0 - 15 m',
        'importance': 'Chế biến thực phẩm, nguồn chiết xuất Agar-agar chất lượng cao',
        'distribution': 'Việt Nam (Khánh Hòa, Bình Thuận, Côn Đảo), Nhật Bản, Hàn Quốc, Tây Thái Bình Dương',
        'biologySummary': 'Thallus foliose, membranous to coriaceous, 5–20 cm high, reddish brown to dark greenish red. Blades flat, repeatedly dichotomously or palmatively branched, with rounded apices and entire or proliferous margins. Attached to rocks or dead coral substrates in lower intertidal to upper subtidal zones. Widely distributed in the Indo-West Pacific, including Vietnam, Japan, and Korea. Important commercial source of high-quality agar.',
        'biologySummaryVn': 'Tản rong dạng phiến dẹt, chất màng đến chất dai như da, cao 5–20 cm, màu nâu đỏ đến lục đỏ sẫm. Các phiến dẹt phân nhánh lưỡng phân hoặc dạng ngón tay nhiều lần, đỉnh nhánh tròn, mép nguyên hoặc mọc chồi con. Mọc bám vào đá hoặc san hô chết ở vùng triều thấp và đới dưới triều nông. Phân bố rộng ở vùng biển Ấn Độ - Tây Thái Bình Dương, bao gồm Việt Nam, Nhật Bản và Hàn Quốc. Là nguồn nguyên liệu tự nhiên quan trọng để chiết xuất thạch Agar chất lượng cao.'
    },
    'thucvat-species-2': {
        'fbName': 'Arcuate Gracilaria',
        'habitat': 'Vùng triều thấp và đới dưới triều nông (Upper subtidal zone)',
        'depth': '0.5 - 5 m',
        'importance': 'Khai thác tự nhiên, nguồn chế biến thạch và agar',
        'distribution': 'Việt Nam (Đảo Phú Quốc, Vịnh Nha Trang, Ninh Thuận), Biển Đỏ, Ấn Độ Dương, Tây Thái Bình Dương',
        'biologySummary': 'Thallus fleshy, erect to caespitose, 5–15 cm tall, dark purple or greenish red, consisting of thick cylindrical branches, 2–4 mm in diameter, characteristically curved like a bow (arcuate). Found growing on rocky reefs and coral substrates in upper subtidal and low intertidal habitats, notably recorded from Phu Quoc Island, Nha Trang, and Con Dao, Vietnam. Utilized as food and raw material for agar production.',
        'biologySummaryVn': 'Tản rong mập mạp dạng sụn, mọc đứng thành bụi dày cao 5–15 cm, màu đỏ tím sẫm hoặc lục đỏ, gồm các nhánh hình trụ tròn đường kính 2–4 mm, uốn cong queo đặc trưng hình cánh cung (arcuata). Mọc bám trên rạn đá và nền san hô ở đới triều thấp và vùng dưới triều nông, tiêu biểu được ghi nhận tại đảo Phú Quốc, Nha Trang và Côn Đảo (Việt Nam). Được khai thác dùng làm thực phẩm và nguyên liệu nấu thạch agar.'
    },
    'thucvat-species-3': {
        'fbName': 'Eucheuma-like Gracilaria',
        'habitat': 'Bám chặt trên bề mặt đá hoặc san hô chết vùng sóng mạnh (Reef crest)',
        'depth': '0 - 3 m',
        'importance': 'Đặc sản ẩm thực (chè rau câu chân vịt Lý Sơn, gỏi rong sụn), giàu khoáng chất',
        'distribution': 'Việt Nam (Đảo Lý Sơn - Quảng Ngãi, Khánh Hòa, Ninh Thuận, Côn Đảo), Nhật Bản, Tây Thái Bình Dương',
        'biologySummary': 'Thallus prostrate, cartilaginous, thick and compressed, 3–8 cm long, forming dense spreading clumps tightly adhering to rocky or coral substrates with ventral haptera. Branches irregular, with cuneate or palmate dentate segments resembling duck feet. Adapted to high wave-energy environments on outer reef crests, recorded in Ly Son Island, Khanh Hoa, and Ninh Thuan. Highly prized local delicacy (rau cau chan vit) rich in minerals and dietary fiber.',
        'biologySummaryVn': 'Tản rong mọc bò, chất sụn dày và cứng, dài 3–8 cm, tạo thành các tảng dày bám chặt vào đá hoặc san hô nhờ các giác bám ở mặt dưới. Các phân nhánh bất quy tắc, dạng phiến dẹt có răng cưa xòe rộng như ngón chân vịt. Thích nghi cao với môi trường sóng vỗ mạnh ở gờ rạn san hô ngoài, phổ biến tại đảo Lý Sơn (Quảng Ngãi), Khánh Hòa và Ninh Thuận. Là đặc sản ẩm thực nổi tiếng (chè rau câu chân vịt, gỏi rong sụn) rất giàu khoáng chất và chất xơ.'
    }
}

for sp_id, bio_obj in DATA.items():
    patch_url = f'{url}/rest/v1/species?id=eq.{sp_id}'
    payload = {'biology': json.dumps(bio_obj, ensure_ascii=False)}
    req = urllib.request.Request(
        patch_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    with urllib.request.urlopen(req) as resp:
        print(f'Updated {sp_id}: status {resp.status}')

print('Done updating bilingual biology data in Supabase!')
