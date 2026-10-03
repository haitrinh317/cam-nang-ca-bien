"""
enrich_names.py — Tổng quát hóa cho mọi tập
Bổ sung specs.en.commonName và specs.vn.alternateNames từ Wikidata.
(Cập nhật 2026-08-23: Sử dụng trực tiếp Supabase REST API, không dùng file json local)

Usage:
  python scripts/enrich_names.py               # Tất cả tập, missing-only
  python scripts/enrich_names.py --volume 3    # Chỉ tập 3
  python scripts/enrich_names.py --force       # Ghi đè kể cả đã có
"""
import json
import urllib.request
import urllib.parse
import sys
import ssl
import time
import argparse
import os

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ── Load .env ──
def _load_dotenv():
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def fetch_supabase(collection_id="ca-bien", volume=None):
    all_data = []
    limit = 1000
    offset = 0
    while True:
        url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.{collection_id}"
        if volume:
            url += f"&volume=eq.{volume}"
        url += f"&limit={limit}&offset={offset}"
        
        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not data:
                break
            all_data.extend(data)
            offset += limit
            if len(data) < limit:
                break
    return all_data

def update_supabase(rows):
    url = f"{SUPABASE_URL}/rest/v1/species"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    data = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.read().decode('utf-8')[:300]}", file=sys.stderr)
        return e.code

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
    except Exception:
        return None

def is_valid_vi(name):
    """Chỉ lấy tên có ký tự tiếng Việt (non-ASCII), tránh lấy tên khoa học."""
    return name and not all(ord(c) < 128 for c in name.strip())

def needs_enrich(sp, force=False):
    if force:
        return True
    common = (sp.get('en_common_name') or '').strip()
    alt = (sp.get('vn_alternate_names') or '').strip()
    sci = sp.get('scientific_name', '')
    return not common or common == sci or not alt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--volume', type=int, default=None, help='Chỉ enrich tập cụ thể (1-5)')
    parser.add_argument('--force', action='store_true', help='Ghi đè kể cả khi đã có dữ liệu')
    args = parser.parse_args()

    targets = fetch_supabase(collection_id="ca-bien", volume=args.volume)
    label = f"Tập {args.volume}" if args.volume else "Tất cả các tập"

    need_enrich = [s for s in targets if needs_enrich(s, args.force)]
    print(f"📊 {label}: {len(targets)} loài tổng")
    print(f"   Cần enrich: {len(need_enrich)} loài")
    print("─" * 50)

    if not need_enrich:
        print("✅ Tất cả đã có tên, không cần enrich.")
        return

    success_count = 0
    updated_count = 0
    missing = []
    
    batch = []
    batch_size = 50

    for idx, sp in enumerate(need_enrich, 1):
        sp_id = sp.get('id')
        sci_name = sp.get('scientific_name', '').strip()
        vn_name = sp.get('vn_name', '').strip().lower()

        # Dùng acceptedName từ WoRMS nếu có (tên hiện hành)
        query_name = (sp.get('worms_accepted_name') or '').strip() or sci_name

        print(f"[{idx}/{len(need_enrich)}] {sp_id}: {query_name} ...", end=" ", flush=True)

        info = fetch_wikidata_info(query_name)
        if not info and query_name != sci_name:
            info = fetch_wikidata_info(sci_name)

        changed = False
        if info:
            current_alt = (sp.get('vn_alternate_names') or '').strip()
            alt_names = set(n.strip() for n in current_alt.split(',') if n.strip()) if current_alt else set()

            if is_valid_vi(info['vi_name']) and info['vi_name'].strip().lower() != vn_name:
                alt_names.add(info['vi_name'].strip())
            for va in info['vi_aliases']:
                if is_valid_vi(va) and va.strip().lower() != vn_name:
                    alt_names.add(va.strip())

            current_en = (sp.get('en_common_name') or '').strip()
            new_en = current_en
            if info['en_name'] and info['en_name'].strip().lower() != query_name.lower():
                new_en = info['en_name'].strip()
            elif not current_en and info['en_aliases']:
                new_en = info['en_aliases'][0].strip()

            alt_str = ', '.join(sorted(alt_names)) if alt_names else ''
            
            update_row = {}
            if new_en and (args.force or not current_en or current_en == sci_name):
                update_row['en_common_name'] = new_en
                changed = True
            if alt_str and (args.force or not current_alt):
                update_row['vn_alternate_names'] = alt_str
                changed = True

            if changed:
                update_row['id'] = sp_id # PK required for upsert
                if 'en_common_name' not in update_row:
                    update_row['en_common_name'] = current_en
                if 'vn_alternate_names' not in update_row:
                    update_row['vn_alternate_names'] = current_alt
                batch.append(update_row)
                updated_count += 1

            print(f"OK -> EN: '{new_en}', Alt VN: '{alt_str}'")
            success_count += 1
        else:
            print("Không tìm thấy.")
            missing.append(f"{sp_id}: {sci_name}")

        time.sleep(0.2)

        # Batch upsert
        if len(batch) >= batch_size:
            status = update_supabase(batch)
            if status in (200, 201):
                print(f"--- ✅ Đã ghi {len(batch)} thay đổi vào DB ---")
            else:
                print(f"--- ✗ Lỗi khi ghi vào DB (HTTP {status}) ---")
            batch = []

    # Dọn nốt batch cuối
    if batch:
        status = update_supabase(batch)
        if status in (200, 201):
            print(f"--- ✅ Đã ghi {len(batch)} thay đổi vào DB ---")

    # Ghi log loài còn thiếu
    if missing:
        os.makedirs('scratch', exist_ok=True)
        with open('scratch/enrichment_missing.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(missing))

    print(f"\n✅ Enrichment hoàn tất:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  ✅ Tìm thấy dữ liệu: {success_count}/{len(need_enrich)}")
    print(f"  ✅ Được cập nhật:    {updated_count}")
    print(f"  ❌ Không tìm thấy:  {len(missing)}")
    if missing:
        print(f"\n📋 Loài cần tra thủ công → scratch/enrichment_missing.txt")

if __name__ == '__main__':
    main()
