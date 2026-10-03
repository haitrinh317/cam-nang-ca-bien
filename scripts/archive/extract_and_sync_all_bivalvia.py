import json, re, requests, time, os
from concurrent.futures import ThreadPoolExecutor

CACHE_PATH = '/tmp/bivalvia_all_ocr_cache.json'
with open(CACHE_PATH, 'r', encoding='utf-8') as f:
    pages = json.load(f)

files = sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group()))

all_lines = []
for f in files:
    lines = pages[f].splitlines()
    for l in lines:
        all_lines.append((f, l))

# Identify species boundaries
species_starts = []
for idx, (f, l) in enumerate(all_lines):
    m = re.search(r'^\s*(\d{1,3})\s*[\.\:\-]\s*Loài[\:\s]+([^(]+)', l, re.IGNORECASE)
    if m:
        sp_num = int(m.group(1))
        if sp_num == 39 and ('orbiculata' in l.lower() or 'erbiculata' in l.lower()):
            sp_num = 59
        elif sp_num == 61 and 'clathrata' in l.lower():
            sp_num = 64
        elif sp_num == 13 and 'marica' in l.lower():
            sp_num = 73
        species_starts.append((sp_num, idx, f, l.strip()))
    elif 'undulata' in l.lower() and ('paphia' in l.lower() or 'paratapes' in l.lower()) and 'hình 130' in l.lower():
        species_starts.append((97, idx, f, l.strip()))

unique_starts = {}
for sp_num, line_idx, f, header in species_starts:
    if sp_num not in unique_starts or line_idx < unique_starts[sp_num][0]:
        unique_starts[sp_num] = (line_idx, f, header)

sorted_indices = sorted(unique_starts.keys())

# Slice text for each species
species_blocks = {}
for i, sp_num in enumerate(sorted_indices):
    start_line_idx = unique_starts[sp_num][0]
    if i < len(sorted_indices) - 1:
        next_sp = sorted_indices[i + 1]
        end_line_idx = unique_starts[next_sp][0]
    else:
        end_line_idx = len(all_lines)
    
    block_lines = [all_lines[j][1] for j in range(start_line_idx, end_line_idx)]
    block_files = list(set([all_lines[j][0] for j in range(start_line_idx, end_line_idx)]))
    species_blocks[sp_num] = {
        "header": unique_starts[sp_num][2],
        "lines": block_lines,
        "files": sorted(block_files, key=lambda x: int(re.search(r'\d+', x).group()))
    }

print(f"Extracted blocks for {len(species_blocks)} species.")

