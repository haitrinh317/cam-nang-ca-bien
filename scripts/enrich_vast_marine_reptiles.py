#!/usr/bin/env python3
"""
scripts/enrich_vast_marine_reptiles.py
Trích xuất dữ liệu Sách Đỏ Việt Nam (VAST 2024-1) toàn diện từ http://vnredlist.vast.vn/
và đồng bộ vào Supabase cho 6 loài bò sát biển (5 loài rùa biển + 1 loài cá sấu hoa cà).

Các trường được làm giàu:
- biology.vnRedList: Hồ sơ Sách Đỏ VAST đầy đủ (tiêu chuẩn, người đánh giá, hiện trạng, sinh cảnh, thức ăn, sinh sản, biện pháp...)
- vn_alternate_names: Bổ sung tên gọi phổ thông từ VAST (Tráng bông, Rùa xanh, Đồi mồi dứa...)
- synonyms: Bổ sung các tên đồng danh từ VAST
- vn_status: Chuẩn hóa đầy đủ các cấp độ bảo tồn (SĐVN 2007, SĐVN VAST 2024, IUCN toàn cầu, CITES, Nghị định 64/2019 và 26/2019)
- vn_distribution: Cập nhật vùng phân bố chi tiết theo hồ sơ VAST
- vn_literature: Thêm citation và tài liệu tham khảo của Sách Đỏ VAST
- ecology_vn: Bổ sung tập tính thức ăn, mùa sinh sản và sinh cảnh phân bố

Tác giả: Antigravity Assistant cho chú Chình
Ngày thực hiện: 13/09/2026
"""

import os
import sys
import json
import re
import html
import urllib.request
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

TARGET_SPECIES = [
    {
        "id": "ruabien-species-1",
        "scientific_name": "Chelonia mydas",
        "url": "http://vnredlist.vast.vn/chelonia-mydas/"
    },
    {
        "id": "ruabien-species-2",
        "scientific_name": "Eretmochelys imbricata",
        "url": "http://vnredlist.vast.vn/eretmochelys-imbricata/"
    },
    {
        "id": "ruabien-species-3",
        "scientific_name": "Lepidochelys olivacea",
        "url": "http://vnredlist.vast.vn/lepidochelys-olivacea/"
    },
    {
        "id": "ruabien-species-4",
        "scientific_name": "Caretta caretta",
        "url": "http://vnredlist.vast.vn/caretta-caretta/"
    },
    {
        "id": "ruabien-species-5",
        "scientific_name": "Dermochelys coriacea",
        "url": "http://vnredlist.vast.vn/dermochelys-coriacea/"
    },
    {
        "id": "casau-species-1",
        "scientific_name": "Crocodylus porosus",
        "url": "http://vnredlist.vast.vn/leiolepis-rubritaeniata/"
    }
]

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

def clean(t: str) -> str:
    if not t:
        return ""
    text = re.sub(r"<[^>]+>", " ", t)
    text = html.unescape(text)
    return " ".join(text.split()).strip()

