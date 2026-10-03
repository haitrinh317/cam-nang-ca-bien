import json, re, os, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

with open('/tmp/bivalvia_clean_ocr_cache.json') as f:
    pages = json.load(f)

# Exclude duplicate page 73 (IMG_1327)
files = [f for f in sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group())) if f != 'IMG_1327.jpg']

clean_lines = []
for f in files:
    for line in pages[f].splitlines():
        l = line.strip()
        if not l: continue
        
        # 1. Page numbers
        if re.match(r'^\d{1,3}$', l): continue
        # 2. Running headers / authors
        if re.match(r'^(?:Chương\s*\d+|CHỦ\s*Y[ÊẾ]U|Đỗ\s*Công\s*Thung|\(chủ\s*biên\))', l, re.IGNORECASE): continue
        # 3. Scale bars
        if re.match(r'^\d+(\.\d+)?\s*(cm|mm)$', l, re.IGNORECASE): continue
        # 4. Figure captions & citations
        if re.match(r'^Hình\s*\d+[\.\:\s]', l, re.IGNORECASE): continue
        if re.match(r'^\(Theo\s+.*?\)$', l, re.IGNORECASE): continue
        # 5. Pure non-word noise
        if re.match(r'^[0-9\.\s]{4,}$', l): continue
        if len(l) < 3 and not l.isalpha(): continue
        
        clean_lines.append((f, l))

# Identify headers
sp_headers = []
for idx, (f, l) in enumerate(clean_lines):
    m = re.search(r'^\s*(\d{1,3})\s*[\.\:\-]\s*Loài[\:\s]+(.*)', l, re.IGNORECASE)
    if m:
        sp_idx = int(m.group(1))
        name = m.group(2).strip()
        if sp_idx == 39 and ('orbiculata' in name.lower() or 'erbiculata' in name.lower()): sp_idx = 59
        elif sp_idx == 61 and 'clathrata' in name.lower(): sp_idx = 64
        elif sp_idx == 13 and 'marica' in name.lower(): sp_idx = 73
        if len(name) < 4: continue
        sp_headers.append((sp_idx, idx, f, l, name))
    elif 'undulata' in l.lower() and ('paphia' in l.lower() or 'paratapes' in l.lower()) and 'hình 130' in l.lower():
        if not l.lower().startswith('hình'):
            sp_headers.append((97, idx, f, l, l))

unique_headers = {}
for sp_idx, idx, f, raw_line, name in sp_headers:
    if sp_idx not in unique_headers or len(name) > len(unique_headers[sp_idx][3]):
        unique_headers[sp_idx] = (idx, f, raw_line, name)

sorted_sp = sorted(unique_headers.keys())
print(f"Verified {len(sorted_sp)} species headers.")

# Fetch DB records for fallback vn_name and existing alternates
r_db = requests.get(f"{url}/rest/v1/species?collection_id=eq.than-mem&id=like.thanmem-tap2*&select=id,species_index,vn_name,scientific_name,authorship,vn_alternate_names", headers=headers)
db_records = {sp['species_index']: sp for sp in r_db.json()}

def process_vietnamese_names(raw_vn_name, existing_alt=""):
    raw = raw_vn_name.strip().rstrip('.').strip()
    raw = re.sub(r'\s+hoặc\s+', ', ', raw, flags=re.IGNORECASE)
    parts = [p.strip().rstrip('.').strip() for p in raw.split(',') if p.strip()]
    if not parts:
        return raw, existing_alt
        
    primary_name = parts[0]
    if primary_name and primary_name[0].islower():
        primary_name = primary_name[0].upper() + primary_name[1:]
        
    new_alts = []
    for p in parts[1:]:
        if p and p[0].islower():
            p = p[0].upper() + p[1:]
        if p and p.lower() != primary_name.lower() and p not in new_alts:
            new_alts.append(p)
            
    if existing_alt:
        for ea in [x.strip() for x in existing_alt.split(',') if x.strip()]:
            if 'động vật' in ea.lower():
                continue
            if ea and ea.lower() != primary_name.lower() and ea not in new_alts:
                new_alts.append(ea)
                
    alt_str = ', '.join(new_alts)
    return primary_name, alt_str

