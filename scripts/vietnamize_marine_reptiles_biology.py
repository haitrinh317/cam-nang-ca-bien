#!/usr/bin/env python3
"""
scripts/vietnamize_marine_reptiles_biology.py
Việt hóa 100% tiếng Việt chuẩn khoa học cho các trường sinh học (habitat, feedingType, reproduction)
của 6 loài bò sát biển mới trên Supabase, đảm bảo UI hoàn toàn thuần Việt không lọt tiếng Anh.

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

VN_BIOLOGY_DATA = {
    "ruabien-species-1": {
        "habitat": "Rạn san hô, Thảm cỏ biển, Bãi cát ven biển, Vùng biển nông ven bờ",
        "habitatVn": "Rạn san hô, Thảm cỏ biển, Bãi cát ven biển, Vùng biển nông ven bờ",
        "feedingType": "Ăn thực vật: Gặm cỏ biển, rong tảo và thực vật thủy sinh (khi trưởng thành)",
        "feedingTypeVn": "Ăn thực vật: Gặm cỏ biển, rong tảo và thực vật thủy sinh (khi trưởng thành)",
        "reproduction": "Đẻ trứng: Lên bãi cát đào tổ đẻ trứng vào ban đêm, 80 - 120 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Lên bãi cát đào tổ đẻ trứng vào ban đêm, 80 - 120 trứng/lứa"
    },
    "ruabien-species-2": {
        "habitat": "Rạn san hô, Rạn đá ven biển",
        "habitatVn": "Rạn san hô, Rạn đá ven biển",
        "feedingType": "Ăn bọt biển: Chuyên ăn bọt biển (hải miên) độc trên rạn san hô",
        "feedingTypeVn": "Ăn bọt biển: Chuyên ăn bọt biển (hải miên) độc trên rạn san hô",
        "reproduction": "Đẻ trứng: Đào tổ trên bãi cát hẻo lánh gần rạn san hô, 100 - 180 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Đào tổ trên bãi cát hẻo lánh gần rạn san hô, 100 - 180 trứng/lứa"
    },
    "ruabien-species-3": {
        "habitat": "Vùng biển nông ven bờ, Đáy bùn cát, Cửa sông ven biển",
        "habitatVn": "Vùng biển nông ven bờ, Đáy bùn cát, Cửa sông ven biển",
        "feedingType": "Ăn thịt / Ăn tạp: Cua ghẹ, động vật thân mềm, tôm và sứa",
        "feedingTypeVn": "Ăn thịt / Ăn tạp: Cua ghẹ, động vật thân mềm, tôm và sứa",
        "reproduction": "Đẻ trứng: Lên bãi cát đẻ trứng đơn lẻ (tại Việt Nam), 90 - 120 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Lên bãi cát đẻ trứng đơn lẻ (tại Việt Nam), 90 - 120 trứng/lứa"
    },
    "ruabien-species-4": {
        "habitat": "Biển khơi đại dương, Vùng biển ngoài khơi, Rạn san hô ngầm",
        "habitatVn": "Biển khơi đại dương, Vùng biển ngoài khơi, Rạn san hô ngầm",
        "feedingType": "Ăn thịt: Nghiền nát động vật không xương sống có vỏ cứng (cua, ốc, cầu gai)",
        "feedingTypeVn": "Ăn thịt: Nghiền nát động vật không xương sống có vỏ cứng (cua, ốc, cầu gai)",
        "reproduction": "Đẻ trứng: Đào tổ đẻ trứng trên các bãi cát lớn vùng cận nhiệt đới, 100 - 120 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Đào tổ đẻ trứng trên các bãi cát lớn vùng cận nhiệt đới, 100 - 120 trứng/lứa"
    },
    "ruabien-species-5": {
        "habitat": "Biển khơi đại dương, Vùng nước sâu đại dương, Bãi cát đẻ trứng",
        "habitatVn": "Biển khơi đại dương, Vùng nước sâu đại dương, Bãi cát đẻ trứng",
        "feedingType": "Chuyên ăn sứa biển (Gelatinivore) và sinh vật thân mềm trôi nổi",
        "feedingTypeVn": "Chuyên ăn sứa biển (Gelatinivore) và sinh vật thân mềm trôi nổi",
        "reproduction": "Đẻ trứng: Đào tổ đẻ trứng trên các bãi cát dốc sâu ven đại dương, 80 - 110 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Đào tổ đẻ trứng trên các bãi cát dốc sâu ven đại dương, 80 - 110 trứng/lứa"
    },
    "casau-species-1": {
        "habitat": "Vùng cửa sông, Rừng ngập mặn, Vùng biển nông ven bờ, Đầm phá nước lợ",
        "habitatVn": "Vùng cửa sông, Rừng ngập mặn, Vùng biển nông ven bờ, Đầm phá nước lợ",
        "feedingType": "Động vật ăn thịt đầu bảng: Săn cá, cua, rùa biển, chim và thú lớn",
        "feedingTypeVn": "Động vật ăn thịt đầu bảng: Săn cá, cua, rùa biển, chim và thú lớn",
        "reproduction": "Đẻ trứng: Đắp tổ gò cao bằng bùn và lá cây mục ven bờ sông rạch, 40 - 70 trứng/lứa",
        "reproductionVn": "Đẻ trứng: Đắp tổ gò cao bằng bùn và lá cây mục ven bờ sông rạch, 40 - 70 trứng/lứa"
    }
}

def main():
    print("=" * 70)
    print(" VIỆT HÓA 100% THÔNG SỐ SINH HỌC CHO 6 LOÀI BÒ SÁT BIỂN")
    print("=" * 70)

    for sp_id, bio_update in VN_BIOLOGY_DATA.items():
        print(f"\n[*] Xử lý {sp_id}...")
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
        # Cập nhật các trường sang tiếng Việt
        curr_bio.update(bio_update)

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
            print(f"  ✅ Đã cập nhật tiếng Việt thuần 100% cho {sp_id} ({curr_row['vn_name']})")

    print("\n HOÀN TẤT VIỆT HÓA DỮ LIỆU SINH HỌC CHO 6 LOÀI BÒ SÁT BIỂN!")

if __name__ == "__main__":
    main()