def parse_vast_full(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        page_html = resp.read().decode("utf-8")

    articles = re.findall(r"<article\s+id=[\x27\"]([^\x27\"]+)[\x27\"][^>]*>(.*?)</article>", page_html, re.DOTALL)
    sections_data = {}
    
    for aid, content in articles:
        pairs = re.findall(r"<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>", content, re.DOTALL)
        pair_dict = {clean(k): clean(v) for k, v in pairs if clean(k)}
        full_text = clean(re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", " ", content))
        sections_data[aid] = {
            "fields": pair_dict,
            "text": full_text
        }

    # Citation & RefCode
    citation = ""
    ref_code = ""
    cit_m = re.search(r"id=[\"\x27]taxonomy-details[\"\x27][^>]*>(.*?)</div>", page_html, re.DOTALL)
    if cit_m:
        citation = clean(cit_m.group(1))
        ref_m = re.search(r"\b([A-Z]{2}\d+)\b", citation)
        if ref_m:
            ref_code = ref_m.group(1)

    tax_f = sections_data.get("taxonomy", {}).get("fields", {})
    assess_f = sections_data.get("assessment-information", {}).get("fields", {})
    geo_f = sections_data.get("geographic-range", {}).get("fields", {})
    pop_f = sections_data.get("population", {}).get("fields", {})
    hab_f = sections_data.get("habitat-ecology", {}).get("fields", {})
    threats_f = sections_data.get("threats", {}).get("fields", {})
    bpbt_f = sections_data.get("bpbt", {}).get("fields", {})
    mdd_text = sections_data.get("mdd", {}).get("text", "")
    use_trade_text = sections_data.get("use-trade", {}).get("text", "")
    biblio_text = sections_data.get("bibliography", {}).get("text", "")

    status = (pop_f.get("Phân hạng") or tax_f.get("Phân hạng bảo tồn") or "").upper().strip()
    criteria = pop_f.get("Tiêu chuẩn đánh giá", "").strip()

    return {
        "scientific_name": tax_f.get("Tên khoa học") or assess_f.get("Tên khoa học", ""),
        "vn_name": tax_f.get("Tên việt nam", ""),
        "alt_names_vast": assess_f.get("Tên phổ thông", ""),
        "synonyms_vast": assess_f.get("Synonym", ""),
        "status": status,
        "statusVn": STATUS_MAP_VN.get(status, status),
        "criteria": criteria,
        "year": tax_f.get("Năm công bố", "2023"),
        "version": "2024-1",
        "assessor": tax_f.get("Người đánh giá", ""),
        "contributor": tax_f.get("Người góp ý", ""),
        "refCode": ref_code,
        "citation": citation,
        "evalRationale": pop_f.get("Diễn giải đánh giá theo các tiêu chuẩn", ""),
        "distributionVn": geo_f.get("Việt nam", ""),
        "distributionWorld": geo_f.get("Thế giới", ""),
        "populationStatus": hab_f.get("Hiện trạng quần thể", ""),
        "populationTrend": hab_f.get("Xu hướng quần thể", ""),
        "habitat": threats_f.get("Đặc điểm sinh cảnh sống", ""),
        "reproduction": threats_f.get("Đặc điểm sinh sản", ""),
        "feeding": threats_f.get("Thức ăn", ""),
        "threats": mdd_text,
        "useTrade": use_trade_text,
        "conservationExisting": bpbt_f.get("Đã có", ""),
        "conservationProposed": bpbt_f.get("Đề xuất", ""),
        "bibliography": biblio_text,
        "url": url,
    }

def main():
    print("=" * 70)
    print(" LÀM GIÀU DỮ LIỆU SÁCH ĐỎ VAST CHO 6 LOÀI BÒ SÁT BIỂN (BẢN TOÀN DIỆN)")
    print("=" * 70)

    for item in TARGET_SPECIES:
        sp_id = item["id"]
        print(f"\n[+] Đang xử lý: {sp_id} ({item['scientific_name']})...")
        vast = parse_vast_full(item["url"])
        print(f"  - Phân hạng: {vast['status']} ({vast['statusVn']}) | Tiêu chuẩn: {vast['criteria'] or 'N/A'}")
        print(f"  - Mã hồ sơ: {vast['refCode']} | Người đánh giá: {vast['assessor']}")
        if vast['alt_names_vast']:
            print(f"  - Tên phổ thông bổ sung: {vast['alt_names_vast']}")
        if vast['synonyms_vast']:
            print(f"  - Đồng danh VAST: {vast['synonyms_vast']}")

        # Lấy dữ liệu hiện tại
        req_get = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}&select=*",
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}"
            }
        )
        with urllib.request.urlopen(req_get) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            if not rows:
                print(f"  [!] Không tìm thấy {sp_id} trong DB!")
                continue
            curr = rows[0]

        curr_bio = curr.get("biology") or {}

        # 1. vnRedList object chuẩn
        vn_red_list_obj = {
            "url": vast["url"],
            "year": vast["year"],
            "status": vast["status"],
            "statusVn": vast["statusVn"],
            "refCode": vast["refCode"],
            "criteria": vast["criteria"],
            "assessor": vast["assessor"],
            "contributor": vast["contributor"],
            "citation": vast["citation"],
            "distributionVn": vast["distributionVn"],
            "distributionWorld": vast["distributionWorld"],
            "populationStatus": vast["populationStatus"],
            "populationTrend": vast["populationTrend"],
            "evalRationale": vast["evalRationale"],
            "habitat": vast["habitat"],
            "reproduction": vast["reproduction"],
            "feeding": vast["feeding"],
            "threats": vast["threats"],
            "conservationExisting": vast["conservationExisting"],
            "conservationProposed": vast["conservationProposed"],
            "useTrade": vast["useTrade"],
            "version": "2024-1"
        }
        curr_bio["vnRedList"] = vn_red_list_obj
        if vast["status"] in ["CR", "EN", "VU"]:
            curr_bio["iucnStatus"] = vast["status"]

        # 2. vn_alternate_names: gộp thêm tên từ VAST
        curr_alt = curr.get("vn_alternate_names") or ""
        alt_list = [x.strip() for x in curr_alt.split(",") if x.strip()]
        if vast["alt_names_vast"]:
            # Tách dấu phẩy / chấm phẩy
            raw_vast_alts = re.split(r"[,;.]", vast["alt_names_vast"])
            for va in raw_vast_alts:
                va_clean = va.strip()
                if va_clean and va_clean.lower() not in [x.lower() for x in alt_list]:
                    alt_list.append(va_clean)
        new_alt_names = ", ".join(alt_list)

        # 3. synonyms: gộp thêm tên đồng danh
        curr_syn = curr.get("synonyms") or []
        if isinstance(curr_syn, str):
            try:
                curr_syn = json.loads(curr_syn)
            except:
                curr_syn = [curr_syn]
        if vast["synonyms_vast"]:
            vast_syns = [s.strip() for s in vast["synonyms_vast"].split(";") if s.strip()]
            for vs in vast_syns:
                if vs and vs not in curr_syn:
                    curr_syn.append(vs)

        # 4. vn_status: Đồng bộ chuẩn hóa
        curr_vn_status = curr.get("vn_status") or ""
        crit_part = f" ({vast['criteria']})" if vast["criteria"] else ""
        vast_status_tag = f"SĐVN VAST (2024): {vast['status']} - {vast['statusVn']}{crit_part}"
        if "SĐVN VAST (2024)" in curr_vn_status:
            new_vn_status = re.sub(r"SĐVN VAST \(2024\):[^;]+", vast_status_tag, curr_vn_status)
        else:
            new_vn_status = f"{curr_vn_status}; {vast_status_tag}".strip("; ")

        # 5. vn_distribution
        curr_dist = curr.get("vn_distribution") or ""
        if vast["distributionVn"] and vast["distributionVn"] not in curr_dist:
            new_dist = f"{curr_dist}. Theo Danh lục Đỏ VAST (2024): {vast['distributionVn']}.".replace("..", ".").strip()
        else:
            new_dist = curr_dist

        # 6. vn_literature
        curr_lit = curr.get("vn_literature") or ""
        lit_additions = []
        if vast["citation"] and vast["citation"] not in curr_lit:
            lit_additions.append(vast["citation"])
        if vast["bibliography"] and len(vast["bibliography"]) > 10:
            # Lấy 1-2 trích dẫn đầu từ bibliography của VAST
            first_ref = vast["bibliography"].split(". ")[0].strip()
            if first_ref and first_ref not in curr_lit:
                lit_additions.append(f"Tài liệu dẫn VAST: {first_ref}")
        if lit_additions:
            new_lit = f"{curr_lit}; {'; '.join(lit_additions)}".strip("; ")
        else:
            new_lit = curr_lit

        # 7. ecology_vn
        curr_eco = curr.get("ecology_vn") or ""
        eco_additions = []
        if vast["habitat"] and vast["habitat"] not in curr_eco:
            eco_additions.append(f"Sinh cảnh (VAST): {vast['habitat']}")
        if vast["reproduction"] and vast["reproduction"] not in curr_eco:
            eco_additions.append(f"Sinh sản: {vast['reproduction']}")
        if vast["feeding"] and vast["feeding"] not in curr_eco:
            eco_additions.append(f"Thức ăn: {vast['feeding']}")
        if vast["populationStatus"] and vast["populationStatus"] not in curr_eco:
            eco_additions.append(f"Hiện trạng & Xu hướng quần thể (VAST 2024): {vast['populationStatus']}. Xu hướng: {vast['populationTrend']}.")

        if eco_additions:
            new_eco = f"{curr_eco}\n\n" + "\n".join(eco_additions)
            new_eco = new_eco.strip()
        else:
            new_eco = curr_eco

        # Payload update
        update_payload = {
            "biology": curr_bio,
            "vn_alternate_names": new_alt_names,
            "synonyms": curr_syn,
            "vn_status": new_vn_status,
            "vn_distribution": new_dist,
            "vn_literature": new_lit,
            "ecology_vn": new_eco,
        }

        # PATCH lên Supabase
        req_patch = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}",
            data=json.dumps(update_payload).encode("utf-8"),
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            method="PATCH"
        )
        try:
            with urllib.request.urlopen(req_patch) as patch_resp:
                print(f"  ✅ Đã đồng bộ thành công dữ liệu VAST toàn diện cho {sp_id}!")
        except Exception as err:
            print(f"  ❌ Lỗi khi cập nhật {sp_id}: {err}")

    print("\n HOÀN TẤT ĐỒNG BỘ SÁCH ĐỎ VAST CHO 6 LOÀI BÒ SÁT BIỂN!")

if __name__ == "__main__":
    main()
