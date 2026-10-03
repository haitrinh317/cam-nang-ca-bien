"""
enrich_tap3_names.py
--------------------
Bổ sung tên gọi khác tiếng Việt (vn_alternate_names) và tên tiếng Anh (en_common_name)
cho 518 loài Tập III từ FishBase Comnames & WoRMS.
"""
import os
import sys
import json
import urllib.request
import re

# Set stdout encoding
sys.stdout.reconfigure(encoding='utf-8')

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

def main():
    # 1. Load backup / species
    backup_file = '.backups/supabase--species--tap3.backup.json'
    if not os.path.exists(backup_file):
        print(f"✗ Không tìm thấy file backup {backup_file}")
        sys.exit(1)
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        tap3_species = json.load(f)

    # 2. Load FishBase lookup
    lookup_file = 'data/fishbase_cache/fb_comnames_lookup.json'
    if not os.path.exists(lookup_file):
        print(f"✗ Không tìm thấy file lookup {lookup_file}")
        sys.exit(1)

    with open(lookup_file, 'r', encoding='utf-8') as f:
        fb_lookup = json.load(f)

    vi_map = fb_lookup.get('sci_to_vi_names', {})
    en_map = fb_lookup.get('sci_to_fbname', {})

    updates = []
    
    for s in tap3_species:
        sp_id = s['id']
        sci = s.get('scientific_name', '').strip().lower()
        parts = sci.split()
        binom = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else sci

        worms = (s.get('worms_accepted_name') or '').strip().lower()
        worms_parts = worms.split()
        worms_binom = f"{worms_parts[0]} {worms_parts[1]}" if len(worms_parts) >= 2 else worms

        names_vi = vi_map.get(binom) or vi_map.get(worms_binom) or []
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
            fb_en = en_map.get(binom) or en_map.get(worms_binom)
            if fb_en:
                new_en = fb_en

        # Determine if changed
        has_change = False
        payload = dict(s)

        if new_alt_str != curr_alt:
            payload["vn_alternate_names"] = new_alt_str
            has_change = True

        if new_en != curr_en:
            payload["en_common_name"] = new_en
            has_change = True

        if has_change:
            updates.append({
                "sp_id": sp_id,
                "sci": s.get('scientific_name'),
                "vn_name": curr_vn,
                "old_alt": curr_alt,
                "new_alt": new_alt_str,
                "old_en": curr_en,
                "new_en": new_en,
                "payload": payload
            })

    print(f"==================================================")
    print(f"Tổng số loài Tập III cần cập nhật: {len(updates)} / {len(tap3_species)}")
    print(f"==================================================")

    # 3. Batch update to Supabase
    batch_size = 50
    success = 0
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    for i in range(0, len(updates), batch_size):
        chunk = updates[i:i + batch_size]
        payloads = [item['payload'] for item in chunk]
        
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species",
            data=json.dumps(payloads, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    success += len(chunk)
                    print(f"  ✓ Đã cập nhật batch {i + 1} - {min(i + batch_size, len(updates))} ({len(chunk)} loài)")
                else:
                    print(f"  ✗ Lỗi HTTP {resp.status} tại batch {i + 1}")
        except Exception as e:
            print(f"  ✗ Lỗi cập nhật batch {i + 1}: {e}")

    print(f"\n✅ Hoàn tất cập nhật thành công {success} / {len(updates)} loài lên Supabase!")

if __name__ == '__main__':
    main()
