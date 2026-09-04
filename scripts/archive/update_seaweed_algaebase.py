"""
Update 3 seaweed species from AlgaeBase:
1. thucvat-species-1: Gracilaria textorii (Rau Câu dẹt)
2. thucvat-species-2: Gracilaria arcuata (Rau Câu cong)
3. thucvat-species-3: Gracilaria eucheumatoides (Rau Câu chân vịt)

Downloads authentic AlgaeBase specimen images, converts to WebP,
uploads to Supabase Storage (species-photos/thuc-vat-bien/...),
inserts records into species_photos, and enriches species table.
"""

import io
import json
import os
import ssl
import sys
import urllib.request
import uuid
from PIL import Image

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Load env
env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k.strip()] = v.strip('\"\'')

url = env['NEXT_PUBLIC_SUPABASE_URL']
key = env.get('SUPABASE_SERVICE_ROLE_KEY') or env['NEXT_PUBLIC_SUPABASE_ANON_KEY']
bucket = 'species-photos'

headers_rest = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS_HTTP = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.algaebase.org/'
}

SPECIES_DATA = [
    {
        'id': 'thucvat-species-1',
        'sci_name': 'Gracilaria textorii',
        'vn_name': 'Rau Câu dẹt',
        'vn_alternate_names': 'Rau Câu bản dẹt, Rau Câu phiến',
        'en_common_name': 'Flat Gracilaria / Textor Gracilaria',
        'algaebase_id': 1934,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1934',
        'img_url': 'https://img.algaebase.org/images/3EE735B10772e02B67Tuk30BC816/NJitqKRvULyj.jpg',
        'photographer': 'Chiba University / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'taxonomy': {
            'class_vn': 'Lớp Rong Đỏ',
            'class_lat': 'Florideophyceae',
            'order_vn': 'Bộ Rau Câu',
            'order_lat': 'Gracilariales',
            'family_vn': 'Họ Rau Câu',
            'family_lat': 'Gracilariaceae',
            'genus_vn': 'Chi Rau Câu Gracilaria',
            'genus_lat': 'Gracilaria'
        },
        'bio': {
            'fbName': 'Flat Gracilaria',
            'habitat': 'Đới dưới triều nông (Subtidal), bám đá hoặc rạn san hô',
            'depth': '0 - 15 m',
            'importance': 'Chế biến thực phẩm, nguồn chiết xuất Agar-agar chất lượng cao',
            'distribution': 'Việt Nam (Khánh Hòa, Bình Thuận, Côn Đảo), Nhật Bản, Hàn Quốc, Tây Thái Bình Dương',
            'biologySummary': 'Tản rong dạng phiến dẹt mỏng như dải lụa, phân nhánh lưỡng phân hoặc dạng ngón tay, mép phiến nguyên hoặc có răng nhỏ. Màu sắc đỏ sẫm đến lục nâu. Là nguồn nguyên liệu chiết xuất Agar tự nhiên quý giá.'
        }
    },
    {
        'id': 'thucvat-species-2',
        'sci_name': 'Gracilaria arcuata',
        'vn_name': 'Rau Câu cong',
        'vn_alternate_names': 'Rau Câu cánh cung, Rau Câu cong Phú Quốc',
        'en_common_name': 'Arcuate Gracilaria',
        'algaebase_id': 1690,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1690',
        'img_url': 'https://img.algaebase.org/images/8CCBD7A40f62320D11qKl34BE02E/kRu1fBE88qVi.jpg',
        'photographer': 'Phu Quoc Island (Vietnam) Specimen / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'taxonomy': {
            'class_vn': 'Lớp Rong Đỏ',
            'class_lat': 'Florideophyceae',
            'order_vn': 'Bộ Rau Câu',
            'order_lat': 'Gracilariales',
            'family_vn': 'Họ Rau Câu',
            'family_lat': 'Gracilariaceae',
            'genus_vn': 'Chi Rau Câu Gracilaria',
            'genus_lat': 'Gracilaria'
        },
        'bio': {
            'fbName': 'Arcuate Gracilaria',
            'habitat': 'Vùng triều thấp và đới dưới triều nông (Upper subtidal zone)',
            'depth': '0.5 - 5 m',
            'importance': 'Khai thác tự nhiên, nguồn chế biến thạch và agar',
            'distribution': 'Việt Nam (Đảo Phú Quốc, Vịnh Nha Trang, Ninh Thuận), Biển Đỏ, Ấn Độ Dương, Tây Thái Bình Dương',
            'biologySummary': 'Tản rong mập mạp hình trụ tròn, các cành nhánh uốn cong queo đặc trưng hình cánh cung (arcuata). Mọc bám trên rạn đá san hô cạn và vũng triều ven các đảo lớn phía Nam Việt Nam.'
        }
    },
    {
        'id': 'thucvat-species-3',
        'sci_name': 'Gracilaria eucheumatoides',
        'vn_name': 'Rau Câu chân vịt',
        'vn_alternate_names': 'Rau Câu sụn, Rau Câu màng',
        'en_common_name': 'Eucheuma-like Gracilaria',
        'algaebase_id': 1900,
        'algaebase_url': 'https://www.algaebase.org/search/species/detail/?species_id=1900',
        'img_url': 'https://img.algaebase.org/images/A4A110171926405753Ogi3A5A553/f6kqX3q9qyAd.jpg',
        'photographer': 'Hideki Yukihira / AlgaeBase',
        'license': 'AlgaeBase / Academic & Research Use',
        'taxonomy': {
            'class_vn': 'Lớp Rong Đỏ',
            'class_lat': 'Florideophyceae',
            'order_vn': 'Bộ Rau Câu',
            'order_lat': 'Gracilariales',
            'family_vn': 'Họ Rau Câu',
            'family_lat': 'Gracilariaceae',
            'genus_vn': 'Chi Rau Câu Gracilaria',
            'genus_lat': 'Gracilaria'
        },
        'bio': {
            'fbName': 'Eucheuma-like Gracilaria',
            'habitat': 'Bám chặt trên bề mặt đá hoặc san hô chết vùng sóng mạnh (Reef crest)',
            'depth': '0 - 3 m',
            'importance': 'Đặc sản ẩm thực (chè rau câu chân vịt Lý Sơn, gỏi rong sụn), giàu khoáng chất',
            'distribution': 'Việt Nam (Đảo Lý Sơn - Quảng Ngãi, Khánh Hòa, Ninh Thuận, Côn Đảo), Nhật Bản, Tây Thái Bình Dương',
            'biologySummary': 'Tản rong có chất sụn dày và cứng, màu đỏ lục sẫm, phân nhánh bất quy tắc với các nhánh dẹt rộng xòe ra như ngón chân vịt. Mặt dưới có nhiều giác bám giúp rong dính chặt vào đá san hô trước lực sóng đập dữ dội.'
        }
    }
]

