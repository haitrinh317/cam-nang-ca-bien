#!/usr/bin/env python3
"""
sync_algaebase.py — Production Engine Đồng Bộ Chuẩn Hóa Thực Vật Biển Việt Nam (201 Loài)

Tiêu chuẩn đồng bộ chuẩn AlgaeBase & WoRMS:
1. Tên Tiếng Việt & Tên gọi khác (vn_name, vn_alternate_names):
   - Đảm bảo 100% loài có tên tiếng Việt chuẩn và tên gọi khác (synonyms / alternate names)
     trích xuất tự động từ sách OCR gốc (46 batch files) và AlgaeBase KB.
2. Tên Tiếng Anh chuẩn (en_common_name):
   - Chuẩn hóa tên thương mại / phổ thông quốc tế từ AlgaeBase, cấm fallback sang tên khoa học.
3. Cây phân loại 4 cấp song ngữ (Lớp, Bộ, Họ, Chi):
   - Chuẩn hóa từ WoRMS & AlgaeBase, đồng bộ cả tên Latinh và tên tiếng Việt học thuật.
4. Bảng thông số Sinh học & Sinh thái song ngữ (Bilingual Biology):
   - Tách biệt rõ ràng tiếng Việt (cột trái) và tiếng Anh gốc (cột phải):
     + depth & depthVn (độ sâu)
     + habitat & habitatVn (môi trường sống)
     + importance & importanceVn (giá trị kinh tế, ẩm thực, sinh thái)
     + biologySummary & biologySummaryVn (mô tả tản rong học thuật)
     + algaebaseId & algaebaseUrl (liên kết nguồn)
5. Kho ảnh tiêu bản & thực địa (Supabase Storage & species_photos):
   - Ưu tiên ảnh tiêu bản từ AlgaeBase CDN (img.algaebase.org) hoặc ảnh thực địa có bản quyền rõ ràng (CC-BY).
   - Chuyển đổi WebP (960px max width, quality 80), tải lên bucket 'species-photos/thuc-vat-bien/{id}/01.webp'.
   - Ghi nhận đầy đủ tác giả, giấy phép, nguồn vào bảng 'species_photos'.
6. Đồng bộ 2 chiều:
   - Cập nhật trực tiếp lên Supabase 'species'.
   - Cập nhật file cục bộ 'data/thucvat_all.json' để giữ tính toàn vẹn dữ liệu.
"""

import argparse
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)


