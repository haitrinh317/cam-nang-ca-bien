#!/usr/bin/env python3
"""
scripts/upsert_marine_reptiles.py
Tái cấu trúc & Nâng cấp Collection Bò sát biển Việt Nam (bo-sat-bien):
1. Chuyển đổi 27 loài rắn biển từ collection ran-bien sang bo-sat-bien.
2. Upsert 6 loài bò sát biển mới (5 loài Rùa biển + 1 loài Cá sấu nước mặn / Cá sấu hoa cà).
3. Tải ảnh research-grade từ iNaturalist, tối ưu hóa WebP, upload Supabase Storage & lưu species_photos.
"""

import os
import sys
import json
import time
import io
import urllib.request
import urllib.parse
from pathlib import Path
import requests
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# ── Load Environment Variables ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("❌ Lỗi: Không tìm thấy SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong file .env!")
    sys.exit(1)

HEADERS_SUPA = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

BUCKET = "species-photos"
INAT_API = "https://api.inaturalist.org/v1"
HEADERS_INAT = {
    "User-Agent": "CamNangSinhVatBienVN/1.0 (haitrinh082@gmail.com)"
}

# ── 1. Cập nhật bảng collections ─────────────────────────────────────
def setup_collection():
    print("\n--- 1. CẬP NHẬT BẢNG COLLECTIONS ---")
    url = f"{SUPABASE_URL}/rest/v1/collections"
    
    # 1.1 Tạo hoặc cập nhật bo-sat-bien
    collection_data = {
        "id": "bo-sat-bien",
        "slug": "bo-sat-bien",
        "name_vn": "Bò sát biển",
        "name_en": "Marine Reptiles of Vietnam",
        "icon": "🐢",
        "accent_color": "#f59e0b",
        "volume_count": 3,
        "status": "active",
        "sort_order": 4
    }
    
    req = urllib.request.Request(
        f"{url}?on_conflict=id",
        headers={**HEADERS_SUPA, "Prefer": "resolution=merge-duplicates,return=representation"},
        data=json.dumps(collection_data).encode("utf-8"),
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        print("✅ Đã thiết lập collection 'bo-sat-bien' trong database.")

    # 1.2 Di chuyển 27 loài rắn biển từ ran-bien sang bo-sat-bien
    patch_req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ran-bien",
        headers={**HEADERS_SUPA, "Prefer": "return=representation"},
        data=json.dumps({"collection_id": "bo-sat-bien"}).encode("utf-8"),
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req) as r:
        migrated = json.loads(r.read().decode("utf-8"))
        print(f"✅ Đã chuyển đổi {len(migrated)} loài rắn biển từ 'ran-bien' sang 'bo-sat-bien'.")

    # 1.3 Đánh dấu archived cho collection ran-bien cũ
    archive_req = urllib.request.Request(
        f"{url}?id=eq.ran-bien",
        headers={**HEADERS_SUPA, "Prefer": "return=representation"},
        data=json.dumps({"status": "archived"}).encode("utf-8"),
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(archive_req) as r:
            print("✅ Đã lưu trữ (archived) collection 'ran-bien' cũ.")
    except Exception as e:
        print(f"ℹ️ Lưu ý khi archive ran-bien: {e}")

# ── 2. Dữ liệu 6 loài bò sát biển mới ──────────────────────────────────
NEW_REPTILES = [
    {
        "id": "ruabien-species-1",
        "collection_id": "bo-sat-bien",
        "volume": 2,
        "species_index": 1,
        "vn_name": "Vích",
        "scientific_name": "Chelonia mydas",
        "authorship": "(Linnaeus, 1758)",
        "en_common_name": "Green sea turtle",
        "vn_alternate_names": "Rùa xanh, Tráng bông",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Rùa",
        "tax_order_latin": "Testudines",
        "tax_family_vn": "Họ Vích / Rùa biển",
        "tax_family_latin": "Cheloniidae",
        "tax_genus_vn": "Chi Vích Chelonia Brongniart, 1800",
        "tax_genus_latin": "Chelonia Brongniart, 1800",
        "vn_size": "Chiều dài mai cá thể trưởng thành đạt 80 - 120 cm; khối lượng trung bình 100 - 200 kg (cực đại tới 300 kg).",
        "vn_distribution": "Toàn cầu: Các đại dương nhiệt đới và cận nhiệt đới thế giới. Việt Nam: Ghi nhận dọc ven biển từ Quảng Ninh đến Kiên Giang và các hải đảo (Bạch Long Vĩ, Cô Tô, Cát Bà, Cù Lao Chàm, Hòn Cau, Côn Đảo, Phú Quốc, Hoàng Sa và Trường Sa). Bãi đẻ trọng yếu và tập trung nhất cả nước là Vườn Quốc gia Côn Đảo (~500+ rùa mẹ/năm) và VQG Núi Chúa (Ninh Thuận).",
        "vn_specimen": "Viện Hải dương học Nha Trang; Vườn quốc gia Côn Đảo; Bảo tàng Thiên nhiên Việt Nam.",
        "vn_status": "Sách Đỏ Việt Nam (2007): EN; Danh Lục Đỏ VAST (2023): EN (Nguy cấp); IUCN Red List: EN; Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP (Nghiêm cấm tuyệt đối khai thác thương mại).",
        "vn_literature": "Quyết định số 811/QĐ-BNN-TCTS ngày 14/03/2016 của Bộ Nông nghiệp & PTNT phê duyệt Kế hoạch hành động bảo tồn rùa biển Việt Nam giai đoạn 2016-2025; Đặng Ngãi Nguyên, Phạm Văn Chiến, 2024. Status and impacts to sea turtles in Vietnam. Tạp chí Khoa học và Công nghệ Biển (VAST), 24(2): 141–151; Hamann et al., 2006. Distribution and abundance of marine turtles in the Socialist Republic of Viet Nam. Biodivers Conserv 15: 3703–3720; Nguyễn Quảng Trường, 2023. Danh lục Đỏ Việt Nam (VAST); Sách Đỏ Việt Nam, 2007. Phần Động vật. NXB KHTN&CN.",
        "en_size": "Curved carapace length 80 - 120 cm; body weight 100 - 200 kg (max up to 300 kg).",
        "en_distribution": "Tropical and subtropical oceans worldwide. In Vietnam: Distributed along coast from North to South; major nesting grounds at Con Dao National Park and Nui Chua National Park.",
        "en_specimen": "Institute of Oceanography (Nha Trang); Con Dao National Park; Vietnam National Museum of Nature.",
        "en_status": "Vietnam Red Data Book: EN; IUCN Red List: EN; CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Decision No. 811/QD-BNN-TCTS (MARD 2016); Nguyen Dang Ngai & Pham Van Chien, 2024; Hamann et al., 2006; Nguyen Quang Truong, 2023; Vietnam Red Data Book, 2007.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Testudo mydas Linnaeus, 1758", "Testudo japonica Thunberg, 1787", "Chelonia agassizii Bocourt, 1868"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Chelonia mydas",
        "worms_id": 137206,
        "morphology_vn": "Đầu tròn, phủ các vảy sừng; có 1 đôi vảy trước trán (khác với các loài rùa biển khác có 2 đôi). Mỏ phẳng, không khoằm nhọn. Mai hình bầu dục hoặc trái tim tròn phẳng, có 4 đôi vảy sườn đối xứng không gối mép lên nhau; màu mai biến đổi từ nâu sẫm, lục ô-liu đến hoa văn tia sọc vàng nâu. Yếm phẳng, màu vàng nhạt hoặc trắng ngà với 4 đôi vảy liên mép. Chi trước biến đổi thành mái chèo khỏe với 1 móng vuốt.",
        "ecology_vn": "Môi trường sống: Rạn san hô, thảm cỏ biển, bãi cát ven biển và vùng lộng. Tập tính dinh dưỡng: Là loài rùa biển duy nhất ăn thực vật khi trưởng thành, thức ăn chủ yếu là cỏ biển (Halophila, Enhalus, Thalassia) và các loài rong biển (Sargassum, Gracilaria). Con non ăn tạp phù du, sứa, giáp xác nhỏ. Sinh sản: Đẻ trứng trên bãi cát bờ biển vào ban đêm (mùa sinh sản từ tháng 4 đến tháng 10 hàng năm). Mỗi ổ từ 80 - 120 quả trứng hình tròn vỏ mềm, thời gian ấp từ 45 - 60 ngày phụ thuộc nhiệt độ cát.",
        "economic_value_vn": "Có giá trị sinh thái đặc biệt to lớn trong việc duy trì và làm sạch các thảm cỏ biển; giá trị du lịch sinh thái và biểu tượng bảo tồn biển Côn Đảo. Nghiêm cấm khai thác và buôn bán.",
        "biology": {
            "iucnStatus": "EN",
            "iucnTaxonId": "4615",
            "habitat": "Coral reefs, Seagrass beds, Sandy beaches, Neritic",
            "feedingType": "Herbivorous, grazing on aquatic plants and seagrass beds",
            "reproduction": "Oviparous, nocturnal beach nesting, 80-120 eggs/clutch",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "EN",
                "statusVn": "Nguy cấp",
                "criteria": "A2acde",
                "year": "2023",
                "assessor": "PGS.TS. Nguyễn Quảng Trường (Viện Sinh thái & Tài nguyên Sinh vật - VAST)",
                "notes": "Suy giảm quần thể tự nhiên ước tính trên 50% trong vòng 20 năm qua do săn bắt lấy thịt, trứng, vướng lưới đánh cá và suy thoái bãi đẻ. Quần thể Vích tại Côn Đảo và Núi Chúa đang phục hồi nhờ các nỗ lực bảo tồn liên tục.",
                "legalMeasures": "Nghị định 26/2019/NĐ-CP (Phụ lục II Nhóm I: nghiêm cấm khai thác vì mục đích thương mại); Phụ lục I CITES; Quyết định 811/QĐ-BNN-TCTS (Kế hoạch hành động bảo tồn rùa biển Việt Nam giai đoạn 2016-2025).",
                "urgentProposals": "Bảo vệ nghiêm ngặt các bãi đẻ tự nhiên còn lại; áp dụng thiết bị thoát rùa (TED) trên tàu cá lưới kéo; ngăn chặn triệt để nạn trộm trứng và săn bắt rùa mẹ."
            }
        }
    },
    {
        "id": "ruabien-species-2",
        "collection_id": "bo-sat-bien",
        "volume": 2,
        "species_index": 2,
        "vn_name": "Đồi mồi",
        "scientific_name": "Eretmochelys imbricata",
        "authorship": "(Linnaeus, 1766)",
        "en_common_name": "Hawksbill sea turtle",
        "vn_alternate_names": "Đồi mồi vảy gối",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Rùa",
        "tax_order_latin": "Testudines",
        "tax_family_vn": "Họ Vích / Rùa biển",
        "tax_family_latin": "Cheloniidae",
        "tax_genus_vn": "Chi Đồi mồi Eretmochelys Fitzinger, 1843",
        "tax_genus_latin": "Eretmochelys Fitzinger, 1843",
        "vn_size": "Chiều dài mai 65 - 90 cm; khối lượng trung bình 40 - 70 kg (hiếm khi vượt quá 80 kg).",
        "vn_distribution": "Toàn cầu: Vùng biển nhiệt đới Đại Tây Dương, Thái Bình Dương và Ấn Độ Dương. Việt Nam: Phân bố chủ yếu tại các rạn san hô Nam Trung Bộ và Tây Nam Bộ: vịnh Nha Trang, Côn Đảo, Phú Quốc, quần đảo Thổ Chu, Trường Sa, Hoàng Sa. Trong 10 năm qua hầu như không còn ghi nhận cá thể lên đẻ tại các bãi biển Việt Nam.",
        "vn_specimen": "Viện Hải dương học Nha Trang; Bảo tàng Thiên nhiên Việt Nam.",
        "vn_status": "Sách Đỏ Việt Nam: CR (Cực kỳ nguy cấp); Danh Lục Đỏ VAST (2023): CR; IUCN Red List: CR; Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP.",
        "vn_literature": "Quyết định số 811/QĐ-BNN-TCTS; Đặng Ngãi Nguyên, Phạm Văn Chiến, 2024; Hamann et al., 2006; Nguyễn Quảng Trường, 2023; Sách Đỏ Việt Nam, 2007.",
        "en_size": "Carapace length 65 - 90 cm; body weight 40 - 70 kg.",
        "en_distribution": "Tropical reefs worldwide. In Vietnam: South Central and South-West reefs (Nha Trang, Con Dao, Phu Quoc, Spratly & Paracel Islands). No nesting records in recent years.",
        "en_specimen": "Institute of Oceanography (Nha Trang); Vietnam National Museum of Nature.",
        "en_status": "Vietnam Red Data Book: CR; IUCN Red List: CR; CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Decision No. 811/QD-BNN-TCTS (MARD 2016); Nguyen Dang Ngai & Pham Van Chien, 2024; Hamann et al., 2006; Vietnam Red Data Book, 2007.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Testudo imbricata Linnaeus, 1766", "Chelonia imbricata (Linnaeus, 1766)"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Eretmochelys imbricata",
        "worms_id": 137207,
        "morphology_vn": "Mỏ hẹp dài và quặp khoằm như mỏ chim ưng/vẹt; đầu có 2 đôi vảy trước trán. Điểm đặc trưng nhất là các tấm vảy sừng trên mai xếp chồng gối lên nhau như ngói lợp (imbricate) ở cá thể chưa già. Rìa sau của mai có răng cưa nhọn rõ rệt. Vảy mai màu hổ phách tuyệt đẹp với các vân cẩm thạch vàng, nâu, đỏ sẫm và đen. Chi trước có 2 móng vuốt.",
        "ecology_vn": "Môi trường sống: Gắn liền mật thiết với hệ sinh thái rạn san hô nhiệt đới nông (độ sâu 1 - 30m). Tập tính dinh dưỡng: Chuyên ăn hải miên (bọt biển - Spongivore), sử dụng mỏ hẹp len lỏi vào các khe san hô để rỉa bọt biển. Nhờ vậy giúp san hô không bị bọt biển cạnh tranh lấn át không gian sống. Sinh sản: Từng đẻ trứng tại các bãi cát ven rạn ở Kiên Giang, Vũng Tàu, Côn Đảo; mỗi lứa đẻ 100 - 150 trứng.",
        "economic_value_vn": "Loài có giá trị sinh thái đặc biệt duy trì sức khỏe rạn san hô. Từng bị săn bắt cạn kiệt để lấy mai làm trâm cài, quạt, đồ mỹ nghệ đồi mồi đắt giá. Nghiêm cấm tuyệt đối mọi hành vi buôn bán mẫu vật đồi mồi.",
        "biology": {
            "iucnStatus": "CR",
            "iucnTaxonId": "8005",
            "habitat": "Coral reefs, Rocky reefs",
            "feedingType": "Spongivore, feeding primarily on marine sponges",
            "reproduction": "Oviparous, nesting on sandy beaches near coral reefs",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "CR",
                "statusVn": "Cực kỳ nguy cấp",
                "criteria": "A2bcd",
                "year": "2023",
                "assessor": "PGS.TS. Nguyễn Quảng Trường (VAST)",
                "notes": "Quần thể Đồi mồi tại Việt Nam đã suy giảm trên 90% do hoạt động khai thác ráo riết để lấy mai làm mỹ nghệ trong nhiều thập kỷ qua. Trong 10 năm qua gần như không còn phát hiện tổ đẻ tự nhiên.",
                "legalMeasures": "Nghị định 26/2019/NĐ-CP (Phụ lục II Nhóm I: nghiêm cấm khai thác vì mục đích thương mại); Phụ lục I CITES.",
                "urgentProposals": "Kiểm soát triệt để các cửa hàng buôn bán hàng lưu niệm mỹ nghệ từ mai đồi mồi; phục hồi hệ sinh thái rạn san hô sinh cư."
            }
        }
    },
    {
        "id": "ruabien-species-3",
        "collection_id": "bo-sat-bien",
        "volume": 2,
        "species_index": 3,
        "vn_name": "Đồi mồi dứa",
        "scientific_name": "Lepidochelys olivacea",
        "authorship": "(Eschscholtz, 1829)",
        "en_common_name": "Olive ridley sea turtle",
        "vn_alternate_names": "Vích ô-liu, Rùa mai gai, Quản đồng (dân gian)",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Rùa",
        "tax_order_latin": "Testudines",
        "tax_family_vn": "Họ Vích / Rùa biển",
        "tax_family_latin": "Cheloniidae",
        "tax_genus_vn": "Chi Vích gai Lepidochelys Fitzinger, 1843",
        "tax_genus_latin": "Lepidochelys Fitzinger, 1843",
        "vn_size": "Chiều dài mai 60 - 75 cm; khối lượng trung bình 35 - 50 kg (loài rùa biển nhỏ nhất tại Việt Nam).",
        "vn_distribution": "Vùng biển nhiệt đới Ấn Độ Dương, Thái Bình Dương. Tại Việt Nam: Phân bố dọc bờ biển từ Bắc vào Nam; các bãi đẻ ghi nhận rải rác ở Quảng Trị, Quảng Nam, Bình Định, Phú Yên và Ninh Thuận. Hiện số lượng cá thể lên đẻ chỉ còn vài con mỗi năm.",
        "vn_specimen": "Viện Hải dương học Nha Trang; Bảo tàng Thiên nhiên Việt Nam.",
        "vn_status": "Sách Đỏ Việt Nam (2007): EN; IUCN Red List: VU; Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP.",
        "vn_literature": "Quyết định 811/QĐ-BNN-TCTS; Đặng Ngãi Nguyên & Phạm Văn Chiến, 2024; Hamann et al., 2006; Sách Đỏ Việt Nam, 2007.",
        "en_size": "Carapace length 60 - 75 cm; body weight 35 - 50 kg.",
        "en_distribution": "Tropical oceans. In Vietnam: Distributed along coast, sparse nesting in Central Vietnam (Quang Tri, Binh Dinh, Ninh Thuan).",
        "en_specimen": "Institute of Oceanography (Nha Trang).",
        "en_status": "Vietnam Red Data Book: EN; IUCN Red List: VU; CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Decision No. 811/QD-BNN-TCTS; Nguyen Dang Ngai & Pham Van Chien, 2024; Hamann et al., 2006; Vietnam Red Data Book, 2007.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Chelonia olivacea Eschscholtz, 1829"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Lepidochelys olivacea",
        "worms_id": 220293,
        "morphology_vn": "Mai có dạng tròn hình tim rộng gồ cao, màu xanh xám ô-liu. Điểm chẩn loại quan trọng: Mai có từ 6 đến 9 đôi vảy sườn (nhiều hơn so với 4 hoặc 5 đôi ở các loài khác), các vảy thường không cân đối giữa hai bên mai. Đầu có 2 đôi vảy trước trán. Yếm có màu vàng xanh nhạt với 4 đôi vảy liên mép, mỗi vảy liên mép có một lỗ nhỏ tiết dịch xua đuổi kẻ thù.",
        "ecology_vn": "Môi trường sống: Vùng biển nông ven bờ, vịnh biển, cửa sông nước lợ và rạn đá. Tập tính dinh dưỡng: Là loài ăn thịt cơ hội, thức ăn gồm cua biển, tôm, ốc, sứa, nhím biển và cá nhỏ. Sinh sản: Ở một số nơi trên thế giới nổi tiếng với hiện tượng đẻ đồng loạt (arribada); tại Việt Nam chỉ ghi nhận đẻ đơn độc từ tháng 5 đến tháng 8, mỗi lứa đẻ 80 - 110 trứng.",
        "economic_value_vn": "Giữ cân bằng chuỗi thức ăn đáy biển ven bờ. Đang bị đe dọa nặng nề do mắc lưới kéo đáy (trawl nets) và ô nhiễm rác thải nhựa.",
        "biology": {
            "iucnStatus": "VU",
            "iucnTaxonId": "11534",
            "habitat": "Neritic, Soft bottom, Estuaries",
            "feedingType": "Carnivore, feeding on crabs, molluscs, shrimps and jellyfish",
            "reproduction": "Oviparous, beach nesting (solitary in Vietnam)",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "EN",
                "statusVn": "Nguy cấp",
                "year": "2007",
                "notes": "Quần thể suy giảm mạnh >80% so với trước thập niên 1980 do vướng lưới đánh cá của ngư dân và bãi đẻ bị san phẳng làm khu nghỉ dưỡng."
            }
        }
    },
    {
        "id": "ruabien-species-4",
        "collection_id": "bo-sat-bien",
        "volume": 2,
        "species_index": 4,
        "vn_name": "Quản đồng",
        "scientific_name": "Caretta caretta",
        "authorship": "(Linnaeus, 1758)",
        "en_common_name": "Loggerhead sea turtle",
        "vn_alternate_names": "Rùa đầu to, Đồi mồi đầu to",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Rùa",
        "tax_order_latin": "Testudines",
        "tax_family_vn": "Họ Vích / Rùa biển",
        "tax_family_latin": "Cheloniidae",
        "tax_genus_vn": "Chi Quản đồng Caretta Rafinesque, 1814",
        "tax_genus_latin": "Caretta Rafinesque, 1814",
        "vn_size": "Chiều dài mai 80 - 110 cm; khối lượng trung bình 80 - 150 kg (cực đại tới 200 kg).",
        "vn_distribution": "Đại dương ấm áp toàn cầu. Tại Việt Nam: Rất hiếm gặp, chỉ bắt gặp ở vùng biển khơi miền Trung, quần đảo Hoàng Sa và Trường Sa; không có ghi nhận bãi đẻ cố định trong nhiều năm qua.",
        "vn_specimen": "Viện Hải dương học Nha Trang.",
        "vn_status": "Sách Đỏ Việt Nam (2007): CR (Cực kỳ nguy cấp); IUCN Red List: VU (toàn cầu); Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP.",
        "vn_literature": "Quyết định 811/QĐ-BNN-TCTS; Đặng Ngãi Nguyên & Phạm Văn Chiến, 2024; Hamann et al., 2006; Sách Đỏ Việt Nam, 2007.",
        "en_size": "Carapace length 80 - 110 cm; body weight 80 - 150 kg.",
        "en_distribution": "Pelagic waters worldwide. In Vietnam: Rare oceanic visitor in Central waters and Spratly/Paracel Islands; no stable nesting recorded.",
        "en_specimen": "Institute of Oceanography (Nha Trang).",
        "en_status": "Vietnam Red Data Book: CR; IUCN Red List: VU; CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Decision No. 811/QD-BNN-TCTS; Nguyen Dang Ngai & Pham Van Chien, 2024; Hamann et al., 2006; Vietnam Red Data Book, 2007.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Testudo caretta Linnaeus, 1758"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Caretta caretta",
        "worms_id": 137205,
        "morphology_vn": "Đặc trưng nổi bật nhất là đầu rất to, rộng, hàm cứng cáp khỏe mạnh thích nghi với việc nghiền nát vỏ cứng động vật thân mềm. Mai hình trái tim kéo dài, màu nâu đỏ hoặc đỏ gạch. Có 5 đôi vảy sườn (đôi đầu tiên tiếp xúc với vảy gáy). Yếm màu vàng ngà có 3 đôi vảy liên mép không có lỗ tiết. Chi trước có 2 móng vuốt.",
        "ecology_vn": "Môi trường sống: Vùng biển khơi đại dương (Pelagic) và rạn ngầm xa bờ. Thích nghi bơi đường dài vượt đại dương. Tập tính dinh dưỡng: Động vật ăn thịt tầng đáy và lơ lửng: cua biển, ốc biển, sò, nhím biển, sao biển và cá nhỏ. Sinh sản: Thành thục sinh dục muộn (25-35 năm tuổi), đẻ trứng ở các bãi cát biển xa xôi.",
        "economic_value_vn": "Chỉ số sinh thái quan trọng của đại dương mở. Nghiêm cấm đánh bắt và buôn bán.",
        "biology": {
            "iucnStatus": "VU",
            "iucnTaxonId": "3897",
            "habitat": "Pelagic, Oceanic, Coral reefs",
            "feedingType": "Carnivore, specialized in crushing hard-shelled invertebrates",
            "reproduction": "Oviparous, beach nesting in subtropical regions",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "CR",
                "statusVn": "Cực kỳ nguy cấp",
                "year": "2007",
                "notes": "Rất hiếm gặp ở vùng biển Việt Nam, đối diện nguy cơ tuyệt chủng cục bộ."
            }
        }
    },
    {
        "id": "ruabien-species-5",
        "collection_id": "bo-sat-bien",
        "volume": 2,
        "species_index": 5,
        "vn_name": "Rùa da",
        "scientific_name": "Dermochelys coriacea",
        "authorship": "(Vandelli, 1761)",
        "en_common_name": "Leatherback sea turtle",
        "vn_alternate_names": "Rùa da đầu to, Ông Da (tôn xưng dân chài)",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Rùa",
        "tax_order_latin": "Testudines",
        "tax_family_vn": "Họ Rùa da",
        "tax_family_latin": "Dermochelyidae",
        "tax_genus_vn": "Chi Rùa da Dermochelys Blainville, 1816",
        "tax_genus_latin": "Dermochelys Blainville, 1816",
        "vn_size": "Loài rùa lớn nhất hành tinh. Chiều dài mai 130 - 180 cm (cực đại tới 220 cm); khối lượng 300 - 600 kg (kỷ lục thế giới trên 900 kg). Sải vây chi trước tới 2.5 - 3 m.",
        "vn_distribution": "Toàn cầu: Khắp các đại dương, có khả năng bơi vào vùng nước lạnh nhờ cơ chế giữ nhiệt đặc biệt (gigantothermy). Việt Nam: Thập niên 1960 từng có ~500 cá thể đẻ mỗi năm dọc duyên hải miền Trung (Quảng Trị, Thừa Thiên Huế, Quảng Ngãi, Bình Định, Phú Yên, Khánh Hòa). Hiện nay gần như tuyệt chủng ở VN: từ 2008-2018 chỉ ghi nhận duy nhất 1 tổ đẻ tại bãi Cát Đài (Cam Lâm, Khánh Hòa năm 2013).",
        "vn_specimen": "Viện Hải dương học Nha Trang (tiêu bản bộ xương và mô hình khổng lồ); Bảo tàng Thiên nhiên Việt Nam.",
        "vn_status": "Sách Đỏ Việt Nam (2007): CR; Danh Lục Đỏ VAST (2023): CR (Cực kỳ nguy cấp); IUCN Red List: VU (Toàn cầu) / CR (Tiểu quần thể Tây Thái Bình Dương); Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP.",
        "vn_literature": "Quyết định số 811/QĐ-BNN-TCTS; Đặng Ngãi Nguyên & Phạm Văn Chiến, 2024; Hamann et al., 2006; Nguyễn Quảng Trường, 2023; Sách Đỏ Việt Nam, 2007.",
        "en_size": "Carapace length 130 - 180 cm; body weight 300 - 600 kg (max >900 kg).",
        "en_distribution": "Circumglobal oceans. In Vietnam: Formerly ~500 nesting females/year in 1960s; only 1 nesting record in Khanh Hoa (2013) between 2008-2018. Nearly extirpated in Vietnam.",
        "en_specimen": "Institute of Oceanography (Nha Trang); Vietnam National Museum of Nature.",
        "en_status": "Vietnam Red Data Book: CR; IUCN Red List: CR (West Pacific subpopulation); CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Decision No. 811/QD-BNN-TCTS; Nguyen Dang Ngai & Pham Van Chien, 2024; Hamann et al., 2006; Vietnam Red Data Book, 2007.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Testudo coriacea Vandelli, 1761"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Dermochelys coriacea",
        "worms_id": 137209,
        "morphology_vn": "Hình thái độc nhất vô nhị: Không có mai xương cứng và không có vảy sừng như các loài rùa khác. Thay vào đó, lưng được bọc bởi lớp da dày, dẻo dai như da thuộc với hàng ngàn mẩu xương nhỏ li ti ẩn dưới da. Trên lưng có 7 đường gờ sống nổi rõ chạy dọc từ cổ đến đuôi. Màu da màu xanh đen hoặc xám than với các đốm trắng hoặc hồng nhạt rải rác. Chi trước cực dài, dạng mái chèo khổng lồ không có móng vuốt.",
        "ecology_vn": "Môi trường sống: Biển khơi đại dương (Pelagic), có khả năng lặn sâu kỷ lục tới hơn 1,200 m để tìm thức ăn. Tập tính dinh dưỡng: Chuyên ăn sứa biển (Jellyfish specialist), khoang miệng và thực quản có hàng trăm gai nhọn mềm hướng ngược vào trong giúp giữ chặt những con sứa trơn tuột khi nuốt. Sinh sản: Đẻ trứng trên các bãi cát dốc thoai thoải đối diện biển sâu, mỗi lứa đẻ 60 - 90 quả trứng lớn kèm một số quả trứng nhỏ không thụ tinh.",
        "economic_value_vn": "Kiểm soát sinh học quần thể sứa đại dương. Trong tín ngưỡng dân gian biển miền Trung, rùa da được coi là hiện thân của Thần biển đem lại may mắn, khi dạt bờ ngư dân đều làm lễ giải cứu hoặc an táng trang trọng.",
        "biology": {
            "iucnStatus": "CR",
            "iucnTaxonId": "6494",
            "habitat": "Pelagic, Oceanic deep water, Sandy beaches",
            "feedingType": "Jellyfish specialist (Gelatinivory)",
            "reproduction": "Oviparous, deep sandy beach nesting",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "CR",
                "statusVn": "Cực kỳ nguy cấp",
                "criteria": "A2bcd",
                "year": "2023",
                "assessor": "PGS.TS. Nguyễn Quảng Trường (VAST)",
                "notes": "Suy giảm tới hơn 99% so với thập niên 1960. Rất nhạy cảm với việc nuốt phải túi nilon và rác thải nhựa (do nhầm là sứa biển) và vướng dây câu cá ngừ đại dương."
            }
        }
    },
    {
        "id": "casau-species-1",
        "collection_id": "bo-sat-bien",
        "volume": 3,
        "species_index": 1,
        "vn_name": "Cá sấu hoa cà",
        "scientific_name": "Crocodylus porosus",
        "authorship": "Schneider, 1801",
        "en_common_name": "Saltwater crocodile",
        "vn_alternate_names": "Cá sấu nước mặn, Cá sấu biển",
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Cá sấu",
        "tax_order_latin": "Crocodylia",
        "tax_family_vn": "Họ Cá sấu",
        "tax_family_latin": "Crocodylidae",
        "tax_genus_vn": "Chi Cá sấu Crocodylus Laurenti, 1768",
        "tax_genus_latin": "Crocodylus Laurenti, 1768",
        "vn_size": "Loài bò sát lớn nhất còn sống trên Trái Đất. Con đực trưởng thành dài 4.3 - 5.2 m (cực đại có thể vượt quá 6 - 7 m); khối lượng 400 - 1,000 kg (cực đại >1,200 kg). Con cái nhỏ hơn, dài 2.5 - 3.5 m.",
        "vn_distribution": "Đông Nam Á, Bắc Úc, Ấn Độ. Tại Việt Nam: Trước đây từng phân bố tự nhiên khá phổ biến ở các thủy vực nước lợ, rừng ngập mặn ven biển Nam Bộ, sông Đồng Nai, sông Cửu Long, Cần Giờ, Cà Mau, Kiên Giang và đảo Côn Đảo. Hiện nay trong tự nhiên gần như đã tuyệt chủng (hoặc chỉ còn vài cá thể sót lại rất hiếm hoi), phần lớn chỉ còn được nuôi nhốt trong các trang trại và khu bảo tồn.",
        "vn_specimen": "Viện Hải dương học Nha Trang; Thảo Cầm Viên Sài Gòn; Bảo tàng Thiên nhiên Việt Nam.",
        "vn_status": "Sách Đỏ Việt Nam (2007): CR (Cực kỳ nguy cấp); Danh Lục Đỏ VAST (2024): CR; IUCN Red List: LC (toàn cầu); Phụ lục I CITES; Nhóm I Phụ lục II Nghị định 26/2019/NĐ-CP (Nghiêm cấm tuyệt đối khai thác thương mại ngoài tự nhiên).",
        "vn_literature": "Sách Đỏ Việt Nam, 2007. Phần I: Động vật. NXB KHTN&CN; Nguyễn Văn Sáng, Hồ Thu Cúc, Nguyễn Quảng Trường, 2009. Herpetofauna of Vietnam. Edition Chimaira; Nguyễn Quảng Trường, 2024. Danh lục Đỏ Việt Nam (VAST); Nghị định 26/2019/NĐ-CP.",
        "en_size": "Male total length 4.3 - 5.2 m (up to 6-7 m); body weight 400 - 1,000 kg. Largest living reptile on Earth.",
        "en_distribution": "Indo-Pacific estuaries and coastal waters. In Vietnam: Formerly widespread in Southern mangroves, estuaries, and Con Dao Islands; virtually extirpated in the wild today, mainly kept in farms and reserves.",
        "en_specimen": "Institute of Oceanography (Nha Trang); Saigon Zoo; Vietnam National Museum of Nature.",
        "en_status": "Vietnam Red Data Book: CR; IUCN Red List: LC (globally); CITES Appendix I; Decree 26/2019/ND-CP Group I.",
        "en_literature": "Vietnam Red Data Book, 2007; Nguyen Van Sang et al., 2009; Nguyen Quang Truong, 2024; Decree 26/2019/ND-CP.",
        "conservation_status": "rare",
        "synonyms": json.dumps(["Crocodilus porosus Schneider, 1801"]),
        "worms_status": "accepted",
        "worms_accepted_name": "Crocodylus porosus",
        "worms_id": 344030,
        "morphology_vn": "Đầu to, mõm dài và rộng. Có một đôi gờ xương chạy dọc từ trước mắt đến giữa mõm (đặc trưng phân biệt với cá sấu xiêm). Thân phủ các tấm vảy sừng dày hình chữ nhật; có 4 vảy gáy lớn xếp thành hình vuông. Màu sắc lưng xám vàng, nâu ô-liu với các đốm sẫm màu tạo hoa văn hoa cà; bụng màu vàng nhạt hoặc trắng ngà. Chi có màng bơi một phần, đuôi dẹp bên khỏe và có hai hàng gai sừng hợp lại thành một hàng ở nửa sau đuôi. Trên lưỡi có các tuyến bài tiết muối chuyên biệt (salt glands) giúp cơ thể loại bỏ lượng muối dư thừa khi sống lâu dài trong nước biển.",
        "ecology_vn": "Môi trường sống: Vùng cửa sông, đầm phá ngập mặn, rừng tràm nước lợ, bờ biển và có khả năng bơi vượt đại dương hàng trăm hải lý giữa các đảo. Tập tính dinh dưỡng: Đỉnh chuỗi thức ăn (Apex predator), có lực cắn mạnh nhất trong giới động vật (~3,700 psi). Thức ăn gồm cá lớn, giáp xác, chim nước, rùa biển và các loài thú lớn uống nước ven bờ. Săn mồi bằng cách phục kích ngầm dưới nước và thực hiện cú xoay người tử thần (death roll). Sinh sản: Đẻ trứng vào mùa mưa (tháng 4 - 8), làm tổ bằng lá cây mục và bùn cao trên bờ, mỗi ổ 40 - 70 trứng. Con mẹ bảo vệ tổ và bảo vệ con non sau khi nở.",
        "economic_value_vn": "Loài động vật chỉ thị sinh thái rừng ngập mặn và đỉnh chuỗi thức ăn. Có giá trị cao trong nghiên cứu cổ sinh và bò sát học. Ngoài tự nhiên được bảo vệ ở cấp độ cao nhất.",
        "biology": {
            "iucnStatus": "LC",
            "iucnTaxonId": "5668",
            "habitat": "Estuaries, Mangroves, Neritic, Marine lagoons",
            "feedingType": "Apex predator, carnivore hunting fish, crabs, turtles and mammals",
            "reproduction": "Oviparous, mound nest made of vegetation and mud, 40-70 eggs",
            "source": "SeaLifeBase v25.04 & VAST 2024",
            "vnRedList": {
                "status": "CR",
                "statusVn": "Cực kỳ nguy cấp",
                "year": "2024",
                "notes": "Trước đây phân bố ở rừng ngập mặn Nam Bộ và Côn Đảo, nay hầu như đã tuyệt chủng ngoài tự nhiên ở Việt Nam do săn bắt lấy da và mất sinh cảnh."
            }
        }
    }
]

