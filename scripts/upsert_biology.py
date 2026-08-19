"""
upsert_biology.py
-----------------
Cập nhật riêng cột biology cho từng loài đã có data trong species.json.
Dùng PATCH request → chỉ update biology, không đụng các cột khác.

QUAN TRỌNG: Chạy AFTER khi đã chạy migration 002_add_biology_column.sql

Cách chạy:
  python scripts/upsert_biology.py           # chỉ loài có biology mới
  python scripts/upsert_biology.py --all     # upsert tất cả (kể cả biology=null)
  python scripts/upsert_biology.py --volume 1
"""

import json
import os
import sys
import urllib.request
import urllib.error
import time
import argparse

sys.stdout.reconfigure(encoding='utf-8')

SPECIES_FILE   = "data/species.json"
SUPABASE_URL   = "https://cjxqogvtzrvnlsssnfob.supabase.co"
SUPABASE_KEY   = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHFvZ3Z0enJ2bmxzc3NuZm9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzOTUxNjIsImV4cCI6MjEwMDk3MTE2Mn0.HBi2zicdL9O7uMJD6r8IYPXI7ztHcv-5PsTdBwa65_I"
)


def patch_biology(species_id: str, biology: dict | None) -> bool:
    """PATCH /rest/v1/species?id=eq.{id} với {biology: ...}"""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{species_id}"
    payload = json.dumps({"biology": biology}, ensure_ascii=False).encode("utf-8")
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 204)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  ✗ HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all",    action="store_true", help="Upsert kể cả biology=null")
    parser.add_argument("--volume", type=int, default=0, help="Chỉ Tập X")
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("[ERROR] Thiếu SUPABASE_KEY")
        sys.exit(1)

    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    targets = species_list
    if args.volume:
        targets = [s for s in species_list if s.get("volume") == args.volume]
    if not args.all:
        targets = [s for s in targets if s.get("biology")]

    print(f"Upserting biology for {len(targets)} species...")
    ok = fail = skip = 0

    for i, sp in enumerate(targets, 1):
        sp_id = sp.get("id", "")
        bio   = sp.get("biology")
        print(f"  [{i}/{len(targets)}] {sp.get('scientificName',''):50s}", end=" ")

        if patch_biology(sp_id, bio):
            ok += 1
            iucn = bio.get("iucnStatus", "?") if bio else "null"
            print(f"✓ IUCN:{iucn}")
        else:
            fail += 1
            print("✗")

        time.sleep(0.05)  # 50ms

        if i % 100 == 0:
            print(f"  ── Progress: {ok} OK, {fail} failed ──")

    print(f"\nDone: {ok} OK | {fail} failed | {skip} skipped")


if __name__ == "__main__":
    main()
