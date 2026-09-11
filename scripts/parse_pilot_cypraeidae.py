#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_pilot_cypraeidae.py — Ghép nối continuation giữa các trang và chuyển đổi
dữ liệu bóc tách thô thành flat Supabase rows cho Họ Ốc sứ Cypraeidae.
"""

import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

RAW_JSON = 'scratch/pilot_cypraeidae_raw.json'
OUT_JSON = 'scratch/pilot_cypraeidae_flat.json'

def clean_text(s):
    if not s:
        return None
    s = s.strip()
    # Normalize excessive spaces and newlines
    s = re.sub(r'\s+', ' ', s)
    return s if s else None

def main():
    with open(RAW_JSON, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    stitched_species = []

    for idx, p in enumerate(pages):
        info = p['page_info']
        data = p['data']
        sp_list = data.get('species', [])
        cont = data.get('continuation_from_previous_page')

        # If there is continuation from previous page, append to the last species of previous page
        if cont and stitched_species:
            last_sp = stitched_species[-1]
            cont_clean = clean_text(cont)
            print(f"[PAGE {info['pdf_pno']}] Merging continuation into {last_sp['scientific_name']}: {cont_clean[:60]}...")
            # Decide where to append based on keywords in continuation
            if 'LITERATURE' in cont_clean.upper() or 'ION collection' in cont_clean:
                last_sp['literature'] = (last_sp.get('literature') or '') + ' ' + cont_clean
            elif 'VOUCHER' in cont_clean.upper():
                last_sp['voucher_material'] = (last_sp.get('voucher_material') or '') + ' ' + cont_clean
            elif 'REMARKS' in cont_clean.upper():
                last_sp['remarks'] = (last_sp.get('remarks') or '') + ' ' + cont_clean
            else:
                # Default append to literature or remarks
                if last_sp.get('literature'):
                    last_sp['literature'] += ' ' + cont_clean
                elif last_sp.get('voucher_material'):
                    last_sp['voucher_material'] += ' ' + cont_clean
                else:
                    last_sp['remarks'] = (last_sp.get('remarks') or '') + ' ' + cont_clean

        for sp in sp_list:
            stitched_species.append(sp)

    print(f"\nTotal stitched species: {len(stitched_species)}")

    # Convert to flat Supabase rows
    flat_rows = []
    for i, sp in enumerate(stitched_species, start=1):
        sci_name = clean_text(sp.get('scientific_name'))
        authorship = clean_text(sp.get('authorship'))
        of_authors = clean_text(sp.get('of_authors'))
        synonyms = clean_text(sp.get('synonyms'))
        voucher = clean_text(sp.get('voucher_material'))
        literature = clean_text(sp.get('literature'))
        remarks = clean_text(sp.get('remarks'))

        # Prepare synonyms array
        syn_list = []
        if of_authors:
            # Extract names from of_authors
            syn_list.append(f"OF AUTHORS: {of_authors}")
        if synonyms:
            syn_list.append(f"SYNONYMS: {synonyms}")

        # Genus extraction
        parts = sci_name.split() if sci_name else []
        genus_latin = parts[0] if parts else "Cypraea"

        row = {
            "id": f"thanmem-species-{i}",
            "collection_id": "than-mem",
            "volume": 1,
            "species_index": i,
            "vn_name": "",  # To be enriched in Step 5
            "scientific_name": sci_name,
            "authorship": authorship or "",
            "tax_class_vn": "Lớp Chân bụng",
            "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Trung chân bụng",
            "tax_order_latin": "Littorinimorpha",
            "tax_family_vn": "Họ Ốc sứ",
            "tax_family_latin": "Cypraeidae",
            "tax_genus_vn": "Chi Ốc sứ",
            "tax_genus_latin": genus_latin,
            "vn_specimen": voucher,
            "en_specimen": voucher,
            "vn_literature": literature,
            "en_literature": literature,
            "en_distribution": remarks if (remarks and any(k in remarks.lower() for k in ['found', 'vietnam', 'ria', 'coast', 'ocean', 'known', 'island'])) else None,
            "en_status": remarks if (remarks and not any(k in remarks.lower() for k in ['found', 'vietnam', 'ria', 'coast', 'ocean', 'known', 'island'])) else None,
            "biology": {
                "source_book": "Marine Molluscs of Vietnam: Annotations, Voucher Material, and Species in Need of Verification (Hylleberg & Kilburn, 2003)",
                "source_volume": 1,
                "source_pages": "49-55",
                "of_authors": of_authors,
                "synonyms": syn_list if syn_list else None,
                "remarks": remarks
            }
        }
        flat_rows.append(row)

    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(flat_rows, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(flat_rows)} flat Supabase rows in {OUT_JSON}")

    # Print summary list
    print("\n--- Danh sách các loài bóc tách được (First 15 & Last 5) ---")
    for r in flat_rows[:15]:
        print(f"  [{r['species_index']:02d}] {r['scientific_name']} {r['authorship']}")
    if len(flat_rows) > 20:
        print("  ...")
        for r in flat_rows[-5:]:
            print(f"  [{r['species_index']:02d}] {r['scientific_name']} {r['authorship']}")

if __name__ == '__main__':
    main()
