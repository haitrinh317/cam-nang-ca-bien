import json, re

with open('.backups/supabase--species--cabien-all-taxonomy-before-fix.backup.json') as f:
    all_sp = json.load(f)

print(f"Loaded {len(all_sp)} species.")

# Check current missing taxonomy
missing_fam = [s for s in all_sp if not s.get('tax_family_latin')]
print(f"Currently missing tax_family_latin: {len(missing_fam)}")

# Load tap 3 mapping
with open('scratch/tap3_toc_full_raw.txt') as f:
    lines = [l.strip() for l in f.readlines()]

family_markers = []
current_order_vn = 'Bộ Cá Vược'
current_order_lat = 'Perciformes'

for i, line in enumerate(lines):
    if 'BỘ PHỤ CÁ ÉP' in line:
        current_order_vn = 'Bộ Cá Vược'
        current_order_lat = 'Perciformes'
    if line.startswith('HỌ CÁ ') or line.startswith('HỌ PHỤ CÁ ') or line.startswith('HỌ HỒNG'):
        m = re.search(r'(HỌ(?:\s+PHỤ)?\s+[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ\s\-\(\)]+?)\s+([A-Z]{4,}(?:IDAE|INAE))', line)
        if m:
            clean_vn = 'Họ ' + ' '.join(w.capitalize() for w in m.group(1).replace('HỌ PHỤ ', '').replace('HỌ ', '').split())
            clean_lat = m.group(2).strip().capitalize()
            family_markers.append((i, clean_vn, clean_lat, current_order_vn, current_order_lat))

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

print(f"Tap 3 line resolution: {len(sp_line)} / {len(tap3_sp)}")
