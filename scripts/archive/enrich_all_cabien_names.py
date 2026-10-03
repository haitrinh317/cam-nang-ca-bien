"""
enrich_all_cabien_names.py
--------------------------
Bổ sung tên thường gọi (tiếng Việt & tiếng Anh) cho toàn bộ 6 tập Cá biển (1,765 loài)
kết hợp FishBase Comnames và Wikidata API.
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import ssl
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Load .env
def load_dotenv():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base, '.env')
    env = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip("'\"")
    return env

env = load_dotenv()
SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("✗ Lỗi: Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong .env")
    sys.exit(1)

def is_valid_vi(name):
    vi_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
                   'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ')
    return any(c in vi_chars for c in name)

def clean_vi_name(name):
    name = re.sub(r'[\r\n\t]+', ' ', name).strip()
    name = re.sub(r'\s+', ' ', name)
    if 'vurot' in name.lower():
        return None
    return name

def fetch_wikidata_info(sci_name):
    try:
        url_search = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(sci_name)}&language=en&format=json&limit=2"
        req = urllib.request.Request(url_search, headers={'User-Agent': 'AntigravityFish/2.0 (contact@cabien.vn)'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            hits = res.get('search', [])
            if not hits:
                return None
            entity_id = hits[0]['id']

        url_get = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&props=labels|aliases&languages=en|vi&format=json"
        req_get = urllib.request.Request(url_get, headers={'User-Agent': 'AntigravityFish/2.0'})
        with urllib.request.urlopen(req_get, context=ctx, timeout=6) as resp:
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

def main():
    # 1. Load backup file
    backup_file = '.backups/supabase--species--ca-bien-all.backup.json'
    if not os.path.exists(backup_file):
        print(f"✗ Không tìm thấy file backup {backup_file}")
        sys.exit(1)

    with open(backup_file, 'r', encoding='utf-8') as f:
        all_species = json.load(f)

    # 2. Load FishBase lookup
    lookup_file = 'data/fishbase_cache/fb_comnames_lookup.json'
    if not os.path.exists(lookup_file):
        print(f"✗ Không tìm thấy file lookup {lookup_file}")
        sys.exit(1)

    with open(lookup_file, 'r', encoding='utf-8') as f:
        fb_lookup = json.load(f)

    vi_map = fb_lookup.get('sci_to_vi_names', {})
    en_map = fb_lookup.get('sci_to_fbname', {})

    print(f"📊 Đang xử lý {len(all_species)} loài cá biển...")

    updates = []
    vol_counts = {}

    for s in all_species:
        sp_id = s['id']
        vol = s.get('volume')
        sci = s.get('scientific_name', '').strip().lower()
        parts = sci.split()
        binom = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else sci

        worms = (s.get('worms_accepted_name') or '').strip().lower()
        worms_parts = worms.split()
        worms_binom = f"{worms_parts[0]} {worms_parts[1]}" if len(worms_parts) >= 2 else worms

        # 1. FishBase names
        names_vi = list(vi_map.get(binom) or vi_map.get(worms_binom) or [])
        fb_en = en_map.get(binom) or en_map.get(worms_binom) or ''

        curr_vn = (s.get('vn_name') or '').strip()
        curr_alt = (s.get('vn_alternate_names') or '').strip()
        if curr_alt == '—':
            curr_alt = ''

        existing_alts = [n.strip() for n in curr_alt.split(',') if n.strip()]
        existing_alts_lower = set(n.lower() for n in existing_alts)

        # Propose new VN alternate names
        new_alts = []
        for raw in names_vi:
            c = clean_vi_name(raw)
            if not c or not is_valid_vi(c):
                continue
            c_lower = c.lower()
            if c_lower == curr_vn.lower() or c_lower in existing_alts_lower:
                continue
            if not any(c_lower == p.lower() for p in new_alts):
                new_alts.append(c)

        final_alts = existing_alts + new_alts
        new_alt_str = ', '.join(final_alts) if final_alts else ''

        # Check EN name
        curr_en = (s.get('en_common_name') or '').strip()
        new_en = curr_en
        if not curr_en or curr_en == '—' or curr_en.lower() == s.get('scientific_name', '').strip().lower():
            if fb_en:
                new_en = fb_en

        has_change = False
        payload = dict(s)

        if new_alt_str != curr_alt:
            payload["vn_alternate_names"] = new_alt_str
            has_change = True

        if new_en != curr_en:
            payload["en_common_name"] = new_en
            has_change = True

        if has_change:
            updates.append(payload)
            vol_counts[vol] = vol_counts.get(vol, 0) + 1

    print(f"Tổng số loài có thay đổi cần cập nhật: {len(updates)} / {len(all_species)}")
    for v in sorted(vol_counts.keys()):
        print(f"  • Tập {v}: {vol_counts[v]} loài")

    # 3. Batch upsert to Supabase
    batch_size = 50
    success = 0
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    print("\n🚀 Bắt đầu cập nhật lên Supabase...")
    for i in range(0, len(updates), batch_size):
        chunk = updates[i:i + batch_size]
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species",
            data=json.dumps(chunk, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 201):
                    success += len(chunk)
                    print(f"  ✓ Đã cập nhật batch {i + 1} - {min(i + batch_size, len(updates))} ({len(chunk)} loài)")
                else:
                    print(f"  ✗ HTTP {resp.status} tại batch {i + 1}")
        except Exception as e:
            print(f"  ✗ Lỗi cập nhật batch {i + 1}: {e}")

    print(f"\n✅ Hoàn tất cập nhật {success} / {len(updates)} loài lên Supabase!")

if __name__ == '__main__':
    main()
