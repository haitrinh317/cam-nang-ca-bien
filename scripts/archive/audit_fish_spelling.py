#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_fish_spelling.py
Rà soát toàn diện lỗi chính tả, sai danh pháp khoa học và sai tên tiếng Việt
cho toàn bộ collection 'ca-bien' (1,767 loài Tập 1-6).
"""

import sys
import os
import re
import json
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('.env.local')
load_dotenv('.env')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SERVICE_KEY:
    print('[LOI] Thieu credentials Supabase!')
    exit(1)

PAGE_SIZE = 1000
all_species = []
offset = 0

print('Dang tai du lieu ca-bien tu Supabase...')
while True:
    url = f'{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&select=id,species_index,volume,vn_name,scientific_name,authorship,worms_id,worms_status,worms_accepted_name,tax_order_latin,tax_family_latin,tax_genus_latin,biology&order=volume,species_index&limit={PAGE_SIZE}&offset={offset}'
    req = urllib.request.Request(url, headers={
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Range-Unit': 'items'
    })
    with urllib.request.urlopen(req) as resp:
        batch = json.loads(resp.read().decode('utf-8'))
        all_species.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

print(f'-> Da tai tong cong {len(all_species)} loai ca bien.\n')

sci_anomalies = []
vn_anomalies = []
worms_missing = []
biology_missing = []

BINOMIAL_REGEX = re.compile(r'^[A-Z][a-z\-]+(\s+\([A-Za-z\-]+\))?\s+[a-z\-]+$')

VN_TYPO_PATTERNS = [
    (r'\bCá đồi\b', 'Nghi ngờ lỗi "Cá đối" (đã từng gặp ở Tập 4)', True),
    (r'\bCá đoi\b', 'Nghi ngờ lỗi "Cá đối" hoặc "Cá đao"', True),
    (r'\bCá nham\b', 'Nghi ngờ thiếu dấu "Cá nhám"', True),
    (r'\bCá trich\b', 'Nghi ngờ thiếu dấu "Cá trích"', True),
    (r'\bCá bơng\b', 'Nghi ngờ lỗi OCR "Cá bống"', True),
    (r'\bCá chuon\b', 'Nghi ngờ thiếu dấu "Cá chuồn"', True),
    (r'\s{2,}', 'Thừa nhiều khoảng trắng liên tiếp', False),
    (r'[,\.\?\/\\!@#$%^&*()_=+]$', 'Dính dấu câu thừa ở cuối tên', False),
    (r'^(Lớp|Bộ|Họ|Giống|Chi)\s+', 'Dính tiền tố phân loại vào tên loài', True),
    (r'^[a-zà-ỹđ]', 'Chữ cái đầu tiên không viết hoa', False)
]

for sp in all_species:
    sp_id = sp.get('id')
    vol = sp.get('volume')
    idx = sp.get('species_index')
    sci = (sp.get('scientific_name') or '').strip()
    vn = (sp.get('vn_name') or '').strip()
    worms_st = sp.get('worms_status')
    worms_id = sp.get('worms_id')
    bio = sp.get('biology')

    if not worms_st or worms_st.lower() in ('not_found', 'unverified') or not worms_id:
        worms_missing.append({
            'id': sp_id, 'vol': vol, 'idx': idx, 'vn': vn, 'sci': sci,
            'worms_id': worms_id, 'status': worms_st
        })

    if not bio or not isinstance(bio, dict) or len(bio) == 0:
        biology_missing.append({
            'id': sp_id, 'vol': vol, 'idx': idx, 'vn': vn, 'sci': sci
        })

    sci_issues = []
    if not sci:
        sci_issues.append('Tên khoa học bị TRỐNG')
    else:
        if re.search(r'\d', sci):
            sci_issues.append(f'Chứa số trong danh pháp: {sci}')
        if re.search(r'[,\.\?\/\\!@#$%^&*_=+[\]{}]', sci):
            sci_issues.append(f'Chứa ký tự lạ/dấu câu thừa: {sci}')
        words = sci.split()
        if len(words) < 2:
            sci_issues.append(f'Thiếu định ngữ loài: {sci}')
        elif len(words) > 3 and not ('(' in sci and ')' in sci):
            sci_issues.append(f'Nhiều hơn 2 từ (nghi ngờ dính tên tác giả/năm): {sci}')
        
        if words:
            genus_word = words[0]
            if not genus_word[0].isupper():
                sci_issues.append(f'Chi không viết hoa: {genus_word}')
            if len(words) >= 2 and not words[-1][0].islower():
                sci_issues.append(f'Tên loài không viết thường: {words[-1]}')

        if not BINOMIAL_REGEX.match(sci) and len(sci_issues) == 0:
            sci_issues.append(f'Cấu trúc danh pháp không chuẩn nhị thức: {sci}')

    if sci_issues:
        sci_anomalies.append({
            'id': sp_id, 'vol': vol, 'idx': idx, 'vn': vn, 'sci': sci,
            'issues': sci_issues
        })

    vn_issues = []
    if not vn:
        vn_issues.append('Tên tiếng Việt bị TRỐNG')
    else:
        for pat, desc, ignore_case in VN_TYPO_PATTERNS:
            flags = re.IGNORECASE if ignore_case else 0
            if re.search(pat, vn, flags):
                vn_issues.append(f'{desc} (Khớp mẫu: {pat})')

    if vn_issues:
        vn_anomalies.append({
            'id': sp_id, 'vol': vol, 'idx': idx, 'vn': vn, 'sci': sci,
            'issues': vn_issues
        })

print('=' * 80)
print(f'BAO CAO RA SOAT DANH MUC CA BIEN (Tong: {len(all_species)} loai)')
print('=' * 80)
print(f'1. WoRMS chua xac thuc hoac not_found : {len(worms_missing)} loai ({len(worms_missing)/len(all_species)*100:.1f}%)')
print(f'2. Chua duoc enrich FishBase (biology) : {len(biology_missing)} loai ({len(biology_missing)/len(all_species)*100:.1f}%)')
print(f'3. Nghi van loi Ten Khoa Hoc (Latin)   : {len(sci_anomalies)} loai')
print(f'4. Nghi van loi Ten Tieng Viet        : {len(vn_anomalies)} loai')
print('=' * 80 + '\n')

if sci_anomalies:
    print(f'--- CHI TIET {len(sci_anomalies)} LOAI CO BAT THUONG TEN KHOA HOC ---')
    for item in sci_anomalies[:25]:
        print(f"[{item['id']}] Tap {item['vol']} #{item['idx']} | VN: '{item['vn']}' | Sci: '{item['sci']}'")
        for iss in item['issues']:
            print(f"    * {iss}")
    if len(sci_anomalies) > 25:
        print(f"    ... va {len(sci_anomalies) - 25} loai khac.")
    print()

if worms_missing:
    print(f'--- DANH SACH {len(worms_missing)} LOAI CHUA CO HOAC LOI WORMS ---')
    for item in worms_missing[:20]:
        print(f"[{item['id']}] Tap {item['vol']} #{item['idx']} | Sci: '{item['sci']}' | Status: {item['status']} | AphiaID: {item['worms_id']}")
    if len(worms_missing) > 20:
        print(f"    ... va {len(worms_missing) - 20} loai khac.")
    print()

if vn_anomalies:
    print(f'--- CHI TIET {len(vn_anomalies)} LOAI NGHI VAN LOI CHINH TA TIENG VIET ---')
    for item in vn_anomalies[:20]:
        print(f"[{item['id']}] Tap {item['vol']} #{item['idx']} | VN: '{item['vn']}' | Sci: '{item['sci']}'")
        for iss in item['issues']:
            print(f"    * {iss}")
    if len(vn_anomalies) > 20:
        print(f"    ... va {len(vn_anomalies) - 20} loai khac.")
    print()

report_data = {
    'total': len(all_species),
    'worms_missing': worms_missing,
    'biology_missing': biology_missing,
    'sci_anomalies': sci_anomalies,
    'vn_anomalies': vn_anomalies
}
with open('scratch/fish_spelling_audit_result.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)
print('Da luu chi tiet vao scratch/fish_spelling_audit_result.json')
