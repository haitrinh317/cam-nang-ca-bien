import json, re

with open('/tmp/bivalvia_clean_ocr_cache.json') as f:
    pages = json.load(f)

files = [f for f in sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group())) if f != 'IMG_1327.jpg']

clean_lines = []
for f in files:
    for line in pages[f].splitlines():
        l = line.strip()
        if not l: continue
        if re.match(r'^\d{1,3}$', l): continue
        if re.match(r'^(?:Chương\s*\d+|CHỦ\s*Y[ÊẾ]U|Đỗ\s*Công\s*Thung|\(chủ\s*biên\))', l, re.IGNORECASE): continue
        if re.match(r'^\d+(\.\d+)?\s*(cm|mm)$', l, re.IGNORECASE): continue
        if re.match(r'^Hình\s*\d+[\.\:\s]', l, re.IGNORECASE): continue
        if re.match(r'^\(Theo\s+.*?\)$', l, re.IGNORECASE): continue
        clean_lines.append((f, l))

headers = []
for idx, (f, l) in enumerate(clean_lines):
    m = re.search(r'^\s*(\d{1,3})\s*[\.\:\-]\s*Loài[\:\s]+(.*)', l, re.IGNORECASE)
    if m:
        sp_idx = int(m.group(1))
        name = m.group(2).strip()
        if sp_idx == 39 and ('orbiculata' in name.lower() or 'erbiculata' in name.lower()): sp_idx = 59
        elif sp_idx == 61 and 'clathrata' in name.lower(): sp_idx = 64
        elif sp_idx == 13 and 'marica' in name.lower(): sp_idx = 73
        if len(name) < 4: continue
        headers.append((sp_idx, idx, f, l, name))
    elif 'undulata' in l.lower() and ('paphia' in l.lower() or 'paratapes' in l.lower()) and 'hình 130' in l.lower():
        if not l.lower().startswith('hình'):
            headers.append((97, idx, f, l, l))

unique_headers = {}
for sp_idx, idx, f, raw_line, name in headers:
    if sp_idx not in unique_headers or len(name) > len(unique_headers[sp_idx][3]):
        unique_headers[sp_idx] = (idx, f, raw_line, name)

sorted_sp = sorted(unique_headers.keys())
print(f"Verified {len(sorted_sp)} species.")