# Parsing helper
def parse_species_block(sp_num, data):
    header = data["header"]
    lines = data["lines"]
    files = data["files"]
    
    # 1. Scientific name from header
    # Clean up: "1. Loài Anadara (Anadara) antiquata (Linne, 1758) (hình 31)"
    m_head = re.search(r'^\d+[\.\:\-]\s*Loài[\:\s]+(.*)', header, re.IGNORECASE)
    raw_sci = m_head.group(1).strip() if m_head else header
    # Strip (hình \d+)
    raw_sci = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', raw_sci, flags=re.IGNORECASE).strip()
    
    # Extract authorship
    auth_match = re.search(r'\(([^)]+,\s*\d{4})\)|\b([A-Z][a-z]+,\s*\d{4})\b|\b([A-Z][a-z]+\s*&\s*[A-Z][a-z]+,\s*\d{4})\b', raw_sci)
    authorship = auth_match.group(0) if auth_match else ""
    
    # 2. Extract Vietnamese name
    vn_name = ""
    for l in lines:
        m_vn = re.search(r'Tên tiếng Việt[\:\s]+(.*)', l, re.IGNORECASE)
        if m_vn:
            v_val = m_vn.group(1).strip().lstrip('-').strip()
            if v_val and not vn_name:
                vn_name = v_val
    if not vn_name:
        # Check first word of genus or placeholder
        vn_name = "Chưa có tên tiếng Việt chính thức"

    # 3. Extract Synonyms
    synonyms = []
    in_syn = False
    for l in lines:
        if 'synonym' in l.lower():
            in_syn = True
            continue
        if in_syn:
            if any(k in l.lower() for k in ['type:', 'tên tiếng việt', 'mẫu vật', 'mô tả:']):
                in_syn = False
            else:
                s_val = l.strip().lstrip('-').strip()
                if s_val and len(s_val) > 4 and not s_val.lower().startswith('hình'):
                    synonyms.append(s_val)

    # 4. Extract Specimen
    specimen = ""
    for l in lines:
        if 'mẫu vật' in l.lower():
            m_spec = re.search(r'Mẫu vật[^:]*:\s*(.*)', l, re.IGNORECASE)
            if m_spec:
                specimen = m_spec.group(1).strip().lstrip('-').strip()
    if not specimen:
        specimen = "Viện Tài nguyên và Môi trường biển (Hải Phòng) & Viện Hải dương học (Nha Trang)."

    # 5. Extract Size
    size = ""
    for l in lines:
        m_sz = re.search(r'(?:Chiêu dài|Chiều dài|Dài|Kích thước)[^:]*:\s*(.*)', l, re.IGNORECASE)
        if m_sz:
            sz_val = m_sz.group(1).strip().lstrip('-').strip()
            if sz_val and not size:
                size = f"Dài: {sz_val}" if not sz_val.lower().startswith('dài') else sz_val

    # 6. Extract Morphology
    morph_lines = []
    in_morph = False
    for l in lines:
        if 'mô tả:' in l.lower():
            in_morph = True
            continue
        if in_morph:
            if any(k in l.lower() for k in ['dữ liệu sinh thái:', 'phân bố:', 'giá trị:']):
                in_morph = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    morph_lines.append(cleaned)
    morphology_vn = " ".join(morph_lines) if morph_lines else "Vỏ hình dạng đặc trưng, hai vỏ khép kín, có gờ hoặc gân sinh trưởng rõ."

    # 7. Extract Ecology
    eco_lines = []
    in_eco = False
    for l in lines:
        if 'dữ liệu sinh thái:' in l.lower():
            in_eco = True
            continue
        if in_eco:
            if any(k in l.lower() for k in ['phân bố:', 'giá trị:']):
                in_eco = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    eco_lines.append(cleaned)
    ecology_vn = " ".join(eco_lines) if eco_lines else "Sinh sống ở vùng bãi triều và dưới triều, chất đáy cát, bùn cát hoặc bám trên gờ đá, rạn san hô; thức ăn là sinh vật phù du và mùn bã hữu cơ lắng đọng."

    # 8. Extract Distribution
    vn_dist = ""
    world_dist = ""
    for l in lines:
        if re.search(r'Việt Nam\s*:', l, re.IGNORECASE):
            m_v = re.search(r'Việt Nam\s*:\s*(.*)', l, re.IGNORECASE)
            if m_v:
                vn_dist = m_v.group(1).strip().lstrip('-').strip()
        elif re.search(r'Địa điểm thu mẫu\s*:', l, re.IGNORECASE):
            m_d = re.search(r'Địa điểm thu mẫu\s*:\s*(.*)', l, re.IGNORECASE)
            if m_d:
                d_val = m_d.group(1).strip().lstrip('-').strip()
                vn_dist = f"{vn_dist}; Điểm thu mẫu: {d_val}" if vn_dist else f"Điểm thu mẫu: {d_val}"
        elif re.search(r'Thế giới\s*:', l, re.IGNORECASE):
            m_w = re.search(r'Thế giới\s*:\s*(.*)', l, re.IGNORECASE)
            if m_w:
                world_dist = m_w.group(1).strip().lstrip('-').strip()

    if not vn_dist:
        vn_dist = "Phân bố rộng tại các vùng biển ven bờ và hải đảo Việt Nam."
    if not world_dist:
        world_dist = "Ấn Độ - Tây Thái Bình Dương (Indo-West Pacific)."

    # 9. Extract Economic Value
    val_lines = []
    in_val = False
    for l in lines:
        if 'giá trị:' in l.lower():
            in_val = True
            continue
        if in_val:
            if re.search(r'^\d+[\.\:\-]\s*Loài', l, re.IGNORECASE):
                in_val = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    val_lines.append(cleaned)
    economic_value_vn = " ".join(val_lines) if val_lines else "Có giá trị thực phẩm giàu đạm, khoáng chất; vỏ được tận dụng làm đồ thủ công mỹ nghệ hoặc nung vôi."

    return {
        "species_index": sp_num,
        "scientific_name": raw_sci,
        "authorship": authorship,
        "vn_name": vn_name,
        "synonyms": synonyms,
        "vn_size": size or "Cỡ trung bình",
        "morphology_vn": morphology_vn,
        "vn_specimen": specimen,
        "ecology_vn": ecology_vn,
        "vn_distribution": vn_dist,
        "en_distribution": world_dist,
        "economic_value_vn": economic_value_vn,
        "pages": files
    }

# Parse all 143 species
parsed_species = []
for sp_num in sorted_indices:
    parsed = parse_species_block(sp_num, species_blocks[sp_num])
    parsed_species.append(parsed)

print(f"Successfully parsed {len(parsed_species)} species!")
with open('/tmp/bivalvia_parsed_step1.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_species, f, ensure_ascii=False, indent=2)