# ── 3. Upsert loài vào bảng species ──────────────────────────────────
def upsert_species():
    print("\n--- 2. UPSERT 6 LOÀI BÒ SÁT BIỂN MỚI ---")
    url = f"{SUPABASE_URL}/rest/v1/species?on_conflict=id"
    for sp in NEW_REPTILES:
        req = urllib.request.Request(
            url,
            headers={**HEADERS_SUPA, "Prefer": "resolution=merge-duplicates,return=representation"},
            data=json.dumps(sp).encode("utf-8"),
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as r:
                res = json.loads(r.read().decode("utf-8"))
                print(f"✅ Upsert thành công: [{sp['id']}] {sp['vn_name']} ({sp['scientific_name']})")
        except Exception as e:
            print(f"❌ Lỗi upsert {sp['scientific_name']}: {e}")

# ── 4. Tải & Đồng bộ ảnh iNaturalist CC-BY ────────────────────────────
def fetch_and_upload_photos():
    print("\n--- 3. ĐỒNG BỘ ẢNH RESEARCH-GRADE iNATURALIST ---")
    
    for sp in NEW_REPTILES:
        sp_id = sp["id"]
        sci_name = sp["scientific_name"]
        print(f"\n🔍 Đang tìm ảnh cho {sp['vn_name']} ({sci_name})...")
        
        # 4.1 Tra cứu iNaturalist API
        inat_url = f"{INAT_API}/observations"
        params = {
            "taxon_name": sci_name,
            "quality_grade": "research",
            "photos": "true",
            "per_page": 5,
            "order_by": "votes"
        }
        
        try:
            r = requests.get(inat_url, headers=HEADERS_INAT, params=params, timeout=20)
            data = r.json()
            results = data.get("results", [])
            
            if not results:
                # Thử bỏ quality_grade=research nếu không có
                params.pop("quality_grade", None)
                r = requests.get(inat_url, headers=HEADERS_INAT, params=params, timeout=20)
                results = r.json().get("results", [])
                
            if not results:
                print(f"⚠️ Không tìm thấy ảnh trên iNaturalist cho {sci_name}")
                continue
                
            photo_count = 0
            uploaded_urls = []
            
            for obs in results:
                if photo_count >= 3:
                    break
                obs_photos = obs.get("photos", [])
                if not obs_photos:
                    continue
                    
                p = obs_photos[0]
                img_url = p.get("url", "").replace("square", "large")
                if not img_url:
                    continue
                    
                attribution = p.get("attribution", "")
                license_code = p.get("license_code", "cc-by")
                
                # Tải ảnh gốc
                img_resp = requests.get(img_url, headers=HEADERS_INAT, timeout=20)
                if img_resp.status_code != 200:
                    continue
                    
                # Chuyển đổi WebP
                im = Image.open(io.BytesIO(img_resp.content))
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                webp_buf = io.BytesIO()
                im.save(webp_buf, format="WEBP", quality=82)
                webp_bytes = webp_buf.getvalue()
                
                # Upload Supabase Storage
                idx_str = f"{photo_count + 1:02d}"
                storage_path = f"bo-sat-bien/{sp_id}/{idx_str}.webp"
                storage_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
                
                up_headers = {
                    "apikey": SERVICE_KEY,
                    "Authorization": f"Bearer {SERVICE_KEY}",
                    "Content-Type": "image/webp",
                    "x-upsert": "true"
                }
                
                up_resp = requests.post(storage_url, headers=up_headers, data=webp_bytes, timeout=30)
                if up_resp.status_code in (200, 201):
                    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"
                    uploaded_urls.append(public_url)
                    photo_count += 1
                    print(f"  📸 Đã upload ảnh {idx_str}: {storage_path} ({len(webp_bytes)//1024} KB)")
                    
                    # Lưu vào species_photos
                    photo_record = {
                        "species_id": sp_id,
                        "storage_path": storage_path,
                        "public_url": public_url,
                        "source": "inaturalist",
                        "photographer": attribution,
                        "license": license_code,
                        "is_primary": (photo_count == 1),
                        "sort_order": photo_count
                    }
                    
                    try:
                        requests.post(
                            f"{SUPABASE_URL}/rest/v1/species_photos",
                            headers=HEADERS_SUPA,
                            json=photo_record,
                            timeout=15
                        )
                    except Exception as ex:
                        pass
                else:
                    print(f"  ❌ Lỗi upload storage: {up_resp.status_code} - {up_resp.text}")
                    
                time.sleep(1.0)
                
            # Cập nhật photo_url chính vào bảng species
            if uploaded_urls:
                patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
                requests.patch(patch_url, headers=HEADERS_SUPA, json={"photo_url": uploaded_urls[0]})
                print(f"  ⭐ Cập nhật photo_url chính cho {sp['vn_name']}: {uploaded_urls[0]}")
                
        except Exception as e:
            print(f"❌ Lỗi fetch ảnh cho {sci_name}: {e}")

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU QUY TRÌNH NÂNG CẤP COLLECTION BÒ SÁT BIỂN (BO-SAT-BIEN)")
    setup_collection()
    upsert_species()
    fetch_and_upload_photos()
    print("\n🎉 HOÀN TẤT TẤT CẢ TÁC VỤ DATABASE VÀ DỮ LIỆU BÒ SÁT BIỂN!")
