#!/usr/bin/env python3
"""
scripts/clean_biology_text_db.py
Rà soát và dọn sạch các ký tự chữ Hán (CJK) và lỗi chính tả dịch thuật trong ghi chú sinh học.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Thiếu credentials Supabase")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

FIXES = [
    {
        "id": "tap5-species-263",
        "field": "biologySummaryVn",
        "old": "thủy动力 học",
        "new": "thủy động lực học"
    },
    {
        "id": "giapxac-species-99",
        "field": "reproductionNotesVn",
        "old": "tập合 lại",
        "new": "tập hợp lại"
    }
]

def main():
    print("🧹 Bắt đầu sửa lỗi chữ Hán trong ghi chú sinh học...")
    for fix in FIXES:
        sp_id = fix["id"]
        # 1. Lấy dữ liệu biology hiện tại
        get_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}&select=id,biology"
        resp = requests.get(get_url, headers=HEADERS)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            print(f"⚠️ Không tìm thấy loài {sp_id}")
            continue

        bio = rows[0].get("biology") or {}
        field = fix["field"]
        old_val = bio.get(field, "")

        if fix["old"] in old_val:
            new_val = old_val.replace(fix["old"], fix["new"])
            bio[field] = new_val

            # Patch lại vào Supabase
            patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
            patch_resp = requests.patch(patch_url, headers=HEADERS, json={"biology": bio})
            patch_resp.raise_for_status()
            print(f"✅ Đã sửa {sp_id} [{field}]: '{fix['old']}' -> '{fix['new']}'")
        else:
            print(f"ℹ️ {sp_id} [{field}] không còn chứa '{fix['old']}'")

    print("🎉 Hoàn tất làm sạch CSDL!")

if __name__ == "__main__":
    main()
