import json, re

# Load all ca-bien species
with open('.backups/supabase--species--cabien-all-taxonomy-before-fix.backup.json') as f:
    all_sp = json.load(f)

# Load tap 3 lines
with open('scratch/tap3_toc_full_raw.txt') as f:
    lines = [l.strip() for l in f.readlines()]

# Family markers for Tap 3
family_markers = []
for i, line in enumerate(lines):
    if line.startswith('HỌ CÁ ') or line.startswith('HỌ PHỤ CÁ ') or line.startswith('HỌ HỒNG'):
        m = re.search(r'(HỌ(?:\s+PHỤ)?\s+[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ\s\-\(\)]+?)\s+([A-Z]{4,}(?:IDAE|INAE))', line)
        if m:
            clean_vn = 'Họ ' + ' '.join(w.capitalize() for w in m.group(1).replace('HỌ PHỤ ', '').replace('HỌ ', '').split())
            clean_lat = m.group(2).strip().capitalize()
            family_markers.append((i, clean_vn, clean_lat))

# Genus markers for Tap 3
genus_markers = []
for i, line in enumerate(lines):
    m = re.search(r'Giống\s+(?:\d+[\.:]\s*)?(?:Giống\s+)?([^\.]+?)\s+([A-Z][a-z]+)\s+', line)
    if m:
        genus_markers.append((i, m.group(1).strip(), m.group(2).strip()))

tap3_sp = [s for s in all_sp if s.get('volume') == 3]
sp_line = {}
for i, line in enumerate(lines):
    m = re.match(r'^(\d{1,3})[\.,\s]', line)
    if m:
        idx = int(m.group(1))
        if 1 <= idx <= 518 and idx not in sp_line:
            sp_line[idx] = i

for sp in tap3_sp:
    idx = sp['species_index']
    if idx not in sp_line:
        sci = sp['scientific_name'].strip().lower()
        parts = sci.split()
        if len(parts) >= 2:
            gen, ep = parts[0], parts[1]
            for i, line in enumerate(lines):
                ll = line.lower()
                if ep in ll and (gen in ll or len(ep) > 5):
                    sp_line[idx] = i
                    break

# Map for Tap 3
tap3_updates = {}
subfamily_to_family = {
    'Serraninae': ('Họ Cá Mú', 'Serranidae'),
    'Oligorrinae': ('Họ Cá Vược Nhật', 'Lateolabracidae'),
    'Centrogenysinae': ('Họ Cá Mao Quỷ', 'Centrogenyidae'),
    'Naucratinae': ('Họ Cá Khế', 'Carangidae'),
    'Scomberoidinae': ('Họ Cá Khế', 'Carangidae'),
    'Trachinotinae': ('Họ Cá Khế', 'Carangidae'),
    'Caranginae': ('Họ Cá Khế', 'Carangidae'),
    'Lutianidae': ('Họ Cá Hồng', 'Lutjanidae'),
    'Brachiostegidae': ('Họ Cá Đầu Vuông', 'Branchiostegidae'),
    'Glaucosomiidae': ('Họ Cá Lá', 'Glaucosomatidae'),
    'Theraponidae': ('Họ Cá Ông Căng', 'Terapontidae'),
    'Pomadasyidae': ('Họ Cá Sạo', 'Haemulidae'),
}

for sp in tap3_sp:
    idx = sp['species_index']
    line_no = sp_line[idx]
    
    # closest family
    fam_candidates = [f for f in family_markers if f[0] <= line_no]
    fam = fam_candidates[-1] if fam_candidates else family_markers[0]
    fam_vn = fam[1]
    fam_lat = fam[2]
    
    if fam_lat in subfamily_to_family:
        fam_vn, fam_lat = subfamily_to_family[fam_lat]
    
    # Normalize some names
    if fam_vn == 'Họ Hồng': fam_vn = 'Họ Cá Hồng'
    if fam_vn == 'Họ Cá Chim Den': fam_vn = 'Họ Cá Chim Đen'
    if fam_vn == 'Họ Cá Đồng (lượng)': fam_vn = 'Họ Cá Đồng (Cá Lượng)'
    if fam_vn == 'Họ Cá Rô Biển (cá Thia)': fam_vn = 'Họ Cá Rô Biển (Cá Thia)'
    if fam_vn == 'Họ Cá Mao Quỉ': fam_vn = 'Họ Cá Mao Quỷ'

    # closest genus
    gen_candidates = [g for g in genus_markers if g[0] <= line_no]
    first_word_sci = sp['scientific_name'].split()[0]
    if gen_candidates and gen_candidates[-1][2].lower() == first_word_sci.lower():
        gen_vn = gen_candidates[-1][1]
        gen_lat = gen_candidates[-1][2]
    else:
        gen_vn = f"Cá {sp['vn_name'].split()[-1]}"
        gen_lat = first_word_sci

    tap3_updates[sp['id']] = {
        'tax_class_vn': 'Lớp Cá Xương',
        'tax_class_latin': 'Osteichthyes',
        'tax_order_vn': 'Bộ Cá Vược',
        'tax_order_latin': 'Perciformes',
        'tax_family_vn': fam_vn,
        'tax_family_latin': fam_lat,
        'tax_genus_vn': gen_vn,
        'tax_genus_latin': gen_lat
    }

