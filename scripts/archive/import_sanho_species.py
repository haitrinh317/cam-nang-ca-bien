#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_sanho_species.py — Bóc tách, chuẩn hóa và UPSERT 42 loài San hô tám ngăn
từ sách 'Đa dạng sinh học san hô tám ngăn vùng biển phía Nam Việt Nam' — TS. Hoàng Xuân Bền
vào Supabase bảng `species`.
"""

import os, glob, re, json, urllib.request

# 1. Load Supabase credentials
env_file = '.env.local' if os.path.exists('.env.local') else '.env'
env = {}
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k] = v.strip('\"').strip('\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not SUPABASE_URL or not KEY:
    raise RuntimeError("Missing Supabase credentials in environment file.")

# 2. Collect and combine OCR text
ocr_dir = "/Users/macbook2016/.gemini/antigravity-ide/brain/0c721b9c-d53e-418b-a401-d01c07e77efd/scratch/ocr_pages"

def sort_key(p):
    m = re.search(r'page_(\d+)_book_(\d+)', p)
    return int(m.group(1)) if m else 0

pages = sorted(glob.glob(f"{ocr_dir}/*.txt"), key=sort_key)

cleaned_pages = []
for idx, p in enumerate(pages):
    if idx == 14: # Skip duplicate page 15 (IMG_1110)
        continue
    with open(p, 'r', encoding='utf-8') as f:
        cleaned_pages.append(f.read())

full_text = ""
for txt in cleaned_pages:
    lines = txt.splitlines()
    filtered = []
    for l in lines:
        l_trim = l.strip()
        if re.match(r'^\d+\s+HOÀNG XUÂN BỀN', l_trim) or re.match(r'^CHƯƠNG 3\..*?\d+$', l_trim) or re.match(r'^vùng biển phía Nam Việt Nam', l_trim):
            continue
        filtered.append(l)
    full_text += "\n" + "\n".join(filtered)

# 3. Species names & common name helpers
SPECIAL_VN_NAMES = {
    "Tubipora musica": "San hô đàn ống (San hô ống đỏ)",
    "Sinularia brassica": "San hô bắp cải",
    "Junceella fragilis": "San hô roi mảnh",
    "Subergorgia suberosa": "San hô sừng Subergorgia",
    "Rumphella aggregata": "San hô sừng Rumphella",
    "Sarcophyton trocheliophorum": "San hô nấm da trocheliophorum",
    "Sarcophyton glaucum": "San hô nấm da glaucum",
}

def make_vn_name(scientific_name):
    if scientific_name in SPECIAL_VN_NAMES:
        return SPECIAL_VN_NAMES[scientific_name]
    genus = scientific_name.split()[0] if ' ' in scientific_name else scientific_name
    if genus in ["Lobophytum", "Sarcophyton", "Sclerophytum", "Sinularia", "Klyxum", "Lemnalia", "Heteroxenia", "Xenia"]:
        return f"San hô mềm {scientific_name}"
    elif genus in ["Rumphella", "Subergorgia", "Junceella"]:
        return f"San hô sừng {scientific_name}"
    return scientific_name

def clean_str(s):
    if not s: return ""
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# 4. Regex parsing for species
sp_header_re = re.compile(
    r'^\s*(\d{1,2})\.\s+([A-Z][a-z]+(?:\s+[a-z\-]+)?)\s+([^\(\n]*\([^\)]+\)[^\(\n]*|\b[A-Z][a-z]+,\s*\d{4}\b)?.*?(?:\(Hình\s+38\.\d+\))?',
    re.MULTILINE
)

matches = list(sp_header_re.finditer(full_text))
species_rows = []

for i in range(len(matches)):
    m = matches[i]
    sp_num = int(m.group(1))
    sc_name = clean_str(m.group(2))
    author_raw = m.group(3).strip() if m.group(3) else ""
    
    # Clean authorship
    author = re.sub(r'\(Hình\s+38\.\d+\)', '', author_raw).strip()
    author = re.sub(r'^\(+|\)+$', '', author) # remove extra outer parens
    if re.search(r'\d{4}', author):
        author = f"({author})" if not author.startswith('(') else author
    
    start = m.end()
    end = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
    block_text = full_text[start:end]
    
    # Fields
    m_orig = re.search(r'Tên gốc:\s*(.*?)(?=\n\s*(?:Đặc điểm hình thái ngoài|Hình dáng|Sinh thái|Phân bố)|\Z)', block_text, re.DOTALL)
    orig_name = clean_str(m_orig.group(1)) if m_orig else ""
    if orig_name:
        orig_name = re.sub(r'(\d{4}\.?)\s+.*$', r'\1', orig_name)
    
    m_ext = re.search(r'Đặc điểm hình thái ngoài:\s*(.*?)(?=\n\s*(?:Hình dáng và kích thước trâm xương|Sinh thái|Phân bố)|\Z)', block_text, re.DOTALL)
    morph_ext = clean_str(m_ext.group(1)) if m_ext else ""
    
    m_scl = re.search(r'Hình dáng và kích thước trâm xương:\s*(.*?)(?=\n\s*(?:Sinh thái|Phân bố)|\Z)', block_text, re.DOTALL)
    sclerites = clean_str(m_scl.group(1)) if m_scl else ""
    
    morph_full = ""
    if morph_ext: morph_full = morph_ext
    if sclerites:
        if morph_full:
            morph_full += "\n\nHình dáng và kích thước trâm xương: " + sclerites
        else:
            morph_full = "Hình dáng và kích thước trâm xương: " + sclerites
            
    m_eco = re.search(r'Sinh thái:\s*(.*?)(?=\n\s*(?:Phân bố trên thế giới|Phân bố ở Việt Nam)|\Z)', block_text, re.DOTALL)
    eco = clean_str(m_eco.group(1)) if m_eco else ""
    
    m_w = re.search(r'Phân bố trên thế giới:\s*(.*?)(?=\n\s*(?:Phân bố ở Việt Nam)|\Z)', block_text, re.DOTALL)
    dist_world = clean_str(m_w.group(1)) if m_w else ""
    
    m_v = re.search(r'Phân bố ở Việt Nam:\s*(.*?)(?=\n\s*(?:\d{1,2}\.\s+[A-Z])|\Z)', block_text, re.DOTALL)
    dist_vn = clean_str(m_v.group(1)) if m_v else ""
    
    # Specific cleanup for OCR quirks
    if sp_num == 6:
        if 'Nha Trang' not in dist_vn and 'vịnh' in dist_vn:
            dist_vn = dist_vn.rstrip('.') + " Nha Trang."
            dist_world = dist_world.replace("Nha Trang.", "").strip()
            
    if sp_num == 29:
        if not dist_vn:
            dist_vn = "[Dữ liệu khuyết do thiếu trang 102]"
        if not dist_world:
            dist_world = "[Missing data due to un-scanned page 102]"
        if not eco:
            eco = "[Dữ liệu khuyết do thiếu trang 102]"
            
    # Clean OCR noise at end of dist_vn
    dist_vn = re.sub(r'\s+[a-zA-Z0-9,\.]{1,3}$', '', dist_vn).strip()
    if dist_vn and not dist_vn.endswith('.') and not dist_vn.endswith(']'):
        dist_vn += '.'
        
    # Taxonomy
    family_latin = "Alcyoniidae"
    m_fam = re.search(r'thuộc họ\s+([A-Z][a-z]+idae)', block_text)
    if m_fam:
        family_latin = m_fam.group(1)
    elif sc_name.startswith('Tubipora'):
        family_latin = 'Tubiporidae'
    elif sc_name.startswith('Heteroxenia') or sc_name.startswith('Xenia'):
        family_latin = 'Xeniidae'
    elif sc_name.startswith('Junceella'):
        family_latin = 'Ellisellidae'
    elif sc_name.startswith('Subergorgia'):
        family_latin = 'Subergorgiidae'
    elif sc_name.startswith('Klyxum'):
        family_latin = 'Cladiellidae'
    elif sc_name.startswith('Lemnalia'):
        family_latin = 'Nephtheidae'
    elif sc_name.startswith('Rumphella'):
        family_latin = 'Isididae'

    genus_latin = sc_name.split()[0] if ' ' in sc_name else sc_name
    synonyms = [orig_name] if orig_name else []
    
    row = {
        "id": f"sanho-species-{sp_num}",
        "collection_id": "san-ho",
        "volume": 1,
        "species_index": sp_num,
        "vn_name": make_vn_name(sc_name),
        "scientific_name": sc_name,
        "authorship": author,
        "en_common_name": "",
        "vn_alternate_names": "",
        "tax_order_latin": "Alcyonacea",
        "tax_family_latin": family_latin,
        "tax_order_vn": "Bộ San hô mềm",
        "tax_family_vn": "",
        "tax_genus_vn": "",
        "tax_genus_latin": genus_latin,
        "tax_class_vn": "Lớp San hô (Phân lớp San hô tám ngăn)",
        "tax_class_latin": "Anthozoa (Octocorallia)",
        "morphology_vn": morph_full,
        "morphology_en": "",
        "vn_size": "",
        "vn_distribution": dist_vn,
        "vn_specimen": "",
        "vn_status": eco,
        "vn_literature": "Hoàng Xuân Bền. Đa dạng sinh học san hô tám ngăn vùng biển phía Nam Việt Nam.",
        "en_size": "",
        "en_distribution": dist_world,
        "en_specimen": "",
        "en_status": "",
        "en_literature": "Hoang Xuan Ben. Biodiversity of Octocorallia in the South of Vietnam.",
        "conservation_status": "common" if ("phổ biến" in eco.lower() or "thường" in eco.lower()) else "unknown",
        "synonyms": synonyms
    }
    species_rows.append(row)

# Add missing species 30 placeholder
missing_sp_30 = {
    "id": "sanho-species-30",
    "collection_id": "san-ho",
    "volume": 1,
    "species_index": 30,
    "vn_name": "San hô mềm Sinularia sp. [KHUYẾT TRANG 102]",
    "scientific_name": "Sinularia sp.",
    "authorship": "[KHÔNG RÕ]",
    "en_common_name": "",
    "vn_alternate_names": "",
    "tax_order_latin": "Alcyonacea",
    "tax_family_latin": "Alcyoniidae",
    "tax_order_vn": "Bộ San hô mềm",
    "tax_family_vn": "",
    "tax_genus_vn": "",
    "tax_genus_latin": "Sinularia",
    "tax_class_vn": "Lớp San hô (Phân lớp San hô tám ngăn)",
    "tax_class_latin": "Anthozoa (Octocorallia)",
    "morphology_vn": "[Dữ liệu khuyết do thiếu trang 102 của tài liệu gốc. Sẽ cập nhật khi có bản scan bổ sung.]",
    "morphology_en": "[Missing data due to un-scanned page 102 of original document.]",
    "vn_size": "",
    "vn_distribution": "[Dữ liệu khuyết do thiếu trang 102]",
    "vn_specimen": "",
    "vn_status": "[Dữ liệu khuyết do thiếu trang 102]",
    "vn_literature": "Hoàng Xuân Bền. Đa dạng sinh học san hô tám ngăn vùng biển phía Nam Việt Nam, tr. 102.",
    "en_size": "",
    "en_distribution": "[Missing data due to un-scanned page 102]",
    "en_specimen": "",
    "en_status": "",
    "en_literature": "Hoang Xuan Ben. Biodiversity of Octocorallia in the South of Vietnam, p. 102.",
    "conservation_status": "unknown",
    "synonyms": []
}

species_rows.insert(29, missing_sp_30)

print(f"Total species rows to UPSERT: {len(species_rows)}")

# 5. Batch UPSERT into Supabase
url = f"{SUPABASE_URL}/rest/v1/species?on_conflict=id"

batch_size = 20
total_upserted = 0

for b_idx in range(0, len(species_rows), batch_size):
    batch = species_rows[b_idx:b_idx+batch_size]
    data = json.dumps(batch).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST', headers={
        'apikey': KEY,
        'Authorization': f'Bearer {KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=representation'
    })
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            total_upserted += len(res)
            print(f"Upserted batch {b_idx//batch_size + 1}: {len(res)} species.")
    except Exception as e:
        print(f"ERROR upserting batch {b_idx//batch_size + 1}:", e)
        if hasattr(e, 'read'):
            print(e.read().decode())
        raise

print(f"SUCCESS! Total species upserted into Supabase: {total_upserted}")
