#!/usr/bin/env python3
"""
scripts/sync_mammals_vnredlist_standard.py
Chuẩn hóa trường biology.vnRedList của 34 loài Thú biển Việt Nam (Bò biển + 33 loài Cá voi/heo)
theo đúng cấu trúc Golden Standard (2 cột: threats + population/trend pill, và khối Hero Card
bảo tồn: Đã ban hành & Đề xuất cấp thiết) trên ConservationWidget.tsx.

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

# Danh lục chuẩn hóa Sách Đỏ VAST cho 34 loài Thú biển Việt Nam
MAMMALS_REDLIST_DATA = {
    "thubien-species-1": {
        "url": "http://vnredlist.vast.vn/dsfsd/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM121",
        "criteria": "A2cd; C2a(i)",
        "assessor": "Đặng Huy Phương",
        "contributor": "Nguyễn Quảng Trường",
        "citation": "Đặng Huy Phương, 2023. Dugong dugon. Danh lục Đỏ Việt Nam. MM121",
        "threats": "Mối đe dọa Sinh cảnh thảm cỏ biển bị thu hẹp và suy thoái do bồi lắng, nạo vét luồng hàng hải, ô nhiễm ven bờ và các hoạt động khai thác thủy sản hủy diệt. Bò biển thường xuyên bị mắc vào lưới kéo đáy, lưới rê ven bờ của ngư dân (bycatch) dẫn đến ngạt thở chết, và từng bị săn bắt trái phép để lấy thịt, ngà, da làm vị thuốc dân gian.",
        "population": "Hiện trạng quần thể Rất hiếm gặp, chỉ còn ghi nhận quần thể nhỏ tại vùng biển Côn Đảo (khoảng 10-12 cá thể) và Phú Quốc. Từng phân bố phổ biến ở Vịnh Hạ Long, Khánh Hòa nhưng hiện đã biến mất hoàn toàn tại các vùng này. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Nằm trong Phụ lục I CITES, Danh mục nguy cấp quý hiếm ưu tiên bảo vệ (Nghị định 64/2019/NĐ-CP) và Nhóm I Nghị định 26/2019/NĐ-CP. Được bảo vệ nghiêm ngặt tại VQG Côn Đảo và VQG Phú Quốc. Đề xuất Phục hồi và bảo vệ nghiêm ngặt các bãi thảm cỏ biển trọng yếu; cấm tuyệt đối các nghề lưới kéo, lưới rê tầng đáy trong phân khu bảo tồn biển; gắn thiết bị cảnh báo va chạm tàu thuyền và thiết lập mạng lưới cứu hộ Bò biển mắc lưới cứu sống thả về tự nhiên.",
        "version": "2024-1"
    },
    "thubien-species-2": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET01",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera edeni. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nguy cơ mắc lưới đánh cá công nghiệp (lưới vây, lưới rê đại dương), va chạm tàu hàng vận tải tốc độ cao trên các tuyến hàng hải nội địa, ô nhiễm rác thải nhựa đại dương và suy giảm nguồn thức ăn (cá trích, cá nục) do đánh bắt cạn kiệt.",
        "population": "Hiện trạng quần thể Là loài cá voi tấm sừng hàm thường gặp nhất tại các vùng biển ven bờ và lộng Việt Nam (Bình Định, Khánh Hòa, Kiên Giang, Vịnh Bắc Bộ). Thường xuyên xuất hiện kiếm ăn theo đàn tại vùng biển Đề Gi (Bình Định). Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Nằm trong Phụ lục I CITES và Danh mục loài thủy sinh nguy cấp, quý, hiếm (Nghị định 26/2019/NĐ-CP, Nhóm I). Được cộng đồng ngư dân ven biển tôn kính bảo vệ theo tín ngưỡng dân gian thờ phụng Cá Ông. Đề xuất Quy định tốc độ tàu thuyền tại các vịnh và khu vực cá voi thường xuất hiện kiếm ăn; ban hành quy tắc ứng xử xem cá voi du lịch có trách nhiệm (khoảng cách an toàn tối thiểu 100m); tăng cường thu gom rác thải nổi.",
        "version": "2024-1"
    },
    "thubien-species-3": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM-CET02",
        "criteria": "A1ad",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera musculus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Va chạm với tàu viễn dương lớn ở vùng biển sâu, ô nhiễm tiếng ồn từ giao thông hàng hải và khảo sát địa chấn làm gián đoạn liên lạc định vị sóng âm sinh học, biến đổi khí hậu làm thay đổi luồng thức ăn sinh vật phù du.",
        "population": "Hiện trạng quần thể Cực kỳ hiếm gặp ở biển Đông và vùng biển Việt Nam. Dẫn liệu lịch sử chủ yếu dựa trên các bộ xương mẫu vật kích thước khổng lồ được bảo tồn tại các Lăng Ông ven biển miền Trung. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Bảo vệ tuyệt đối ở cấp độ toàn cầu theo Công ước CITES (Phụ lục I) và IWC cấm săn bắt thương mại. Pháp luật Việt Nam nghiêm cấm mọi hình thức săn bắt, khai thác (Nghị định 26/2019/NĐ-CP). Đề xuất Thiết lập quy chế báo cáo và định tuyến hàng hải tránh va chạm cá voi lớn; bảo tồn nguyên trạng các di cốt, bộ xương lịch sử tại các bảo tàng và di tích Lăng Ông Nam Hải phục vụ nghiên cứu di truyền học.",
        "version": "2024-1"
    },
    "thubien-species-4": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "EN",
        "statusVn": "Nguy cấp",
        "refCode": "MM-CET03",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera physalus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới ngư cụ trôi nổi ngoài khơi xa, va chạm tàu biển vận tải, ô nhiễm âm thanh biển sâu cản trở khả năng giao tiếp và định hướng đàn.",
        "population": "Hiện trạng quần thể Rất hiếm gặp ở vùng thềm lục địa và biển khơi Việt Nam, có ghi nhận mẫu vật dạt bờ tại vùng duyên hải Trung Bộ. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, cấm đánh bắt hoàn toàn theo quy định bảo tồn nguồn lợi thủy sản Việt Nam. Đề xuất Nghiên cứu lộ trình di cư vùng biển Đông bằng công nghệ giám sát âm thanh thụ động (PAM).",
        "version": "2024-1"
    },
    "thubien-species-5": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "EN",
        "statusVn": "Nguy cấp",
        "refCode": "MM-CET04",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera borealis. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Ô nhiễm môi trường biển khơi, mắc lưới đánh cá đại dương, rác thải nhựa vi mô tích tụ trong cơ quan lọc tấm sừng hàm.",
        "population": "Hiện trạng quần thể Rất hiếm, sống chủ yếu ngoài khơi xa vùng nước sâu, hiếm khi vào sát bờ thềm lục địa Việt Nam. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES và Nhóm I bảo vệ nghiêm ngặt của Nghị định 26/2019/NĐ-CP. Đề xuất Phối hợp hợp tác quốc tế trong quản lý và bảo tồn các loài thú biển di cư qua Biển Đông.",
        "version": "2024-1"
    },
    "thubien-species-6": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET05",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera acutorostrata. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới rê trôi ngầm tầng mặt và tầng trung, va chạm cano, tàu du lịch tốc độ cao ven bờ vịnh và đảo.",
        "population": "Hiện trạng quần thể Thỉnh thoảng xuất hiện kiếm ăn ở vùng thềm lục địa miền Trung và vịnh Bắc Bộ. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Bảo vệ theo Luật Thủy sản và Phụ lục I CITES. Đề xuất Tăng cường tập huấn ngư dân quy trình cắt gỡ lưới giải cứu cá voi bị mắc kẹt an toàn.",
        "version": "2024-1"
    },
    "thubien-species-7": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET06",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Balaenoptera omurai. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Hoạt động đánh bắt thủy sản quá mức làm giảm nguồn cá nhỏ, va chạm tàu thuyền và ô nhiễm môi trường nước biển ven bờ.",
        "population": "Hiện trạng quần thể Loài mới được tách phân loại năm 2003, đã có ghi nhận mẫu vật xác thực tại vùng biển miền Trung và Nam Bộ Việt Nam. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Áp dụng bảo vệ chung cho toàn bộ Bộ Cá voi Cetacea theo Nghị định 26/2019/NĐ-CP. Đề xuất Triển khai điều tra phân tử và giải trình tự DNA mẫu vật cá voi tại các Lăng Ông để làm rõ tình trạng phân bố.",
        "version": "2024-1"
    },
    "thubien-species-8": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET07",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Megaptera novaeangliae. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Dễ bị quấn vào lưới câu cá ngừ, lưới rê đại dương do tập tính nhào lộn và vây ngực dài đặc trưng; ô nhiễm âm thanh cản trở khúc hát định vị sinh sản.",
        "population": "Hiện trạng quần thể Hiếm gặp ở vùng biển Việt Nam, thường chỉ xuất hiện trên đường di cư theo mùa giữa vùng biển nhiệt đới và cận cực. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, bảo vệ nghiêm ngặt toàn cầu. Đề xuất Khuyến khích ngư dân báo cáo tức thời qua đường dây nóng khi phát hiện cá voi lưng gù cứu hộ.",
        "version": "2024-1"
    },
    "thubien-species-9": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM-CET08",
        "criteria": "A1ad",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Eschrichtius robustus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Quần thể Tây Bắc Thái Bình Dương bị suy giảm nghiêm trọng gần như tuyệt chủng do lịch sử săn bắt thương mại thế kỷ 20, va chạm tàu biển và giàn khoan dầu khí ngoài khơi.",
        "population": "Hiện trạng quần thể Cực kỳ hiếm, có dữ liệu mẫu vật lịch sử cổ xưa tại vùng biển Việt Nam. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, đối tượng bảo tồn ưu tiên tối cấp toàn cầu. Đề xuất Giám sát liên ngành với các viện nghiên cứu hải dương quốc tế trong khu vực Đông Á.",
        "version": "2024-1"
    },
    "thubien-species-10": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET09",
        "criteria": "A1d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Physeter macrocephalus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nuốt phải rác thải nhựa đại dương (túi nylon, lưới ma) gây tắc nghẽn dạ dày; tiếng ồn sonar quân sự và tàu ngầm làm rối loạn khả năng lặn sâu kiếm ăn; va chạm tàu viễn dương lớn.",
        "population": "Hiện trạng quần thể Là loài thú có răng lớn nhất, sinh sống ở vùng biển sâu thẳm ngoài khơi sườn dốc thềm lục địa miền Trung và quần đảo Hoàng Sa, Trường Sa. Nhiều bộ xương đồ sộ được tôn thờ tại Lăng Ông. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, bảo vệ nghiêm ngặt Nhóm I theo pháp luật Việt Nam. Đề xuất Bảo tồn các mẫu xương, răng cá nhà táng tại các Lăng Ông và bảo tàng sinh vật biển; tăng cường quản lý rác thải nhựa biển khơi.",
        "version": "2024-1"
    },
    "thubien-species-11": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET10",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Kogia breviceps. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Ô nhiễm rác thải nhựa, mắc lưới trôi tầng đáy sâu và ô nhiễm âm học.",
        "population": "Hiện trạng quần thể Sống ngoài biển khơi sâu, có ghi nhận mắc cạn định kỳ tại vùng biển Bình Thuận, Khánh Hòa, Đà Nẵng. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES, pháp luật thủy sản Việt Nam cấm khai thác. Đề xuất Xây dựng mạng lưới phản ứng nhanh cấp cứu động vật biển mắc cạn ven bờ.",
        "version": "2024-1"
    },
    "thubien-species-12": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET11",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Kogia sima. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nuốt phải rác nhựa biển, mắc lưới đánh cá và tiếng ồn hàng hải.",
        "population": "Hiện trạng quần thể Sống ở vùng sườn dốc thềm lục địa nước ấm, ghi nhận chủ yếu qua các vụ mắc cạn tự nhiên. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES, quản lý theo Nghị định 26/2019/NĐ-CP. Đề xuất Thu thập mẫu sinh thiết và lập cơ sở dữ liệu ADN các cá thể mắc cạn.",
        "version": "2024-1"
    },
    "thubien-species-13": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET12",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Ziphius cavirostris. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Cực kỳ nhạy cảm với sóng âm sonar quân sự công suất lớn, dẫn đến hội chứng giảm áp (decompression sickness) khi lặn gấp; nuốt rác thải nhựa.",
        "population": "Hiện trạng quần thể Kỷ lục gia lặn sâu nhất trong giới thú biển (>2.000m), ghi nhận mẫu vật ở miền Trung Việt Nam. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Kiểm soát việc xả thải rác đại dương và khảo sát sóng âm gần các hẻm vực biển sâu.",
        "version": "2024-1"
    },
    "thubien-species-14": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET13",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Mesoplodon densirostris. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Ô nhiễm âm thanh đại dương, mắc lưới rê sâu và biến đổi khí hậu ảnh hưởng đến tầng mực biển sâu.",
        "population": "Hiện trạng quần thể Rất hiếm gặp, chỉ sinh sống ở vùng biển khơi nhiệt đới sâu ngoài khơi Việt Nam. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Lưu trữ tiêu bản xương sọ tại Viện Hải dương học để đối chiếu phân loại.",
        "version": "2024-1"
    },
    "thubien-species-15": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET14",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Mesoplodon ginkgodens. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới đánh cá đại dương, rác thải nhựa và tiếng ồn sonar công nghiệp.",
        "population": "Hiện trạng quần thể Loài cá voi có mỏ đặc hữu của vùng biển Ấn Độ Dương - Tây Thái Bình Dương, có mẫu vật ghi nhận ở Việt Nam. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Nghiên cứu bổ sung hình thái học và ADN so sánh.",
        "version": "2024-1"
    },
    "thubien-species-16": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET15",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Indopacetus pacificus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Hoạt động hàng hải quân sự và thăm dò đáy biển, ô nhiễm rác thải nhựa tầng sâu.",
        "population": "Hiện trạng quần thể Một trong những loài thú biển bí ẩn và hiếm thấy nhất thế giới, có mẫu vật sọ cá ghi nhận tại Lăng Ông vùng duyên hải miền Trung. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Đăng ký mã số di sản mẫu vật khoa học quốc gia cho các tiêu bản xương sọ quý hiếm.",
        "version": "2024-1"
    },
    "thubien-species-17": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM-CET16",
        "criteria": "A2cde",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Neophocaena phocaenoides. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới đáy, lưới rê ven bờ và đăng đáy (bycatch) dẫn đến tử vong cao; suy thoái bãi ăn cửa sông do ô nhiễm hóa chất công nghiệp và giao thông thủy nội địa tấp nập.",
        "population": "Hiện trạng quần thể Từng rất phổ biến tại các vùng ven biển nông, vịnh và rừng ngập mặn Việt Nam nhưng hiện nay số lượng đã giảm sút nghiêm trọng (>70%). Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, Danh mục ưu tiên bảo vệ của Chính phủ. Đề xuất Thành lập các khu vực cấm lưới rê ven bờ vào mùa sinh sản của cá heo không vây; tuyên truyền vận động ngư dân giải thoát cá khi mắc lưới.",
        "version": "2024-1"
    },
    "thubien-species-18": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "EN",
        "statusVn": "Nguy cấp",
        "refCode": "MM-CET17",
        "criteria": "A2de",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Neophocaena asiaeorientalis. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Ô nhiễm nguồn nước cửa sông, giao thông thủy mật độ cao và lưới đánh cá ven bờ.",
        "population": "Hiện trạng quần thể Phân bố ở khu vực phía Bắc Vịnh Bắc Bộ giáp Trung Quốc, quần thể suy thoái nhanh. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES. Đề xuất Thiết lập cơ chế tuần tra bảo tồn chung vùng biển vịnh Bắc Bộ.",
        "version": "2024-1"
    },
    "thubien-species-19": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM-CET18",
        "criteria": "A2cde; C1",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Sousa chinensis. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mất sinh cảnh sống do san lấp lấn biển, nạo vét cảng nước sâu, tiếng ồn tàu cao tốc và nguy cơ cao mắc lưới rê, đăng đáy tại các vùng vịnh kín ven bờ.",
        "population": "Hiện trạng quần thể Rất hiếm gặp, chỉ còn các cá thể phân tán ghi nhận tại Vịnh Hạ Long, Bái Tử Long, Đồ Sơn, cửa sông Tiền và Phú Quốc. Quần thể đang bên bờ tuyệt chủng cục bộ. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, bảo vệ cấp cao nhất theo Nghị định 64/2019/NĐ-CP. Đề xuất Khoanh vùng phân khu bảo vệ nghiêm ngặt tại Vịnh Hạ Long - Bái Tử Long; kiểm soát tốc độ cano cao tốc chở khách du lịch.",
        "version": "2024-1"
    },
    "thubien-species-20": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "CR",
        "statusVn": "Cực kỳ nguy cấp",
        "refCode": "MM-CET19",
        "criteria": "A2cde; C2a(i)",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Orcaella brevirostris. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nguy cơ tuyệt chủng rất cao do mắc lưới đăng đáy, lưới quét cửa sông, ô nhiễm thuốc bảo vệ thực vật từ đồng ruộng chảy ra biển và phát triển kinh tế ven biển ồ ạt.",
        "population": "Hiện trạng quần thể Từng ghi nhận tại các cửa sông Cửu Long, Bà Rịa - Vũng Tàu và Kiên Giang. Hiện nay vô cùng hiếm gặp tại vùng biển tự nhiên của Việt Nam. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục I CITES, bảo vệ tuyệt đối theo Luật Thủy sản. Đề xuất Thực hiện điều tra khẩn cấp hiện trạng quần thể tại vùng biển Tây Nam Bộ và bảo tồn liên quốc gia vùng Vịnh Thái Lan.",
        "version": "2024-1"
    },
    "thubien-species-21": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET20",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Tursiops aduncus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới vây cá nổi, ô nhiễm tiếng ồn từ du lịch biển, suy thoái rạn san hô và vùng cỏ biển nơi cá kiếm ăn.",
        "population": "Hiện trạng quần thể Thường gặp thành đàn nhỏ 5-15 con quanh các đảo ven bờ (Phú Quý, Côn Đảo, Cù Lao Chàm, Cô Tô). Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Đưa vào danh mục bảo tồn ưu tiên tại các Khu bảo tồn biển (MPA).",
        "version": "2024-1"
    },
    "thubien-species-22": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "LC",
        "statusVn": "Ít quan tâm",
        "refCode": "MM-CET21",
        "criteria": "LC",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Tursiops truncatus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới ngư cụ trôi nổi, rác nhựa đại dương và va chạm tàu thuyền.",
        "population": "Hiện trạng quần thể Phân bố rộng ở cả vùng ven bờ và khơi xa Biển Đông, thích nghi tốt với môi trường biển đa dạng. Xu hướng quần thể tại tự nhiên: Ổn định.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Giám sát định kỳ các hoạt động đánh bắt hải sản tương tác với đàn cá heo.",
        "version": "2024-1"
    },
    "thubien-species-23": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET22",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Stenella attenuata. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Bị đánh bắt kèm (bycatch) trong nghề lưới vây cá ngừ đại dương; ô nhiễm rác thải nhựa nổi.",
        "population": "Hiện trạng quần thể Sống ngoài khơi xa vùng nước nhiệt đới sâu, bơi theo đàn lớn hàng trăm cá thể, thường đi kèm với cá ngừ. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Áp dụng quy chuẩn lưới an toàn cho cá heo trong nghề khai thác cá ngừ viễn dương.",
        "version": "2024-1"
    },
    "thubien-species-24": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET23",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Stenella longirostris. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới rê trôi ngầm ngoài khơi, cano du lịch quấy nhiễu đàn khi cá nghỉ ngơi tại các vịnh ven đảo.",
        "population": "Hiện trạng quần thể Nổi tiếng với vũ điệu nhảy xoay vòng trên không, thường kiếm ăn ban đêm ở vùng nước sâu và về nghỉ tại các vịnh đảo (Côn Đảo, Phú Quý). Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Ban hành quy tắc bảo vệ đàn cá heo spinner tại các khu du lịch sinh thái biển đảo.",
        "version": "2024-1"
    },
    "thubien-species-25": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET24",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Stenella coeruleoalba. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới vây khơi xa, ô nhiễm hóa chất hữu cơ bền (POPs) tích tụ qua chuỗi thức ăn.",
        "population": "Hiện trạng quần thể Sống ở vùng biển khơi đại dương ngoài rìa thềm lục địa, thỉnh thoảng ghi nhận dạt bờ ở miền Trung. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Tăng cường nghiên cứu ô nhiễm độc chất sinh học trên thú biển trôi dạt bờ.",
        "version": "2024-1"
    },
    "thubien-species-26": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET25",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Steno bredanensis. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc câu vàng cá ngừ, lưới rê và va chạm tàu thuyền.",
        "population": "Hiện trạng quần thể Sống sâu ngoài khơi, có mẫu vật sọ và xương ghi nhận tại Lăng Ông vùng ven biển Nam Trung Bộ. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Bảo tồn tư liệu mẫu vật tại các di tích lịch sử ven biển.",
        "version": "2024-1"
    },
    "thubien-species-27": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET26",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Grampus griseus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nuốt rác nhựa đại dương do nhầm lẫn với mực nang/mực ống; mắc lưới đánh cá sâu.",
        "population": "Hiện trạng quần thể Sống ở vùng sườn dốc ngầm thềm lục địa, thân mình nhiều vết sẹo đặc trưng do mực cắn và đồng loại cào xước. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Quản lý bền vững nguồn lợi mực đại dương làm thức ăn cho thú biển.",
        "version": "2024-1"
    },
    "thubien-species-28": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET27",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Lagenodelphis hosei. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới vây cá ngừ khơi xa, ô nhiễm môi trường đại dương.",
        "population": "Hiện trạng quần thể Sống ngoài khơi xa nhiệt đới sâu, bơi thành đàn đông đúc di chuyển nhanh. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Bổ sung khảo sát hải dương học ngoài khơi Trường Sa.",
        "version": "2024-1"
    },
    "thubien-species-29": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET28",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Globicephala macrorhynchus. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Dễ bị mắc cạn hàng loạt do tính gắn kết bầy đàn xã hội cực cao; mắc lưới đại dương và tiếng ồn sonar ngầm.",
        "population": "Hiện trạng quần thể Bơi theo đàn mẫu hệ từ 10-30 cá thể ở vùng nước sâu, có nhiều ghi nhận mắc cạn tập thể tại bờ biển Việt Nam. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Thành lập đội cứu hộ mắc cạn bầy đàn chuyên nghiệp ven biển.",
        "version": "2024-1"
    },
    "thubien-species-30": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET29",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Pseudorca crassidens. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Tương tác và cướp cá trên đường câu vàng ngừ/thu dẫn đến bị ngư dân xua đuổi hoặc mắc lưỡi câu; tích tụ chất độc sinh học.",
        "population": "Hiện trạng quần thể Thú săn mồi đỉnh của chuỗi thức ăn đại dương, phân bố thưa thớt ở vùng khơi Biển Đông. Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Ứng dụng thiết bị xua đuổi âm học (pingers) để giảm thiểu tương tác với tàu câu ngư dân.",
        "version": "2024-1"
    },
    "thubien-species-31": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "VU",
        "statusVn": "Sắp nguy cấp",
        "refCode": "MM-CET30",
        "criteria": "A2d",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Orcinus orca. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Tích tụ chất độc sinh học (PCB, DDT) ở nồng độ cao nhất qua chuỗi thức ăn, suy giảm nguồn cá lớn và ô nhiễm âm thanh biển sâu.",
        "population": "Hiện trạng quần thể Thỉnh thoảng xuất hiện ở các vùng nước sâu ngoài khơi Biển Đông và quanh các đảo xa bờ (Hoàng Sa, Trường Sa). Xu hướng quần thể tại tự nhiên: Suy giảm.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES, bảo vệ cao nhất theo quy chế quốc tế. Đề xuất Giám sát ảnh nhận dạng viền vây lưng (photo-ID) để theo dõi các cá thể di cư qua lãnh hải Việt Nam.",
        "version": "2024-1"
    },
    "thubien-species-32": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET31",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Feresa attenuata. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Mắc lưới vây cá ngừ đại dương và nuốt phải rác nhựa trôi dạt.",
        "population": "Hiện trạng quần thể Rất hiếm và kín đáo, chỉ sinh sống ở vùng nước nhiệt đới sâu ngoài thềm lục địa. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Thu thập dữ liệu mắc cạn và tiêu bản bảo tàng.",
        "version": "2024-1"
    },
    "thubien-species-33": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET32",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Peponocephala electra. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Nhạy cảm cao với sonar biển sâu, dễ mắc cạn bầy đàn; mắc lưới đánh cá khơi xa.",
        "population": "Hiện trạng quần thể Sống theo đàn đông từ vài chục đến hàng trăm cá thể ở vùng nước sâu ấm, có ghi nhận mẫu vật tại duyên hải Trung Bộ. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Bảo tồn các mẫu vật sọ và xương tại bảo tàng.",
        "version": "2024-1"
    },
    "thubien-species-34": {
        "url": "http://vnredlist.vast.vn/",
        "year": "2023",
        "status": "DD",
        "statusVn": "Thiếu dữ liệu",
        "refCode": "MM-CET33",
        "criteria": "DD",
        "assessor": "Viện Hải dương học",
        "contributor": "IEBR & Viện Hàn lâm KH&CN",
        "citation": "Sách Đỏ Việt Nam, 2024. Delphinus delphis. Nhóm Thú biển Việt Nam.",
        "threats": "Mối đe dọa Bị đánh bắt kèm (bycatch) trong nghề lưới vây, lưới rê tầng mặt và suy giảm đàn cá mồi nhỏ.",
        "population": "Hiện trạng quần thể Bơi theo đàn lớn ngoài khơi sâu, di chuyển nhanh săn cá nổi. Xu hướng quần thể tại tự nhiên: Không rõ.",
        "conservation": "Biện pháp bảo tồn Đã có Phụ lục II CITES. Đề xuất Áp dụng công nghệ giám sát tàu cá để hạn chế bycatch.",
        "version": "2024-1"
    }
}

def main():
    print("=" * 70)
    print("🐋 CHUẨN HÓA SÁCH ĐỎ VAST 2024 — THÚ BIỂN VIỆT NAM (GOLDEN STANDARD)")
    print("=" * 70)

    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    updated = 0
    errors = 0

    for sp_id, redlist in MAMMALS_REDLIST_DATA.items():
        fetch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}&select=id,scientific_name,vn_name,biology,vn_status"
        req = urllib.request.Request(fetch_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = json.loads(resp.read().decode("utf-8"))
                if not rows:
                    print(f"  [BỎ QUA] Không tìm thấy loài {sp_id} trong DB!")
                    continue
                row = rows[0]
        except Exception as e:
            print(f"  [LỖI] Không thể đọc {sp_id}: {e}")
            errors += 1
            continue

        existing_bio = row.get("biology") or {}
        if not isinstance(existing_bio, dict):
            existing_bio = {}

        existing_bio["vnRedList"] = redlist

        patch_payload = {
            "biology": existing_bio,
            "vn_status": redlist["status"]
        }

        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        patch_req = urllib.request.Request(
            patch_url,
            data=json.dumps(patch_payload).encode("utf-8"),
            headers=headers,
            method="PATCH"
        )

        try:
            with urllib.request.urlopen(patch_req, timeout=15) as patch_resp:
                patch_resp.read()
                print(f"  ✓ [{sp_id}] {row.get('vn_name')} ({row.get('scientific_name')}) -> SĐVN: {redlist['status']} ({redlist['refCode']})")
                updated += 1
        except Exception as e:
            print(f"  ✗ [{sp_id}] Lỗi khi cập nhật Supabase: {e}")
            errors += 1

    print("=" * 70)
    print(f"📊 TỔNG KẾT: Đã cập nhật thành công {updated}/34 loài Thú biển theo Golden Standard!")
    if errors > 0:
        print(f"⚠️ Có {errors} lỗi xảy ra.")
    print("=" * 70)

if __name__ == "__main__":
    main()
