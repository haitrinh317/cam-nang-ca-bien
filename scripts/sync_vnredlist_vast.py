#!/usr/bin/env python3
"""
scripts/sync_vnredlist_vast.py
Đồng bộ dữ liệu Danh lục Đỏ Việt Nam (Version 2024-1) từ http://vnredlist.vast.vn/
vào cơ sở dữ liệu Supabase (bảng species, trường biology.vnRedList).

Tác giả: Antigravity Assistant cho chú Chình
Ngày tạo: 13/09/2026
"""

import os
import sys
import json
import time
import re
import html
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

STATUS_MAP_VN = {
    "EX": "Tuyệt chủng",
    "EW": "Tuyệt chủng ngoài tự nhiên",
    "CR": "Cực kỳ nguy cấp",
    "EN": "Nguy cấp",
    "VU": "Sắp nguy cấp",
    "NT": "Gần bị đe dọa",
    "LC": "Ít quan tâm",
    "DD": "Thiếu dữ liệu"
}

# Các category sinh vật biển trên vnredlist.vast.vn
MARINE_CATEGORIES = [
    (15, "Nhóm Cá nước mặn"),
    (19, "Nhóm San hô"),
    (18, "Nhóm Thủy sinh nước mặn"),
    (41, "Ngành Rong đỏ"),
    (40, "Ngành Rong nâu"),
    (39, "Ngành Rong lục"),
]

# Các loài bò sát biển (rùa biển, rắn biển) trong Cat 12
MARINE_REPTILE_SLUGS = [
    "caretta-caretta",
    "chelonia-mydas",
    "eretmochelys-imbricata",
    "dermochelys-coriacea",
    "lepidochelys-olivacea",
]


def clean_text(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return " ".join(text.split()).strip()


def extract_latin_base(name: str) -> str:
    """Tách tên chi + loài cơ bản (bỏ tác giả, năm, ngoặc đơn)"""
    if not name:
        return ""
    clean = re.sub(r"\(.*?\)", "", name).strip()
    words = clean.split()
    if len(words) >= 2:
        return f"{words[0]} {words[1]}".strip()
    return clean


def fetch_posts_for_category(cat_id: int):
    url = f"http://vnredlist.vast.vn/wp-json/wp/v2/posts?categories={cat_id}&per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [LỖI] Không thể tải danh sách category {cat_id}: {e}")
        return []


def fetch_post_by_slug(slug: str):
    url = f"http://vnredlist.vast.vn/wp-json/wp/v2/posts?slug={slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            posts = json.loads(resp.read().decode("utf-8"))
            return posts[0] if posts else None
    except Exception as e:
        print(f"  [LỖI] Không thể tải bài {slug}: {e}")
        return None


