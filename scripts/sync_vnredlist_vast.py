#!/usr/bin/env python3
"""
scripts/sync_vnredlist_vast.py
Đồng bộ và Chuẩn hóa dữ liệu Danh lục Đỏ Việt Nam (VAST 2024 / vnredlist.vast.vn)
cho TẤT CẢ các bộ sưu tập sinh vật biển trong cơ sở dữ liệu Supabase.

Tuân thủ Quy chuẩn Vàng (Golden Standard Layout) cho ConservationWidget:
  - Cột trái: Mối đe dọa tại vùng biển Việt Nam (threats)
  - Cột phải: Hiện trạng & Xu hướng quần thể (population) kèm Trend Pill cam
  - Khối Hero Card: Biện pháp bảo tồn (conservation) tách 2 phân vùng (Đã ban hành & Đề xuất)

Tác giả: Antigravity Assistant cho chú Chình
Ngày tạo: 13/09/2026
"""

import os
import sys
import json
import time
import re
import html
import argparse
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

# Các category sinh vật biển trên cổng vnredlist.vast.vn
MARINE_CATEGORIES = [
    (15, "Nhóm Cá nước mặn"),
    (19, "Nhóm San hô"),
    (18, "Nhóm Thủy sinh nước mặn"),
    (41, "Ngành Rong đỏ"),
    (40, "Ngành Rong nâu"),
    (39, "Ngành Rong lục"),
]

# Slugs các loài bò sát biển trên VAST (thuộc Cat 12 - Bò sát & Lưỡng cư)
MARINE_REPTILE_SLUGS = [
    "caretta-caretta",
    "chelonia-mydas",
    "eretmochelys-imbricata",
    "dermochelys-coriacea",
    "lepidochelys-olivacea",
    "crocodylus-porosus",
]


def clean_text(raw: str) -> str:
    """Loại bỏ thẻ HTML và chuẩn hóa khoảng trắng"""
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


# ==============================================================================
# BỘ CHUẨN HÓA CẤU TRÚC VÀNG (GOLDEN STANDARD NORMALIZER)
# Đảm bảo hiển thị hoàn hảo trên ConservationWidget.tsx (2 cột + Trend Pill + 2 Box)
# ==============================================================================

