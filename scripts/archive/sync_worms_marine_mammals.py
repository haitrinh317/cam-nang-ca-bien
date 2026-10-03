#!/usr/bin/env python3
"""
scripts/sync_worms_marine_mammals.py
-----------------------------------
Bước ② trong pipeline ocr-to-audit.md:
Xác thực danh pháp khoa học cho toàn bộ 34 loài Thú biển Việt Nam (collection: 'thu-bien')
qua World Register of Marine Species (WoRMS) REST API.

Cập nhật các cột:
  - worms_id (AphiaID)
  - worms_status (accepted / synonym)
  - worms_accepted_name
  - worms_lsid

Tác giả: Antigravity Assistant cho chú Chình
Ngày tạo: 13/09/2026
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("❌ Lỗi: Không tìm thấy SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY!")
    sys.exit(1)

HEADERS_SUPA = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

WORMS_API = "https://www.marinespecies.org/rest/AphiaRecordsByName"
HEADERS_WORMS = {
    "User-Agent": "CamNangSinhVatBienVN/1.0 (haitrinh082@gmail.com)"
}

def sync_worms():
    print("🌊 BẮT ĐẦU XÁC THỰC DANH PHÁP WORMS CHO THÚ BIỂN VIỆT NAM (thu-bien) 🌊")
    
    # 1. Lấy danh sách 34 loài thú biển
    fetch_url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.thu-bien&select=id,species_index,vn_name,scientific_name,worms_status&order=species_index.asc"
    req = urllib.request.Request(fetch_url, headers=HEADERS_SUPA)
    with urllib.request.urlopen(req) as r:
        species_list = json.loads(r.read().decode("utf-8"))
        
    print(f"📋 Tìm thấy {len(species_list)} loài trong collection 'thu-bien'.\n")
    
    success = 0
    errors = 0
    
    for i, sp in enumerate(species_list, 1):
        sp_id = sp["id"]
        sci_name = sp["scientific_name"]
        vn_name = sp["vn_name"]
        
        encoded_name = urllib.parse.quote(sci_name)
        worms_url = f"{WORMS_API}/{encoded_name}?like=false&marine_only=false"
        
        try:
            req_w = urllib.request.Request(worms_url, headers=HEADERS_WORMS)
            with urllib.request.urlopen(req_w) as rw:
                records = json.loads(rw.read().decode("utf-8"))
                
            if records and len(records) > 0:
                rec = records[0]
                aphia_id = rec.get("AphiaID")
                status_raw = rec.get("status", "").lower()
                status = "accepted" if status_raw == "accepted" else "synonym"
                accepted_name = rec.get("valid_name") or sci_name
                lsid = rec.get("lsid") or f"urn:lsid:marinespecies.org:taxname:{aphia_id}"
                
                # Cập nhật Supabase
                patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
                payload = {
                    "worms_id": aphia_id,
                    "worms_status": status,
                    "worms_accepted_name": accepted_name
                }
                req_patch = urllib.request.Request(
                    patch_url,
                    headers=HEADERS_SUPA,
                    data=json.dumps(payload).encode("utf-8"),
                    method="PATCH"
                )
                with urllib.request.urlopen(req_patch) as rp:
                    print(f"  ✅ [{i:02d}/{len(species_list)}] {vn_name} ({sci_name}) -> WoRMS ID: {aphia_id} [{status}] -> {accepted_name}")
                    success += 1
            else:
                print(f"  ⚠️ [{i:02d}/{len(species_list)}] {vn_name} ({sci_name}) -> Không tìm thấy trên WoRMS.")
                errors += 1
        except urllib.error.HTTPError as he:
            if he.code == 204:
                print(f"  ⚠️ [{i:02d}/{len(species_list)}] {vn_name} ({sci_name}) -> HTTP 204 (No Content) trên WoRMS.")
            else:
                print(f"  ❌ [{i:02d}/{len(species_list)}] {vn_name} ({sci_name}) -> Lỗi HTTP {he.code}")
            errors += 1
        except Exception as e:
            print(f"  ❌ [{i:02d}/{len(species_list)}] {vn_name} ({sci_name}) -> Lỗi: {e}")
            errors += 1
            
        time.sleep(1.0) # Tuân thủ rate-limit WoRMS
        
    print(f"\n🎯 KẾT QUẢ WORMS SYNC: Thành công {success}/{len(species_list)} loài. Thất bại: {errors}.")

if __name__ == "__main__":
    sync_worms()