def parse_species_page(url: str):
    """Parse toàn bộ thông tin chi tiết từ trang HTML của loài"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            page_html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [LỖI] Không thể tải URL {url}: {e}")
        return None

    # Parse taxonomy card
    tax_section_m = re.search(r"<article\s+id=[\"\x27]taxonomy[\"\x27][^>]*>(.*?)</article>", page_html, re.DOTALL)
    tax_data = {}
    citation = ""
    if tax_section_m:
        tax_sec = tax_section_m.group(1)
        items = re.findall(r"<h3[^>]*>(.*?)</h3>.*?<p[^>]*>(.*?)</p>", tax_sec, re.DOTALL)
        for h, p in items:
            h_clean = clean_text(h)
            p_clean = clean_text(p)
            tax_data[h_clean] = p_clean

        cit_m = re.search(r"id=[\"\x27]taxonomy-details[\"\x27][^>]*>(.*?)</div>", tax_sec, re.DOTALL)
        if cit_m:
            citation = clean_text(cit_m.group(1))

    # Tách mã hồ sơ (refCode) từ citation (VD: FS45, CN51, AR28, PL621, RE12...)
    ref_code = ""
    if citation:
        ref_m = re.search(r"\b([A-Z]{2}\d+)\b", citation)
        if ref_m:
            ref_code = ref_m.group(1)

    # Parse các section khác
    def get_section_text(art_id: str):
        m = re.search(rf"<article\s+id=[\"\x27]{art_id}[\"\x27][^>]*>(.*?)</article>", page_html, re.DOTALL)
        if not m:
            return ""
        content = m.group(1)
        # Loại bỏ các tiêu đề h2/h3 mặc định
        content = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", content)
        return clean_text(content)

    criteria_raw = get_section_text("population")
    criteria = ""
    if criteria_raw:
        crit_m = re.search(r"Tiêu chuẩn đánh giá\s+([A-Z0-9\+\.\s]+?)(?:\.|$|Diễn giải)", criteria_raw)
        if crit_m:
            criteria = crit_m.group(1).strip()

    population = get_section_text("habitat-ecology")
    threats = get_section_text("mdd")
    conservation = get_section_text("bpbt")

    scientific_name = tax_data.get("Tên khoa học", "")
    vn_name = tax_data.get("Tên việt nam", "")
    status = tax_data.get("Phân hạng bảo tồn", "").upper().strip()
    assessor = tax_data.get("Người đánh giá", "")
    contributor = tax_data.get("Người góp ý", "")
    year = tax_data.get("Năm công bố", "2023")

    return {
        "scientific_name": scientific_name,
        "base_scientific_name": extract_latin_base(scientific_name),
        "vn_name": vn_name,
        "status": status,
        "status_vn": STATUS_MAP_VN.get(status, status),
        "year": year,
        "version": "2024-1",
        "assessor": assessor,
        "contributor": contributor,
        "refCode": ref_code,
        "citation": citation,
        "criteria": criteria,
        "threats": threats[:1000] if threats else "",
        "conservation": conservation[:1000] if conservation else "",
        "population": population[:1000] if population else "",
        "url": url,
    }


def query_species_in_supabase(all_species_cache, red_item):
    """
    Đối chiếu loài từ vnredlist với cache dữ liệu Supabase:
    1. Trùng chính xác scientific_name
    2. Trùng qua worms_accepted_name
    3. Trùng qua base genus species
    4. Trùng qua vn_name (nếu có)
    """
    base_target = red_item["base_scientific_name"].lower()
    full_target = red_item["scientific_name"].lower()
    vn_target = red_item["vn_name"].lower().replace(" ", "")

    # 1. Khớp scientific_name
    for sp in all_species_cache:
        sp_name = (sp.get("scientific_name") or "").lower()
        if sp_name and (sp_name == full_target or sp_name == base_target):
            return sp, "Tên khoa học gốc"

    # 2. Khớp worms_accepted_name
    for sp in all_species_cache:
        worms_name = (sp.get("worms_accepted_name") or "").lower()
        if worms_name and (worms_name == full_target or worms_name == base_target):
            return sp, "WoRMS Accepted Name"

    # 3. Khớp base latin name
    for sp in all_species_cache:
        sp_base = extract_latin_base(sp.get("scientific_name") or "").lower()
        worms_base = extract_latin_base(sp.get("worms_accepted_name") or "").lower()
        if base_target and (base_target == sp_base or base_target == worms_base):
            return sp, "Base Latin Name"

    # 4. Khớp tên tiếng Việt
    if vn_target:
        for sp in all_species_cache:
            sp_vn = (sp.get("vn_name") or "").lower().replace(" ", "")
            if sp_vn and sp_vn == vn_target:
                return sp, "Tên tiếng Việt"

    return None, None


def main():
    dry_run = "--apply" not in sys.argv
    print("=" * 70)
    print(" DANH LỤC ĐỎ VIỆT NAM (VAST 2024-1) -> SUPABASE ENRICHMENT PIPELINE")
    print(f" Chế độ: {'GIẢ LẬP (DRY-RUN) — Không ghi DB' if dry_run else 'ÁP DỤNG THẬT (--apply)'}")
    print("=" * 70)

    if not SUPABASE_URL or not SERVICE_KEY:
        print("[LỖI] Thiếu NEXT_PUBLIC_SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY!")
        sys.exit(1)

    # 1. Tải toàn bộ danh sách loài hiện có từ Supabase
    print("\n[1/4] Đang tải danh sách loài từ Supabase...")
    all_species = []
    page = 0
    limit = 1000
    while True:
        offset = page * limit
        req_url = f"{SUPABASE_URL}/rest/v1/species?select=id,collection_id,scientific_name,worms_accepted_name,vn_name,vn_status,biology&limit={limit}&offset={offset}"
        req = urllib.request.Request(req_url, headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}"
        })
        with urllib.request.urlopen(req) as resp:
            chunk = json.loads(resp.read().decode("utf-8"))
            if not chunk:
                break
            all_species.extend(chunk)
            if len(chunk) < limit:
                break
            page += 1

    print(f"  -> Đã nạp {len(all_species)} loài từ CSDL Supabase.")

    # 2. Thu thập danh sách bài viết từ vnredlist.vast.vn
    print("\n[2/4] Đang thu thập danh mục sinh vật biển từ vnredlist.vast.vn...")
    candidate_posts = {}

    for cat_id, cat_name in MARINE_CATEGORIES:
        print(f"  - Lấy danh mục: {cat_name} (Cat {cat_id})...")
        posts = fetch_posts_for_category(cat_id)
        for p in posts:
            candidate_posts[p["slug"]] = (p, cat_name)
        time.sleep(0.5)

    print("  - Lấy nhóm Bò sát biển (Cat 12)...")
    for slug in MARINE_REPTILE_SLUGS:
        p = fetch_post_by_slug(slug)
        if p:
            candidate_posts[slug] = (p, "Bò sát biển")
        time.sleep(0.3)

    print(f"  -> Tổng cộng tìm thấy {len(candidate_posts)} bài viết sinh vật biển trên VAST.")

    # 3. Bóc tách chi tiết từng loài và đối chiếu
    print("\n[3/4] Đang phân tích chi tiết và đối chiếu với CSDL...")
    matched_results = []
    unmatched_results = []

    count = 0
    for slug, (p, cat_name) in candidate_posts.items():
        count += 1
        link = p["link"]
        parsed = parse_species_page(link)
        if not parsed or not parsed["status"]:
            continue

        matched_sp, match_type = query_species_in_supabase(all_species, parsed)
        if matched_sp:
            matched_results.append({
                "source": parsed,
                "target_species": matched_sp,
                "match_type": match_type,
                "category": cat_name
            })
            print(f"  [{count}/{len(candidate_posts)}] ✅ Khớp ({match_type}): {parsed['scientific_name']} [{parsed['status']}] -> [{matched_sp['collection_id']}] {matched_sp['vn_name']}")
        else:
            unmatched_results.append({
                "source": parsed,
                "category": cat_name
            })
            print(f"  [{count}/{len(candidate_posts)}] ⚠️ Chưa khớp: {parsed['scientific_name']} ({parsed['vn_name']}) [{parsed['status']}]")

        time.sleep(0.2)

    total_candidates = len(matched_results) + len(unmatched_results)
    rate = (len(matched_results) / total_candidates * 100) if total_candidates > 0 else 0
    print("\n" + "=" * 70)
    print(f" KẾT QUẢ ĐỐI CHIẾU: {len(matched_results)}/{total_candidates} loài ({rate:.1f}%)")
    print("=" * 70)

    # 4. Ghi vào Supabase nếu ở chế độ --apply
    if dry_run:
        print("\n💡 Chạy ở chế độ --dry-run. KHÔNG CÓ THAY ĐỔI NÀO ĐƯỢC GHI VÀO CSDL.")
        print("   Để cập nhật thật, hãy chạy: python3 scripts/sync_vnredlist_vast.py --apply")
        return

    print("\n[4/4] Đang cập nhật dữ liệu vào Supabase...")
    updated_count = 0
    error_count = 0

    for item in matched_results:
        src = item["source"]
        target = item["target_species"]
        sp_id = target["id"]

        current_bio = target.get("biology") or {}
        if isinstance(current_bio, str):
            try:
                current_bio = json.loads(current_bio)
            except Exception:
                current_bio = {}

        # Cập nhật vnRedList vào biology
        current_bio["vnRedList"] = {
            "status": src["status"],
            "statusVn": src["status_vn"],
            "year": src["year"],
            "version": src["version"],
            "assessor": src["assessor"],
            "contributor": src["contributor"],
            "refCode": src["refCode"],
            "citation": src["citation"],
            "criteria": src["criteria"],
            "threats": src["threats"],
            "conservation": src["conservation"],
            "population": src["population"],
            "url": src["url"]
        }

        # Cập nhật vn_status thân thiện nếu chưa có hoặc có thể bổ sung
        cur_status = target.get("vn_status") or ""
        new_status_tag = f"SĐVN (2024): {src['status']} - {src['status_vn']}"
        if new_status_tag not in cur_status:
            updated_vn_status = f"{cur_status}; {new_status_tag}".strip("; ") if cur_status else new_status_tag
        else:
            updated_vn_status = cur_status

        # Payload gửi Supabase
        payload = {
            "biology": current_bio,
            "vn_status": updated_vn_status
        }

        # Gửi PATCH request
        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        patch_req = urllib.request.Request(
            patch_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            method="PATCH"
        )

        try:
            with urllib.request.urlopen(patch_req) as patch_resp:
                if patch_resp.status in (200, 204):
                    updated_count += 1
                else:
                    error_count += 1
        except Exception as e:
            print(f"  [LỖI] Cập nhật loài {sp_id} thất bại: {e}")
            error_count += 1

    print(f"\n🎉 HOÀN TẤT: Cập nhật thành công {updated_count} loài! (Lỗi: {error_count})")


if __name__ == "__main__":
    main()
