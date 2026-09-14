import json, re

with open('scratch/parsed_toc_species.json') as f:
    toc = json.load(f)

with open('scratch/tap4_species.json') as f:
    db = json.load(f)

db_by_idx = {sp.get('species_index'): sp for sp in db}

# Clean OCR artifacts in TOC names
# Regex to parse TOC 'raw' field: e.g. "Cá Bàng Chài sọc to Bodianus macrurus (Gunther, 1862)"
diffs = []
all_341 = {}

for i in range(1, 342):
    t = toc.get(str(i), {})
    raw = t.get('raw', '').strip()
    fam = t.get('family', '')
    gen = t.get('genus', '')

    db_sp = db_by_idx.get(i)
    
    all_341[i] = {
        'index': i,
        'toc_raw': raw,
        'toc_family': fam,
        'toc_genus': gen,
        'db_id': db_sp.get('id') if db_sp else None,
        'db_vn_name': db_sp.get('vn_name') if db_sp else None,
        'db_scientific_name': db_sp.get('scientific_name') if db_sp else None,
        'db_family_vn': db_sp.get('tax_family_vn') if db_sp else None
    }

print(f"Total processed: {len(all_341)}")
# Print samples of discrepancies
count_diff = 0
for i in range(1, 342):
    info = all_341[i]
    db_vn = info['db_vn_name'] or '[MISSING]'
    db_sn = info['db_scientific_name'] or '[MISSING]'
    # Check if mismatch
    # print differences
    if info['db_id'] is None:
        print(f"MISSING #{i}: {info['toc_raw'][:70]}")
    elif 51 <= i <= 61:
        print(f"REPLACE #{i}: DB=[{db_vn} | {db_sn}] -> TOC=[{info['toc_raw'][:70]}]")
    elif i in [78, 105, 106, 107, 108]:
        print(f"CRITICAL #{i}: DB=[{db_vn} | {db_sn}] -> TOC=[{info['toc_raw'][:70]}]")

