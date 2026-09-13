#!/usr/bin/env python3
"""
scripts/audit_marine_mammals.py
Audit chất lượng dữ liệu toàn bộ 34 loài Thú biển Việt Nam (Bộ sưu tập thu-bien)
theo quy trình audit-sinhvat v2.0 và workflow ocr-to-audit.md.

Tác giả: Antigravity Assistant cho chú Chình
Ngày thực hiện: 13/09/2026
"""

import os
import sys
import json
import urllib.request
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

CORE_VN_FIELDS = [
    ("vn_name", "Tên tiếng Việt"),
    ("vn_alternate_names", "Tên gọi khác VN"),
    ("vn_distribution", "Phân bố VN"),
    ("vn_size", "Kích thước VN"),
    ("vn_specimen", "Mẫu vật VN"),
    ("vn_status", "Tình trạng bảo tồn VN"),
    ("vn_literature", "Tài liệu dẫn VN"),
    ("morphology_vn", "Hình thái VN"),
    ("ecology_vn", "Sinh thái học VN"),
    ("economic_value_vn", "Giá trị kinh tế/bảo tồn VN")
]

CORE_EN_FIELDS = [
    ("en_common_name", "Tên tiếng Anh"),
    ("en_distribution", "Phân bố EN"),
    ("en_size", "Kích thước EN"),
    ("en_specimen", "Mẫu vật EN"),
    ("en_status", "Tình trạng bảo tồn EN"),
    ("en_literature", "Tài liệu dẫn EN"),
    ("morphology_en", "Hình thái EN"),
    ("ecology_en", "Sinh thái học EN"),
    ("economic_value_en", "Giá trị kinh tế EN")
]

def check_val(v):
    if v is None:
        return False
    if isinstance(v, str) and not v.strip():
        return False
    if isinstance(v, (list, dict)) and len(v) == 0:
        return False
    return True

def main():
    print("=" * 80)
    print("🐋 BẮT ĐẦU AUDIT DỮ LIỆU TOÀN BỘ 34 LOÀI THÚ BIỂN VIỆT NAM (thu-bien)")
    print("=" * 80)

    # 1. Query toàn bộ loài thu-bien
    req_sp = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.thu-bien&order=species_index",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}"
        }
    )
    with urllib.request.urlopen(req_sp) as resp:
        species_rows = json.loads(resp.read().decode("utf-8"))

    # 2. Query bảng species_photos
    sp_ids = [r["id"] for r in species_rows]
    ids_str = ",".join(sp_ids)
    req_ph = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species_photos?species_id=in.({ids_str})&select=*",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}"
        }
    )
    with urllib.request.urlopen(req_ph) as resp:
        photo_rows = json.loads(resp.read().decode("utf-8"))

    photos_by_sp = {}
    for p in photo_rows:
        sid = p.get("species_id")
        photos_by_sp.setdefault(sid, []).append(p)

    total_species = len(species_rows)
    complete_count = 0
    partial_count = 0
    skeleton_count = 0

    results = []

    for sp in species_rows:
        sid = sp["id"]
        sci = sp.get("scientific_name", "")
        vn = sp.get("vn_name", "")
        en = sp.get("en_common_name", "")
        
        # Check VN Fields
        missing_vn = []
        for f, lbl in CORE_VN_FIELDS:
            if not check_val(sp.get(f)):
                missing_vn.append(lbl)

        # Check EN Fields
        missing_en = []
        for f, lbl in CORE_EN_FIELDS:
            if not check_val(sp.get(f)):
                missing_en.append(lbl)

        # Check WoRMS
        worms_id = sp.get("worms_id")
        worms_status = sp.get("worms_status")
        worms_ok = bool(worms_id and (worms_status in ("accepted", "valid") or (worms_status == "synonym" and sp.get("worms_accepted_name"))))

        # Check SeaLifeBase Biology
        bio = sp.get("biology") or {}
        has_bio = bool(bio.get("specCode") or bio.get("biologySummary") or bio.get("biologySummaryVn"))

        # Check Sách Đỏ VAST
        redlist = bio.get("vnRedList") if isinstance(bio, dict) else None
        has_redlist = bool(redlist and redlist.get("status") and redlist.get("threats") and redlist.get("population") and redlist.get("conservation"))

        # Check Photos
        photos = photos_by_sp.get(sid, [])
        photo_count = len(photos)
        has_primary = bool(sp.get("photo_url"))

        # Scoring
        total_checks = len(CORE_VN_FIELDS) + len(CORE_EN_FIELDS) + 4 # WoRMS, Bio, RedList, Photos
        passed = (len(CORE_VN_FIELDS) - len(missing_vn)) + (len(CORE_EN_FIELDS) - len(missing_en))
        if worms_ok: passed += 1
        if has_bio: passed += 1
        if has_redlist: passed += 1
        if photo_count > 0 and has_primary: passed += 1

        pct = (passed / total_checks) * 100

        if pct >= 95:
            tier = "Complete"
            complete_count += 1
        elif pct >= 70:
            tier = "Partial"
            partial_count += 1
        else:
            tier = "Skeleton"
            skeleton_count += 1

        results.append({
            "id": sid,
            "sci": sci,
            "vn": vn,
            "en": en,
            "pct": pct,
            "tier": tier,
            "missing_vn": missing_vn,
            "missing_en": missing_en,
            "worms_ok": worms_ok,
            "has_bio": has_bio,
            "has_redlist": has_redlist,
            "photo_count": photo_count
        })

    # In kết quả dạng bảng
    print(f"\n{'STT':<4} | {'ID':<18} | {'Tên Khoa Học':<28} | {'Tên Tiếng Việt':<26} | {'Điểm':<6} | {'Xếp Loại':<10} | {'Ảnh':<4} | {'WoRMS':<6} | {'SĐVN'}")
    print("-" * 120)

    for i, r in enumerate(results, 1):
        worms_mark = "✓" if r["worms_ok"] else "✗"
        redlist_mark = "✓" if r["has_redlist"] else "✗"
        print(f"{i:<4} | {r['id']:<18} | {r['sci']:<28} | {r['vn'][:24]:<26} | {r['pct']:>5.1f}% | {r['tier']:<10} | {r['photo_count']:<4} | {worms_mark:<6} | {redlist_mark}")

    print("\n" + "=" * 80)
    print(f"📊 BÁO CÁO TỔNG QUAN CHẤT LƯỢNG DỮ LIỆU THÚ BIỂN (thu-bien):")
    print(f"   • Tổng số loài: {total_species}")
    print(f"   • Complete (≥95%): {complete_count}/{total_species} ({complete_count/total_species*100:.1f}%)")
    print(f"   • Partial  (70-94%): {partial_count}/{total_species} ({partial_count/total_species*100:.1f}%)")
    print(f"   • Skeleton (<70%):  {skeleton_count}/{total_species} ({skeleton_count/total_species*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
