"""
Sync complete taxonomy for Volume VI (Atlas cá rạn san hô) to Supabase.
Enriches Class, Order, Family, Genus (both VN and Latin) for all 263 species.
"""

import json
import os
import sys
import urllib.request

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
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# 2. Load species and worms cache
with open('scratch/tap6_species_current.json', 'r', encoding='utf-8') as f:
    species_list = json.load(f)

with open('scratch/tap6_worms_cache.json', 'r', encoding='utf-8') as f:
    worms_cache = json.load(f)

FAM_DICT = {
    'acanthuridae': ('Họ Cá Đuôi Gai', 'Bộ Cá Đuôi Gai', 'Acanthuriformes', 'Cá Đuôi Gai'),
    'apogonidae': ('Họ Cá Sơn', 'Bộ Cá Sơn', 'Apogoniformes', 'Cá Sơn'),
    'balistidae': ('Họ Cá Bò', 'Bộ Cá Nóc', 'Tetraodontiformes', 'Cá Bò'),
    'caesionidae': ('Họ Cá Miền', 'Bộ Cá Vược', 'Perciformes', 'Cá Miền'),
    'carangidae': ('Họ Cá Khế', 'Bộ Cá Khế', 'Carangiformes', 'Cá Khế'),
    'chaetodontidae': ('Họ Cá Bướm', 'Bộ Cá Vược', 'Perciformes', 'Cá Bướm'),
    'cirrhitidae': ('Họ Cá Mào', 'Bộ Cá Vược', 'Perciformes', 'Cá Mào'),
    'ephippidae': ('Họ Cá Tai Bàng', 'Bộ Cá Vược', 'Perciformes', 'Cá Tai Bàng'),
    'epinephelidae': ('Họ Cá Mú', 'Bộ Cá Vược', 'Perciformes', 'Cá Mú'),
    'gobiidae': ('Họ Cá Bống Trắng', 'Bộ Cá Bống', 'Gobiiformes', 'Cá Bống'),
    'haemulidae': ('Họ Cá Sộp', 'Bộ Cá Vược', 'Perciformes', 'Cá Sộp'),
    'hemiramphidae': ('Họ Cá Kìm', 'Bộ Cá Nhái', 'Beloniformes', 'Cá Kìm'),
    'holocentridae': ('Họ Cá Sơn Đá', 'Bộ Cá Sơn Đá', 'Holocentriformes', 'Cá Sơn Đá'),
    'kyphosidae': ('Họ Cá Rầm', 'Bộ Cá Vược', 'Perciformes', 'Cá Rầm'),
    'labridae': ('Họ Cá Bàng Chài', 'Bộ Cá Vược', 'Perciformes', 'Cá Bàng Chài'),
    'lethrinidae': ('Họ Cá Hè', 'Bộ Cá Vược', 'Perciformes', 'Cá Hè'),
    'liopropomatidae': ('Họ Cá Mú Liopropoma', 'Bộ Cá Vược', 'Perciformes', 'Cá Mú'),
    'lutjanidae': ('Họ Cá Hồng', 'Bộ Cá Vược', 'Perciformes', 'Cá Hồng'),
    'monacanthidae': ('Họ Cá Bò Giấy', 'Bộ Cá Nóc', 'Tetraodontiformes', 'Cá Bò Giấy'),
    'mullidae': ('Họ Cá Phèn', 'Bộ Cá Phèn', 'Mulliformes', 'Cá Phèn'),
    'muraenidae': ('Họ Cá Lịch Biển', 'Bộ Cá Chình', 'Anguilliformes', 'Cá Lịch'),
    'nemipteridae': ('Họ Cá Lượng', 'Bộ Cá Vược', 'Perciformes', 'Cá Lượng'),
    'ostraciidae': ('Họ Cá Hòm', 'Bộ Cá Nóc', 'Tetraodontiformes', 'Cá Hòm'),
    'pomacanthidae': ('Họ Cá Bướm Gai', 'Bộ Cá Vược', 'Perciformes', 'Cá Bướm Gai'),
    'pomacentridae': ('Họ Cá Thia', 'Bộ Cá Vược', 'Perciformes', 'Cá Thia'),
    'priacanthidae': ('Họ Cá Trao Tráo', 'Bộ Cá Vược', 'Perciformes', 'Cá Trao Tráo'),
    'pseudochromidae': ('Họ Cá Đạm Nham', 'Bộ Cá Vược', 'Perciformes', 'Cá Đạm Nham'),
    'scaridae': ('Họ Cá Mó', 'Bộ Cá Vược', 'Perciformes', 'Cá Mó'),
    'scorpaenidae': ('Họ Cá Mù Làn', 'Bộ Cá Mù Làn', 'Scorpaeniformes', 'Cá Mù Làn'),
    'siganidae': ('Họ Cá Dìa', 'Bộ Cá Đuôi Gai', 'Acanthuriformes', 'Cá Dìa'),
    'sphyraenidae': ('Họ Cá Nhồng', 'Bộ Cá Vược', 'Perciformes', 'Cá Nhồng'),
    'syngnathidae': ('Họ Cá Chìa Vôi', 'Bộ Cá Chìa Vôi', 'Syngnathiformes', 'Cá Chìa Vôi'),
    'synodontidae': ('Họ Cá Mối', 'Bộ Cá Mối', 'Aulopiformes', 'Cá Mối'),
    'tetraodontidae': ('Họ Cá Nóc', 'Bộ Cá Nóc', 'Tetraodontiformes', 'Cá Nóc'),
    'zanclidae': ('Họ Cá Ngựa Râu', 'Bộ Cá Vược', 'Perciformes', 'Cá Ngựa Râu'),
}