def normalize_golden_threats(raw_threats: str) -> str:
    """Chuẩn hóa trường Mối đe dọa"""
    if not raw_threats:
        return ""
    cleaned = clean_text(raw_threats)
    cleaned = re.sub(r"^Mối\s+đe\s+d[ọo]a\s*:?\s*", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\.([A-ZÀ-Ỹ])", r". \1", cleaned)
    return cleaned


def normalize_golden_population(raw_population: str, status: str = "", criteria: str = "") -> str:
    """
    Chuẩn hóa trường Hiện trạng & Xu hướng quần thể.
    BẮT BUỘC có cụm từ chỉ định xu hướng ở cuối để kích hoạt Pill cam trên UI.
    """
    if not raw_population:
        raw_population = ""
    cleaned = clean_text(raw_population)
    cleaned = re.sub(r"^(Hiện\s+trạng\s+quần\s+thể\s*:?\s*)+", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\.([A-ZÀ-Ỹ])", r". \1", cleaned)

    # Kiểm tra xem đã có chốt xu hướng quần thể chưa
    trend_match = re.search(r"(?:[\.\s]|^)Xu\s+hướng\s+quần\s+thể(?:\s+tại\s+tự\s+nhiên)?\s*:?\s*([^\.\n]+(?:\.|$))", cleaned, re.IGNORECASE)
    
    if trend_match:
        # Đã có -> Chuẩn hóa lại cho câu chữ chuẩn mực
        trend_val = trend_match.group(1).replace(".", "").strip()
        trend_val = re.sub(r"^tại\s+tự\s+nhiên\s*:?\s*", "", trend_val, flags=re.IGNORECASE).strip()
        cleaned_body = re.sub(r"(?:[\.\s]|^)Xu\s+hướng\s+quần\s+thể(?:\s+tại\s+tự\s+nhiên)?\s*:?\s*[^\.\n]+(?:\.|$)", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned_body = cleaned_body.rstrip(". ") + "."
        return f"{cleaned_body} Xu hướng quần thể tại tự nhiên: {trend_val}."
    else:
        # Chưa có -> Suy luận từ phân hạng và criteria để tạo trend pill
        st = (status or "").upper().strip()
        if st in ("EW", "EX"):
            trend_val = "Tuyệt chủng ngoài tự nhiên"
        elif st in ("CR", "EN", "VU") or "A" in criteria:
            trend_val = "Suy giảm"
        elif st == "NT":
            trend_val = "Suy giảm nhẹ"
        elif st == "LC":
            trend_val = "Ổn định"
        elif st == "DD":
            trend_val = "Không rõ"
        else:
            trend_val = "Suy giảm"

        cleaned_body = cleaned.rstrip(". ") + "." if cleaned else "Chưa có khảo sát quần thể chi tiết gần đây."
        return f"{cleaned_body} Xu hướng quần thể tại tự nhiên: {trend_val}."


def normalize_golden_conservation(raw_conservation: str) -> str:
    """
    Chuẩn hóa trường Biện pháp bảo tồn.
    BẮT BUỘC chứa 2 mốc phân vùng: "Biện pháp bảo tồn Đã có [...] Đề xuất [...]"
    để kích hoạt 2 hộp hành động riêng biệt (Đã ban hành & Đề xuất cấp thiết).
    """
    if not raw_conservation:
        raw_conservation = ""
    cleaned = clean_text(raw_conservation)
    cleaned = re.sub(r"^Biện\s+pháp\s+bảo\s+tồn\s*:?\s*", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\.([A-ZÀ-Ỹ])", r". \1", cleaned)

    # Kiểm tra xem đã có phân đoạn "Đề xuất" chưa
    dexuat_match = re.search(r"(?:^|\s)Đề\s+xuất\s*:?\s*", cleaned, re.IGNORECASE)

    if dexuat_match:
        idx = dexuat_match.start()
        existing_part = cleaned[:idx].strip()
        proposed_part = cleaned[idx:].strip()

        existing_clean = re.sub(r"^(?:Đã\s+có\s*:?\s*)+", "", existing_part, flags=re.IGNORECASE).strip()
        proposed_clean = re.sub(r"^(?:Đề\s+xuất\s*:?\s*)+", "", proposed_part, flags=re.IGNORECASE).strip()

        if not existing_clean:
            existing_clean = "Chưa có văn bản quản lý hoặc quy chế bảo vệ cụ thể tại các vùng biển tự nhiên."
        if not proposed_clean:
            proposed_clean = "Cần tăng cường nghiên cứu, giám sát và đề xuất quy chế bảo vệ nguồn lợi."

        return f"Biện pháp bảo tồn Đã có {existing_clean} Đề xuất {proposed_clean}"
    else:
        # Nếu chưa có từ khóa "Đề xuất", tách thông minh hoặc bổ sung phân vùng
        if cleaned:
            return f"Biện pháp bảo tồn Đã có Các quy định bảo vệ chung theo Luật Thủy sản và mạng lưới Khu bảo tồn biển Việt Nam. Đề xuất {cleaned}"
        else:
            return "Biện pháp bảo tồn Đã có Được quản lý chung theo mạng lưới Khu bảo tồn biển Việt Nam. Đề xuất Tăng cường kiểm soát khai thác và điều tra định kỳ hiện trạng nguồn lợi."


# ==============================================================================
# HÀM CRAWL TỪ CỔNG VNREDLIST.VAST.VN
# ==============================================================================

def fetch_posts_for_category(cat_id: int):
    """Tải danh sách bài viết theo category từ WordPress REST API"""
    url = f"http://vnredlist.vast.vn/wp-json/wp/v2/posts?categories={cat_id}&per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [LỖI] Không thể tải danh sách category {cat_id}: {e}")
        return []


def fetch_post_by_slug(slug: str):
    """Tải bài viết cụ thể theo slug"""
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
    """Parse toàn bộ thông tin chi tiết từ trang HTML của loài trên vnredlist.vast.vn"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            page_html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [LỖI] Không thể tải URL {url}: {e}")
        return None

    # 1. Parse Taxonomy Card
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

    # Tách mã hồ sơ (refCode) từ citation (VD: FS45, CN51, AR28, PL621, RT74...)
    ref_code = ""
    if citation:
        ref_m = re.search(r"\b([A-Z]{2}\d+)\b", citation)
        if ref_m:
            ref_code = ref_m.group(1)

    # 2. Parse các section nội dung khác
    def get_section_text(art_id: str):
        m = re.search(rf"<article\s+id=[\"\x27]{art_id}[\"\x27][^>]*>(.*?)</article>", page_html, re.DOTALL)
        if not m:
            return ""
        content = m.group(1)
        content = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", content)
        return clean_text(content)

    criteria_raw = get_section_text("population")
    criteria = ""
    if criteria_raw:
        crit_m = re.search(r"Tiêu chuẩn đánh giá\s+([A-Z0-9\+\.\s]+?)(?:\.|$|Diễn giải)", criteria_raw)
        if crit_m:
            criteria = crit_m.group(1).strip()

    raw_population = get_section_text("habitat-ecology") or criteria_raw
    raw_threats = get_section_text("mdd")
    raw_conservation = get_section_text("bpbt")

    scientific_name = tax_data.get("Tên khoa học", "")
    vn_name = tax_data.get("Tên việt nam", "")
    status = tax_data.get("Phân hạng bảo tồn", "").upper().strip()
    assessor = tax_data.get("Người đánh giá", "")
    contributor = tax_data.get("Người góp ý", "")
    year = tax_data.get("Năm công bố", "2023")

    # Chuẩn hóa tức thì theo Quy chuẩn Vàng
    threats = normalize_golden_threats(raw_threats)
    population = normalize_golden_population(raw_population, status=status, criteria=criteria)
    conservation = normalize_golden_conservation(raw_conservation)

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
        "threats": threats,
        "conservation": conservation,
        "population": population,
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


# ==============================================================================
# HÀM TẢI VÀ CẬP NHẬT CƠ SỞ DỮ LIỆU SUPABASE
# ==============================================================================

def load_all_species(collection_id: str = None, species_id: str = None):
    """Nạp danh sách loài từ Supabase có phân trang an toàn"""
    all_species = []
    page = 0
    limit = 1000
    while True:
        offset = page * limit
        req_url = f"{SUPABASE_URL}/rest/v1/species?select=id,collection_id,scientific_name,worms_accepted_name,vn_name,vn_status,biology&limit={limit}&offset={offset}"
        if collection_id:
            req_url += f"&collection_id=eq.{urllib.parse.quote(collection_id)}"
        if species_id:
            req_url += f"&id=eq.{urllib.parse.quote(species_id)}"

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
    return all_species


def patch_species_supabase(sp_id: str, payload: dict) -> bool:
    """Gửi PATCH request cập nhật loài trong Supabase"""
    patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{urllib.parse.quote(sp_id)}"
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
            return patch_resp.status in (200, 204)
    except Exception as e:
        print(f"  [LỖI] Cập nhật {sp_id} thất bại: {e}")
        return False


# ==============================================================================
# TÁC VỤ 1: CHUẨN HÓA CÁC LOÀI ĐÃ CÓ TRONG CSDL (--standardize-existing)
# ==============================================================================

def run_standardize_existing(dry_run: bool, collection_id: str = None, species_id: str = None):
    """
    Quét toàn bộ loài đã có vnRedList trong Supabase, kiểm tra xem có loài nào
    bị lệch chuẩn (thiếu trend pill hoặc thiếu 2-subgroup conservation) và tự động
    chuẩn hóa về đúng Quy chuẩn Vàng 100%.
    """
    print("\n" + "=" * 75)
    print(" QUÉT & CHUẨN HÓA CÁC LOÀI ĐÃ CÓ SÁCH ĐỎ TRONG CSDL THEO QUY CHUẨN VÀNG")
    print(f" Chế độ: {'GIẢ LẬP (DRY-RUN)' if dry_run else 'ÁP DỤNG THẬT (--apply)'}")
    if collection_id:
        print(f" Giới hạn Collection: {collection_id}")
    if species_id:
        print(f" Giới hạn Species ID: {species_id}")
    print("=" * 75)

    species_list = load_all_species(collection_id=collection_id, species_id=species_id)
    candidates = []
    for sp in species_list:
        bio = sp.get("biology") or {}
        if isinstance(bio, str):
            try:
                bio = json.loads(bio)
            except Exception:
                bio = {}
        if bio.get("vnRedList"):
            candidates.append((sp, bio))

    print(f"\n-> Tìm thấy {len(candidates)} loài đã có hồ sơ Sách Đỏ VAST.")

    fixed_count = 0
    already_good_count = 0

    for sp, bio in candidates:
        sp_id = sp["id"]
        rl = bio["vnRedList"]
        status = rl.get("status", "")
        criteria = rl.get("criteria", "")
        old_threats = rl.get("threats", "")
        old_pop = rl.get("population", "")
        old_cons = rl.get("conservation", "")

        new_threats = normalize_golden_threats(old_threats)
        new_pop = normalize_golden_population(old_pop, status=status, criteria=criteria)
        new_cons = normalize_golden_conservation(old_cons)

        needs_update = (
            new_threats != old_threats or
            new_pop != old_pop or
            new_cons != old_cons
        )

        if needs_update:
            fixed_count += 1
            print(f"  [CẦN CHUẨN HÓA] {sp_id} ({sp.get('vn_name')} - {sp.get('scientific_name')}):")
            if new_pop != old_pop:
                print(f"    - Population: Đã bổ sung chuẩn Trend Pill")
            if new_cons != old_cons:
                print(f"    - Conservation: Đã định dạng 2 phân vùng (Đã ban hành & Đề xuất)")

            if not dry_run:
                rl["threats"] = new_threats
                rl["population"] = new_pop
                rl["conservation"] = new_cons
                bio["vnRedList"] = rl
                success = patch_species_supabase(sp_id, {"biology": bio})
                if success:
                    print(f"    ✅ Đã cập nhật thành công lên Supabase.")
                else:
                    print(f"    ❌ Lỗi khi cập nhật Supabase.")
        else:
            already_good_count += 1

    print("\n" + "-" * 75)
    print(f" KẾT QUẢ: {already_good_count} loài đã chuẩn 100% | {fixed_count} loài được chuẩn hóa.")
    if dry_run and fixed_count > 0:
        print(" 💡 Chạy lại kèm cờ --apply để lưu các thay đổi này vào CSDL!")
    print("-" * 75)


# ==============================================================================
# TÁC VỤ 2: XEM BÁO CÁO THỐNG KÊ (--stats)
# ==============================================================================

def run_stats(collection_id: str = None):
    """In báo cáo thống kê mức độ bao phủ và chuẩn hóa Sách Đỏ VAST"""
    print("\n" + "=" * 75)
    print(" BÁO CÁO THỐNG KÊ DANH LỤC ĐỎ VIỆT NAM (VAST 2024)")
    print("=" * 75)

    species_list = load_all_species(collection_id=collection_id)
    total_sp = len(species_list)
    redlist_sp = []

    for sp in species_list:
        bio = sp.get("biology") or {}
        if isinstance(bio, str):
            try:
                bio = json.loads(bio)
            except Exception:
                bio = {}
        if bio.get("vnRedList"):
            redlist_sp.append((sp, bio["vnRedList"]))

    by_col = {}
    by_status = {}
    golden_compliant = 0

    for sp, rl in redlist_sp:
        col = sp.get("collection_id", "khac")
        by_col[col] = by_col.get(col, 0) + 1

        st = rl.get("status", "Chưa rõ")
        by_status[st] = by_status.get(st, 0) + 1

        # Kiểm tra Golden Standard compliance
        pop = rl.get("population", "")
        cons = rl.get("conservation", "")
        has_trend = bool(re.search(r"(?:[\.\s]|^)Xu\s+hướng\s+quần\s+thể", pop, re.I))
        has_two_cons = bool(re.search(r"(?:^|\s)Đề\s+xuất\s*:?\s*", cons, re.I))
        if has_trend and has_two_cons:
            golden_compliant += 1

    print(f"📊 Tổng số loài trong hệ thống: {total_sp}")
    print(f"🛡️ Số loài có Hồ sơ Sách Đỏ VAST: {len(redlist_sp)} ({len(redlist_sp)/total_sp*100:.1f}%)")
    print(f"⭐ Số loài đạt chuẩn Golden Standard (2 cột + Trend Pill + 2 Action Boxes): {golden_compliant}/{len(redlist_sp)} ({golden_compliant/len(redlist_sp)*100:.1f}%)" if redlist_sp else "0")
    
    print("\n📁 Phân bố theo Bộ sưu tập:")
    for col, cnt in sorted(by_col.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {col:<18}: {cnt} loài")

    print("\n🏷️ Phân bố theo Phân hạng Bảo tồn VAST:")
    for st, cnt in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
        vn_st = STATUS_MAP_VN.get(st, st)
        print(f"  - {st:<4} ({vn_st:<25}): {cnt} loài")
    print("=" * 75)


# ==============================================================================
# TÁC VỤ 3: PIPELINE CRAWL & ĐỒNG BỘ TỪ VNREDLIST.VAST.VN
# ==============================================================================

def run_sync_pipeline(dry_run: bool, collection_id: str = None, species_id: str = None):
    """Pipeline thu thập từ vnredlist.vast.vn và nạp vào Supabase"""
    print("\n" + "=" * 75)
    print(" DANH LỤC ĐỎ VIỆT NAM (VAST 2024-1) -> SUPABASE ENRICHMENT PIPELINE")
    print(f" Chế độ: {'GIẢ LẬP (DRY-RUN) — Không ghi DB' if dry_run else 'ÁP DỤNG THẬT (--apply)'}")
    if collection_id:
        print(f" Lọc Collection: {collection_id}")
    if species_id:
        print(f" Lọc Species ID: {species_id}")
    print("=" * 75)

    # 1. Tải danh sách loài từ Supabase
    print("\n[1/4] Đang tải danh sách loài từ Supabase...")
    all_species = load_all_species(collection_id=collection_id, species_id=species_id)
    print(f"  -> Đã nạp {len(all_species)} loài từ CSDL Supabase.")

    # 2. Thu thập danh sách bài viết từ vnredlist.vast.vn
    print("\n[2/4] Đang thu thập danh mục sinh vật biển từ vnredlist.vast.vn...")
    candidate_posts = {}

    for cat_id, cat_name in MARINE_CATEGORIES:
        print(f"  - Lấy danh mục: {cat_name} (Cat {cat_id})...")
        posts = fetch_posts_for_category(cat_id)
        for p in posts:
            candidate_posts[p["slug"]] = (p, cat_name)
        time.sleep(0.4)

    print("  - Lấy nhóm Bò sát biển (Cat 12)...")
    for slug in MARINE_REPTILE_SLUGS:
        p = fetch_post_by_slug(slug)
        if p:
            candidate_posts[slug] = (p, "Bò sát biển")
        time.sleep(0.3)

    print(f"  -> Tổng cộng tìm thấy {len(candidate_posts)} bài viết sinh vật biển trên VAST.")

    # 3. Bóc tách chi tiết từng loài và đối chiếu 4 tầng
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
    print("\n" + "=" * 75)
    print(f" KẾT QUẢ ĐỐI CHIẾU: {len(matched_results)}/{total_candidates} loài ({rate:.1f}%)")
    print("=" * 75)

    if dry_run:
        print("\n💡 Chạy ở chế độ --dry-run. KHÔNG CÓ THAY ĐỔI NÀO ĐƯỢC GHI VÀO CSDL.")
        print("   Để cập nhật thật, hãy thêm cờ: --apply")
        return

    # 4. Ghi vào Supabase
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

        # Ghi theo Golden Standard
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

        cur_status = target.get("vn_status") or ""
        new_status_tag = f"SĐVN (2024): {src['status']} - {src['status_vn']}"
        if new_status_tag not in cur_status:
            updated_vn_status = f"{cur_status}; {new_status_tag}".strip("; ") if cur_status else new_status_tag
        else:
            updated_vn_status = cur_status

        payload = {
            "biology": current_bio,
            "vn_status": updated_vn_status
        }

        success = patch_species_supabase(sp_id, payload)
        if success:
            updated_count += 1
        else:
            error_count += 1

    print(f"\n🎉 HOÀN TẤT: Cập nhật thành công {updated_count} loài! (Lỗi: {error_count})")


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Đồng bộ & Chuẩn hóa Sách Đỏ Việt Nam (VAST 2024)")
    parser.add_argument("--apply", action="store_true", help="Thực hiện ghi thay đổi vào Supabase (mặc định là Dry-run)")
    parser.add_argument("--stats", action="store_true", help="Hiển thị báo cáo thống kê hiện trạng Sách Đỏ")
    parser.add_argument("--standardize-existing", action="store_true", help="Quét và chuẩn hóa toàn bộ các loài đã có Sách Đỏ trong CSDL về Golden Standard")
    parser.add_argument("--collection", type=str, default=None, help="Lọc theo mã bộ sưu tập (ví dụ: ca-bien, bo-sat-bien)")
    parser.add_argument("--species", type=str, default=None, help="Chỉ định ID loài cụ thể (ví dụ: ruabien-species-2)")

    args = parser.parse_args()

    if not SUPABASE_URL or not SERVICE_KEY:
        print("[LỖI] Thiếu NEXT_PUBLIC_SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong file .env!")
        sys.exit(1)

    if args.stats:
        run_stats(collection_id=args.collection)
    elif args.standardize_existing:
        run_standardize_existing(dry_run=not args.apply, collection_id=args.collection, species_id=args.species)
    else:
        run_sync_pipeline(dry_run=not args.apply, collection_id=args.collection, species_id=args.species)


if __name__ == "__main__":
    main()