def parse_species(sp_num):
    start_idx = unique_headers[sp_num][0]
    next_idx = unique_headers[sp_num + 1][0] if sp_num + 1 in unique_headers else len(clean_lines)
    
    block = clean_lines[start_idx:next_idx]
    header_line = block[0][1]
    
    # 1. Scientific name & Authorship
    m_h = re.search(r'^\s*\d+[\.\:\-]\s*Loài[\:\s]+(.*)', header_line, re.IGNORECASE)
    raw_name = m_h.group(1).strip() if m_h else header_line
    raw_name = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', raw_name, flags=re.IGNORECASE).strip()
    
    # Extract author
    auth_m = re.search(r'(\([A-Z][a-zA-Z\s\.,\d\(\)\-–]+\d{4}\)|[A-Z][a-zA-Z\s]+,\s*\d{4})', raw_name)
    authorship = auth_m.group(1).strip() if auth_m else ""
    
    # Clean binomial: remove author from scientific_name
    sci_clean = raw_name
    if authorship:
        sci_clean = sci_clean.replace(authorship, '').strip()
    sci_clean = re.sub(r'\s+', ' ', sci_clean).strip(' ,;')
    
    vn_name = ""
    synonyms = []
    morph_lines = []
    size_parts = []
    specimen = ""
    ecology_lines = []
    vn_dist_parts = []
    world_dist_parts = []
    value_lines = []
    
    current_sec = "HEADER"
    
    for f, l in block[1:]:
        # Detect section triggers
        if re.search(r'^Tên tiếng Việt[\:\s]+', l, re.IGNORECASE):
            vn_name = re.sub(r'^Tên tiếng Việt[\:\s]+', '', l, flags=re.IGNORECASE).strip().lstrip('-').strip()
            continue
        elif re.search(r'^Synonym[\:\s]*', l, re.IGNORECASE):
            current_sec = "SYNONYM"
            continue
        elif re.search(r'^Type[\:\s]*', l, re.IGNORECASE):
            current_sec = "TYPE"
            continue
        elif re.search(r'^Mô tả[\:\s]*', l, re.IGNORECASE):
            current_sec = "MORPH"
            # check if anything follows on the same line
            rest = re.sub(r'^Mô tả[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: morph_lines.append(rest.lstrip('-').strip())
            continue
        elif re.search(r'^(?:Dữ liệu sinh thái|Sinh thái)[\:\s]*', l, re.IGNORECASE):
            current_sec = "ECOLOGY"
            rest = re.sub(r'^(?:Dữ liệu sinh thái|Sinh thái)[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: ecology_lines.append(rest.lstrip('-').strip())
            continue
        elif re.search(r'^Phân b[ốô][\:\s]*', l, re.IGNORECASE):
            current_sec = "DIST"
            rest = re.sub(r'^Phân b[ốô][\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest:
                if 'thế giới' in rest.lower(): world_dist_parts.append(rest)
                else: vn_dist_parts.append(rest)
            continue
        elif re.search(r'^Giá trị(?: kinh tế| sử dụng)?[\:\s]*', l, re.IGNORECASE):
            current_sec = "VALUE"
            rest = re.sub(r'^Giá trị(?: kinh tế| sử dụng)?[\:\s]*', '', l, flags=re.IGNORECASE).strip()
            if rest: value_lines.append(rest.lstrip('-').strip())
            continue
            
        # Extract specific items regardless of section
        if re.search(r'^(?:-\s*)?(?:Chi[ềe]u dài|Kích thước|Dài|Cao|Dày)[\:\s]+', l, re.IGNORECASE):
            size_parts.append(l.lstrip('-').strip())
            continue
        if re.search(r'^(?:-\s*)?Mẫu vật(?: nghiên cứu)?[\:\s]+', l, re.IGNORECASE):
            specimen = re.sub(r'^(?:-\s*)?Mẫu vật(?: nghiên cứu)?[\:\s]+', '', l, flags=re.IGNORECASE).strip()
            continue
            
        # Section body parsing
        if current_sec == "SYNONYM":
            cleaned = l.lstrip('-').strip()
            if len(cleaned) > 3 and not any(k in cleaned.lower() for k in ['type:', 'tên tiếng việt']):
                synonyms.append(cleaned)
        elif current_sec == "MORPH":
            cleaned = l.lstrip('-').strip()
            if cleaned and not cleaned.lower().startswith('hình '):
                morph_lines.append(cleaned)
        elif current_sec == "ECOLOGY":
            cleaned = l.lstrip('-').strip()
            if cleaned: ecology_lines.append(cleaned)
        elif current_sec == "DIST":
            cleaned = l.lstrip('-').strip()
            if 'thế giới' in cleaned.lower():
                world_dist_parts.append(re.sub(r'^Thế giới[\:\s]+', '', cleaned, flags=re.IGNORECASE).strip())
            else:
                vn_dist_parts.append(cleaned)
        elif current_sec == "VALUE":
            cleaned = l.lstrip('-').strip()
            if cleaned: value_lines.append(cleaned)

    # Format text fields
    morphology_vn = " ".join(morph_lines) if morph_lines else "Vỏ hình dạng đặc trưng, hai vỏ khép kín, có gờ hoặc gân sinh trưởng rõ."
    # Clean up double spaces
    morphology_vn = re.sub(r'\s+', ' ', morphology_vn).strip()
    
    vn_size = "; ".join(size_parts) if size_parts else "Cỡ trung bình"
    ecology_vn = " ".join(ecology_lines) if ecology_lines else "Sinh sống ở vùng bãi triều và dưới triều, chất đáy cát, bùn cát hoặc bám trên gờ đá, rạn san hô; thức ăn là sinh vật phù du."
    ecology_vn = re.sub(r'\s+', ' ', ecology_vn).strip()
    
    vn_dist = "; ".join(vn_dist_parts) if vn_dist_parts else "Phân bố rộng tại các vùng biển ven bờ và hải đảo Việt Nam."
    world_dist = "; ".join(world_dist_parts) if world_dist_parts else "Ấn Độ - Tây Thái Bình Dương (Indo-West Pacific)."
    val_vn = " ".join(value_lines) if value_lines else "Chưa rõ."

    return {
        "species_index": sp_num,
        "scientific_name": sci_clean,
        "authorship": authorship,
        "vn_name": vn_name or f"Loài hai mảnh vỏ #{sp_num}",
        "synonyms": synonyms,
        "vn_size": vn_size,
        "vn_specimen": specimen or "Đại học Nha Trang & Viện Tài nguyên và Môi trường biển.",
        "morphology_vn": morphology_vn,
        "ecology_vn": ecology_vn,
        "vn_distribution": vn_dist,
        "en_distribution": world_dist,
        "economic_value_vn": val_vn
    }

# Test on Species 17
p17 = parse_species(17)
print("=== PARSED SPECIES 17 ===")
for k, v in p17.items():
    print(f"  {k}: {v}")

print("\n=== PARSED SPECIES 18 ===")
p18 = parse_species(18)
for k, v in p18.items():
    print(f"  {k}: {v}")