GENUS_VN_CUSTOM = {
    'amphiprion': 'Cá Hề (Cá Khoang Cổ)',
    'premnas': 'Cá Hề Má Gai',
    'chaetodon': 'Cá Bướm',
    'forcipiger': 'Cá Bướm Mũi Dài',
    'heniochus': 'Cá Bướm Cờ',
    'chelmon': 'Cá Bướm Mỏ Dài',
    'pomacanthus': 'Cá Bướm Gai (Thiên Nga)',
    'centropyge': 'Cá Bướm Gai Lùn',
    'epinephelus': 'Cá Mú (Cá Song)',
    'cephalopholis': 'Cá Mú Chấm',
    'chromis': 'Cá Thia Thoi',
    'dascyllus': 'Cá Thia Ba Sọc',
    'abudefduf': 'Cá Thia Sọc Đen',
    'chrysiptera': 'Cá Thia Xanh',
    'pomacentrus': 'Cá Thia Đá',
    'stephanolepis': 'Cá Bò Giấy',
    'canthigaster': 'Cá Nóc Chuột',
    'pterois': 'Cá Mao Tiên (Cá Sư Tử)',
    'dendrochirus': 'Cá Mao Tiên Ngắn',
    'echidna': 'Cá Lịch Hoa',
    'gymnothorax': 'Cá Lịch Biển',
}

print(f'Starting sync taxonomy for {len(species_list)} species of Volume VI...')
success_count = 0

for sp in species_list:
    aphia = str(sp.get('worms_id'))
    wrec = worms_cache.get(aphia, {})
    fam_lat = (wrec.get('family') or '').strip()
    fam_key = fam_lat.lower()
    gen_lat = (wrec.get('genus') or sp['scientific_name'].split()[0]).strip()

    if fam_key in FAM_DICT:
        fam_vn, ord_vn, ord_lat, group_vn = FAM_DICT[fam_key]
    else:
        fam_vn = f'Họ {fam_lat}'
        ord_vn = 'Bộ Cá Vược'
        ord_lat = 'Perciformes'
        group_vn = 'Cá'

    g_custom = GENUS_VN_CUSTOM.get(gen_lat.lower())
    if g_custom:
        gen_vn = f'Giống {g_custom} {gen_lat}'
    else:
        gen_vn = f'Giống {group_vn} {gen_lat}'

    payload = {
        'tax_class_vn': 'Lớp Cá Xương',
        'tax_class_latin': 'Osteichthyes',
        'tax_order_vn': ord_vn,
        'tax_order_latin': ord_lat,
        'tax_family_vn': fam_vn,
        'tax_family_latin': fam_lat,
        'tax_genus_vn': gen_vn,
        'tax_genus_latin': gen_lat,
    }

    patch_url = f"{url}/rest/v1/species?id=eq.{sp['id']}"
    req = urllib.request.Request(
        patch_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                success_count += 1
                if success_count % 50 == 0 or success_count == len(species_list):
                    print(f'  Updated {success_count}/{len(species_list)} species...')
    except Exception as e:
        print(f"Error updating {sp['id']}: {e}")

print(f'FINISHED! Successfully updated taxonomy for {success_count} / {len(species_list)} species in Supabase.')
