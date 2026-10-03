#!/usr/bin/env python3
"""
scripts/sync_reptiles_vnredlist_standard.py
Chuẩn hóa trường biology.vnRedList của 6 loài bò sát biển (5 Rùa biển + 1 Cá sấu hoa cà)
theo đúng cấu trúc chuẩn của nhóm Cá biển (đầy đủ threats, population, conservation),
đảm bảo hiển thị đầy đủ 2 cột (Mối đe dọa + Hiện trạng/Xu hướng quần thể) và
khối Biện pháp bảo tồn hiện hành & Đề xuất cấp thiết trên ConservationWidget.

Tác giả: Antigravity Assistant cho chú Chình
Ngày thực hiện: 13/09/2026
"""

import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

STANDARDIZED_REPTILES_REDLIST = {
    "ruabien-species-1": {
        "url": "http://vnredlist.vast.vn/chelonia-mydas/",
        "year": "2023",
        "status": "EN",
        "statusVn": "Nguy cấp",
        "refCode": "RT73",
        "criteria": "A2acde",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Hoàng Văn Hà, Phạm Văn Thông",
        "citation": "Nguyễn Quảng Trường, 2023. Chelonia mydas. Danh lục Đỏ Việt Nam. RT73",
        "threats": "Mối đe dọa Quần thể của loài này trong tự nhiên bị suy giảm nghiêm trọng do mất sinh cảnh sống, mất bãi đẻ, ô nhiễm nước biển, rùa và trứng bị săn bắt làm thực phẩm, mai làm đồ mỹ nghệ.",
        "population": "Hiện trạng quần thể Rất hiếm gặp trong vùng phân bố ngoại trừ quần thể ở Côn Đảo. Đây là loài có vùng phân bố rộng ở các đại dương lớn trên thế giới, có khả năng di cư xa nhưng số lượng cá thể đã bị suy giảm nghiêm trọng do môi trường sống và bãi đẻ bị xâm hại hoặc ô nhiễm, nuốt phải rác thải nhựa, cá thể non hoặc trưởng thành bị bắt khi mắc vào lưới đánh cá, bị săn bắt làm thực phẩm, mỹ nghệ hoặc đồ trang trí, nuôi làm cảnh; ước tính quần thể trong tự nhiên đã bị suy giảm khoảng hơn 50% trong vòng hơn 20 năm trở lại đây, nhân tố tác động này hiện vẫn tồn tại ảnh hưởng trực tiếp đến quần thể của loài. Xu hướng quần thể Suy giảm",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố của loài có một phần nằm trong các khu bảo tồn biển nên được bảo vệ. Loài này có tên trong Nghị định số 64/2019/NĐ-CP của Chính phủ và Phụ lục I của CITES. Đề xuất Tiến hành các biện pháp bảo vệ sinh cảnh và bãi đẻ của rùa ở các khu vực ven biển và đảo, phục hồi quần thể trong tự nhiên. Quản lý các hoạt động săn bắt trái phép loài này. Tuyên truyền nhằm hạn chế tác động của con người đến sinh cảnh sống, bãi đẻ của loài.",
        "version": "2024-1"
    },
    "ruabien-species-2": {
        "url": "http://vnredlist.vast.vn/eretmochelys-imbricata/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "RT74",
        "criteria": "A2cde",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Hoàng Văn Hà, Phạm Văn Thông",
        "citation": "Nguyễn Quảng Trường, 2023. Eretmochelys imbricata. Danh lục Đỏ Việt Nam. RT74",
        "threats": "Mối đe dọa Quần thể của loài này trong tự nhiên bị suy giảm nghiêm trọng do mất sinh cảnh sống, mất bãi đẻ, ô nhiễm nước biển, rác thải nhựa, rùa và trứng bị săn bắt làm thực phẩm, mai làm đồ mỹ nghệ.",
        "population": "Hiện trạng quần thể Rất hiếm gặp. Đây là loài có vùng phân bố rộng ở các đại dương lớn trên thế giới, có khả năng di cư rất xa nhưng số lượng cá thể đã bị suy giảm nghiêm trọng do môi trường sống và bãi đẻ bị xâm hại hoặc ô nhiễm, nuốt phải rác thải nhựa, cá thể non hoặc trưởng thành bị bắt khi mắc vào lưới đánh cá, bị săn bắt cạn kiệt làm đồ mỹ nghệ hoặc trang trí, nuôi làm cảnh; ước tính quần thể trong tự nhiên đã bị suy giảm khoảng hơn 80% trong vòng 100 năm trở lại đây (tương đương 3 thế hệ), nhân tố tác động này hiện vẫn tồn tại ảnh hưởng trực tiếp đến quần thể của loài (tiêu chuẩn A2cde). Ghi nhận phân bố của loài này ở Việt Nam dọc theo vùng biển từ Vịnh Bắc bộ vào đến Vịnh Thái Lan nhưng rất hiếm gặp. Xu hướng quần thể Suy giảm",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố của loài có một phần nằm trong các khu bảo tồn biển nên được bảo vệ. Loài này có tên trong Nghị định số 64/2019/NĐ-CP của Chính phủ. Đề xuất Tiến hành các biện pháp bảo vệ sinh cảnh và bãi đẻ của rùa ở các khu vực ven biển và đảo, phục hồi quần thể trong tự nhiên. Quản lý các hoạt động săn bắt trái phép loài này. Tuyên truyền nhằm hạn chế tác động của con người đến sinh cảnh sống, bãi đẻ của loài.",
        "version": "2024-1"
    },
    "ruabien-species-3": {
        "url": "http://vnredlist.vast.vn/lepidochelys-olivacea/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "RT75",
        "criteria": "A2cde",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Hoàng Văn Hà, Phạm Văn Thông",
        "citation": "Nguyễn Quảng Trường, 2023. Lepidochelys olivacea. Danh lục Đỏ Việt Nam. RT75",
        "threats": "Mối đe dọa Quần thể của loài này trong tự nhiên bị suy giảm nghiêm trọng do mất sinh cảnh sống, mất bãi đẻ, ô nhiễm nước biển, rùa và trứng bị săn bắt làm thực phẩm, mai làm đồ mỹ nghệ.",
        "population": "Hiện trạng quần thể Phân bố rải rác, rất hiếm gặp, đặc biệt là vùng biển phía bắc. Đây là loài có vùng phân bố rộng ở các đại dương lớn trên thế giới, có khả năng di cư rất xa nhưng số lượng cá thể đã bị suy giảm nghiêm trọng do môi trường sống và bãi đẻ bị xâm hại hoặc ô nhiễm, nuốt phải rác thải nhựa, cá thể non hoặc trưởng thành bị bắt khi mắc vào lưới đánh cá, bị săn bắt làm thực phẩm hoặc đồ mỹ nghệ, nuôi làm cảnh; ước tính quần thể trong tự nhiên đã bị suy giảm khoảng hơn 80% trong vòng 100 năm trở lại đây (tương đương 3 thế hệ), nhân tố tác động này hiện vẫn tồn tại ảnh hưởng trực tiếp đến quần thể của loài. Ghi nhận phân bố của loài này ở Việt Nam dọc theo vùng biển từ Vịnh Bắc bộ vào đến Vịnh Thái Lan nhưng rất hiếm gặp. Xu hướng quần thể Suy giảm",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố của loài có một phần nằm trong các khu bảo tồn biển nên được bảo vệ. Loài này có tên trong Nghị định số 64/2019/NĐ-CP của Chính phủ. Đề xuất Tiến hành các biện pháp bảo vệ sinh cảnh và bãi đẻ của rùa ở các khu vực ven biển và đảo, phục hồi quần thể trong tự nhiên. Quản lý các hoạt động săn bắt trái phép loài này. Tuyên truyền nhằm hạn chế tác động của con người đến sinh cảnh sống, bãi đẻ của loài.",
        "version": "2024-1"
    },
    "ruabien-species-4": {
        "url": "http://vnredlist.vast.vn/caretta-caretta/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "RT72",
        "criteria": "A2cde",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Hoàng Văn Hà, Phạm Văn Thông",
        "citation": "Nguyễn Quảng Trường, 2023. Caretta caretta. Danh lục Đỏ Việt Nam. RT72",
        "threats": "Mối đe dọa Quần thể của loài này trong tự nhiên bị suy giảm nghiêm trọng do mất sinh cảnh sống, mất bãi đẻ, ô nhiễm nước biển, rùa và trứng bị săn bắt làm thực phẩm, mai làm đồ mỹ nghệ.",
        "population": "Hiện trạng quần thể Cực kỳ hiếm gặp. Đây là loài có vùng phân bố rộng ở các đại dương lớn trên thế giới, có khả năng di cư rất xa nhưng số lượng cá thể đã bị suy giảm nghiêm trọng do môi trường sống và bãi đẻ bị xâm hại hoặc ô nhiễm, nuốt phải rác thải nhựa, cá thể non hoặc trưởng thành bị bắt khi mắc vào lưới đánh cá, bị săn bắt làm thực phẩm hoặc làm đồ trang trí, nuôi làm cảnh; ước tính quần thể trong tự nhiên đã bị suy giảm khoảng hơn 80% trong vòng 100 năm trở lại đây (tương đương 3 thế hệ), nhân tố tác động này hiện vẫn tồn tại ảnh hưởng trực tiếp đến quần thể của loài. Ghi nhận phân bố của loài này ở Việt Nam dọc theo vùng biển từ Vịnh Bắc bộ vào đến Vịnh Thái Lan nhưng cực kỳ hiếm gặp. Xu hướng quần thể Suy giảm",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố của loài có một phần nằm trong các khu bảo tồn biển nên được bảo vệ. Loài này có tên trong Nghị định số 64/2019/NĐ-CP của Chính phủ. Đề xuất Tiến hành các biện pháp bảo vệ sinh cảnh và bãi đẻ của rùa ở các khu vực ven biển và đảo, phục hồi quần thể trong tự nhiên. Quản lý các hoạt động săn bắt trái phép loài này. Tuyên truyền nhằm hạn chế tác động của con người đến sinh cảnh sống, bãi đẻ của loài.",
        "version": "2024-1"
    },
    "ruabien-species-5": {
        "url": "http://vnredlist.vast.vn/dermochelys-coriacea/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "RT76",
        "criteria": "A2acde",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Hoàng Văn Hà, Phạm Văn Thông",
        "citation": "Nguyễn Quảng Trường, 2023. Dermochelys coriacea. Danh lục Đỏ Việt Nam. RT76",
        "threats": "Mối đe dọa Quần thể của loài này trong tự nhiên bị suy giảm nghiêm trọng do mất sinh cảnh sống, mất bãi đẻ, ô nhiễm nước biển, rùa da và trứng bị săn bắt làm thực phẩm.",
        "population": "Hiện trạng quần thể Cực kỳ hiếm gặp. Đây là loài có vùng phân bố rộng ở các đại dương lớn trên thế giới, có khả năng di cư rất xa nhưng số lượng cá thể đã bị suy giảm nghiêm trọng do môi trường sống và bãi đẻ bị xâm hại hoặc ô nhiễm, nuốt phải rác thải nhựa, cá thể non hoặc trưởng thành bị bắt khi mắc vào lưới đánh cá, bị săn bắt làm thực phẩm hoặc làm đồ trang trí; ước tính quần thể trong tự nhiên đã bị suy giảm khoảng hơn 80% trong vòng 100 năm trở lại đây (tương đương 3 thế hệ), nhân tố tác động này hiện vẫn tồn tại ảnh hưởng trực tiếp đến quần thể của loài. Ghi nhận phân bố của loài này ở Việt Nam dọc theo vùng biển từ Vịnh Bắc bộ vào đến Vịnh Thái Lan nhưng cực kỳ hiếm gặp, gần như không còn ghi nhận bãi đẻ. Xu hướng quần thể Suy giảm",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố của loài có một phần nằm trong các khu bảo tồn biển nên được bảo vệ. Loài này có tên trong Nghị định số 64/2019/NĐ-CP của Chính phủ. Đề xuất Tiến hành các biện pháp bảo vệ sinh cảnh và bãi đẻ của rùa ở các khu vực ven biển và đảo, phục hồi quần thể trong tự nhiên. Quản lý các hoạt động săn bắt trái phép loài này. Tuyên truyền nhằm hạn chế tác động của con người đến sinh cảnh sống, bãi đẻ của loài.",
        "version": "2024-1"
    },
    "casau-species-1": {
        "url": "http://vnredlist.vast.vn/leiolepis-rubritaeniata/",
        "year": "2023",
        "status": "EW",
        "statusVn": "Tuyệt chủng ngoài tự nhiên",
        "refCode": "RT1",
        "criteria": "",
        "assessor": "Nguyễn Quảng Trường",
        "contributor": "Nguyễn Ngọc Sang",
        "citation": "Nguyễn Quảng Trường, 2023. Crocodylus porosus. Danh lục Đỏ Việt Nam. RT1",
        "threats": "Mối đe dọa Loài này đã săn bắt cạn kiệt phục vụ mục đích làm thực phẩm, kỹ nghệ da; sinh cảnh sống và bãi đẻ của loài bị chia cắt và suy thoái nghiêm trọng do phát triển nuôi trồng thủy sản, đô thị hóa vùng cửa sông ven biển.",
        "population": "Hiện trạng quần thể Loài này đã từng ghi nhận ở khu vực cửa sông Cần Giờ, vùng biển Côn Đảo và Phú Quốc, miền Nam Việt Nam, ghi nhận gần nhất cách đây hơn 30 năm trước. Hiện nay không còn ghi nhận cá thể nào ngoài tự nhiên tại Việt Nam. Xu hướng quần thể Tuyệt chủng ngoài tự nhiên",
        "conservation": "Biện pháp bảo tồn Đã có Vùng phân bố trước đây của loài có một phần nằm trong hai VQG Côn Đảo và Phú Quốc. Loài này có tên trong Nghị định số 84/2021/NĐ-CP của Chính phủ và Phụ lục I của CITES. Đề xuất Bảo vệ sinh cảnh tiềm năng của loài trong tự nhiên, giảm thiểu tác động của con người đến các khu vực rừng ngập mặn và cửa sông. Nghiên cứu khả năng tái thả loài này từ nguồn nuôi sinh sản nhân tạo vào các khu bảo tồn phù hợp.",
        "version": "2024-1"
    }
}

