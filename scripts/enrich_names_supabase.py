import json
import time
import os
import sys
import ssl
import argparse
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_dotenv():
    env_path = os.path.join(BASE, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_dotenv()

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('VITE_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('✗ Missing SUPABASE_SERVICE_ROLE_KEY or SUPABASE_URL in .env', file=sys.stderr)
    sys.exit(1)


# Bypass SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def fetch_wikidata_info(sci_name):
    try:
        url_search = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(sci_name)}&language=en&format=json&limit=3"
        req = urllib.request.Request(url_search, headers={'User-Agent': 'AntigravityFish/1.0 (contact@haitrinh.org)'})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            hits = res.get('search', [])
            if not hits:
                return None
            entity_id = hits[0]['id']

        url_get = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&props=labels|aliases&languages=en|vi&format=json"
        req_get = urllib.request.Request(url_get, headers={'User-Agent': 'AntigravityFish/1.0'})
        with urllib.request.urlopen(req_get, context=ctx, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            entity = data.get('entities', {}).get(entity_id, {})
            labels = entity.get('labels', {})
            aliases = entity.get('aliases', {})
            return {
                'en_name': labels.get('en', {}).get('value', ''),
                'vi_name': labels.get('vi', {}).get('value', ''),
                'en_aliases': [a['value'] for a in aliases.get('en', [])],
                'vi_aliases': [a['value'] for a in aliases.get('vi', [])]
            }
    except Exception as e:
        return None

def is_valid_vi(name):
    """Chỉ lấy tên có ký tự tiếng Việt (non-ASCII), tránh lấy tên khoa học."""
    return name and not all(ord(c) < 128 for c in name.strip())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Ghi đè kể cả khi đã có dữ liệu')
    parser.add_argument('--collection', type=str, default='ca-bien', help='ID của collection cần enrich')
    args = parser.parse_args()

    print(f"Fetching species from Supabase (collection_id = {args.collection})...")
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.{args.collection}&select=id,scientific_name,worms_accepted_name,en_common_name,vn_alternate_names,vn_name"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            species_list = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    targets = []
    for sp in species_list:
        if args.force:
            targets.append(sp)
            continue
            
        common = (sp.get('en_common_name') or '').strip()
        alt_names = sp.get('vn_alternate_names')
        if isinstance(alt_names, str):
            alt_names = [n.strip() for n in alt_names.split(',') if n.strip()]
        if not alt_names:
            alt_names = []
            
        sci = sp.get('scientific_name') or ''
        
        # Cần enrich nếu: en_common_name trống, hoặc en_common_name giống hệt tên khoa học, hoặc ko có vn_alternate_names
        if not common or common.lower() == sci.lower() or not alt_names:
            targets.append(sp)

    print(f"📊 Cá biển tổng số: {len(species_list)} loài")
    print(f"   Cần enrich: {len(targets)} loài")
    print("─" * 50)

    success_count = 0
    updated_count = 0
    missing = []

    for i, sp in enumerate(targets):
        sp_id = sp['id']
        sci_name = sp.get('worms_accepted_name') or sp.get('scientific_name')
        if not sci_name:
            continue
            
        print(f"[{i+1}/{len(targets)}] Đang tra {sci_name} ...", end=" ", flush=True)
        
        wiki_data = fetch_wikidata_info(sci_name)
        if not wiki_data:
            print("❌ Không tìm thấy")
            missing.append((sp_id, sci_name))
            time.sleep(0.5)
            continue

        success_count += 1
        
        new_en = sp.get('en_common_name') or ''
        
        alt_names = sp.get('vn_alternate_names')
        if isinstance(alt_names, str):
            new_alt = [n.strip() for n in alt_names.split(',') if n.strip()]
        else:
            new_alt = alt_names or []
        
        # Resolve English Name
        if not new_en or new_en.lower() == sci_name.lower() or args.force:
            if wiki_data['en_name']:
                new_en = wiki_data['en_name']
            elif wiki_data['en_aliases']:
                new_en = wiki_data['en_aliases'][0]
        
        # Tiền xử lý chữ cái đầu viết hoa
        if new_en:
            new_en = new_en[:1].upper() + new_en[1:]
            
        # Resolve VN Aliases
        vn_candidates = set(new_alt)
        if wiki_data['vi_name'] and is_valid_vi(wiki_data['vi_name']):
            vn_candidates.add(wiki_data['vi_name'])
        for alias in wiki_data['vi_aliases']:
            if is_valid_vi(alias):
                vn_candidates.add(alias)
                
        # Bỏ tên chính thức khỏi alternateNames
        main_vn = sp.get('vn_name') or ''
        if main_vn in vn_candidates:
            vn_candidates.remove(main_vn)
            
        new_alt_list = list(vn_candidates)
        # Format lại vn_alternate_names thành chuỗi (vì Supabase đang để text, xem import script)
        new_alt_str = ", ".join(new_alt_list)
        old_alt_str = sp.get('vn_alternate_names') or ''
        
        has_change = (new_en != (sp.get('en_common_name') or '')) or (new_alt_str != old_alt_str)
        
        if has_change:
            payload = {}
            if new_en != (sp.get('en_common_name') or ''): payload['en_common_name'] = new_en
            if new_alt_str != old_alt_str: payload['vn_alternate_names'] = new_alt_str
            
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            patch_req = urllib.request.Request(patch_url, data=json.dumps(payload).encode('utf-8'), headers=HEADERS, method='PATCH')
            
            try:
                with urllib.request.urlopen(patch_req, context=ctx) as r:
                    r.read()
                print(f"✅ Đã cập nhật ({new_en}, {new_alt_str})")
                updated_count += 1
            except Exception as e:
                print(f"⚠️ Lỗi cập nhật Supabase: {e}")
        else:
            print("✅ Có dữ liệu (Không đổi)")
            
        time.sleep(1)

    print("\n✅ Enrichment hoàn tất:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 Tổng loài cần enrich: {len(targets)}")
    print(f"  ✅ Tìm thấy dữ liệu Wikidata: {success_count} ({success_count/max(1,len(targets))*100:.0f}%)")
    print(f"  ✅ Đã cập nhật Supabase: {updated_count}")
    print(f"  ❌ Không tìm thấy: {len(missing)}")

if __name__ == '__main__':
    main()
