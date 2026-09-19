#!/usr/bin/env python3
"""
sync_banyuls_dvpd.py
Đồng bộ và làm giàu dữ liệu sinh học cho 101 loài Động vật phù du (Copepoda)
từ CSDL quốc tế Biodiversity of Marine Planktonic Copepods (Sorbonne / CNRS / Banyuls).
Trích xuất: Dải kích thước (mm) theo giới tính F/M, tầng nước sinh thái (Epipelagic/Mesopelagic/Neritic),
phân vùng đại dương và dẫn liệu nghiên cứu quốc tế.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

INPUT_JSON = 'scratch/dvpd_atlat_with_photos.json'
OUTPUT_JSON = 'scratch/dvpd_atlat_enriched_banyuls.json'
CACHE_MAP = 'scratch/banyuls_species_map.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def clean_latin_name(name):
    """Loại bỏ subgenus trong ngoặc đơn và chuẩn hóa khoảng trắng:
       Acartia (Odontacartia) amboinensis -> Acartia amboinensis
    """
    cleaned = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    return ' '.join(cleaned.split()).strip()

def get_banyuls_species_map():
    """Tải và trích xuất bảng mapping 2701 loài từ Banyuls."""
    if os.path.exists(CACHE_MAP):
        with open(CACHE_MAP, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    print("[*] Đang tải danh mục loài toàn cầu từ copepodes.obs-banyuls.fr...")
    url = 'https://copepodes.obs-banyuls.fr/en/fichesp.php?sp=39'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('iso-8859-1', errors='ignore')
        
    options = re.findall(r'<option\s+value=\"([^\"]+)\">([^<]+)</option>', html)
    banyuls_map = {}
    
    for val, full_name in options:
        if val in ('0', '') or '---' in full_name:
            continue
        cleaned = clean_latin_name(full_name)
        banyuls_map[cleaned.lower()] = {
            'sp_id': val,
            'full_name': full_name.strip(),
            'clean_name': cleaned
        }
        # Lưu thêm key theo full_name viết thường
        banyuls_map[full_name.lower().strip()] = {
            'sp_id': val,
            'full_name': full_name.strip(),
            'clean_name': cleaned
        }
        
    print(f"[✓] Đã nạp {len(banyuls_map)} ánh xạ loài từ Banyuls!")
    with open(CACHE_MAP, 'w', encoding='utf-8') as f:
        json.dump(banyuls_map, f, ensure_ascii=False, indent=2)
    return banyuls_map

def fetch_banyuls_card(sp_id):
    """Tải và bóc tách thông tin thẻ loài fichesp.php?sp=X."""
    url = f"https://copepodes.obs-banyuls.fr/en/fichesp.php?sp={sp_id}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('iso-8859-1', errors='ignore')
    except Exception as e:
        print(f"  [!] Lỗi fetch sp={sp_id}: {e}")
        return None
        
    # Cắt từ vùng nội dung chính (khoảng sau 140000 hoặc sau 'Species Card')
    clean_text = re.sub(r'<[^>]+>', '\n', html)
    lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
    
    info = {
        'banyuls_sp_id': sp_id,
        'banyuls_url': url,
        'dimensions_raw': '',
        'dimensions_summary': '',
        'female_size': '',
        'male_size': '',
        'remarks': '',
        'localisations': '',
        'quotations': '',
        'nz_zones': ''
    }
    
    # Tìm Dimensions
    for i, line in enumerate(lines):
        if line.startswith('Dimensions (mm)'):
            # Các dòng tiếp theo
            sub_lines = lines[i+1:i+15]
            for sl in sub_lines:
                if sl.startswith('{') and sl.endswith('}'):
                    info['dimensions_summary'] = sl.strip('{} ')
                elif 'Remarks' in sl or 'Localisations' in sl:
                    break
                elif not info['dimensions_raw'] and ('F:' in sl or 'M:' in sl):
                    info['dimensions_raw'] = sl
                    
        elif line.startswith('Remarks'):
            sub_lines = lines[i+1:i+8]
            rem_parts = []
            for sl in sub_lines:
                if any(kw in sl for kw in ['Last update', 'Contributor Remarks', 'Login', 'Any use of this site']):
                    break
                rem_parts.append(sl)
            info['remarks'] = '; '.join(rem_parts)
            
        elif line.startswith('Localisations'):
            if i+2 < len(lines):
                info['localisations'] = lines[i+2]
                
        elif line.startswith('Quotations'):
            if i+1 < len(lines):
                info['quotations'] = lines[i+1]
                
        elif line.startswith('NZ:'):
            if i+1 < len(lines):
                info['nz_zones'] = lines[i+1]

    # Chuẩn hóa kích thước
    dim_str = info['dimensions_summary'] or info['dimensions_raw']
    if dim_str:
        # Chuẩn hóa dấu phẩy thành dấu chấm trong số thập phân
        dim_norm = re.sub(r'(\d+),(\d+)', r'\1.\2', dim_str)
        f_match = re.search(r'F:\s*([0-9.\-\s–]+)', dim_norm)
        m_match = re.search(r'M:\s*([0-9.\-\s–]+)', dim_norm)
        if f_match:
            info['female_size'] = f_match.group(1).strip()
        if m_match:
            info['male_size'] = m_match.group(1).strip()

    return info

def translate_remarks_vn(remarks_en):
    """Phiên dịch học thuật các thuật ngữ sinh thái học từ Banyuls sang tiếng Việt."""
    if not remarks_en:
        return ""
    trans_map = {
        'neritic-oceanic': 'vùng biển ven bờ đến viễn duyên (neritic-oceanic)',
        'neritic': 'vùng biển ven bờ (neritic)',
        'oceanic': 'vùng biển khơi xa bờ (oceanic)',
        'epipelagic': 'tầng mặt hải dương (epipelagic, 0–200 m)',
        'mesopelagic': 'tầng giữa hải dương (mesopelagic, 200–1000 m)',
        'bathypelagic': 'tầng sâu hải dương (bathypelagic, >1000 m)',
        'benthopelagic': 'tầng sát đáy biển (benthopelagic)',
        'estuarine': 'vùng cửa sông nước lợ (estuarine)',
        'cosmopolitan': 'phân bố rộng toàn cầu (cosmopolitan)',
        'tropical': 'nhiệt đới',
        'subtropical': 'cận nhiệt đới',
        'temperate': 'ôn đới'
    }
    vn_terms = []
    rem_lower = remarks_en.lower()
    for en_kw, vn_kw in trans_map.items():
        if en_kw in rem_lower:
            vn_terms.append(vn_kw)
    if vn_terms:
        return "Tập tính sinh thái: " + "; ".join(vn_terms) + "."
    return remarks_en

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[!] Không tìm thấy {INPUT_JSON}")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    banyuls_map = get_banyuls_species_map()
    matched_count = 0
    enriched_records = []

    print(f"\n[*] Bắt đầu đối chiếu và làm giàu {len(species_list)} loài từ Banyuls Copepoda...")

    for idx, sp in enumerate(species_list, 1):
        sp_id = sp['id']
        sci_name = sp['scientific_name']
        worms_name = sp.get('worms_accepted_name', '')
        
        # Thử tìm theo sci_name -> worms_name -> clean_name
        match_info = None
        for candidate in [sci_name, worms_name, clean_latin_name(sci_name), clean_latin_name(worms_name)]:
            if candidate and candidate.lower() in banyuls_map:
                match_info = banyuls_map[candidate.lower()]
                break

        if match_info:
            matched_count += 1
            b_sp_id = match_info['sp_id']
            print(f"[{idx}/{len(species_list)}] ✓ Match Banyuls: {sci_name} -> ID {b_sp_id} ({match_info['full_name']})")
            
            card_info = fetch_banyuls_card(b_sp_id)
            time.sleep(0.3) # Giãn cách gọi nhẹ nhàng
            
            if card_info:
                # Xây dựng trường kích thước chuẩn
                size_vn_parts = []
                size_en_parts = []
                if card_info['female_size']:
                    size_vn_parts.append(f"Cá thể cái (F): {card_info['female_size']} mm")
                    size_en_parts.append(f"Female (F): {card_info['female_size']} mm")
                if card_info['male_size']:
                    size_vn_parts.append(f"Cá thể đực (M): {card_info['male_size']} mm")
                    size_en_parts.append(f"Male (M): {card_info['male_size']} mm")
                    
                size_vn = " · ".join(size_vn_parts)
                size_en = " · ".join(size_en_parts)
                
                # Cập nhật thông tin vào record
                sp['vn_size'] = size_vn
                sp['en_size'] = size_en
                
                eco_banyuls_vn = translate_remarks_vn(card_info['remarks'])
                if eco_banyuls_vn and eco_banyuls_vn not in sp.get('ecology_vn', ''):
                    sp['ecology_vn'] = (sp.get('ecology_vn', '') + ' ' + eco_banyuls_vn).strip()
                    
                sp['ecology_en'] = card_info['remarks']
                
                # Cập nhật biology JSONB
                if 'biology' not in sp:
                    sp['biology'] = {}
                sp['biology'].update({
                    'banyuls_database_id': b_sp_id,
                    'banyuls_url': card_info['banyuls_url'],
                    'banyuls_full_name': match_info['full_name'],
                    'dimensions_banyuls': {
                        'summary': card_info['dimensions_summary'],
                        'female_mm': card_info['female_size'],
                        'male_mm': card_info['male_size']
                    },
                    'ecological_remarks': card_info['remarks'],
                    'global_quotations_count': card_info['quotations'],
                    'database_source': 'Sorbonne University / CNRS / Banyuls Marine Planktonic Copepods (Razouls et al. 2005-2026)'
                })
        else:
            print(f"[{idx}/{len(species_list)}] ⚠ Không khớp Banyuls: {sci_name}")
            
        enriched_records.append(sp)

    print(f"\n[✓] Khớp thành công {matched_count}/{len(species_list)} loài ({matched_count/len(species_list)*100:.1f}%) từ Banyuls!")

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(enriched_records, f, ensure_ascii=False, indent=2)

    # Cập nhật hàng loạt vào Supabase DB
    print(f"\n[*] Đang đồng bộ dữ liệu làm giàu vào Supabase...")
    patch_count = 0
    patch_headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    for sp in enriched_records:
        sp_id = sp['id']
        payload = {
            'vn_size': sp.get('vn_size', ''),
            'en_size': sp.get('en_size', ''),
            'ecology_vn': sp.get('ecology_vn', ''),
            'ecology_en': sp.get('ecology_en', ''),
            'biology': sp.get('biology', {})
        }
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        req = urllib.request.Request(patch_url, data=json.dumps(payload).encode('utf-8'), headers=patch_headers, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 204):
                    patch_count += 1
        except Exception as e:
            print(f"  [!] Lỗi PATCH {sp_id}: {e}")

    print(f"[✓] Đã cập nhật thành công {patch_count}/{len(enriched_records)} loài trong Supabase DB!")
    print("\n" + "="*50)
    print("=== HOÀN TẤT ENRICHMENT BANYULS COPEPODA ===")

if __name__ == '__main__':
    main()