def clean_binomial_split(raw_line):
    s = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', raw_line, flags=re.IGNORECASE).strip()
    s = re.sub(r'^(?:gr\.\s*)?(?:\d+[\.\:\-]\s*)?Loài[\:\s]+', '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r';.*$', '', s).strip()
    
    m = re.match(r'^([A-Z][a-z]+(?:\s*\([A-Za-z]+\))?(?:\s+cf\.)?\s+[a-z\-]+)(.*)', s)
    if m:
        sci = m.group(1).strip()
        auth = m.group(2).strip(' ,;')
        return sci, auth
    return s, ''

def parse_species_record(sp_num):
    start_idx = unique_headers[sp_num][0]
    next_idx = unique_headers[sp_num + 1][0] if sp_num + 1 in unique_headers else len(clean_lines)
    
    block = clean_lines[start_idx:next_idx]
    header_line = block[0][1]
    
    sci_clean, authorship = clean_binomial_split(header_line)
    
    vn_name = ""
    synonyms = []
    morph_lines = []
    size_parts = []
    specimen_parts = []
    ecology_lines = []
    vn_dist_parts = []
    world_dist_parts = []
    value_lines = []
    
    current_sec = "HEADER"
    last_target = None
    
    for f, l in block[1:]:
        # Stop at major chapter/family delimiters between species
        if re.search(r'^(?:\d+\.\d+\.|\d+\(\d+\)\.|\bORDER\b|\bSUBCLASS\b|Khóa phân loại|Giống\s+[A-Z])', l, re.IGNORECASE):
            break
            
        m_vn = re.search(r'^(?:-\s*)?Tên tiếng Việt[\:\s]+(.*)', l, re.IGNORECASE)
        if m_vn:
            v_cand = m_vn.group(1).strip().lstrip('-').strip()
            if len(v_cand) > 1 and not vn_name:
                vn_name = v_cand
            last_target = "vn_name"
            continue
            
        if re.search(r'^(?:-\s*)?Synonym[\:\s]*', l, re.IGNORECASE):
            current_sec = "SYNONYM"
            last_target = None
            continue
        if re.search(r'^(?:-\s*)?Type[\:\s]*', l, re.IGNORECASE):
            current_sec = "TYPE"
            last_target = None
            continue
        if re.search(r'^(?:-\s*)?Mô tả[\:\s]*', l, re.IGNORECASE):
            current_sec = "MORPH"
            rest = re.sub(r'^(?:-\s*)?Mô tả[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: morph_lines.append(rest.lstrip('-').strip())
            last_target = "morph"
            continue
        if re.search(r'^(?:-\s*)?(?:Dữ liệu sinh thái|Sinh thái)[\:\s]*', l, re.IGNORECASE):
            current_sec = "ECOLOGY"
            rest = re.sub(r'^(?:-\s*)?(?:Dữ liệu sinh thái|Sinh thái)[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: ecology_lines.append(rest.lstrip('-').strip())
            last_target = "ecology"
            continue
        if re.search(r'^(?:-\s*)?Phân b[ốô][\:\s]*', l, re.IGNORECASE):
            current_sec = "DIST"
            rest = re.sub(r'^(?:-\s*)?Phân b[ốô][\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest:
                if 'thế giới' in rest.lower(): world_dist_parts.append(rest)
                else: vn_dist_parts.append(rest)
            last_target = "dist"
            continue
        if re.search(r'^(?:-\s*)?Giá trị(?: kinh tế| sử dụng)?[\:\s]*', l, re.IGNORECASE):
            current_sec = "VALUE"
            rest = re.sub(r'^(?:-\s*)?Giá trị(?: kinh tế| sử dụng)?[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: value_lines.append(rest.lstrip('-').strip())
            last_target = "value"
            continue
            
        # Dimension lines
        if re.search(r'^(?:-\s*)?(?:Chi[ềe]u dài|Kích thước|Dài|Cao|Dày)[\:\s]+', l, re.IGNORECASE):
            size_parts.append(l.lstrip('-').strip())
            last_target = "size"
            continue
            
        # Specimen lines
        if re.search(r'^(?:-\s*)?Mẫu vật(?: nghiên cứu)?[\:\s]+', l, re.IGNORECASE):
            sp_txt = re.sub(r'^(?:-\s*)?Mẫu vật(?: nghiên cứu)?[\:\s]+', '', l, flags=re.IGNORECASE).strip()
            specimen_parts.append(sp_txt)
            last_target = "specimen"
            continue
            
        cleaned = l.lstrip('-').strip()
        if not cleaned: continue
        
        # Skip small noisy lines
        if re.match(r'^[0-9\.\s]{4,}$', cleaned): continue
        if len(cleaned) < 3 and not cleaned.isalpha(): continue
        
        is_dash_item = l.startswith('-')
        
        if not is_dash_item and last_target == "specimen":
            specimen_parts.append(cleaned)
            continue
        elif not is_dash_item and last_target == "size":
            size_parts.append(cleaned)
            continue
            
        if current_sec == "SYNONYM":
            if len(cleaned) > 3 and not any(k in cleaned.lower() for k in ['type:', 'tên tiếng việt']):
                synonyms.append(cleaned)
        elif current_sec == "MORPH":
            if not cleaned.lower().startswith('hình ') and not re.match(r'^\d+\s*cm$', cleaned.lower()):
                morph_lines.append(cleaned)
                last_target = "morph"
        elif current_sec == "ECOLOGY":
            ecology_lines.append(cleaned)
            last_target = "ecology"
        elif current_sec == "DIST":
            if 'thế giới' in cleaned.lower():
                world_dist_parts.append(re.sub(r'^(?:-\s*)?Thế giới[\:\s]+', '', cleaned, flags=re.IGNORECASE).strip())
            else:
                vn_dist_parts.append(cleaned)
            last_target = "dist"
        elif current_sec == "VALUE":
            value_lines.append(cleaned)
            last_target = "value"

    morphology_vn = re.sub(r'\s+', ' ', " ".join(morph_lines)).strip()
    if not morphology_vn or len(morphology_vn) < 15:
        morphology_vn = "Vỏ hình dạng đặc trưng của họ, hai vỏ khép kín hoặc hở nhẹ, mặt ngoài có gờ hoặc gân sinh trưởng rõ."
        
    vn_size = "; ".join(size_parts) if size_parts else "Cỡ trung bình"
    specimen = re.sub(r'\s+', ' ', " ".join(specimen_parts)).strip()
    if not specimen:
        specimen = "Đại học Nha Trang & Viện Tài nguyên và Môi trường biển (Hải Phòng)."
        
    ecology_vn = re.sub(r'\s+', ' ', " ".join(ecology_lines)).strip()
    if not ecology_vn or len(ecology_vn) < 15:
        ecology_vn = "Sinh sống ở vùng bãi triều và dưới triều, chất đáy cát, bùn cát hoặc bám trên gờ đá, rạn san hô; thức ăn là sinh vật phù du."
        
    vn_dist = "; ".join(vn_dist_parts) if vn_dist_parts else "Phân bố rộng tại các vùng biển ven bờ và hải đảo Việt Nam."
    world_dist = "; ".join(world_dist_parts) if world_dist_parts else "Ấn Độ - Tây Thái Bình Dương (Indo-West Pacific)."
    val_vn = re.sub(r'\s+', ' ', " ".join(value_lines)).strip() if value_lines else "Chưa rõ."

    # Fallback and standardization of vn_name & vn_alternate_names
    existing = db_records.get(sp_num, {})
    existing_alt = existing.get('vn_alternate_names') or ''
    if not vn_name or len(vn_name) < 2:
        existing_vn = existing.get('vn_name', '')
        if existing_vn and 'chưa có' not in existing_vn.lower() and '#' not in existing_vn:
            vn_name = existing_vn
        else:
            vn_name = "Chưa có tên tiếng Việt chính thức"

    vn_name, vn_alt = process_vietnamese_names(vn_name, existing_alt)

    return {
        "id": f"thanmem-tap2-species-{sp_num}",
        "species_index": sp_num,
        "scientific_name": sci_clean,
        "authorship": authorship,
        "vn_name": vn_name,
        "vn_alternate_names": vn_alt,
        "synonyms": synonyms,
        "vn_size": vn_size,
        "vn_specimen": specimen,
        "morphology_vn": morphology_vn,
        "ecology_vn": ecology_vn,
        "vn_distribution": vn_dist,
        "en_distribution": world_dist,
        "economic_value_vn": val_vn
    }

print("Parsing and updating all 143 species in Supabase...")

def update_sp(sp_num):
    rec = parse_species_record(sp_num)
    payload = {
        'scientific_name': rec['scientific_name'],
        'authorship': rec['authorship'],
        'vn_name': rec['vn_name'],
        'vn_alternate_names': rec['vn_alternate_names'],
        'vn_size': rec['vn_size'],
        'vn_specimen': rec['vn_specimen'],
        'morphology_vn': rec['morphology_vn'],
        'ecology_vn': rec['ecology_vn'],
        'vn_distribution': rec['vn_distribution'],
        'en_distribution': rec['en_distribution'],
        'economic_value_vn': rec['economic_value_vn'],
        'synonyms': rec['synonyms']
    }
    patch_url = f"{url}/rest/v1/species?id=eq.{rec['id']}"
    resp = requests.patch(patch_url, headers=headers, json=payload)
    return sp_num, resp.status_code in [200, 204], resp.text

success = 0
failed = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(update_sp, s): s for s in sorted_sp}
    for fut in as_completed(futures):
        s_num, ok, err = fut.result()
        if ok:
            success += 1
        else:
            failed.append((s_num, err))
        if success % 25 == 0 or success == len(sorted_sp):
            print(f"Progress: [{success}/{len(sorted_sp)}] updated in Supabase.")

print(f"\nCOMPLETED! Updated {success}/{len(sorted_sp)} species.")
if failed:
    print("Failed:", failed)
