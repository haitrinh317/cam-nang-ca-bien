"""
sync_worms_tap6.py
------------------
Đồng bộ trạng thái danh pháp WoRMS (World Register of Marine Species)
cho 136 loài còn lại của Tập VI (Cá rạn san hô Việt Nam).
Cập nhật song song:
1. Supabase species table (worms_status, worms_accepted_name, worms_id, worms_synced_at)
2. data/fishbase_sync.json
"""
import os
import sys
import json
import time
import ssl
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_dotenv():
    env_path = os.path.join(BASE, '.env')
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

WORMS_BASE = "https://www.marinespecies.org/rest"
DELAY_SECONDS = 1.0

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def parse_sci_name(full_name: str):
    if not full_name:
        return None
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None
    genus = parts[0].capitalize()
    epithet = parts[1].lower()
    if not re.match(r'^[A-Za-z\-]+$', genus) or not re.match(r'^[A-Za-z\-]+$', epithet):
        return None
    return f"{genus} {epithet}"

def worms_get(endpoint: str, params: dict = None, max_retries: int = 3) -> list | dict | None:
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{WORMS_BASE}/{endpoint}{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes-SyncBot/1.0 (+research)"})
    
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            elif e.code == 429:
                time.sleep(5.0)
                continue
            else:
                if attempt == max_retries - 1:
                    print(f"    [HTTP {e.code}] {url}")
                time.sleep(2.0)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"    [Lỗi mạng/API] {e}")
            time.sleep(2.0)
    return None

def sync_one(sci_name: str) -> dict:
    name = parse_sci_name(sci_name)
    now_iso = datetime.now(timezone.utc).isoformat()
    if not name:
        return {
            "worms_status": "parse_error",
            "worms_accepted_name": None,
            "worms_id": None,
            "authority": "",
            "synced_at": now_iso
        }

    encoded = urllib.parse.quote(name)
    records = worms_get(f"AphiaRecordsByName/{encoded}", {"like": "false", "marine_only": "true"})

    if not records or not isinstance(records, list) or len(records) == 0:
        return {
            "worms_status": "not_found",
            "worms_accepted_name": None,
            "worms_id": None,
            "authority": "",
            "synced_at": now_iso
        }

    rec = records[0]
    raw_status = rec.get("status", "").lower()
    valid_name = rec.get("valid_name", "")
    aphia_id = rec.get("AphiaID")
    valid_aphia = rec.get("valid_AphiaID")
    authority = rec.get("valid_authority", "") or rec.get("authority", "")
    last_mod = rec.get("modified", "")[:10] if rec.get("modified") else ""

    if raw_status == "accepted":
        return {
            "worms_status": "valid",
            "worms_accepted_name": valid_name,
            "worms_id": aphia_id,
            "authority": authority,
            "last_updated": last_mod,
            "synced_at": now_iso
        }
    elif raw_status in ("unaccepted", "synonym"):
        return {
            "worms_status": "synonym",
            "worms_accepted_name": valid_name,
            "worms_id": valid_aphia,
            "authority": authority,
            "last_updated": last_mod,
            "synced_at": now_iso
        }
    else:
        return {
            "worms_status": "uncertain",
            "worms_accepted_name": valid_name or None,
            "worms_id": aphia_id,
            "authority": authority,
            "last_updated": last_mod,
            "synced_at": now_iso
        }

def update_supabase_row(sp_id: str, res: dict):
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    update_doc = {
        "worms_status": res["worms_status"],
        "worms_accepted_name": res["worms_accepted_name"] or "",
        "worms_id": res["worms_id"],
        "worms_synced_at": res["synced_at"]
    }
    data = json.dumps(update_doc, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"  [Lỗi cập nhật Supabase {sp_id}]: {e}")
        return False

def main():
    # 1. Fetch missing species for Tập VI
    print("🔍 Đang tải danh sách các loài Tập VI chưa sync WoRMS...")
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.6&or=(worms_status.is.null,worms_status.eq.)&select=id,species_index,scientific_name,vn_name&order=species_index"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    with urllib.request.urlopen(req) as resp:
        species_list = json.loads(resp.read().decode("utf-8"))

    total = len(species_list)
    print(f"📊 Cần sync WoRMS cho {total} loài Tập VI.\n")

    if total == 0:
        print("✅ Tất cả các loài đã có trạng thái WoRMS. Không cần sync thêm.")
        return

    # 2. Đọc file data/fishbase_sync.json
    fb_path = os.path.join(BASE, 'data', 'fishbase_sync.json')
    fb_data = {}
    if os.path.exists(fb_path):
        with open(fb_path, 'r', encoding='utf-8') as f:
            fb_data = json.load(f)

    stats = {"valid": 0, "synonym": 0, "uncertain": 0, "not_found": 0, "error": 0}

    # 3. Tiến hành sync tuần tự
    for idx, sp in enumerate(species_list, 1):
        sp_id = sp["id"]
        sci_name = sp["scientific_name"]
        vn_name = sp.get("vn_name", "")

        print(f"[{idx}/{total}] {sp_id}: {sci_name} ({vn_name})...", end=" ", flush=True)

        res = sync_one(sci_name)
        st = res["worms_status"]
        stats[st] = stats.get(st, 0) + 1

        if st == "valid":
            print(f"✅ VALID (AphiaID: {res['worms_id']})")
        elif st == "synonym":
            print(f"🔄 SYNONYM ➔ {res['worms_accepted_name']} (AphiaID: {res['worms_id']})")
        elif st == "not_found":
            print("❓ NOT FOUND")
        else:
            print(f"⚠️ {st.upper()}")

        # Update Supabase
        update_supabase_row(sp_id, res)

        # Update fishbase_sync.json entry
        fb_data[sp_id] = {
            "status": res["worms_status"],
            "acceptedName": res["worms_accepted_name"] or sci_name,
            "acceptedBy": res["authority"],
            "wormsId": res["worms_id"],
            "lastUpdated": res.get("last_updated", ""),
            "note": "Tên hợp lệ trên WoRMS" if st == "valid" else ("Tên đồng nghĩa trên WoRMS" if st == "synonym" else "Chưa xác minh được trên WoRMS"),
            "syncedAt": res["synced_at"],
            "sourceId": sp_id,
            "sourceName": sci_name
        }

        # Lưu checkpoint mỗi 15 loài
        if idx % 15 == 0 or idx == total:
            with open(fb_path, 'w', encoding='utf-8') as f:
                json.dump(fb_data, f, ensure_ascii=False, indent=2)

        time.sleep(DELAY_SECONDS)

    print("\n" + "="*50)
    print("🎉 HOÀN TẤT WORMS SYNC TẬP VI!")
    print(f"  • Tổng loài đã query: {total}")
    print(f"  • ✅ Valid (Hợp lệ): {stats['valid']} ({stats['valid']/total*100:.1f}%)")
    print(f"  • 🔄 Synonym (Đồng nghĩa): {stats['synonym']} ({stats['synonym']/total*100:.1f}%)")
    print(f"  • ❓ Not found: {stats['not_found']} ({stats['not_found']/total*100:.1f}%)")
    print(f"  • ⚠️ Khác: {stats.get('uncertain', 0) + stats.get('parse_error', 0)}")
    print(f"  • File cập nhật: data/fishbase_sync.json (Hiện có: {len(fb_data)} loài)")

if __name__ == "__main__":
    main()
