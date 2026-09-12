import requests
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_sanho_wikidata.py
-------------------------
Bổ sung tên tiếng Anh (en_common_name) và tên gọi khác (vn_alternate_names)
cho các loài San hô từ Wikidata API.
"""

import os, sys, time, json, urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

env_file = '.env.local' if os.path.exists('.env.local') else '.env'
env = {}
with open(env_file) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k] = v.strip('\"').strip('\'')

SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json'
}

def search_wikidata(name):
    query = urllib.parse.quote(name)
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json&limit=3"
    req = urllib.request.Request(url, headers={'User-Agent': 'VietnameseMarineSpecies/1.0 (contact: haitrinh082@gmail.com)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('search', [])
            if results:
                entity_id = results[0]['id']
                return get_wikidata_entity(entity_id)
    except Exception as e:
        pass
    return None

def get_wikidata_entity(entity_id):
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&props=labels|aliases|descriptions&languages=en|vi&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'VietnameseMarineSpecies/1.0 (contact: haitrinh082@gmail.com)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            ent = data.get('entities', {}).get(entity_id, {})
            
            # EN label / aliases
            en_name = ""
            labels = ent.get('labels', {})
            aliases = ent.get('aliases', {})
            
            # If label in EN is not just the scientific name
            if 'en' in labels:
                val = labels['en']['value']
                en_name = val
                
            # If aliases in EN
            en_aliases = [a['value'] for a in aliases.get('en', [])]
            
            # VI label / aliases
            vi_name = ""
            if 'vi' in labels:
                vi_name = labels['vi']['value']
            vi_aliases = [a['value'] for a in aliases.get('vi', [])]
            
            return {
                "id": entity_id,
                "en_label": en_name,
                "en_aliases": en_aliases,
                "vi_label": vi_name,
                "vi_aliases": vi_aliases
            }
    except Exception as e:
        pass
    return None

def main():
    print("=== BẮT ĐẦU ENRICH TÊN GỌI TỪ WIKIDATA CHO SAN-HO ===")
    
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.san-ho&select=id,species_index,scientific_name,vn_name,en_common_name,vn_alternate_names,worms_accepted_name&order=species_index.asc"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        species_list = json.loads(resp.read().decode('utf-8'))
        
    print(f"Tổng số loài san-ho: {len(species_list)}")
    
    updated_count = 0
    for s in species_list:
        sp_id = s['id']
        sp_idx = s['species_index']
        sc = s['scientific_name']
        accepted = s.get('worms_accepted_name')
        
        if sp_idx == 30 or ' ' not in sc:
            continue
            
        # Target search name: accepted name or scientific name
        search_target = accepted if accepted else sc
        
        res = search_wikidata(search_target)
        time.sleep(0.3)
        if not res and search_target != sc:
            res = search_wikidata(sc)
            time.sleep(0.3)
            
        if not res:
            continue
            
        # Check if EN common name can be filled
        current_en = s.get('en_common_name') or ""
        best_en = current_en
        
        en_label = res.get('en_label', '')
        en_aliases = res.get('en_aliases', [])
        
        if not best_en:
            # Pick non-scientific name if possible
            for candidate in [en_label] + en_aliases:
                if candidate and candidate.lower() != sc.lower() and candidate.lower() != (accepted or '').lower():
                    best_en = candidate
                    break
                    
        # Check VI alternate names
        current_vn_alts = s.get('vn_alternate_names') or ""
        vi_candidates = []
        vi_label = res.get('vi_label', '')
        vi_aliases = res.get('vi_aliases', [])
        for v in [vi_label] + vi_aliases:
            if v and v != s.get('vn_name') and v.lower() != sc.lower() and v not in vi_candidates:
                vi_candidates.append(v)
                
        new_vn_alts = current_vn_alts
        if vi_candidates and not current_vn_alts:
            new_vn_alts = ", ".join(vi_candidates)
            
        # Patch if changed
        payload = {}
        if best_en and best_en != current_en:
            payload['en_common_name'] = best_en
        if new_vn_alts and new_vn_alts != current_vn_alts:
            payload['vn_alternate_names'] = new_vn_alts
            
        if payload:
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            try:
                requests.patch(patch_url, headers={**HEADERS, 'Content-Type': 'application/json'}, json=payload)
                updated_count += 1
                print(f"✅ [#{sp_idx:2d}] {sc} -> {payload}")
            except Exception as e:
                print(f"❌ Error patching {sp_id}: {e}")

    print(f"\n🎉 Hoàn tất enrich Wikidata cho {updated_count} loài!")

if __name__ == '__main__':
    main()
