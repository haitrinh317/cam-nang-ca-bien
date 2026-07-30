"""
sync_fishbase.py
----------------
Bước riêng biệt: Tra cứu FishBase cho từng loài trong species.json.
Kết quả lưu vào data/fishbase_sync.json (tách bạch hoàn toàn khỏi pipeline cào NLM).

API sử dụng: https://fishbase.ropensci.org (miễn phí, không cần API key)

Endpoint tra cứu:
  1. Tìm loài hợp lệ:  GET /species?Genus=X&Species=Y
  2. Tìm synonym:       GET /synonyms?Genus=X&Species=Y

Cách chạy:
  python scripts/sync_fishbase.py
  python scripts/sync_fishbase.py --force   # cập nhật lại cả loài đã sync
"""

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

SPECIES_FILE  = "data/species.json"
SYNC_FILE     = "data/fishbase_sync.json"
WORMS_BASE    = "https://www.marinespecies.org/rest"
DELAY_SECONDS = 1.0

# Bypass SSL certificate verification cho môi trường proxy/intranet
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


# ─── Helpers ────────────────────────────────────────────────────────────────

def parse_sci_name(full_name: str):
    """Tách 'Epinephelus merra (Author, 1790)' thành 'Epinephelus merra'."""
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
    """Gọi WoRMS REST API, trả về parsed JSON hoặc None nếu lỗi."""
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


# ─── Logic tra cứu WoRMS ────────────────────────────────────────────────────

def sync_one(sci_name: str) -> dict:
    """
    Tra WoRMS cho 1 tên khoa học.
    Endpoint: GET /AphiaRecordsByName/{name}?like=false&marine_only=true
    
    Trả về dict với các trường:
      status      : "valid" | "synonym" | "not_found"
      acceptedName: tên hợp lệ hiện tại
      acceptedBy  : tác giả tên hợp lệ
      wormsId     : AphiaID
      lastUpdated : ngày WoRMS cập nhật
      note        : ghi chú ngắn
    """
    name = parse_sci_name(sci_name)
    if not name:
        return {
            "status": "parse_error",
            "acceptedName": None,
            "note": "Không phân tích được tên khoa học"
        }

    # Encode tên loài cho URL (thay space bằng %20)
    encoded = urllib.parse.quote(name)
    records = worms_get(f"AphiaRecordsByName/{encoded}",
                        {"like": "false", "marine_only": "true"})

    if not records or not isinstance(records, list) or len(records) == 0:
        return {
            "status": "not_found",
            "acceptedName": None,
            "acceptedBy": None,
            "wormsId": None,
            "lastUpdated": None,
            "note": "Chưa xác minh được trên WoRMS"
        }

    rec = records[0]  # Lấy kết quả khớp đầu tiên
    worms_status  = rec.get("status", "").lower()   # "accepted" | "unaccepted" | ...
    valid_name    = rec.get("valid_name", "")
    valid_author  = rec.get("valid_authority", "")
    aphia_id      = rec.get("AphiaID")
    valid_aphia   = rec.get("valid_AphiaID")
    modified      = rec.get("modified", "")
    # Cắt lấy ngày từ ISO string "2023-04-12T10:00:00Z"
    last_updated  = modified[:10] if modified else ""

    if worms_status == "accepted":
        return {
            "status": "valid",
            "acceptedName": valid_name,
            "acceptedBy": valid_author,
            "wormsId": aphia_id,
            "lastUpdated": last_updated,
            "note": "Tên hợp lệ trên WoRMS"
        }
    elif worms_status in ("unaccepted", "synonym"):
        return {
            "status": "synonym",
            "acceptedName": valid_name,
            "acceptedBy": valid_author,
            "wormsId": valid_aphia,
            "lastUpdated": last_updated,
            "note": f"Tên cũ (synonym). Tên hiện hành: {valid_name}"
        }
    else:
        # nomen dubium, uncertain, etc.
        return {
            "status": "uncertain",
            "acceptedName": valid_name or None,
            "acceptedBy": valid_author,
            "wormsId": aphia_id,
            "lastUpdated": last_updated,
            "note": f"Trạng thái chưa chắc chắn trên WoRMS: {worms_status}"
        }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Cập nhật lại cả những loài đã sync trước đó")
    args = parser.parse_args()

    # Đọc danh sách loài
    if not os.path.exists(SPECIES_FILE):
        print(f"[ERROR] Không tìm thấy {SPECIES_FILE}. Hãy chạy build_database.py trước.")
        sys.exit(1)

    with open(SPECIES_FILE, "r", encoding="utf-8") as f:
        species_list = json.load(f)

    # Đọc file sync cũ nếu có
    existing: dict = {}
    if os.path.exists(SYNC_FILE):
        with open(SYNC_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    print(f"Tổng số loài cần đồng bộ: {len(species_list)}")
    print(f"Đã có sẵn trong cache   : {len(existing)}")
    print("-" * 50)

    updated_count = 0
    skipped_count = 0

    for i, sp in enumerate(species_list, 1):
        sp_id     = sp.get("id", "")
        sci_name  = sp.get("scientificName", "")

        # Bỏ qua nếu đã sync và không ép force
        if not args.force and sp_id in existing:
            skipped_count += 1
            continue

        print(f"[{i}/{len(species_list)}] {sci_name}...", end=" ", flush=True)

        result = sync_one(sci_name)
        result["syncedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        result["sourceId"] = sp_id
        result["sourceName"] = sci_name

        existing[sp_id] = result
        updated_count += 1

        # Ghi file mỗi lần để không mất data nếu bị ngắt giữa chừng
        with open(SYNC_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        print(f"[{result['status'].upper()}]")
        time.sleep(DELAY_SECONDS)

    print("-" * 50)
    print(f"Hoàn tất! Đã đồng bộ: {updated_count} loài | Đã bỏ qua (cache): {skipped_count}")
    print(f"Kết quả lưu tại: {SYNC_FILE}")


if __name__ == "__main__":
    main()
