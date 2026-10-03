"""
sync_gbif_biology.py
--------------------
Bổ sung thêm vào trường 'biology' từ GBIF API:
  - iucnStatus  : LC / NT / VU / EN / CR
  - gbifKey     : usageKey GBIF
  - descriptions: mô tả hình thái (tiếng Anh)

GBIF API: https://api.gbif.org/v1 — miễn phí, không cần API key

Cách chạy:
  python scripts/sync_gbif_biology.py             # chỉ loài chưa có iucnStatus
  python scripts/sync_gbif_biology.py --force     # ghi đè tất cả
  python scripts/sync_gbif_biology.py --volume 2  # chỉ Tập 2
"""

import json
import os
import sys
import ssl
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

SPECIES_FILE   = "data/species.json"
GBIF_BASE      = "https://api.gbif.org/v1"
DELAY_SECONDS  = 0.3   # GBIF rate limit thoải mái

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# Loại descriptions hữu ích, ưu tiên theo thứ tự này
USEFUL_TYPES = ("diagnosis", "description", "biology", "habitat")


# ─── GBIF helpers ─────────────────────────────────────────────────────────────

def gbif_get(path: str) -> dict | list | None:
    url = f"{GBIF_BASE}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "VietnamFishes/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  [HTTP {e.code}] {url}")
        return None
    except Exception as e:
        print(f"  [error] {e}")
        return None


def match_species(sci_name: str) -> tuple[int | None, str | None]:
    """
    Trả về (gbifKey, iucnStatus) hoặc (None, None).
    gbifKey: có thể là key của accepted taxon nếu tên đang sync là synonym.
    """
    parts = sci_name.strip().split()
    if len(parts) < 2:
        return None, None

    canonical = f"{parts[0]} {parts[1]}"
    data = gbif_get(f"species/match?name={urllib.parse.quote(canonical)}&kingdom=Animalia")
    if not data or data.get("matchType") == "NONE":
        return None, None

    # Lấy speciesKey (accepted taxon)
    key = data.get("speciesKey") or data.get("usageKey")
    if not key:
        return None, None

    # IUCN status nằm trong occurrence data hoặc trong checklist
    # Cách nhanh nhất: lấy từ /species/{key} classifications
    iucn = data.get("iucnRedListCategory")  # không phải lúc nào cũng có trong /match
    return int(key), iucn


def get_iucn_and_desc(gbif_key: int) -> tuple[str | None, str | None]:
    """
    Lấy IUCN status và best description cho 1 species key.
    """
    iucn = None
    description = None

    # Lấy descriptions
    desc_data = gbif_get(f"species/{gbif_key}/descriptions")
    if desc_data and desc_data.get("results"):
        results = desc_data["results"]
        # Ưu tiên các loại hữu ích
        for pref_type in USEFUL_TYPES:
            for r in results:
                if r.get("type", "").lower() == pref_type and r.get("language", "").lower() in ("eng", "en", ""):
                    txt = r.get("description", "").strip()
                    if txt and len(txt) > 80:  # bỏ mô tả quá ngắn
                        description = txt[:2000]  # cap 2000 chars
                        break
            if description:
                break

    # Lấy occurrence 1 record để lấy iucnRedListCategory
    occ = gbif_get(f"occurrence/search?taxonKey={gbif_key}&limit=1")
    if occ and occ.get("results"):
        iucn = occ["results"][0].get("iucnRedListCategory")

    return iucn, description


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bổ sung GBIF biology vào species.json")
    parser.add_argument("--force",  action="store_true", help="Ghi đè cả loài đã có gbifKey")
    parser.add_argument("--volume", type=int, default=0, help="Chỉ xử lý tập X (1-5)")
    args = parser.parse_args()

    if not os.path.exists(SPECIES_FILE):
        print(f"[ERROR] Không tìm thấy {SPECIES_FILE}")
        sys.exit(1)

    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    targets = species_list
    if args.volume:
        targets = [s for s in species_list if s.get("volume") == args.volume]

    print("=" * 60)
    print(f"Sync GBIF Biology → species.json")
    print(f"Loài cần xử lý: {len(targets)}" + (f" (Tập {args.volume})" if args.volume else ""))
    print("=" * 60)

    matched  = 0
    skipped  = 0
    no_match = 0
    saved_count = 0

    for i, sp in enumerate(targets, 1):
        sci_name = sp.get("scientificName", "")
        bio      = sp.get("biology") or {}

        # Skip nếu đã có gbifKey và không force
        if not args.force and bio.get("gbifKey"):
            skipped += 1
            continue

        print(f"  [{i}/{len(targets)}] {sci_name:50s}", end=" ", flush=True)

        gbif_key, iucn_match = match_species(sci_name)
        if gbif_key is None:
            no_match += 1
            print("→ no match")
            time.sleep(DELAY_SECONDS)
            continue

        # Lấy thêm IUCN + descriptions
        iucn, description = get_iucn_and_desc(gbif_key)
        iucn = iucn or iucn_match   # fallback về kết quả từ /match

        # Ghi vào bio
        bio["gbifKey"] = gbif_key
        if iucn:
            bio["iucnStatus"] = iucn
        if description and not bio.get("morphDescription"):
            bio["morphDescription"] = description

        sp["biology"] = bio
        matched += 1

        status_str = iucn or "?"
        has_desc   = "📄" if description else "  "
        print(f"→ #{gbif_key} | IUCN:{status_str:2s} {has_desc}")

        time.sleep(DELAY_SECONDS)

        # Auto-save mỗi 100 loài
        if matched % 100 == 0:
            with open(SPECIES_FILE, "w", encoding="utf-8") as f:
                json.dump(species_list, f, ensure_ascii=False, indent=2)
            saved_count += 1
            print(f"  ── Auto-saved ({matched} matched) ──")

    # Final save
    with open(SPECIES_FILE, "w", encoding="utf-8") as f:
        json.dump(species_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("Hoàn tất GBIF sync!")
    print(f"  Matched   : {matched}")
    print(f"  Skipped   : {skipped}")
    print(f"  No match  : {no_match}")
    print(f"  File lưu  : {SPECIES_FILE}")


if __name__ == "__main__":
    main()