def upload_supabase_storage(storage_path, img_bytes):
    storage_url = f'{url}/storage/v1/object/{bucket}/{storage_path}'
    req = urllib.request.Request(
        storage_url,
        data=img_bytes,
        headers={
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'image/webp',
            'x-upsert': 'true'
        },
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status == 200

for item in SPECIES_DATA:
    sp_id = item['id']
    sci = item['sci_name']
    vn = item['vn_name']
    print(f'\n--- Dang xu ly {sp_id}: {sci} ({vn}) ---')

    img_u = item['img_url']
    print(f'  1. Dang tai anh tu AlgaeBase: {img_u}')
    req = urllib.request.Request(img_u, headers=HEADERS_HTTP)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        raw_bytes = r.read()
    
    # 2. Convert to optimized WebP
    im = Image.open(io.BytesIO(raw_bytes))
    if im.mode in ('RGBA', 'P'):
        im = im.convert('RGB')
    
    # Resize max width 960 if larger
    if im.width > 960:
        ratio = 960 / im.width
        im = im.resize((960, int(im.height * ratio)), Image.Resampling.LANCZOS)
    
    out_buf = io.BytesIO()
    im.save(out_buf, format='WEBP', quality=82)
    webp_bytes = out_buf.getvalue()
    print(f'  2. Chuyen doi WebP thanh cong: {len(webp_bytes)} bytes')

    # 3. Upload to Supabase Storage
    storage_path = f'thuc-vat-bien/{sp_id}/01.webp'
    ok = upload_supabase_storage(storage_path, webp_bytes)
    print(f'  3. Upload len Supabase Storage: {ok} ({storage_path})')

    public_img_url = f'{url}/storage/v1/object/public/{bucket}/{storage_path}'

    # 4. Insert / Upsert into species_photos table
    # First delete existing photos for this species if any
    del_req = urllib.request.Request(
        f'{url}/rest/v1/species_photos?species_id=eq.{sp_id}',
        headers=headers_rest,
        method='DELETE'
    )
    try:
        urllib.request.urlopen(del_req)
    except:
        pass

    photo_row = {
        'species_id': sp_id,
        'storage_path': storage_path,
        'source': 'algaebase',
        'photographer': item['photographer'],
        'license': item['license'],
        'source_url': item['algaebase_url'],
        'is_primary': True,
        'sort_order': 0
    }
    insert_photo_req = urllib.request.Request(
        f'{url}/rest/v1/species_photos',
        data=json.dumps(photo_row).encode('utf-8'),
        headers=headers_rest,
        method='POST'
    )
    with urllib.request.urlopen(insert_photo_req) as resp:
        print(f'  4. Ghi ban ghi species_photos thanh cong: status {resp.status}')

    # 5. Patch species table
    species_patch = {
        'vn_name': item['vn_name'],
        'vn_alternate_names': item['vn_alternate_names'],
        'en_common_name': item['en_common_name'],
        'photo_url': public_img_url,
        'tax_class_vn': item['taxonomy']['class_vn'],
        'tax_class_latin': item['taxonomy']['class_lat'],
        'tax_order_vn': item['taxonomy']['order_vn'],
        'tax_order_latin': item['taxonomy']['order_lat'],
        'tax_family_vn': item['taxonomy']['family_vn'],
        'tax_family_latin': item['taxonomy']['family_lat'],
        'tax_genus_vn': item['taxonomy']['genus_vn'],
        'tax_genus_latin': item['taxonomy']['genus_lat'],
        'biology': json.dumps(item['bio'], ensure_ascii=False)
    }
    patch_req = urllib.request.Request(
        f'{url}/rest/v1/species?id=eq.{sp_id}',
        data=json.dumps(species_patch).encode('utf-8'),
        headers=headers_rest,
        method='PATCH'
    )
    with urllib.request.urlopen(patch_req) as resp:
        print(f'  5. Cap nhat species table thanh cong: status {resp.status}')

print('\n======================================================')
print('HOAN TAT 100%! Da cap nhat 3 loai Rong bien tu AlgaeBase.')
