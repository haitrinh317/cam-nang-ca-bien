#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/enrich_sinhvatdoc_authors_and_photos.py
Bổ sung tác giả danh pháp chi cho 10 taxa dạng Genus sp.
và chuẩn hóa trường photographer trong biology->toxicology của 76 loài.
"""

import os
import sys
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    for f in ['.env.local', '.env']:
        env_path = os.path.join(BASE, f)
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip('\"\''))

load_env()
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

GENUS_AUTHORS = {
    1: 'Gray, 1867',
    2: 'Linnaeus, 1758',
    3: 'Allman, 1883',
    5: 'Lamarck, 1801',
    9: 'Péron & Lesueur, 1810',
    10: 'L. Agassiz, 1862',
    21: 'Rafinesque, 1810',
    22: 'Schinz, 1822',
    23: 'Linnaeus, 1758',
    24: 'Bloch & Schneider, 1801',
}

def main():
    print("==================================================")
    print(" CHUẨN HÓA AUTHORSHIP & PHOTOGRAPHER CHO 76 LOÀI ")
    print("==================================================")
    
    # 1. Fetch current species
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.sinh-vat-doc&select=id,species_index,authorship,biology"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        species_list = json.loads(resp.read().decode('utf-8'))
        
    print(f"Tổng số loài tải về: {len(species_list)}")
    
    # Load parsed json to get exact photographer attribution per species
    with open(os.path.join(BASE, 'scratch', 'sinhvatdoc_parsed.json'), 'r', encoding='utf-8') as fp:
        parsed = json.load(fp)
    photog_by_index = {s['species_index']: s.get('biology', {}).get('photographer') for s in parsed}

    patched = 0
    for sp in species_list:
        sp_id = sp['id']
        sp_idx = sp['species_index']
        authorship = sp.get('authorship')
        bio = sp.get('biology') or {}
        tox = bio.get('toxicology') or {}
        
        needs_patch = False
        payload = {}
        
        # 1. Authorship check
        if not authorship and sp_idx in GENUS_AUTHORS:
            payload['authorship'] = GENUS_AUTHORS[sp_idx]
            needs_patch = True
            
        # 2. Photographer check
        p_name = photog_by_index.get(sp_idx) or bio.get('photographer') or 'Tư liệu khoa học'
        if not tox.get('photographer') or tox.get('photographer') != p_name:
            tox['photographer'] = p_name
            bio['toxicology'] = tox
            bio['photographer'] = p_name
            payload['biology'] = bio
            needs_patch = True
            
        if needs_patch:
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            data = json.dumps(payload).encode('utf-8')
            preq = urllib.request.Request(patch_url, headers={**HEADERS, 'Prefer': 'return=minimal'}, data=data, method='PATCH')
            with urllib.request.urlopen(preq) as presp:
                if presp.status in (200, 204):
                    patched += 1
                    print(f"  ✓ [{sp_id}] Author: {payload.get('authorship', authorship)} | Photog: {p_name}")

    print(f"\n--> Hoàn tất: Đã patch chuẩn hóa {patched} loài trong Supabase!")

if __name__ == '__main__':
    main()