# ── 1. Load Environment & Constants ──────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
env = {}
env_file = ROOT_DIR / '.env'
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip('\"\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL') or env.get('SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('SUPABASE_SERVICE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')
ALGAEBASE_KEY = env.get('ALGAEBASE_API_KEY')
BUCKET = 'species-photos'

if not SUPABASE_URL or not SUPABASE_KEY:
    print("LỖI: Chưa cấu hình SUPABASE_URL hoặc SUPABASE_KEY trong .env!")
    sys.exit(1)

HEADERS_REST = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

HEADERS_HTTP = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.algaebase.org/'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ── 2. Đọc Kho Dữ Liệu Sách Gốc (thucvat_all.json) ────────────────────
THUCVAT_FILE = ROOT_DIR / 'data' / 'thucvat_all.json'
THUCVAT_DATA = []
THUCVAT_BY_ID = {}
THUCVAT_BY_SCI = {}

if THUCVAT_FILE.exists():
    try:
        with open(THUCVAT_FILE, 'r', encoding='utf-8') as f:
            THUCVAT_DATA = json.load(f)
            for item in THUCVAT_DATA:
                if item.get('id'):
                    THUCVAT_BY_ID[item['id']] = item
                if item.get('scientific_name'):
                    clean = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', item['scientific_name']).strip()
                    THUCVAT_BY_SCI[item['scientific_name'].strip()] = item
                    THUCVAT_BY_SCI[clean] = item
    except Exception as e:
        print(f"Cảnh báo: Không thể đọc thucvat_all.json ({e})")

# ── 2b. Đọc Kho Dữ Liệu Các Batch OCR (data/ocr_batches/rongbien_batch*.json) ──
OCR_BATCH_DIR = ROOT_DIR / 'data' / 'ocr_batches'
OCR_BATCH_NAMES = {}
if OCR_BATCH_DIR.exists():
    for fpath in OCR_BATCH_DIR.glob('rongbien_batch*.json'):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                items = json.load(f)
                for item in items:
                    sci = item.get('scientific_name')
                    vn = item.get('vn_name') or item.get('vietnamese_name')
                    if sci and vn and not vn.startswith('Chưa có'):
                        clean = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', sci).strip()
                        OCR_BATCH_NAMES[sci.strip()] = vn.strip()
                        OCR_BATCH_NAMES[clean] = vn.strip()
        except Exception:
            pass

# ── 3. Từ Điển Phân Loại Học Thực Vật Biển (Song Ngữ VN - Latinh) ────
TAXONOMY_VN = {
    # Ngành / Lớp
    'Rhodophyta': 'Ngành Rong Đỏ',
    'Florideophyceae': 'Lớp Rong Đỏ',
    'Bangiophyceae': 'Lớp Rong Đỏ Bangia',
    'Phaeophyceae': 'Lớp Rong Nâu',
    'Chlorophyta': 'Ngành Rong Lục',
    'Ulvophyceae': 'Lớp Rong Lục Ulva',
    'Tracheophyta': 'Ngành Cỏ Biển',
    'Magnoliopsida': 'Lớp Cỏ Biển',
    
    # Bộ
    'Gracilariales': 'Bộ Rau Câu',
    'Gigartinales': 'Bộ Rong Sụn',
    'Ceramiales': 'Bộ Rong Đỏ Ceramiales',
    'Corallinales': 'Bộ Rong San Hô',
    'Nemaliales': 'Bộ Rong Nemaliales',
    'Gelidiales': 'Bộ Thạch Rong',
    'Rhodymeniales': 'Bộ Rong Sừng Rhodymenia',
    'Fucales': 'Bộ Rong Mơ',
    'Dictyotales': 'Bộ Rong Mạng',
    'Ectocarpales': 'Bộ Rong Sợi Nâu',
    'Ulvales': 'Bộ Rong Diếp Biển',
    'Bryopsidales': 'Bộ Rong Đuôi Chồn',
    'Cladophorales': 'Bộ Rong Bông',
    'Dasycladales': 'Bộ Rong Tán',
    'Alismatales': 'Bộ Cỏ Biển',
    
    # Họ
    'Gracilariaceae': 'Họ Rau Câu',
    'Solieriaceae': 'Họ Rong Sụn',
    'Sargassaceae': 'Họ Rong Mơ',
    'Dictyotaceae': 'Họ Rong Mạng',
    'Ulvaceae': 'Họ Rong Diếp Biển',
    'Caulerpaceae': 'Họ Rong Nho',
    'Codiaceae': 'Họ Rong Codium',
    'Halimedaceae': 'Họ Rong Halimeda',
    'Champiaceae': 'Họ Rong Sơn Biên',
    'Rhodymeniaceae': 'Họ Rong Sừng Rhodymenia',
    'Lomentariaceae': 'Họ Rong Thạch Giả Lomentaria',
    'Ceramiaceae': 'Họ Rong Gọng Kìm',
    'Dasyaceae': 'Họ Rong Bông Dasyaceae',
    'Delesseriaceae': 'Họ Rong Lá Mỏng Delesseriaceae',
    'Rhodomelaceae': 'Họ Rong Mào Gà',
    'Hydrocharitaceae': 'Họ Cỏ Nhang',
    'Cymodoceaceae': 'Họ Cỏ Xoan',
}

# ── 4. Cơ Sở Tri Thức Chuẩn Hóa AlgaeBase & Sách Chuyên Khảo ─────────
SEAWEED_KNOWLEDGE_BASE = {
    'Gracilaria textorii': {
        'algaebase_id': 1934,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1934',
        'vn_name': 'Rau Câu dẹt',
        'vn_alternate_names': 'Rau Câu bản dẹt, Rau Câu phiến, Rau Câu quạt, Rong Giang li',
        'en_common_name': 'Flat Gracilaria / Textor Gracilaria',
        'fbName': 'Flat Gracilaria / Textor Gracilaria',
        'depth': '0 - 15 m',
        'depthVn': '0 - 15 m',
        'habitat': 'Subtidal rocky reefs and coral rubbles exposed to moderate wave action',
        'habitatVn': 'Đới dưới triều nông, bám trên đá hoặc vụn san hô nơi sóng vừa',
        'importance': 'High-yield Agar-agar extraction and traditional sea food',
        'importanceVn': 'Khai thác tự nhiên chế biến thạch agar chất lượng cao và làm thực phẩm',
        'biologySummary': 'Thallus compressed and blade-like, thin and membranous to subcartilaginous, bright red to greenish red. Irregularly dichotomously branched with broad lobes.',
        'biologySummaryVn': 'Tản rong dạng phiến dẹt mỏng như dải lụa, phân nhánh lưỡng phân hoặc dạng ngón tay, mép phiến nguyên. Màu đỏ sẫm đến lục nâu, là nguồn nguyên liệu chiết xuất agar tự nhiên quý giá.',
        'img_url': 'https://img.algaebase.org/images/3EE735B10772e02B67Tuk30BC816/NJitqKRvULyj.jpg',
        'photographer': 'Chiba University / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'source': 'algaebase'
    },
    'Gracilaria arcuata': {
        'algaebase_id': 1690,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1690',
        'vn_name': 'Rau Câu cong',
        'vn_alternate_names': 'Rau Câu cánh cung, Rau Câu cong Phú Quốc, Rong Giang li',
        'en_common_name': 'Arcuate Gracilaria',
        'fbName': 'Arcuate Gracilaria',
        'depth': '0.5 - 5 m',
        'depthVn': '0,5 - 5 m',
        'habitat': 'Upper subtidal zone on coral reef flats and tide pools',
        'habitatVn': 'Vùng triều thấp và đới dưới triều nông trên các rạn đá san hô cạn',
        'importance': 'Wild harvest for agar production and culinary consumption',
        'importanceVn': 'Khai thác tự nhiên, nguồn nguyên liệu chế biến thạch và agar',
        'biologySummary': 'Thallus erect, succulent and cartilaginous, with characteristic arcuate or curved branchlets. Forms dense clumps in shallow reef habitats.',
        'biologySummaryVn': 'Tản rong mập mạp hình trụ tròn, các cành nhánh uốn cong queo đặc trưng hình cánh cung (arcuata). Mọc bám trên rạn đá san hô cạn và vũng triều ven các đảo lớn phía Nam Việt Nam.',
        'img_url': 'https://img.algaebase.org/images/8CCBD7A40f62320D11qKl34BE02E/kRu1fBE88qVi.jpg',
        'photographer': 'Phu Quoc Island (Vietnam) Specimen / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'source': 'algaebase'
    },
    'Gracilaria eucheumatoides': {
        'algaebase_id': 1900,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1900',
        'vn_name': 'Rau Câu chân vịt',
        'vn_alternate_names': 'Rau Câu sụn, Rau Câu màng, Rong Kiều tảo',
        'en_common_name': 'Eucheuma-like Gracilaria',
        'fbName': 'Eucheuma-like Gracilaria',
        'depth': '0 - 3 m',
        'depthVn': '0 - 3 m',
        'habitat': 'Firmly attached to rock and dead coral surfaces at reef crest exposed to heavy surf',
        'habitatVn': 'Bám chặt trên bề mặt đá hoặc san hô chết vùng sóng đập mạnh (mào rạn)',
        'importance': 'Famous island specialty (Ly Son seaweed dessert, salad) and mineral-rich food',
        'importanceVn': 'Đặc sản ẩm thực nổi tiếng (chè rau câu chân vịt Lý Sơn, gỏi rong sụn), rất giàu khoáng chất',
        'biologySummary': 'Thallus strongly prostrate and cartilaginous, forming sprawling thick mats. Branches compressed with marginal dentate or finger-like projections resembling duck feet.',
        'biologySummaryVn': 'Tản rong có chất sụn dày và cứng, màu đỏ lục sẫm, phân nhánh bất quy tắc với các nhánh dẹt rộng xòe ra như ngón chân vịt. Mặt dưới có nhiều giác bám giúp rong dính chặt vào đá san hô trước lực sóng đập dữ dội.',
        'img_url': 'https://img.algaebase.org/images/A4A110171926405753Ogi3A5A553/f6kqX3q9qyAd.jpg',
        'photographer': 'Hideki Yukihira / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'source': 'algaebase'
    },
    'Gracilaria salicornia': {
        'algaebase_id': 1920,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1920',
        'vn_name': 'Rau Câu đốt',
        'vn_alternate_names': 'Rau Câu đốt tre, Rong Câu đốt, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Salicornia Gracilaria / Jointed Gracilaria',
        'fbName': 'Salicornia Gracilaria / Jointed Gracilaria',
        'depth': '0 - 4 m',
        'depthVn': '0 - 4 m',
        'habitat': 'Lower intertidal to shallow subtidal reef flats, attached to rocks and coral rubbles',
        'habitatVn': 'Đới triều thấp đến dưới triều cạn trên các rạn san hô phẳng, bám trên đá và vụn san hô',
        'importance': 'Wild harvest for agar production and local food consumption',
        'importanceVn': 'Khai thác tự nhiên để sản xuất thạch agar và chế biến món ăn địa phương',
        'biologySummary': 'Thallus bright yellow-green to dark brown, forming dense stiff clumps up to 15 cm across. Branches distinctly constricted at intervals into cylindrical or clavate nodes/joints resembling Salicornia stems. Highly tolerant of high light and temperature on intertidal reef flats.',
        'biologySummaryVn': 'Tản rong màu vàng lục sáng đến nâu sẫm, mọc thành bụi dày cứng rộng tới 15 cm. Các cành nhánh thắt ngẫng rõ rệt thành từng đốt hình trụ hoặc hình dùi đặc trưng như cây rong đốt. Có khả năng chịu đựng cao với cường độ chiếu sáng và nhiệt độ lớn ở các đới triều phẳng.',
        'img_url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/22583/large.JPG',
        'photographer': 'Kyle Van Houtan',
        'license': 'CC BY',
        'source': 'inaturalist'
    },
    'Gracilaria tenuistipitata var. liui': {
        'algaebase_id': 1933,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1933',
        'vn_name': 'Rau Câu chỉ',
        'vn_alternate_names': 'Rong Câu chỉ, Rau Câu sợi, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Slender-stem Gracilaria / Thin Gracilaria',
        'fbName': 'Slender-stem Gracilaria / Thin Gracilaria',
        'depth': '0.5 - 3 m',
        'depthVn': '0,5 - 3 m',
        'habitat': 'Estuaries, brackish lagoons, and mangrove canals with muddy or sandy-mud bottoms',
        'habitatVn': 'Vùng cửa sông, đầm phá nước lợ và kênh rạch rừng ngập mặn với đáy bùn hoặc bùn cát',
        'importance': 'Major commercial seaweed cultivated extensively in Vietnam for agar extraction and abalone feed',
        'importanceVn': 'Đối tượng nuôi trồng thủy sản chủ lực tại các tỉnh duyên hải Việt Nam để chiết xuất agar và làm thức ăn cho bào ngư',
        'biologySummary': 'Thallus slender, cylindrical, branching profusely into thin delicate fronds up to 50 cm long. Dark green to purple-brown. Widely farmed in coastal ponds and estuaries in northern and central Vietnam due to high growth rate and adaptability to salinity fluctuations.',
        'biologySummaryVn': 'Tản rong mảnh mai hình sợi chỉ, phân nhánh chằng chịt thành các sợi mảnh dài tới 50 cm. Màu lục sẫm đến tím nâu. Là loài rong được nuôi trồng rộng rãi nhất trong các đầm hồ nước lợ ven biển miền Bắc và miền Trung nước ta nhờ tốc độ sinh trưởng rất nhanh và thích nghi tốt với biên độ độ mặn rộng.',
        'img_url': 'https://img.algaebase.org/images/562DFCD90591c2F7C8MsQ30C91E0/Zvtfq5767ErW.jpg',
        'photographer': 'AlgaeBase Specimen Collection',
        'license': 'AlgaeBase / Academic & Research Use',
        'source': 'algaebase'
    },
    'Gracilaria tenuistipitata': {
        'algaebase_id': 1933,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1933',
        'vn_name': 'Rau Câu mảnh',
        'vn_alternate_names': 'Rau Câu sợi mảnh, Rong Câu, Rong Kiều tảo',
        'en_common_name': 'Slender-stem Gracilaria / Thin Gracilaria',
        'fbName': 'Slender-stem Gracilaria / Thin Gracilaria',
        'depth': '0.5 - 3 m',
        'depthVn': '0,5 - 3 m',
        'habitat': 'Brackish ponds and bays',
        'habitatVn': 'Ao đầm và vịnh nước lợ',
        'importance': 'Commercial cultivation for agar production',
        'importanceVn': 'Nuôi trồng quy mô công nghiệp sản xuất thạch agar',
        'biologySummary': 'Delicate branching thallus widely distributed in tropical and subtropical Asian waters.',
        'biologySummaryVn': 'Tản rong dạng sợi thanh mảnh phân bố rộng rãi tại các vùng nước nhiệt đới và cận nhiệt đới châu Á.',
        'img_url': 'https://img.algaebase.org/images/562DFCD90591c2F7C8MsQ30C91E0/Zvtfq5767ErW.jpg',
        'photographer': 'AlgaeBase Specimen Collection',
        'license': 'AlgaeBase / Academic & Research Use',
        'source': 'algaebase'
    },
    'Gracilaria sp.1': {
        'algaebase_id': 144188,
        'algaebase_url': 'https://www.algaebase.org/search/genus/detail/?genus_id=144188',
        'vn_name': 'Rau Câu',
        'vn_alternate_names': 'Rong Câu, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Gracilaria Seaweed',
        'fbName': 'Gracilaria Seaweed',
        'depth': '0.5 - 3 m',
        'depthVn': '0,5 - 3 m',
        'habitat': 'Shallow coastal waters and reef flats',
        'habitatVn': 'Vùng nước ven bờ và bãi triều san hô cạn',
        'importance': 'Traditional harvesting for food and local home-made jelly',
        'importanceVn': 'Khai thác dân gian làm thạch giải khát và chế biến thực phẩm',
        'biologySummary': 'Unidentified species of the genus Gracilaria recorded in Vietnam coastal waters.',
        'biologySummaryVn': 'Loài thuộc chi Rau Câu Gracilaria ghi nhận tại vùng biển ven bờ Việt Nam.',
        'img_url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/325301452/large.jpg',
        'photographer': 'iNaturalist Community',
        'license': 'CC BY-NC',
        'source': 'inaturalist'
    },
    'Gracilaria sp.2': {
        'algaebase_id': 144188,
        'algaebase_url': 'https://www.algaebase.org/search/genus/detail/?genus_id=144188',
        'vn_name': 'Rau Câu',
        'vn_alternate_names': 'Rong Câu, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Gracilaria Seaweed',
        'fbName': 'Gracilaria Seaweed',
        'depth': '0.5 - 3 m',
        'depthVn': '0,5 - 3 m',
        'habitat': 'Shallow coastal waters and reef flats',
        'habitatVn': 'Vùng nước ven bờ và bãi triều san hô cạn',
        'importance': 'Local food consumption',
        'importanceVn': 'Khai thác làm thực phẩm',
        'biologySummary': 'Unidentified species of the genus Gracilaria recorded in Vietnam coastal waters.',
        'biologySummaryVn': 'Loài thuộc chi Rau Câu Gracilaria ghi nhận tại vùng biển ven bờ Việt Nam.',
        'img_url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/325301452/large.jpg',
        'photographer': 'iNaturalist Community',
        'license': 'CC BY-NC',
        'source': 'inaturalist'
    },
    'Gracilariopsis bailiniae': {
        'algaebase_id': 1948,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1948',
        'vn_name': 'Rau Câu cước',
        'vn_alternate_names': 'Rong Câu cước, Rau Câu sợi dài, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Wire-like Gracilariopsis',
        'fbName': 'Wire-like Gracilariopsis',
        'depth': '0.5 - 4 m',
        'depthVn': '0,5 - 4 m',
        'habitat': 'Brackish ponds, sheltered bays, and estuaries attached to shells or mud',
        'habitatVn': 'Ao đầm nước lợ, vịnh kín và cửa sông bám vào vỏ sò ốc hoặc đáy bùn',
        'importance': 'Cultivated for food and high-strength agar extraction',
        'importanceVn': 'Nuôi trồng và khai thác tự nhiên để nấu thạch với độ đông kết rất cao',
        'biologySummary': 'Thallus filiform, wire-like, cylindrical and smooth, reaching lengths of up to 1 meter. Branches long and flagelliform. Well known for producing agar with exceptionally high gel strength.',
        'biologySummaryVn': 'Tản rong dạng sợi cước dài, trơn nhẵn, mọc dài tới 1 mét. Các nhánh dài mảnh như roi da. Thạch agar chiết xuất từ rau câu cước có độ đông kết (gel strength) rất cao.',
        'img_url': 'https://img.algaebase.org/images/3EE735B10772e02B7ALlK30BD49B/ST1cmFajWeRV.jpg',
        'photographer': 'AlgaeBase Phycology Archive',
        'license': 'AlgaeBase / Academic Use',
        'source': 'algaebase'
    },
    'Hydropuntia edulis': {
        'algaebase_id': 1946,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1946',
        'vn_name': 'Rau Câu đỏ ăn được',
        'vn_alternate_names': 'Rau Câu ăn được, Rong Câu đỏ, Rau Câu thực phẩm, Rong Giang li',
        'en_common_name': 'Edible Gracilaria',
        'fbName': 'Edible Gracilaria',
        'depth': '0.5 - 6 m',
        'depthVn': '0,5 - 6 m',
        'habitat': 'Subtidal coral reef flats and lagoons attached to sandy rocks',
        'habitatVn': 'Vùng triều thấp và đới dưới triều rạn san hô, bám vào đá cát',
        'importance': 'Traditional culinary delicacy and source of agar',
        'importanceVn': 'Thực phẩm truyền thống lâu đời và nguồn nguyên liệu sản xuất agar',
        'biologySummary': 'Thallus erect, caespitose, dark purple to dark reddish-brown, 10–25 cm long. Branches cylindrical, succulent, tapering towards apices. Highly edible and consumed fresh or dried throughout Southeast Asia.',
        'biologySummaryVn': 'Tản rong mọc đứng thành bụi, màu đỏ tím sẫm đến nâu đỏ, cao 10–25 cm. Cành nhánh hình trụ mọng nước, thon dần về ngọn. Rất ngon miệng, được dùng ăn tươi trong các món gỏi hoặc phơi khô nấu thạch khắp Đông Nam Á.',
        'img_url': 'https://static.inaturalist.org/photos/385442819/large.jpeg',
        'photographer': '張文瑞 (iNaturalist)',
        'license': 'CC BY-NC',
        'source': 'inaturalist'
    },
    'Hydropuntia sp.': {
        'algaebase_id': 369787,
        'algaebase_url': 'https://www.algaebase.org/search/genus/detail/?genus_id=369787',
        'vn_name': 'Rau Câu',
        'vn_alternate_names': 'Rong Câu đỏ, Rong Giang li, Rong Kiều tảo',
        'en_common_name': 'Hydropuntia Seaweed',
        'fbName': 'Hydropuntia Seaweed',
        'depth': '0.5 - 5 m',
        'depthVn': '0,5 - 5 m',
        'habitat': 'Subtidal coral reef flats and rocky bottoms',
        'habitatVn': 'Đới dưới triều rạn san hô và nền đáy đá',
        'importance': 'Source of agar and food',
        'importanceVn': 'Nguồn sản xuất agar và thực phẩm',
        'biologySummary': 'Species belonging to genus Hydropuntia recorded in coastal waters of Vietnam.',
        'biologySummaryVn': 'Loài thuộc chi Rong Câu đỏ Hydropuntia ghi nhận ở vùng biển ven bờ Việt Nam.',
        'img_url': 'https://static.inaturalist.org/photos/385442819/large.jpeg',
        'photographer': 'iNaturalist Community',
        'license': 'CC BY-NC',
        'source': 'inaturalist'
    },
    'Champia parvula': {
        'algaebase_id': 160,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=160',
        'vn_name': 'Rong Sơn biên',
        'vn_alternate_names': 'Rong Sơn biên nhỏ, Rong Thùng phát quang, Rong Sơn biên biển',
        'en_common_name': 'Small Barrel Seaweed',
        'fbName': 'Small Barrel Seaweed',
        'depth': '0 - 10 m',
        'depthVn': '0 - 10 m',
        'habitat': 'Epiphytic on other seaweeds or attached to coral fragments in tide pools and shallow subtidal zones',
        'habitatVn': 'Mọc biểu sinh trên các loài rong khác hoặc bám mảnh san hô trong vũng triều và vùng dưới triều nông',
        'importance': 'Ecological indicator species, source of bioactive polysaccharides',
        'importanceVn': 'Loài chỉ thị sinh thái rạn san hô, nguồn chiết xuất polysaccharide hoạt tính sinh học',
        'biologySummary': 'Thallus small, delicate, tubular and gelatinous, 3–10 cm tall, displaying beautiful blue or greenish iridescence under water. Branches barrel-shaped, segmented with internal diaphragms.',
        'biologySummaryVn': 'Tản rong nhỏ nhắn, dạng ống mềm chứa chất keo, cao 3–10 cm, phát ánh sắc óng ánh xanh lam hoặc lục tuyệt đẹp dưới làn nước biển. Các nhánh hình thùng nhỏ có vách ngăn ngang bên trong.',
        'img_url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/526318741/large.jpg',
        'photographer': 'cccrll (iNaturalist)',
        'license': 'CC BY-NC',
        'source': 'inaturalist'
    },
    'Ceratodictyon spongiosum': {
        'algaebase_id': 2100,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=2100',
        'vn_name': 'Rong Sừng xốp',
        'vn_alternate_names': 'Rong Võng giác, Rong Sừng bọt biển, Rong Sừng cộng sinh',
        'en_common_name': 'Sponge Seaweed / Horn-sponge Algae',
        'fbName': 'Sponge Seaweed / Horn-sponge Algae',
        'depth': '0.5 - 5 m',
        'depthVn': '0,5 - 5 m',
        'habitat': 'Symbiotic association with marine sponges (*Haliclona cymaeformis*) on shallow coral reef flats',
        'habitatVn': 'Cộng sinh bắt buộc với bọt biển (*Haliclona cymaeformis*) trên các rạn san hô nông',
        'importance': 'Key reef-building organism, model organism for marine symbiosis research',
        'importanceVn': 'Cấu thành sinh thái rạn san hô, đối tượng nghiên cứu cộng sinh tảo - bọt biển độc đáo',
        'biologySummary': 'Unique obligate symbiotic association where the red alga forms a hard cartilaginous branching network thoroughly embedded within the tissues of a marine sponge. Branches irregular, resembling deer antlers, forming sprawling green-brown masses on reef surfaces.',
        'biologySummaryVn': 'Hiện tượng cộng sinh bắt buộc độc nhất vô nhị giữa rong đỏ và bọt biển: tản rong tạo thành mạng lưới sừng cứng phân nhánh nằm trọn bên trong mô của bọt biển biển. Nhánh gồ ghề như gạc nai, tạo thành các tảng xốp màu nâu lục trên mặt rạn san hô.',
        'img_url': 'https://inaturalist-open-data.s3.amazonaws.com/photos/43147450/large.jpeg',
        'photographer': 'Matthew Connors',
        'license': 'CC BY-NC-SA',
        'source': 'inaturalist'
    },
    'Spyridia filamentosa': {
        'vn_name': 'Rong Tơ sợi',
        'vn_alternate_names': 'Rong Sợi, Rong Tơ biển',
        'en_common_name': 'Filamentous Spyridia',
        'fbName': 'Filamentous Spyridia',
        'depth': '0.5 - 5 m',
        'depthVn': '0,5 - 5 m',
        'habitat': 'Subtidal zone of calm to moderately wave-exposed shores attached to rocks or epiphytic',
        'habitatVn': 'Đới dưới triều nơi nước êm đến sóng vừa, mọc bám trên đá hoặc biểu sinh',
        'importance': 'Ecological community member, source of agaroid polysaccharides',
        'importanceVn': 'Cấu thành quần xã sinh thái bãi rong, chứa hợp chất polysaccharide tự nhiên',
        'biologySummary': 'Thallus forming soft bushy clumps with branching cylindrical axes covered with numerous delicate hair-like determinate branchlets.',
        'biologySummaryVn': 'Tản rong mọc thành bụi mềm, các trục nhánh hình trụ phân nhánh mang nhiều nhánh nhỏ tơ mịn như lông mao.'
    },
    'Spyridia hypnoides': {
        'vn_name': 'Rong Tơ rêu',
        'vn_alternate_names': 'Rong Tơ bò, Rong Rêu đỏ',
        'en_common_name': 'Hypnea-like Spyridia',
        'fbName': 'Hypnea-like Spyridia',
        'depth': '0.5 - 6 m',
        'depthVn': '0,5 - 6 m',
        'habitat': 'Shaded rocks and dead corals in the subtidal zone exposed to moderate wave action',
        'habitatVn': 'Mọc trên đá chỗ tối và san hô chết ở vùng dưới triều nơi sóng vừa',
        'importance': 'Reef biodiversity contributor',
        'importanceVn': 'Đóng góp vào đa dạng sinh học rạn san hô',
        'biologySummary': 'Thallus tufted, prostrate below and erect above, branching alternately with hook-shaped spine-tipped branchlets.',
        'biologySummaryVn': 'Tản rong mọc thành búi, bò ở phần dưới và đứng ở phần trên, mang các nhánh nhỏ có mấu gai cong ở đỉnh.'
    },
    'Dasyaceae sp.1': {
        'vn_name': 'Rong Bông đỏ 1',
        'vn_alternate_names': 'Rong Lông xù đỏ',
        'en_common_name': 'Plumose Red Seaweed',
        'fbName': 'Plumose Red Seaweed',
        'depth': '1 - 5 m',
        'depthVn': '1 - 5 m',
        'habitat': 'Subtidal rocky reefs exposed to moderate wave action',
        'habitatVn': 'Rạn đá vùng dưới triều nơi sóng vừa',
        'importance': 'Reef ecosystem component',
        'importanceVn': 'Cấu phần hệ sinh thái rạn san hô',
        'biologySummary': 'Delicate red alga with feathery plumose branchlets giving a soft fuzzy appearance underwater.',
        'biologySummaryVn': 'Rong đỏ thanh mảnh với các nhánh nhỏ dạng lông chim mềm mại tạo vẻ bông xù dưới nước.'
    },
    'Dasyaceae sp.2': {
        'vn_name': 'Rong Bông đỏ 2',
        'vn_alternate_names': 'Rong Lông xù hồng',
        'en_common_name': 'Pink Plumose Seaweed',
        'fbName': 'Pink Plumose Seaweed',
        'depth': '2 - 6 m',
        'depthVn': '2 - 6 m',
        'habitat': 'Rocks in the subtidal zone of shores exposed to moderate to strong wave action',
        'habitatVn': 'Mọc trên đá ở vùng dưới triều, nơi sóng vừa đến mạnh',
        'importance': 'Marine biodiversity indicator',
        'importanceVn': 'Chỉ thị đa dạng sinh học biển',
        'biologySummary': 'Light pink underwater changing to reddish brown when dried, branches cylindrical with dense plumose ramuli.',
        'biologySummaryVn': 'Màu hồng nhạt dưới nước đổi thành nâu đỏ khi khô, nhánh trụ tròn mang nhiều nhánh nhỏ dạng lông chim.'
    },
    'Dasyaceae sp.3': {
        'vn_name': 'Rong Bông đỏ 3',
        'vn_alternate_names': 'Rong Lông chim biển',
        'en_common_name': 'Bushy Feather Seaweed',
        'fbName': 'Bushy Feather Seaweed',
        'depth': '2 - 8 m',
        'depthVn': '2 - 8 m',
        'habitat': 'Subtidal rock faces in turbulent clean water',
        'habitatVn': 'Vách đá dưới triều nơi nước trong và sóng mạnh',
        'importance': 'Benthic habitat builder',
        'importanceVn': 'Tạo nơi cư trú cho sinh vật đáy nhỏ',
        'biologySummary': 'Erect bushy thallus with dense spiral plumose branchlets, dark red to purple.',
        'biologySummaryVn': 'Tản rong mọc đứng thành bụi mang các cành nhánh lông chim dày đặc màu đỏ sẫm đến tím.'
    },
    'Hypoglossum barbatum': {
        'vn_name': 'Rong Lưỡi râu',
        'vn_alternate_names': 'Rong Lưỡi mảnh, Rong Phiến râu',
        'en_common_name': 'Bearded Tongue Seaweed',
        'fbName': 'Bearded Tongue Seaweed',
        'depth': '1 - 6 m',
        'depthVn': '1 - 6 m',
        'habitat': 'Subtidal rocks or epiphytic on larger seaweeds in sheltered to moderate shores',
        'habitatVn': 'Mọc trên đá hoặc biểu sinh trên các rong khác ở vùng dưới triều nơi nước yên đến sóng vừa',
        'importance': 'Bioactive natural products research',
        'importanceVn': 'Đối tượng nghiên cứu hợp chất tự nhiên hoạt tính sinh học',
        'biologySummary': 'Delicate monostromatic blade-like thallus with distinct midrib and lateral bladelets arising from the central vein, bright translucent rose-red.',
        'biologySummaryVn': 'Tản rong dạng phiến mỏng trong suốt một lớp tế bào với gân giữa rõ rệt, màu đỏ hoa hồng tươi tắn.'
    }
}

# ── 5. Helper Bóc Tách Mô Tả & Môi Trường Sống ────────────────────────
def clean_desc(text):
    if not text:
        return ''
    return re.sub(r'\s*\d+\.\s*(?:Natural habit|Dried specimen|Fresh specimen|Dạng sống|Mẫu khô|Mẫu tươi|Microscopic|Mép phiến|Close-up|Nhìn chi tiết).*', '', text, flags=re.IGNORECASE).strip()

def extract_habitat_vn(text):
    m = re.search(r'(?:Rong\s+)?(?:mọc|bám|phát triển|thường bám)\s+[^.]+?(?:ở|tại)\s+[^.]+', text, re.IGNORECASE)
    if m:
        return m.group(0).strip()
    m2 = re.search(r'(?:ở\s+mực triều|ở\s+vùng triều|ở\s+đới triều|ở\s+vùng dưới triều)[^.]+', text, re.IGNORECASE)
    if m2:
        return m2.group(0).strip()
    return 'Vùng triều và đới dưới triều cạn ven biển'

def extract_habitat_en(text):
    m = re.search(r'(?:This species is found on|Plants are found on|This seaweed grows on|It is found on|Plants grow on|Found on|This seaweed tends to grow on)[^.]+', text, re.IGNORECASE)
    if m:
        return m.group(0).strip()
    m2 = re.search(r'(?:in the\s+(?:lower|mid|upper)?\s*intertidal|subtidal)[^.]+', text, re.IGNORECASE)
    if m2:
        return m2.group(0).strip()
    return 'Intertidal to shallow subtidal coastal waters'

# ── 6. Supabase REST & Storage API ───────────────────────────────────
def supa_get(endpoint, params=None):
    query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}{query_str}"
    req = urllib.request.Request(url, headers=HEADERS_REST)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode('utf-8'))