print(f"Prepared updates for {len(tap3_updates)} species of Tap 3.")

# Check how many still missing in total
print("Now analyzing standardization for Tap 1, 2, 5, 6...")
total_updates = {}
total_updates.update(tap3_updates)

# Tap 1 fixes
tap1_genus_fixes = {
    'tap1-species-23': ('Cá Nhám răng chìa', 'Negogaleus'),
    'tap1-species-24': ('Cá Nhám răng chìa', 'Negogaleus'),
    'tap1-species-25': ('Cá Nhám răng chìa', 'Negogaleus'),
    'tap1-species-26': ('Cá Nhám răng chìa', 'Negogaleus'),
    'tap1-species-27': ('Cá Nhám răng chìa', 'Negogaleus'),
}

for sp in all_sp:
    sp_id = sp['id']
    vol = sp.get('volume')
    if vol == 3:
        continue # handled above
    
    fam_vn = sp.get('tax_family_vn') or ''
    fam_lat = sp.get('tax_family_latin') or ''
    ord_vn = sp.get('tax_order_vn') or ''
    ord_lat = sp.get('tax_order_latin') or ''
    gen_vn = sp.get('tax_genus_vn') or ''
    gen_lat = sp.get('tax_genus_latin') or ''
    class_vn = sp.get('tax_class_vn') or 'Lớp Cá Xương'
    class_lat = sp.get('tax_class_latin') or 'Osteichthyes'

    changed = False
    
    # Tap 1 genus fixes
    if sp_id in tap1_genus_fixes:
        gen_vn, gen_lat = tap1_genus_fixes[sp_id]
        changed = True

    # Tap 5 species 86 fix
    if sp_id == 'tap5-species-86':
        ord_vn = 'Bộ Cá Bơn'
        ord_lat = 'Pleuronectiformes'
        fam_vn = 'Họ Cá Ngộ'
        fam_lat = 'Psettodidae'
        gen_vn = 'Cá Ngộ'
        gen_lat = 'Psettodes'
        changed = True

    # Normalize family prefix
    if fam_vn:
        # Clean latin leaks in vn: e.g. "Họ Cá Giống Đĩa Platyrhinidae" -> "Họ Cá Giống Đĩa"
        fam_vn = re.sub(r'\s+[A-Z][a-z]+idae\b', '', fam_vn)
        fam_vn = re.sub(r'^HỌ\s+', 'Họ ', fam_vn)
        fam_vn = re.sub(r'^Họ\s+CÁ\s+', 'Họ Cá ', fam_vn)
        if not fam_vn.startswith('Họ '):
            fam_vn = 'Họ ' + fam_vn
            changed = True

    if fam_lat:
        fam_lat = fam_lat.replace('Family ', '').strip().capitalize()

    # Normalize order prefix
    if ord_vn:
        ord_vn = re.sub(r'^BỘ\s+', 'Bộ ', ord_vn)
        if not ord_vn.startswith('Bộ '):
            ord_vn = 'Bộ ' + ord_vn
            changed = True

    # Fallback genus latin from scientific name if missing
    if not gen_lat:
        gen_lat = sp['scientific_name'].split()[0].capitalize()
        changed = True

    if not gen_vn:
        gen_vn = f"Cá {sp['vn_name'].split()[-1]}"
        changed = True

    if changed:
        total_updates[sp_id] = {
            'tax_class_vn': class_vn,
            'tax_class_latin': class_lat,
            'tax_order_vn': ord_vn,
            'tax_order_latin': ord_lat,
            'tax_family_vn': fam_vn,
            'tax_family_latin': fam_lat,
            'tax_genus_vn': gen_vn,
            'tax_genus_latin': gen_lat
        }

print(f"Total species to update across all 6 volumes: {len(total_updates)} / {len(all_sp)}")

with open('scratch/full_fish_taxonomy_updates.json', 'w', encoding='utf-8') as f:
    json.dump(total_updates, f, ensure_ascii=False, indent=2)

print("Saved plan to scratch/full_fish_taxonomy_updates.json")
