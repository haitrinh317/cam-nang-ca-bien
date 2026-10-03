import json, re

with open('/tmp/bivalvia_clean_ocr_cache.json') as f:
    pages = json.load(f)

# Sort files and exclude duplicate IMG_1327
files = [f for f in sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group())) if f != 'IMG_1327.jpg']

# Clean lines while filtering noise
clean_lines = []
for f in files:
    for line in pages[f].splitlines():
        l = line.strip()
        if not l: continue
        
        # 1. Drop page numbers (e.g. 73, 74, 85)
        if re.match(r'^\d{1,3}$', l):
            continue
            
        # 2. Drop running headers / authors
        if re.match(r'^(?:Chương\s*\d+|CHỦ\s*Y[ÊẾ]U|Đỗ\s*Công\s*Thung|\(chủ\s*biên\))', l, re.IGNORECASE):
            continue
            
        # 3. Drop scale bar lines (e.g. 1 cm, 2 cm, 11 cm)
        if re.match(r'^\d+(\.\d+)?\s*(cm|mm)$', l, re.IGNORECASE):
            continue
            
        # 4. Drop figure captions and citations
        if re.match(r'^Hình\s*\d+[\.\:\s]', l, re.IGNORECASE):
            continue
        if re.match(r'^\(Theo\s+.*?\)$', l, re.IGNORECASE):
            continue
            
        clean_lines.append((f, l))

# Identify 143 species headers
headers = []
for idx, (f, l) in enumerate(clean_lines):
    m = re.search(r'^\s*(\d{1,3})\s*[\.\:\-]\s*Loài[\:\s]+(.*)', l, re.IGNORECASE)
    if m:
        sp_idx = int(m.group(1))
        name = m.group(2).strip()
        if sp_idx == 39 and ('orbiculata' in name.lower() or 'erbiculata' in name.lower()): sp_idx = 59
        elif sp_idx == 61 and 'clathrata' in name.lower(): sp_idx = 64
        elif sp_idx == 13 and 'marica' in name.lower(): sp_idx = 73
        
        # Discard incomplete fragmented headers like '26. Loài Lít' or '26. Loài Lu' if followed by full header
        if len(name) < 4:
            continue
        headers.append((sp_idx, idx, f, l, name))
    elif 'undulata' in l.lower() and ('paphia' in l.lower() or 'paratapes' in l.lower()) and 'hình 130' in l.lower():
        if not l.lower().startswith('hình'):
            headers.append((97, idx, f, l, l))

# Keep the most complete / proper header for each species index
unique_headers = {}
for sp_idx, idx, f, raw_line, name in headers:
    if sp_idx not in unique_headers:
        unique_headers[sp_idx] = (idx, f, raw_line, name)
    else:
        # Pick the one with longer name / not a fragment
        if len(name) > len(unique_headers[sp_idx][3]):
            unique_headers[sp_idx] = (idx, f, raw_line, name)

print(f"Total unique species headers: {len(unique_headers)}")
sorted_indices = sorted(unique_headers.keys())

# Let us verify species 16, 17, 18, 1, 143
for sp_num in [1, 16, 17, 18, 25, 26, 97, 143]:
    if sp_num in unique_headers:
        idx, f, raw_line, name = unique_headers[sp_num]
        print(f"Species #{sp_num}: {name} ({f}, line {idx})")