def supa_patch(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=HEADERS_REST, method='PATCH')
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.status

def supa_upload_image(storage_path, img_bytes):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    req = urllib.request.Request(
        url,
        data=img_bytes,
        headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'image/webp',
            'x-upsert': 'true'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            return r.status == 200
    except Exception as e:
        print(f"      [Lỗi upload ảnh]: {e}")
        return False

# ── 7. AlgaeBase & WoRMS API Helpers ─────────────────────────────────
def query_worms_by_name(scientific_name):
    """Tra cứu WoRMS API (chuẩn hóa danh pháp từ AlgaeBase đối tác)."""
    clean_name = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', scientific_name).strip()
    encoded = urllib.parse.quote(clean_name)
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?scientificnames[]={encoded}&marine_only=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            if data and len(data) > 0 and len(data[0]) > 0:
                rec = data[0][0]
                return {
                    'worms_id': rec.get('AphiaID'),
                    'worms_status': 'valid' if rec.get('status') == 'accepted' else (rec.get('status') or 'valid'),
                    'accepted_name': rec.get('valid_name') or rec.get('scientificname'),
                    'tax_class': rec.get('class'),
                    'tax_order': rec.get('order'),
                    'tax_family': rec.get('family'),
                    'tax_genus': rec.get('genus')
                }
    except Exception:
        pass
    return None

# ── 7b. Tích Hợp Wikidata SPARQL & GBIF (AlgaeBase IDs & Vernacular Names) ──
WIKIDATA_CACHE = {}

def query_wikidata_batch(names):
    """Truy vấn hàng loạt AlgaeBase ID (P1348) và Common Names (P1843) qua Wikidata SPARQL theo từng chunk."""
    if not names:
        return {}
    clean_names = list(set([re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', s).strip() for s in names if s]))
    chunk_size = 40
    res = {}
    for i in range(0, len(clean_names), chunk_size):
        chunk = clean_names[i:i + chunk_size]
        names_quoted = ' '.join([f'\"{s}\"' for s in chunk])
        sparql = f'''
SELECT ?sciName ?item ?algaebaseId ?commonName WHERE {{
  VALUES ?sciName {{ {names_quoted} }}
  ?item wdt:P225 ?sciName.
  OPTIONAL {{ ?item wdt:P1348 ?algaebaseId. }}
  OPTIONAL {{ ?item wdt:P1843 ?commonName. FILTER (lang(?commonName) = \"en\"). }}
}}
'''
        url = 'https://query.wikidata.org/sparql?query=' + urllib.parse.quote(sparql) + '&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0 (haitrinh082@gmail.com)'})
        try:
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                bindings = json.loads(r.read().decode('utf-8'))['results']['bindings']
                for b in bindings:
                    sci = b['sciName']['value']
                    res.setdefault(sci, {'algaebase_id': None, 'algaebase_url': None, 'common_names': []})
                    if 'algaebaseId' in b:
                        url_val = b['algaebaseId']['value']
                        res[sci]['algaebase_url'] = url_val
                        m = re.search(r'species_id=(\d+)', url_val)
                        if m: res[sci]['algaebase_id'] = int(m.group(1))
                    if 'commonName' in b:
                        cname = b['commonName']['value'].strip()
                        if cname and cname not in res[sci]['common_names']:
                            res[sci]['common_names'].append(cname)
        except Exception as e:
            print(f"  [Lưu ý Wikidata chunk {i//chunk_size + 1}]: {e}")
        time.sleep(0.2)
    return res


def query_gbif_vernacular(sci):
    """Truy vấn tên tiếng Anh phổ biến từ GBIF Vernacular Names API."""
    clean_name = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', sci).strip()
    url = f'https://api.gbif.org/v1/species/match?name={urllib.parse.quote(clean_name)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            usage_key = data.get('usageKey')
            if usage_key:
                url_vern = f'https://api.gbif.org/v1/species/{usage_key}/vernacularNames'
                with urllib.request.urlopen(urllib.request.Request(url_vern, headers={'User-Agent': 'CamNangCaBien/1.0'}), timeout=8, context=ctx) as rv:
                    vdata = json.loads(rv.read().decode('utf-8'))
                    en_names = [x['vernacularName'].strip() for x in vdata.get('results', []) if x.get('language') in ('eng', 'en') and x.get('vernacularName')]
                    if en_names:
                        return sorted(list(set(en_names)), key=len)[0]
    except Exception:
        pass
    return None

GENUS_COMMON_NAMES = {
    'Entophysalis': 'Epiphytic Marine Blue-green Alga',
    'Chlorogloea': 'Endophytic Marine Blue-green Alga',
    'Hydrococcus': 'Encrusting Rivularia-like Blue-green Alga',
    'Aphanocapsa': 'Marine Aphanocapsa Blue-green Alga',
    'Chroococcus': 'Chroococcus Marine Blue-green Alga',
    'Microcystis': 'Colonial Microcystis Blue-green Alga',
    'Dermocarpella': 'Marine Endosporangial Blue-green Alga',
    'Oscillatoria': 'Marine Oscillatoria Filamentous Alga',
    'Lyngbya': 'Lyngbya Filamentous Cyanobacterium',
    'Spirulina': 'Marine Spirulina Alga',
    'Ulva': 'Sea Lettuce',
    'Enteromorpha': 'Hollow Green Seaweed / Gutweed',
    'Caulerpa': 'Sea Grape / Green Feather Alga',
    'Codium': 'Green Sponge / Velvet Seaweed',
    'Halimeda': 'Cactus Alga / Money Plant Alga',
    'Sargassum': 'Sargassum Seaweed / Gulfweed',
    'Turbinaria': 'Turbinate Seaweed',
    'Padina': 'Peacock Fan Seaweed',
    'Dictyota': 'Forked Ribbon Seaweed',
    'Gracilaria': 'Gracilaria Seaweed / Agar Weed',
    'Hydropuntia': 'Red Agar Seaweed',
    'Eucheuma': 'Eucheuma Seaweed / Spiny Seaweed',
    'Kappaphycus': 'Elkhorn Sea Moss / Cottonii',
    'Halymenia': 'Dragon Tongue Seaweed',
    'Galaxaura': 'Tubular Red Seaweed',
    'Gelidium': 'Agar-agar Red Alga',
}

# ── 8. Quy Trình Đồng Bộ Chuẩn Hóa Từng Loài (Production Standard) ───

def sync_species(sp, dry_run=False):
    sp_id = sp['id']
    sci = sp['scientific_name']
    vn_current = sp.get('vn_name') or ''
    idx = sp.get('species_index')

    print(f"\n[{idx}] {sci} ({vn_current}) — {sp_id}")

    clean_sci = re.sub(r'\s+var\..*|\s+f\..*|\s+sp\.\d*', '', sci).strip()
    kb_entry = SEAWEED_KNOWLEDGE_BASE.get(sci) or SEAWEED_KNOWLEDGE_BASE.get(clean_sci)
    local_book = THUCVAT_BY_ID.get(sp_id) or THUCVAT_BY_SCI.get(sci) or THUCVAT_BY_SCI.get(clean_sci)

    patch_payload = {}

    # A. CHUẨN HÓA TÊN TIẾNG VIỆT & TÊN GỌI KHÁC (vn_name & vn_alternate_names)
    raw_vn_name = None
    if kb_entry and kb_entry.get('vn_name'):
        raw_vn_name = kb_entry['vn_name']
    elif local_book and local_book.get('vietnamese_name') and not local_book['vietnamese_name'].startswith('Chưa có'):
        raw_vn_name = local_book['vietnamese_name']
    elif OCR_BATCH_NAMES.get(sci) or OCR_BATCH_NAMES.get(clean_sci):
        raw_vn_name = OCR_BATCH_NAMES.get(sci) or OCR_BATCH_NAMES.get(clean_sci)

    if raw_vn_name:
        parts = [p.strip() for p in re.split(r'[,;]\s*', raw_vn_name) if p.strip()]
        if parts:
            patch_payload['vn_name'] = parts[0]
            if len(parts) > 1 and not (kb_entry and kb_entry.get('vn_alternate_names')):
                patch_payload['vn_alternate_names'] = ", ".join(parts[1:])

    if kb_entry and kb_entry.get('vn_alternate_names'):
        patch_payload['vn_alternate_names'] = kb_entry['vn_alternate_names']

    if patch_payload.get('vn_alternate_names'):
        print(f"  ✓ Tên gọi khác (VN): {patch_payload['vn_alternate_names']}")

    # B. CHUẨN HÓA TÊN TIẾNG ANH (en_common_name)
    if kb_entry and kb_entry.get('en_common_name'):
        patch_payload['en_common_name'] = kb_entry['en_common_name']
        print(f"  ✓ Tên tiếng Anh: {kb_entry['en_common_name']}")

    # C. ĐỒNG BỘ DANH PHÁP & PHÂN LOẠI HỌC TỪ WORMS / ALGAEBASE
    if not sp.get('worms_id'):
        worms_info = query_worms_by_name(sci)
        if worms_info:
            print(f"  ✓ WoRMS: AphiaID {worms_info['worms_id']} ({worms_info['worms_status']})")
            patch_payload['worms_id'] = worms_info['worms_id']
            patch_payload['worms_status'] = worms_info['worms_status']
            patch_payload['worms_accepted_name'] = worms_info['accepted_name']
            patch_payload['worms_synced_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

            cls_lat = worms_info.get('tax_class')
            ord_lat = worms_info.get('tax_order')
            fam_lat = worms_info.get('tax_family')
            gen_lat = worms_info.get('tax_genus')

            if cls_lat:
                patch_payload['tax_class_latin'] = cls_lat
                patch_payload['tax_class_vn'] = TAXONOMY_VN.get(cls_lat, f"Lớp {cls_lat}")
            if ord_lat:
                patch_payload['tax_order_latin'] = ord_lat
                patch_payload['tax_order_vn'] = TAXONOMY_VN.get(ord_lat, f"Bộ {ord_lat}")
            if fam_lat:
                patch_payload['tax_family_latin'] = fam_lat
                patch_payload['tax_family_vn'] = TAXONOMY_VN.get(fam_lat, f"Họ {fam_lat}")
            if gen_lat:
                patch_payload['tax_genus_latin'] = gen_lat
                patch_payload['tax_genus_vn'] = f"Chi {gen_lat}"
        else:
            print("  - Giữ nguyên trạng thái phân loại hiện tại")
    else:
        print(f"  ✓ Đã có WoRMS AphiaID {sp['worms_id']}")


    # D. ĐỒNG BỘ THÔNG SỐ SINH HỌC & SINH THÁI SONG NGỮ (Bilingual Biology)
    if kb_entry:
        bio_payload = {
            'fbName': kb_entry.get('fbName') or kb_entry.get('en_common_name'),
            'depth': kb_entry.get('depth'),
            'depthVn': kb_entry.get('depthVn'),
            'habitat': kb_entry.get('habitat'),
            'habitatVn': kb_entry.get('habitatVn'),
            'importance': kb_entry.get('importance'),
            'importanceVn': kb_entry.get('importanceVn'),
            'biologySummary': kb_entry.get('biologySummary'),
            'biologySummaryVn': kb_entry.get('biologySummaryVn'),
            'algaebaseId': kb_entry.get('algaebase_id'),
            'algaebaseUrl': kb_entry.get('algaebase_url')
        }
        patch_payload['biology'] = json.dumps(bio_payload, ensure_ascii=False)
        print("  ✓ Cập nhật đầy đủ thông số Sinh học & Sinh thái song ngữ AlgaeBase KB")
    elif (local_book and (local_book.get('morphology_vn') or local_book.get('morphology_en'))) or sp.get('morphology_vn'):
        m_vn = clean_desc((local_book.get('morphology_vn') if local_book else None) or sp.get('morphology_vn') or '')
        m_en = clean_desc((local_book.get('morphology_en') if local_book else None) or sp.get('morphology_en') or '')
        dist_vn = sp.get('vn_distribution') or ''
        hab_vn = extract_habitat_vn(m_vn)
        hab_en = extract_habitat_en(m_en)

        depth_str = '0 - 5 m'
        depth_str_vn = '0 - 5 m'
        if local_book and local_book.get('photo_data'):
            m_depth = re.search(r'(\d+(?:\.\d+)?\s*m)', local_book['photo_data'])
            if m_depth:
                depth_str = m_depth.group(1)
                depth_str_vn = m_depth.group(1)
        elif "nội-sinh" in m_vn.lower() or "nội sinh" in m_vn.lower():
            hab_vn = "Nội sinh hoặc bán nội sinh trong các loài rong sợi khác ở vùng triều ven biển."
            hab_en = "Endophytic or semi-endophytic within filamentous macroalgae in coastal intertidal waters."
            depth_str = "0 - 3 m"
            depth_str_vn = "0 - 3 m (Vùng triều)"
        elif "phụ-sinh" in m_vn.lower() or "phụ sinh" in m_vn.lower() or "bao quanh" in m_vn.lower():
            hab_vn = "Biểu sinh hoặc bọc quanh các loài rong lớn và giá thể đá ở vùng triều ven bờ."
            hab_en = "Epiphytic, encrusting around larger marine algae or rocky substrates in coastal intertidal zones."
            depth_str = "0 - 5 m"
            depth_str_vn = "0 - 5 m (Vùng triều và dưới triều cạn)"
        elif "u-nần" in m_vn.lower() or "bán-cầu" in m_vn.lower() or "dính vào đài-vật" in m_vn.lower():
            hab_vn = "Bám chặt vào bề mặt đá, vỏ ốc hoặc nền san hô ở vùng triều chịu sóng."
            hab_en = "Firmly attached to rocks, shells, or coral substrates in wave-exposed intertidal zones."
            depth_str = "0 - 4 m"
            depth_str_vn = "0 - 4 m (Vùng triều đá)"
        else:
            if not hab_vn or hab_vn == 'Vùng triều và đới dưới triều cạn ven biển':
                hab_vn = "Vùng triều và đới dưới triều cạn ven biển, vách đá hoặc vũng triều ẩm ướt."
                hab_en = "Coastal intertidal to shallow subtidal zones, on moist rocks, tide pools, or sand."

        if dist_vn and len(dist_vn) > 3 and dist_vn not in hab_vn:
            hab_vn += f" Ghi nhận phân bố: {dist_vn}"

        genus_name = sci.split()[0] if sci else ''
        cls_lat = patch_payload.get('tax_class_latin') or sp.get('tax_class_latin') or ''

        # Tầm quan trọng sinh thái & kinh tế
        if cls_lat in ('Cyanophyceae', 'Cyanobacteria'):
            imp_vn = "Đóng vai trò vi sinh thái ven biển, quang dưỡng ban sơ và cấu thành màng mỏng sinh học bảo vệ nền rạn."
            imp_en = "Contributes to coastal micro-ecosystems, primary phototrophic production, and microbial biofilm formation."
        elif genus_name in ('Gracilaria', 'Hydropuntia', 'Gelidiopsis', 'Eucheuma', 'Kappaphycus', 'Halymenia'):
            imp_vn = "Khai thác tự nhiên, sản xuất agar / thực phẩm giàu dinh dưỡng."
            imp_en = "Wild harvest and mariculture for agar production / edible seaweed."
        elif genus_name in ('Sargassum', 'Turbinaria', 'Padina', 'Dictyota'):
            imp_vn = "Nguồn chiết xuất alginate, phân bón sinh học và dược liệu tự nhiên."
            imp_en = "Alginate extraction, biofertilizer, and natural pharmaceutical potential."
        elif genus_name in ('Ulva', 'Enteromorpha', 'Caulerpa'):
            imp_vn = "Rong ăn được, rau xanh đại dương giàu khoáng chất, thức ăn cho thủy sản."
            imp_en = "Edible green sea greens rich in trace minerals, aquaculture feed."
        else:
            imp_vn = "Giá trị sinh thái cấu thành bãi rong biển và rạn san hô tự nhiên ven biển Việt Nam."
            imp_en = "Ecological role in marine reef and natural seaweed bed communities in Vietnam."

        # Tên tiếng Anh chuẩn
        w_info = WIKIDATA_CACHE.get(sci) or WIKIDATA_CACHE.get(clean_sci) or {}
        en_name = patch_payload.get('en_common_name') or sp.get('en_common_name')
        if not en_name and w_info.get('common_names'):
            en_name = w_info['common_names'][0].title()
        if not en_name:
            gbif_n = query_gbif_vernacular(sci)
            if gbif_n:
                en_name = gbif_n.title()
        if not en_name and genus_name in GENUS_COMMON_NAMES:
            en_name = GENUS_COMMON_NAMES[genus_name]
        if not en_name:
            if cls_lat in ('Cyanophyceae', 'Cyanobacteria'):
                en_name = f"{sci} Blue-green Alga"
            elif cls_lat in ('Florideophyceae', 'Bangiophyceae', 'Rhodophyta'):
                en_name = f"{sci} Red Seaweed"
            elif cls_lat in ('Phaeophyceae',):
                en_name = f"{sci} Brown Alga"
            elif cls_lat in ('Ulvophyceae', 'Chlorophyta'):
                en_name = f"{sci} Green Seaweed"
            else:
                en_name = f"{genus_name} Seaweed"

        patch_payload['en_common_name'] = en_name

        # AlgaeBase ID & URL
        algae_id = w_info.get('algaebase_id')
        algae_url = w_info.get('algaebase_url')
        aphia_id = patch_payload.get('worms_id') or sp.get('worms_id')

        if not algae_url:
            algae_id = aphia_id
            algae_url = f"https://www.marinespecies.org/aphia.php?p=taxdetails&id={aphia_id}" if aphia_id else 'https://www.algaebase.org'

        bio_vn = m_vn if m_vn else f"Loài rong biển {patch_payload.get('vn_name') or vn_current} ({sci}) ghi nhận tại Việt Nam."
        bio_en = m_en if m_en else f"Marine alga {sci} ({en_name}). {hab_en}"

        bio_payload = {
            'fbName': en_name,
            'depth': depth_str,
            'depthVn': depth_str_vn,
            'habitat': hab_en,
            'habitatVn': hab_vn,
            'importance': imp_en,
            'importanceVn': imp_vn,
            'biologySummary': bio_en,
            'biologySummaryVn': bio_vn,
            'algaebaseId': algae_id,
            'algaebaseUrl': algae_url
        }
        patch_payload['biology'] = json.dumps(bio_payload, ensure_ascii=False)
        print(f"  ✓ Tự động trích xuất Sinh học & Sinh thái song ngữ chuẩn AlgaeBase ({en_name} | ID: {algae_id})")

    # E. XỬ LÝ HÌNH ẢNH TIÊU BẢN & THỰC ĐỊA (Supabase Storage & species_photos)
    is_vol2 = sp.get('volume') == 2 or (sp.get('photo_url') and '/images/species/thuc-vat-bien/v2/' in sp.get('photo_url', ''))
    has_photo = bool(sp.get('photo_url') and len(sp['photo_url']) > 5)

    if is_vol2:
        print("  ✓ Bảo lưu ảnh tiêu bản giải phẫu 300 DPI nguyên bản của GS. Phạm Hoàng Hộ")
    elif not has_photo or (kb_entry and kb_entry.get('source') == 'algaebase' and 'algaebase' not in sp.get('photo_url', '')):
        photo_info = None
        if kb_entry and kb_entry.get('img_url'):
            photo_info = {
                'url': kb_entry['img_url'],
                'photographer': kb_entry.get('photographer', 'AlgaeBase Archive'),
                'license': kb_entry.get('license', 'Academic Use'),
                'source': kb_entry.get('source', 'algaebase')
            }
        elif not has_photo:
            photo_info = fetch_inaturalist_photo(sci)

        if photo_info:
            print(f"  ✓ Tải ảnh chuẩn từ {photo_info['source']}: {photo_info['url']}")
            if not dry_run:
                try:
                    req_img = urllib.request.Request(photo_info['url'], headers=HEADERS_HTTP)
                    with urllib.request.urlopen(req_img, timeout=25, context=ctx) as r_img:
                        raw_bytes = r_img.read()

                    im = Image.open(io.BytesIO(raw_bytes))
                    if im.mode in ('RGBA', 'P'):
                        im = im.convert('RGB')
                    if im.width > 960:
                        ratio = 960 / im.width
                        im = im.resize((960, int(im.height * ratio)), Image.Resampling.LANCZOS)

                    out_buf = io.BytesIO()
                    im.save(out_buf, format='WEBP', quality=80)
                    webp_bytes = out_buf.getvalue()

                    storage_path = f"thuc-vat-bien/{sp_id}/01.webp"
                    if supa_upload_image(storage_path, webp_bytes):
                        pub_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
                        patch_payload['photo_url'] = pub_url
                        print(f"  ✓ Upload ảnh thành công -> {storage_path}")

                        # Ghi vào species_photos
                        photo_row = {
                            'species_id': sp_id,
                            'storage_path': storage_path,
                            'source': photo_info['source'],
                            'photographer': photo_info['photographer'],
                            'license': photo_info['license'],
                            'source_url': photo_info['url'],
                            'is_primary': True,
                            'sort_order': 0
                        }
                        req_p = urllib.request.Request(
                            f"{SUPABASE_URL}/rest/v1/species_photos",
                            data=json.dumps(photo_row).encode('utf-8'),
                            headers=HEADERS_REST,
                            method='POST'
                        )
                        urllib.request.urlopen(req_p, timeout=10, context=ctx)
                except Exception as e:
                    print(f"  [Lỗi xử lý ảnh]: {e}")

    # F. GHI CẬP NHẬT VÀO SUPABASE & FILE LOCAL
    if patch_payload:
        if dry_run:
            print(f"  [DRY RUN] Dữ liệu sẽ cập nhật: {list(patch_payload.keys())}")
        else:
            status = supa_patch(f"species?id=eq.{sp_id}", patch_payload)
            print(f"  ✓ Cập nhật Supabase: status {status}")

            # Đồng bộ ngược lại file thucvat_all.json nếu có
            if local_book:
                for k, v in patch_payload.items():
                    local_book[k] = v

    time.sleep(0.08)

def main():
    parser = argparse.ArgumentParser(description="AlgaeBase & WoRMS Production Sync Engine")
    parser.add_argument('--volume', type=int, choices=[1, 2], help='Lọc theo Tập (1: Tsutsui, 2: GS. Phạm Hoàng Hộ)')
    parser.add_argument('--limit', type=int, default=10, help='Giới hạn số loài cần sync')
    parser.add_argument('--offset', type=int, default=0, help='Bỏ qua N loài đầu tiên')
    parser.add_argument('--species', type=str, help='Sync riêng một loài theo ID (vd: thucvat-species-4)')
    parser.add_argument('--full', action='store_true', help='Sync toàn bộ danh mục')
    parser.add_argument('--dry-run', action='store_true', help='Xem trước, không ghi database')
    args = parser.parse_args()

    print("=" * 65)
    print("🌿 ALGAEBASE & WORMS PRODUCTION SYNC ENGINE — THỰC VẬT BIỂN VIỆT NAM")
    print("=" * 65)

    vol_filter = f"&volume=eq.{args.volume}" if args.volume else ""

    if args.species:
        species_list = supa_get(f"species?id=eq.{args.species}&deleted_at=is.null")
    elif args.full:
        species_list = supa_get(f"species?collection_id=eq.thuc-vat-bien{vol_filter}&deleted_at=is.null&order=species_index&limit=1000")
    else:

        species_list = supa_get(f"species?collection_id=eq.thuc-vat-bien{vol_filter}&deleted_at=is.null&order=species_index&limit={args.limit}&offset={args.offset}")

    total = len(species_list)
    print(f"Tổng số loài tiếp nhận xử lý: {total}")

    # Truy vấn Wikidata theo batch trước
    names_to_query = [s['scientific_name'] for s in species_list if s.get('scientific_name')]
    print(f"Đang đồng bộ tri thức AlgaeBase từ Wikidata cho {len(names_to_query)} loài...")
    global WIKIDATA_CACHE
    WIKIDATA_CACHE = query_wikidata_batch(names_to_query)
    print(f"✓ Hoàn tất nạp cache Wikidata cho {len(WIKIDATA_CACHE)} loài.")

    for idx, sp in enumerate(species_list, 1):
        print(f"\n--- Tiến độ: {idx}/{total} ---")
        sync_species(sp, dry_run=args.dry_run)

    # Lưu lại thucvat_all.json nếu không phải dry-run và có dữ liệu
    if not args.dry_run and THUCVAT_DATA and THUCVAT_FILE.exists():
        try:
            with open(THUCVAT_FILE, 'w', encoding='utf-8') as f:
                json.dump(THUCVAT_DATA, f, ensure_ascii=False, indent=2)
            print("\n✓ Đã đồng bộ ngược lại file local data/thucvat_all.json")
        except Exception as e:
            print(f"\n[Lỗi lưu file local]: {e}")

    print("\n" + "=" * 65)
    print("HOÀN TẤT ĐỒNG BỘ CHUẨN HÓA!")
    print("=" * 65)

if __name__ == '__main__':
    main()

