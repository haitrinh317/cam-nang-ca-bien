"""
Chuan hoa 19 loai Ca Duoi o Tap 1 (Lop Ca Sun):
Sua loi OCR mat dau sac tu 'Ca Duoi' thanh 'Ca Duoi' (Dasyatidae, Gymnuridae, Torpedinidae, Narkidae, Rajidae).
"""

import json
import sys
import urllib.request

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

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

CORRECTIONS = {
    # 10 loai Ca Duoi bong
    'tap1-species-65': {
        'vn_name': 'Cá Đuối bồng thân tròn',
        'vn_alternate_names': 'Cá Đuối bồng thân tròn, Cá Đuối'
    },
    'tap1-species-66': {
        'vn_name': 'Cá Đuối bồng chấm xanh',
        'vn_alternate_names': 'Cá Đuối bồng chấm xanh, Cá Đuối chấm xanh'
    },
    'tap1-species-67': {
        'vn_name': 'Cá Đuối bồng lồi',
        'vn_alternate_names': 'Cá Đuối bồng lồi'
    },
    'tap1-species-68': {
        'vn_name': 'Cá Đuối bồng Trung Hoa',
        'vn_alternate_names': 'Cá Đuối bồng Trung Hoa'
    },
    'tap1-species-69': {
        'vn_name': 'Cá Đuối bồng đuôi vằn',
        'vn_alternate_names': 'Cá Đuối bồng đuôi vằn, Cá Đuối bông đuôi vằn'
    },
    'tap1-species-70': {
        'vn_name': 'Cá Đuối bồng mõm tù',
        'vn_alternate_names': 'Cá Đuối bồng mõm tù'
    },
    'tap1-species-71': {
        'vn_name': 'Cá Đuối bồng đỏ',
        'vn_alternate_names': 'Cá Đuối bồng đỏ'
    },
    'tap1-species-72': {
        'vn_name': 'Cá Đuối bồng mõm nhọn',
        'vn_alternate_names': 'Cá Đuối bồng mõm nhọn'
    },
    'tap1-species-73': {
        'vn_name': 'Cá Đuối bồng Bleeker',
        'vn_alternate_names': 'Cá Đuối bồng Bleeker'
    },
    'tap1-species-77': {
        'vn_name': 'Cá Đuối bồng hoa trắng',
        'vn_alternate_names': 'Cá Đuối bồng hoa trắng'
    },

    # 9 loai Ca Duoi khac
    'tap1-species-64': {
        'vn_name': 'Cá Đuối quạt',
        'vn_alternate_names': 'Cá Đuối quạt, Cá Đuối'
    },
    'tap1-species-74': {
        'vn_name': 'Cá Đuối ngói',
        'vn_alternate_names': 'Cá Đuối ngói'
    },
    'tap1-species-75': {
        'vn_name': 'Cá Đuối mồi',
        'vn_alternate_names': 'Cá Đuối mồi, Cá Đuối mối'
    },
    'tap1-species-80': {
        'vn_name': 'Cá Đuối bướm Nhật Bản',
        'vn_alternate_names': 'Cá Đuối bướm Nhật Bản'
    },
    'tap1-species-81': {
        'vn_name': 'Cá Đuối bướm chấm trắng',
        'vn_alternate_names': 'Cá Đuối bướm chấm trắng'
    },
    'tap1-species-94': {
        'vn_name': 'Cá Đuối điện Bắc Bộ',
        'vn_alternate_names': 'Cá Đuối điện Bắc Bộ'
    },
    'tap1-species-97': {
        'vn_name': 'Cá Đuối điện nhiều chấm',
        'vn_alternate_names': 'Cá Đuối điện nhiều chấm, Cá Đuối điện chấm'
    },
    'tap1-species-98': {
        'vn_name': 'Cá Đuối điện chấm trắng',
        'vn_alternate_names': 'Cá Đuối điện chấm trắng'
    },
    'tap1-species-99': {
        'vn_name': 'Cá Đuối điện Nhật Bản',
        'vn_alternate_names': 'Cá Đuối điện Nhật Bản'
    },
}

print(f'Bat dau cap nhat {len(CORRECTIONS)} loai ca duoi vao Supabase...')
success = 0
for sp_id, payload in CORRECTIONS.items():
    patch_url = f'{url}/rest/v1/species?id=eq.{sp_id}'
    req = urllib.request.Request(
        patch_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                success += 1
                name_vn = payload['vn_name']
                print(f'  [OK] {sp_id} -> {name_vn}')
    except Exception as e:
        print(f'  [ERR] {sp_id}: {e}')

print(f'HOAN TAT! Da cap nhat thanh cong {success} / {len(CORRECTIONS)} loai.')
