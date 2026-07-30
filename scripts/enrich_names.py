"""
enrich_names.py — Tổng quát hóa cho mọi tập
Bổ sung specs.en.commonName và specs.vn.alternateNames từ Wikidata.

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
    specs = sp.get('specs') or {}
    en = specs.get('en') or {}
    vn = specs.get('vn') or {}
    common = (en.get('commonName') or '').strip()
    alt = (vn.get('alternateNames') or '').strip()
    sci = sp.get('scientificName', '')
    return not common or common == sci or not alt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--volume', type=int, default=None, help='Chỉ enrich tập cụ thể (1-6)')
    parser.add_argument('--force', action='store_true', help='Ghi đè kể cả khi đã có dữ liệu')
    args = parser.parse_args()

    with open('data/species.json', 'r', encoding='utf-8') as f:
        species_db = json.load(f)

    fb_sync = {}
    if os.path.exists('data/fishbase_sync.json'):
        with open('data/fishbase_sync.json', 'r', encoding='utf-8') as f:
            fb_sync = json.load(f)

    # Filter by volume
    if args.volume:
        targets = [s for s in species_db if s.get('volume') == args.volume]
        label = f"Tập {args.volume}"
    else:
        targets = species_db
        label = "Tất cả các tập"

    need_enrich = [s for s in targets if needs_enrich(s, args.force)]
    print(f"📊 {label}: {len(targets)} loài tổng")
    print(f"   Cần enrich: {len(need_enrich)} loài")
    print("─" * 50)

    success_count = 0
    updated_count = 0
    missing = []

    # Build index for fast lookup
    id_to_index = {sp['id']: i for i, sp in enumerate(species_db)}

    for idx, sp in enumerate(need_enrich, 1):
        sp_id = sp.get('id')
        sci_name = sp.get('scientificName', '').strip()
        vn_name = sp.get('vnName', '').strip().lower()

        # Dùng acceptedName từ WoRMS nếu có (tên hiện hành)
        fb_info = fb_sync.get(sp_id, {})
        query_name = (fb_info.get('acceptedName') or '').strip() or sci_name

        print(f"[{idx}/{len(need_enrich)}] {sp_id}: {query_name} ...", end=" ", flush=True)

        info = fetch_wikidata_info(query_name)
        if not info and query_name != sci_name:
            info = fetch_wikidata_info(sci_name)

        changed = False
        if info:
            # Gom alternateNames tiếng Việt
            specs = sp.get('specs') or {}
            vn_specs = specs.get('vn') or {}
            en_specs = specs.get('en') or {}
            
            current_alt = (vn_specs.get('alternateNames') or '').strip()
            alt_names = set(n.strip() for n in current_alt.split(',') if n.strip()) if current_alt else set()

            if is_valid_vi(info['vi_name']) and info['vi_name'].strip().lower() != vn_name:
                alt_names.add(info['vi_name'].strip())
            for va in info['vi_aliases']:
                if is_valid_vi(va) and va.strip().lower() != vn_name:
                    alt_names.add(va.strip())

            # CommonName tiếng Anh
            current_en = (en_specs.get('commonName') or '').strip()
            new_en = current_en
            if info['en_name'] and info['en_name'].strip().lower() != query_name.lower():
                new_en = info['en_name'].strip()
            elif not current_en and info['en_aliases']:
                new_en = info['en_aliases'][0].strip()

            alt_str = ', '.join(sorted(alt_names)) if alt_names else ''

            # Ghi vào DB (đúng path)
            db_idx = id_to_index.get(sp_id)
            if db_idx is not None:
                if 'specs' not in species_db[db_idx]:
                    species_db[db_idx]['specs'] = {'vn': {}, 'en': {}}
                if 'vn' not in species_db[db_idx]['specs']:
                    species_db[db_idx]['specs']['vn'] = {}
                if 'en' not in species_db[db_idx]['specs']:
                    species_db[db_idx]['specs']['en'] = {}

                if new_en and (args.force or not species_db[db_idx]['specs']['en'].get('commonName') or species_db[db_idx]['specs']['en'].get('commonName') == sci_name):
                    species_db[db_idx]['specs']['en']['commonName'] = new_en
                    changed = True
                if alt_str and (args.force or not species_db[db_idx]['specs']['vn'].get('alternateNames')):
                    species_db[db_idx]['specs']['vn']['alternateNames'] = alt_str
                    changed = True

            print(f"OK -> EN: '{new_en}', Alt VN: '{alt_str}'")
            success_count += 1
            if changed:
                updated_count += 1
        else:
            print("Không tìm thấy.")
            missing.append(f"{sp_id}: {sci_name}")

        time.sleep(0.2)

        # Checkpoint mỗi 50 loài
        if idx % 50 == 0:
            with open('data/species.json', 'w', encoding='utf-8') as f:
                json.dump(species_db, f, ensure_ascii=False, indent=2)
            print(f"--- ✅ Checkpoint {idx}/{len(need_enrich)} ---")

    # Ghi cuối
    with open('data/species.json', 'w', encoding='utf-8') as f:
        json.dump(species_db, f, ensure_ascii=False, indent=2)

    import shutil
    shutil.copy('data/species.json', 'public/data/species.json')

    # Ghi log loài còn thiếu
    if missing:
        with open('scratch/enrichment_missing.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(missing))

    print(f"\n✅ Enrichment hoàn tất:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  ✅ Tìm thấy dữ liệu: {success_count}/{len(need_enrich)}")
    print(f"  ✅ Được cập nhật:    {updated_count}")
    print(f"  ❌ Không tìm thấy:  {len(missing)}")
    if missing:
        print(f"\n📋 Loài cần tra thủ công → scratch/enrichment_missing.txt")
    print(f"\n📁 Đã sync: public/data/species.json")

if __name__ == '__main__':
    main()
