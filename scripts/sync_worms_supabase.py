import json
import time
import os
import re
import sys
import ssl
import argparse
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://cjxqogvtzrvnlsssnfob.supabase.co"
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHFvZ3Z0enJ2bmxzc3NuZm9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzOTUxNjIsImV4cCI6MjEwMDk3MTE2Mn0.HBi2zicdL9O7uMJD6r8IYPXI7ztHcv-5PsTdBwa65_I"
)

WORMS_BASE    = "https://www.marinespecies.org/rest"
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
    genus   = parts[0].capitalize()
    epithet = parts[1].lower()
    if not re.match(r'^[A-Za-z\-]+$', genus) or not re.match(r'^[A-Za-z\-]+$', epithet):
        return None
    return f"{genus} {epithet}"


def worms_get(endpoint: str, params: dict = None) -> list | dict | None:
    qs  = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{WORMS_BASE}/{endpoint}{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes-SyncBot/1.0 (+research)"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"    [HTTP {e.code}] {url}")
        return None
    except Exception as e:
        print(f"    [API Error] {e}")
        return None


def sync_one(sci_name: str) -> dict:
    name = parse_sci_name(sci_name)
    if not name:
        return {
            "worms_status": "parse_error",
            "worms_accepted_name": None,
            "worms_id": None
        }

    encoded = urllib.parse.quote(name)
    records = worms_get(f"AphiaRecordsByName/{encoded}",
                        {"like": "false", "marine_only": "true"})

    if not records or not isinstance(records, list) or len(records) == 0:
        return {
            "worms_status": "not_found",
            "worms_accepted_name": None,
            "worms_id": None
        }

    rec = records[0]
    worms_status  = rec.get("status", "").lower()
    valid_name    = rec.get("valid_name", "")
    aphia_id      = rec.get("AphiaID")
    valid_aphia   = rec.get("valid_AphiaID")

    if worms_status == "accepted":
        return {
            "worms_status": "valid",
            "worms_accepted_name": valid_name,
            "worms_id": aphia_id,
            "authorship": rec.get("valid_authority", "") or rec.get("authority", "")
        }
    elif worms_status in ("unaccepted", "synonym"):
        return {
            "worms_status": "synonym",
            "worms_accepted_name": valid_name,
            "worms_id": valid_aphia,
            "authorship": rec.get("valid_authority", "") or rec.get("authority", "")
        }
    else:
        return {
            "worms_status": "uncertain",
            "worms_accepted_name": valid_name or None,
            "worms_id": aphia_id,
            "authorship": rec.get("valid_authority", "") or rec.get("authority", "")
        }


def get_missing_worms(collection_id=None, force=False):
    """Fetch species from Supabase that don't have worms_status set (or all if forced)."""
    url = f"{SUPABASE_URL}/rest/v1/species?select=id,scientific_name"
    if collection_id:
        url += f"&collection_id=eq.{collection_id}"
    if not force:
        url += "&or=(worms_status.is.null,worms_status.eq.)"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range": "0-9999"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"Lỗi fetch: {e.code} {body}")
        return []


def update_supabase_row(sp_id, worms_status, worms_accepted_name, worms_id, authorship=None):
    """Update worms_status, worms_accepted_name, worms_id in Supabase for a single row"""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    update_doc = {
        "worms_status": worms_status,
        "worms_accepted_name": worms_accepted_name if worms_accepted_name else "",
        "worms_id": worms_id
    }
    if authorship:
        update_doc["authorship"] = authorship
    
    data = json.dumps(update_doc, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"Lỗi update ({sp_id}): {e.code} {body}")
        return e.code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="thuc-vat-bien", help="Collection ID (mặc định: thuc-vat-bien)")
    parser.add_argument("--force", action="store_true", help="Force sync tất cả loài kể cả đã có worms_status")
    args = parser.parse_args()

    print(f"Đang lấy danh sách các loài từ Supabase (collection: {args.collection}, force: {args.force})...")
    species_list = get_missing_worms(args.collection, args.force)
    
    if not species_list:
        print("Không có loài nào cần sync.")
        return

    print(f"Cần sync {len(species_list)} loài.")
    
    for i, sp in enumerate(species_list, 1):
        sp_id = sp["id"]
        sci_name = sp["scientific_name"]
        print(f"[{i}/{len(species_list)}] {sci_name}...", end=" ", flush=True)
        
        result = sync_one(sci_name)
        
        print(f"[{result['worms_status'].upper()}]")
        
        update_supabase_row(sp_id, result["worms_status"], result["worms_accepted_name"], result["worms_id"], result.get("authorship"))
            
        time.sleep(DELAY_SECONDS)

    print("Hoàn tất!")

if __name__ == "__main__":
    main()