def main():
    print("=" * 70)
    print(" CHUẨN HÓA CẤU TRÚC VNREDLIST BÒ SÁT BIỂN THEO CHUẨN CÁ BIỂN")
    print("=" * 70)

    for sp_id, redlist_data in STANDARDIZED_REPTILES_REDLIST.items():
        print(f"\n[*] Cập nhật {sp_id}...")
        # Lấy biology hiện tại
        req_get = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}&select=id,vn_name,biology",
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}"
            }
        )
        with urllib.request.urlopen(req_get) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not data:
                print(f"  ❌ Không tìm thấy {sp_id}")
                continue
            curr_row = data[0]

        curr_bio = curr_row.get("biology") or {}
        # Ghi đè trường vnRedList theo chuẩn cá biển
        curr_bio["vnRedList"] = redlist_data

        # PATCH lên Supabase
        req_patch = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}",
            data=json.dumps({"biology": curr_bio}).encode("utf-8"),
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            method="PATCH"
        )
        with urllib.request.urlopen(req_patch) as patch_resp:
            print(f"  ✅ Đã đồng bộ thành công vnRedList chuẩn cho {sp_id} ({curr_row['vn_name']})")

    print("\n HOÀN TẤT ĐỒNG BỘ VNREDLIST CHUẨN CHO 6 LOÀI BÒ SÁT BIỂN!")

if __name__ == "__main__":
    main()
