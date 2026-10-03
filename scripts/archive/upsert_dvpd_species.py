#!/usr/bin/env python3
"""
upsert_dvpd_species.py
Nạp toàn diện 101 loài Động vật phù du (Copepoda) vào bảng species
và nạp metadata ảnh vào bảng species_photos trong Supabase.
"""

import os
import json
import uuid
import urllib.request
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

INPUT_JSON = 'scratch/dvpd_atlat_with_photos.json'

if not SUPABASE_URL or not SERVICE_KEY:
    print("[!] Thiếu biến môi trường SUPABASE")
    exit(1)

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates,return=representation'
}

def postgrest_upsert(table, records, chunk_size=25):
    endpoint = f"{SUPABASE_URL}/rest/v1/{table}"
    total = len(records)
    upserted = 0
    
    for i in range(0, total, chunk_size):
        chunk = records[i:i+chunk_size]
        data = json.dumps(chunk).encode('utf-8')
        req = urllib.request.Request(endpoint, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 201):
                    res = json.loads(resp.read().decode('utf-8'))
                    upserted += len(res)
                    print(f"  [+] Đã upsert {upserted}/{total} bản ghi vào bảng '{table}'")
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8')
            print(f"  [!] Lỗi HTTP {e.code} khi upsert vào '{table}': {err}")
            raise e
        except Exception as e:
            print(f"  [!] Lỗi: {e}")
            raise e
    return upserted

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[!] File {INPUT_JSON} chưa sẵn sàng!")
        exit(1)

    print(f"[*] Đang đọc dữ liệu từ {INPUT_JSON}...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    now_iso = datetime.now(timezone.utc).isoformat()
    species_rows = []
    photo_rows = []

    for sp in species_list:
        sp_id = sp['id']
        specimens_str = ', '.join(sp.get('specimens', []))
        
        # Biology JSONB metadata
        biology_data = {
            'subclass': 'Copepoda',
            'order': sp.get('taxonomy_order', 'Calanoida'),
            'family': sp.get('taxonomy_family', ''),
            'genus': sp.get('taxonomy_genus', ''),
            'specimens_vnmn': sp.get('specimens', []),
            'environmental_indicator': True if any(kw in sp.get('ecology_vn', '').lower() for kw in ['chỉ thị', 'nước trồi', 'biển khơi', 'nước mặn']) else False,
            'source_project': 'Viện Hải dương học (2016–2019)',
            'atlat_captions': sp.get('captions', [])
        }

        morph_desc = f"Đặc điểm hình thái và giải phẫu hiển vi xác định loài trên cơ sở tiêu bản mẫu vật {specimens_str if specimens_str else 'Viện Hải dương học'}. Tiêu bản chụp lát cắt vi thể độ nét cao."

        row = {
            'id': sp_id,
            'collection_id': 'dong-vat-phu-du',
            'volume': 1,
            'species_index': sp.get('species_index', 1),
            'scientific_name': sp['scientific_name'],
            'vn_name': sp['vn_name'], # Quy ước: dùng Danh pháp khoa học
            'authorship': sp.get('author_year', ''),
            'en_common_name': 'Marine Planktonic Copepod',
            'vn_alternate_names': '',
            'tax_class_latin': 'Hexanauplia',
            'tax_class_vn': 'Lớp Chân sáu ấu trùng (Phù du Chân mái chèo)',
            'tax_order_latin': sp.get('taxonomy_order', 'Calanoida'),
            'tax_order_vn': f"Bộ {sp.get('taxonomy_order', 'Calanoida')}",
            'tax_family_latin': sp.get('taxonomy_family', ''),
            'tax_family_vn': f"Họ {sp.get('taxonomy_family', '')}" if sp.get('taxonomy_family') else '',
            'tax_genus_latin': sp.get('taxonomy_genus', ''),
            'tax_genus_vn': f"Chi {sp.get('taxonomy_genus', '')}" if sp.get('taxonomy_genus') else '',
            'morphology_vn': morph_desc,
            'morphology_en': 'Microscopic diagnostic morphology and anatomical dissection illustrated from Institute of Oceanography museum specimens.',
            'ecology_vn': sp.get('ecology_vn', ''),
            'ecology_en': '',
            'vn_distribution': sp.get('vn_distribution', ''),
            'en_distribution': sp.get('en_distribution', ''),
            'vn_specimen': specimens_str if specimens_str else 'Mẫu lưu trữ Viện Hải dương học',
            'en_specimen': specimens_str if specimens_str else 'Institute of Oceanography',
            'vn_literature': sp.get('vn_literature', ''),
            'en_literature': 'Atlas of Marine Planktonic Copepods in Vietnam (2016-2019), Truong Si Hai Trinh et al., Institute of Oceanography.',
            'photo_url': sp.get('photo_url'),
            'worms_id': sp.get('worms_id'),
            'worms_status': sp.get('worms_status', ''),
            'worms_accepted_name': sp.get('worms_accepted_name', ''),
            'worms_synced_at': now_iso,
            'synonyms': sp.get('synonyms', []),
            'conservation_status': 'unknown',
            'biology': biology_data
        }
        species_rows.append(row)

        # Xử lý metadata ảnh cho species_photos
        for s_idx, ph in enumerate(sp.get('photos', []), 1):
            storage_path = ph.get('storage_path')
            if not storage_path:
                pub_url = ph.get('photo_url', '')
                if '/species-photos/' in pub_url:
                    storage_path = pub_url.split('/species-photos/')[-1]
                else:
                    storage_path = f"dong-vat-phu-du/{sp_id}/image_{s_idx}.webp"

            deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"dvpd-photo-{sp_id}-{s_idx}"))
            photo_row = {
                'id': deterministic_id,
                'species_id': sp_id,
                'storage_path': storage_path,
                'source': 'vnmn_atlat_2016_2019',
                'photographer': ph.get('photographer', 'TS. Trương Sĩ Hải Trình & CS / Bảo tàng Thiên nhiên Việt Nam (VNMN)'),
                'license': ph.get('license', 'VNMN Academic Research'),
                'source_url': ph.get('photo_url', ''),
                'is_primary': ph.get('is_primary', s_idx == 1),
                'sort_order': ph.get('sort_order', s_idx)
            }
            photo_rows.append(photo_row)

    print(f"\n[*] Chuẩn bị UPSERT {len(species_rows)} loài vào bảng 'species'...")
    upserted_sp = postgrest_upsert('species', species_rows)
    print(f"[✓] Thành công upsert {upserted_sp} loài vào Supabase 'species'!")

    if photo_rows:
        print(f"\n[*] Chuẩn bị UPSERT {len(photo_rows)} bản ghi ảnh vào bảng 'species_photos'...")
        upserted_ph = postgrest_upsert('species_photos', photo_rows)
        print(f"[✓] Thành công upsert {upserted_ph} ảnh vào Supabase 'species_photos'!")

    print("\n" + "="*50)
    print("=== HOÀN TẤT NẠP DỮ LIỆU ĐỘNG VẬT PHÙ DU VÀO SUPABASE ===")

if __name__ == '__main__':
    main()
