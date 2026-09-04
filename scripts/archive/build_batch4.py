"""
build_batch4.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 74 loài Hồng-tảo (Rhodophyceae - Đợt 4, loài 134-207)
cho Volume 2 (Rong biển Việt Nam - GS. Phạm Hoàng Hộ, 1969).
"""
import os
import sys
import json
import time
import urllib.request
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE, 'public', 'images', 'species', 'thuc-vat-bien', 'v2')
DPI300_DIR = os.path.join(BASE, 'scratch', 'phh_300dpi')
os.makedirs(IMAGE_DIR, exist_ok=True)

BATCH4_DATA = [
    {
        "idx": 134, "name": "Jania decussatodichotoma", "author": "(Yendo) Yendo",
        "vn": "Rong San-hô chéo-lưỡng-phân", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong San-hô-tơ", "gen_lat": "Jania",
        "p": 146, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_69.png",
        "morphology": "Búi tơ vôi cao 1-3cm, màu hồng tươi; các nhánh phân chia lưỡng phân chéo góc 90 độ luân phiên nhau rất đặc sắc; các lóng hình trụ tròn dài 1-2mm, rộng 100-120µ; khớp nối ngắn.",
        "distribution": "Nhật-bản, Thái-bình-dương, Việt Nam (Nha-trang).",
        "status": "Phụ sinh trên các loài rong lớn ở tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Yendo 1905 : Corall. Jap. : 37; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430, fig. 40f."
    },
    {
        "idx": 135, "name": "Cheilosporum jungermannioides", "author": "Ruprecht ex Yendo",
        "vn": "Rong Kiều-bào rêu", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Kiều-bào", "gen_lat": "Cheilosporum",
        "p": 147, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_70.png",
        "morphology": "Tản tẩm vôi dẹp, cao 1-2cm; các đốt vôi xòe rộng sang hai bên như cánh mộng hoặc lá rêu; phân nhánh lưỡng phân; màu hồng tía.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Mọc bám kẽ đá nơi sóng vỗ mạnh ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Ruprecht 1851 : Tange Ochotsk. Meer. : 345; Yendo 1902 : Corall. Jap. : 18."
    },
    {
        "idx": 136, "name": "Amphiroa foliacea", "author": "Lamouroux",
        "vn": "Rong Lưỡng-thoa lá", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Lưỡng-thoa", "gen_lat": "Amphiroa",
        "p": 149, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_73.png",
        "morphology": "Tản tẩm vôi cứng, cao 3-6cm, màu hồng tía hay xám phấn; các lóng dẹp xòe rộng thành hình chiếc lá nhỏ có gờ giữa; chia nhánh lưỡng phân.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Mọc trên đá và rạn san hô tầng triều dưới.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Lamouroux 1824 : Voy. Uranie Bot. : 628, pl. 93; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430, fig. 40c."
    },
    {
        "idx": 137, "name": "Corallina officinalis", "author": "Linnaeus",
        "vn": "Rong San-hô thuốc", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong San-hô", "gen_lat": "Corallina",
        "p": 150, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_74.png",
        "morphology": "Tản hình lông chim kép đối xứng, cao 4-10cm, tẩm vôi cứng màu hồng đỏ; trục chính mang các nhánh mọc đối; đốt trục hình nêm, đốt nhánh con thon nhỏ; ổ khái-bao ở ngọn.",
        "distribution": "Toàn cầu ở các vùng biển ôn đới và nhiệt đới. Việt Nam: Miền Trung.",
        "status": "Được dùng làm thuốc trị giun sán từ cổ xưa; mọc trên đá vùng triều.",
        "specimen": "Mẫu thu tại Quy-nhơn và Nha-trang.",
        "literature": "Linnaeus 1758 : Syst. Nat. ed. 10 : 805; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430."
    },
    {
        "idx": 138, "name": "Lithothamnion erubescens", "author": "Foslie",
        "vn": "Rong Thạch-chi ửng-đỏ", "fam_vn": "Họ Thạch-chi", "fam_lat": "Hapalidiaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Thạch-chi", "gen_lat": "Lithothamnion",
        "p": 152, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_76.png",
        "morphology": "Tản dạng khối đá vôi màu hồng tím, phủ đầy các mấu nhánh hình trụ tròn hoặc hình chùy ngắn; tẩm vôi rất cứng; nắp ổ bào-tử có nhiều lỗ thoát (multiporate).",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Rạn san hô Nha-trang.",
        "status": "Loài tạo rạn san hô quan trọng, gắn kết cát sỏi thành đá rạn vôi.",
        "specimen": "Mẫu rạn san hô Nha-trang (Foslie 1904).",
        "literature": "Foslie 1900 : Siboga Exped. : 31; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 427."
    },
    {
        "idx": 139, "name": "Mesophyllum mesomorphum", "author": "(Foslie) Adey",
        "vn": "Rong Trung-phiến trung-hình", "fam_vn": "Họ Thạch-chi", "fam_lat": "Hapalidiaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Trung-phiến", "gen_lat": "Mesophyllum",
        "p": 153, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_77.png",
        "morphology": "Tản dạng phiến vôi mỏng xếp lớp chồng lên nhau như vảy nấm, màu hồng xám; mép phiến tự do lượn sóng; ổ bào-tử nhiều lỗ thoát.",
        "distribution": "Biển nhiệt đới toàn cầu. Gặp ở rạn san hô Nha-trang.",
        "status": "Mọc trên san hô chết tầng triều dưới.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Foslie 1901 : Siboga : 19; Adey 1970 : K. Norske Vidensk. Selsk. Skr. : 25."
    },
    {
        "idx": 140, "name": "Fosliella farinosa", "author": "(Lamouroux) M. Howe",
        "vn": "Rong Phốt-li phấn", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Phốt-li", "gen_lat": "Fosliella",
        "p": 154, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_78.png",
        "morphology": "Tản vi thể hình đĩa tròn mỏng tẩm vôi màu trắng hay hồng phấn, đường kính 2-5mm; mép tản có các tế-bào lông tơ lớn (trichocytes) xếp đơn độc.",
        "distribution": "Toàn cầu. Rất phổ biến khắp vùng biển Việt Nam.",
        "status": "Phụ sinh dày đặc trên lá cỏ biển (Enhalus, Thalassia) và các rong lớn.",
        "specimen": "Mẫu bãi cỏ biển Nha-trang.",
        "literature": "Lamouroux 1816 : Hist. Polyp. Corall. : 315; Howe 1920 : Bahama Flora : 587; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 427."
    },
    {
        "idx": 141, "name": "Neogoniolithon myriocarpum", "author": "(Foslie) Setchell & Mason",
        "vn": "Rong Giác-thạch vạn-quả", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Giác-thạch", "gen_lat": "Neogoniolithon",
        "p": 155, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_79.png",
        "morphology": "Tản vỏ tẩm vôi dày màu tím đỏ; bề mặt phủ đầy các nốt ổ bào-tử hình nón cụt nổi rõ (uniporate); các tế-bào lông tơ mọc thành cụm.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Tạo vỏ bọc trên đá và rạn san hô chết vùng triều thấp.",
        "specimen": "Mẫu Hòn-tre, Nha-trang.",
        "literature": "Foslie 1897 : Norv. Lith. : 19; Setchell & Mason 1943 : Proc. Nat. Acad. Sci. 29 : 91."
    },
    {
        "idx": 142, "name": "Lithophyllum okamurai", "author": "Foslie",
        "vn": "Rong Thạch-phiến Ô-ca-mu-ra", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Thạch-phiến", "gen_lat": "Lithophyllum",
        "p": 156, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_80.png",
        "morphology": "Tản đá vôi cứng màu hồng tím, hình khối mang nhiều mấu gai nhọn hoặc cành ngắn hình trụ; ổ bào-tử chỉ mở 1 lỗ.",
        "distribution": "Nhật-bản, Biển Đông, Thái-bình-dương. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Thành phần kiến tạo rạn san hô quan trọng ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu rạn san hô Nha-trang.",
        "literature": "Foslie 1900 : Siboga : 16; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 427."
    },
    {
        "idx": 143, "name": "Lithophyllum samoense", "author": "Foslie",
        "vn": "Rong Thạch-phiến Sa-mô-a", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Thạch-phiến", "gen_lat": "Lithophyllum",
        "p": 156, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_81.png",
        "morphology": "Tản vỏ vôi láng bóng bám sát nền đá san hô, màu hồng tím sẫm; mép tản mỏng; các ổ bào-tử hình chóp nón thấp rải rác đều.",
        "distribution": "Thái-bình-dương nhiệt đới (Samoa, Việt Nam).",
        "status": "Mọc trên đá san hô ở rạn nông.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Foslie 1906 : Algol. Notiser II : 20; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 427."
    },
    {
        "idx": 144, "name": "Dermatolithon pustulatum", "author": "(Lamouroux) Foslie",
        "vn": "Rong Bì-thạch mụn", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Bì-thạch", "gen_lat": "Dermatolithon",
        "p": 157, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_82.png",
        "morphology": "Tản vôi nhỏ hình vảy tròn lồi như mụn, đường kính 2-8mm, màu hồng tím; tế-bào gốc xếp nghiêng xiên; ổ bào-tử lồi to ở trung tâm.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Phụ sinh trên các loài rong đỏ và rong nâu lớn vùng triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Lamouroux 1816 : Hist. Polyp. Corall. : 315; Foslie 1898 : Syst. Surv. : 11."
    },
    {
        "idx": 145, "name": "Porolithon onkodes", "author": "(Heydrich) Foslie",
        "vn": "Rong Khổng-thạch u", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Khổng-thạch", "gen_lat": "Porolithon",
        "p": 158, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_83.png",
        "morphology": "Tản đá vôi cực kỳ dày cứng màu hồng gạch hay vàng nâu, bề mặt lồi lõm dạng u bướu; tế-bào lông tơ mọc thành cụm ngang lớn đặc trưng; chịu sóng đánh cực mạnh.",
        "distribution": "Rất đặc trưng ở các rạn san hô nhiệt đới Ấn-độ-Tây Thái-bình-dương. Việt Nam: Hoàng-sa, Trường-sa, Côn-đảo, Nha-trang.",
        "status": "Loài chủ đạo tạo thành gờ rạn ngoài (algal ridge) che chắn sóng cho các đảo san hô.",
        "specimen": "Mẫu rạn ngoài vịnh Nha-trang.",
        "literature": "Heydrich 1897 : Ber. Deutsch. Bot. Ges. XV : 410; Foslie 1909 : Algol. Notiser VI : 57; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 427."
    },
    {
        "idx": 146, "name": "Mastophora rosea", "author": "(C. Agardh) Setchell",
        "vn": "Rong Nhũ-thảo hồng", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Nhũ-thảo", "gen_lat": "Mastophora",
        "p": 159, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_84.png",
        "morphology": "Tản tẩm vôi dẻo dai dạng phiến màng xòe rộng, màu hồng tía; mép phiến quăn cuốn xuống; ổ bào-tử hình núm vú nhô cao nổi bật trên mặt tản.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương nhiệt đới. Việt Nam: Duyên hải Nam Trung bộ.",
        "status": "Mọc trên đá và san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 264; Setchell 1943 : Proc. Nat. Acad. Sci. 29 : 127; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 428."
    },
    {
        "idx": 147, "name": "Halymenia floresia", "author": "(Clemente) C. Agardh",
        "vn": "Rong Hồng-mạc hoa", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 160, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_85.png",
        "morphology": "Tản màng nhầy mềm mỏng màu đỏ hồng cánh sen cực kỳ đẹp; cao 10-30cm; chia nhánh lông chim nhiều lần; mép nhánh có răng nhỏ; cơ cấu tủy hình sợi lỏng lẻo chìm trong chất keo nhớt.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Thái-bình-dương. Việt Nam: Nha-trang, Qui-nhơn.",
        "status": "Mọc ở tầng hạ-duyên-hải sâu 2-10m trên đá san hô nơi nước chảy êm.",
        "specimen": "Mẫu lặn vịnh Nha-trang.",
        "literature": "Clemente 1807 : Ensayo : 312; C. Agardh 1817 : Syn. Alg. Scand. : XIX; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 432."
    },
    {
        "idx": 148, "name": "Halymenia durvillaei", "author": "Bory de Saint-Vincent",
        "vn": "Rong Hồng-mạc Đuyếc-vin", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 161, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_86.png",
        "morphology": "Tản to lớn, cao 15-35cm, sụn mềm nhầy dai, màu đỏ tươi đến đỏ thẫm; thân dẹp chia nhánh lông chim nhiều lần, mép nhánh phủ đầy các gai thịt nhỏ và nhánh con tua tủa.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở vùng biển miền Trung và Nam Việt Nam.",
        "status": "Rong đẹp mắt có thể chế biến thực phẩm và chiết polysaccharide; mọc trên đá ngầm dưới triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Phú-quốc.",
        "literature": "Bory 1828 : Voy. Coquille Bot. : 180, pl. 15; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 432, fig. 44."
    },
    {
        "idx": 149, "name": "Halymenia maculata", "author": "J. Agardh",
        "vn": "Rong Hồng-mạc đốm", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 162, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_87.png",
        "morphology": "Tản hình phiến rộng lượn sóng màu đỏ tía, bề mặt có những đốm màu đậm nhạt loang lổ; mép phiến có gai nhỏ; chất keo dày mềm.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở rạn san hô sâu 3-8m.",
        "specimen": "Mẫu lặn thu thập tại Nha-trang.",
        "literature": "J. Agardh 1885 : Till Alg. Syst. VII : 12; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 432."
    },
    {
        "idx": 150, "name": "Halymenia dilatata", "author": "Zanardini",
        "vn": "Rong Hồng-mạc nở", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 163, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_88.png",
        "morphology": "Tản phiến to hình quạt xòe rộng, cao 10-20cm, chất màng mềm nhầy, màu hồng đỏ tươi; mép nguyên hoặc xẻ thùy cạn lượn sóng.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải trên đá san hô.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Zanardini 1851 : Flora : 35; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 433, fig. 43."
    },
    {
        "idx": 151, "name": "Halymenia ceylanica", "author": "Harvey ex Kützing",
        "vn": "Rong Hồng-mạc Tích-lan", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 164, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_89.png",
        "morphology": "Tản phân nhánh lưỡng phân hoặc lông chim hẹp, thân dẹp rộng 2-5mm, màu đỏ thắm; chất nhầy dai.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Rạn san hô sâu 1-4m.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1866 : Tab. Phyc. XVI : 33, pl. 93."
    },
    {
        "idx": 152, "name": "Halymenia microcarpa", "author": "(Montagne) P.C. Silva",
        "vn": "Rong Hồng-mạc quả-nhỏ", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 165, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_90.png",
        "morphology": "Tản chia nhánh dẹp thon dài, mép có nhiều nhánh con dạng gai nhỏ; ổ quả-nang rất nhỏ chìm trong chất nhầy của vỏ.",
        "distribution": "Thái-bình-dương, Ấn-độ-dương.",
        "status": "Mọc trên đá ngầm.",
        "specimen": "Mẫu khảo sát vịnh Nha-trang.",
        "literature": "Montagne 1844 : Ann. Sci. Nat. Bot. : 65."
    },
    {
        "idx": 153, "name": "Halymenia ulvoidea", "author": "Zanardini",
        "vn": "Rong Hồng-mạc dạng-diếp", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Hồng-mạc", "gen_lat": "Halymenia",
        "p": 166, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_94.png",
        "morphology": "Tản phiến mỏng mềm nhầy hình quạt rộng giống rong Diếp-biển (Ulva), màu hồng nhạt trong suốt; mép có phụ bộ hình gai nhỏ.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng nước sâu êm sóng.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Zanardini 1868 : Mem. R. Ist. Veneto XIV : 206."
    },
    {
        "idx": 154, "name": "Polyopes ligulatus", "author": "(Harvey) De Toni",
        "vn": "Rong Đa-khổng dải", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đa-khổng", "gen_lat": "Polyopes",
        "p": 167, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_95.png",
        "morphology": "Tản sụn dai cứng, màu nâu đỏ đen, cao 4-8cm; thân dẹp hình dải hẹp rộng 1-2mm, phân nhánh lưỡng phân dày đặc; tủy đặc gồm các sợi xếp dọc sít sao.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Việt Nam: Nha-trang, Cà-ná.",
        "status": "Bám chặt trên đá nơi sóng dữ dội ở tầng trung-duyên-hải thượng.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Harvey 1860 : Proc. Amer. Acad. IV : 331; De Toni 1905 : Syll. Alg. IV : 1595; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 433."
    },
    {
        "idx": 155, "name": "Grateloupia filicina", "author": "(Lamouroux) C. Agardh",
        "vn": "Rong Gai dương-xỉ", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Gai", "gen_lat": "Grateloupia",
        "p": 168, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_96.png",
        "morphology": "Tản sụn mềm dẻo, cao 5-15cm, màu tím đỏ đến lục đen; thân chính dẹp hẹp, mang 2 hàng nhánh con mọc đối sít sao hình lá dương xỉ; các nhánh con thon nhỏ hai đầu.",
        "distribution": "Toàn cầu ở vùng duyên hải. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Rong ăn được, mọc thành dải dày trên đá ở tầng trung-duyên-hải nơi có sóng vừa.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Vũng-Tàu.",
        "literature": "Lamouroux 1813 : Essai : 42; C. Agardh 1822 : Sp. Alg. I : 223; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 432, fig. 42a."
    },
    {
        "idx": 156, "name": "Grateloupia ramosissima", "author": "Okamura",
        "vn": "Rong Gai nhiều-nhánh", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Gai", "gen_lat": "Grateloupia",
        "p": 169, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_97.png",
        "morphology": "Tản mọc thành búi dày, cao 8-20cm, màu đỏ tím đậm; thân chia nhánh rất nhiều lần chằng chịt, các nhánh uốn éo hình sợi dẹp hẹp.",
        "distribution": "Nhật-bản, Biển Đông. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc trên đá vùng triều giữa vào mùa xuân và hè.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Okamura 1913 : Icones Jap. Alg. III : 60, pl. 117; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 432."
    },
    {
        "idx": 157, "name": "Grateloupia prolifera", "author": "Okamura",
        "vn": "Rong Gai đâm-chồi", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Gai", "gen_lat": "Grateloupia",
        "p": 170, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_98.png",
        "morphology": "Tản phiến dẹp rộng 1-2cm, cao 10-20cm, màu đỏ nâu; bề mặt và mép phiến mọc ra vô số nhánh chồi con nhỏ li ti dày đặc.",
        "distribution": "Nhật-bản, Việt Nam (Nha-trang, Qui-nhơn).",
        "status": "Mọc trên gờ đá tầng triều thấp.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Okamura 1903 : Alg. Jap. Exsicc. : no 85."
    },
    {
        "idx": 158, "name": "Grateloupia phuquocensis", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Gai Phú-quốc", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Gai", "gen_lat": "Grateloupia",
        "p": 171, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_99.png",
        "morphology": "Tản sụn dai màu đỏ tía, cao 5-10cm; thân dẹp rộng 2-3mm, phân nhánh đôi ở gốc rồi mang các nhánh con mọc cách thon dài; giải phẫu tủy có các tế bào hình sao liên kết dày đặc. Loài mới phát hiện cho khoa học tại đảo Phú Quốc.",
        "distribution": "Đặc hữu vùng biển đảo Phú-quốc (Kiên-giang, Việt Nam).",
        "status": "Bám trên rạn đá san hô ven đảo Phú-quốc.",
        "specimen": "Holotype thu tại bãi An-thới, Phú-quốc.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 167, fig. 2.99."
    },
    {
        "idx": 159, "name": "Prionitis vietnamensis", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Cưa việtnam", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Cưa", "gen_lat": "Prionitis",
        "p": 172, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_100.png",
        "morphology": "Tản sụn rất cứng chắc như sừng, cao 6-12cm, màu nâu đỏ sẫm; thân dẹp, phân nhánh lưỡng phân hoặc lông chim; mép nhánh mang các mấu gai nhỏ xếp đều như răng cưa; tủy gồm các sợi xếp cực kỳ khít khao.",
        "distribution": "Đặc hữu bờ biển Việt Nam (Khánh-hòa, Ninh-thuận).",
        "status": "Bám chắc vào đá dốc đứng nơi sóng lớn dữ dội ở đới triều thấp.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 168, fig. 2.100."
    },
    {
        "idx": 160, "name": "Carpopeltis formosana", "author": "Okamura",
        "vn": "Rong Quả-bì Đài-loan", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Quả-bì", "gen_lat": "Carpopeltis",
        "p": 173, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_101.png",
        "morphology": "Tản sụn dai cứng, màu đỏ nâu hay đen, cao 4-8cm; thân dẹp rộng 2-3mm, phân nhánh lưỡng phân nhiều lần tạo bụi hình quạt; các ổ sinh sản hình đĩa tròn tạo thành ở ngọn các nhánh con dẹp.",
        "distribution": "Đài-loan, Biển Đông, Việt Nam (Nha-trang, Cà-ná).",
        "status": "Mọc trên đá vùng trung-duyên-hải thượng nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Okamura 1931 : Icones Jap. Alg. VI : 70, pl. 284; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 433."
    },
    {
        "idx": 161, "name": "Carpopeltis cornea", "author": "Okamura",
        "vn": "Rong Quả-bì sừng", "fam_vn": "Họ Hồng-mạc", "fam_lat": "Halymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Quả-bì", "gen_lat": "Carpopeltis",
        "p": 174, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_102.png",
        "morphology": "Tản rất cứng như chất sừng, màu nâu sẫm, cao 3-6cm; các nhánh hẹp hình dải, ngọn tù tròn.",
        "distribution": "Nhật-bản, Việt Nam.",
        "status": "Bám kẽ đá nơi sóng to.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Okamura 1934 : Icones Jap. Alg. VII : 36, pl. 318."
    },
    {
        "idx": 162, "name": "Titanophora pulchra", "author": "Dawson",
        "vn": "Rong Cương-thảo đẹp", "fam_vn": "Họ Nhầy-hoa", "fam_lat": "Schizymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Cương-thảo", "gen_lat": "Titanophora",
        "p": 176, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_103.png",
        "morphology": "Tản phiến dẹp tẩm vôi xốp bên trong, cao 8-15cm, màu hồng phấn tươi; phiến xẻ thùy hình ngón tay, bề mặt phủ đầy các gai thịt nhỏ li ti; chất sụn dẻo dai.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Mọc ở rạn san hô sâu 3-10m nơi nước trong.",
        "specimen": "Mẫu thu tại vịnh Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 433, fig. 45; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 172."
    },
    {
        "idx": 163, "name": "Schizymenia dubyi", "author": "(Chauvin ex Duby) J. Agardh",
        "vn": "Rong Nhầy-hoa Đuy-bi", "fam_vn": "Họ Nhầy-hoa", "fam_lat": "Schizymeniaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Nhầy-hoa", "gen_lat": "Schizymenia",
        "p": 177, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_104.png",
        "morphology": "Tản phiến rộng hình bầu dục hay hình tim, cao 10-25cm, chất mềm như da nhầy, màu đỏ máu tươi; mép phiến nguyên hoặc lượn sóng; tủy gồm các sợi dài lỏng lẻo trong chất nhầy.",
        "distribution": "Châu Âu, Bắc Mỹ, Nhật-bản, Việt Nam (Nha-trang).",
        "status": "Mọc trên đá ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Chauvin in Duby 1830 : Bot. Gall. II : 944; J. Agardh 1851 : Sp. Alg. II : 171."
    },
    {
        "idx": 164, "name": "Gelidiopsis gracilis", "author": "(Kützing) Feldmann",
        "vn": "Rong Thạch-giả thanh", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Thạch-giả", "gen_lat": "Gelidiopsis",
        "p": 179, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_105.png",
        "morphology": "Tản sụn hình sợi tròn mảnh khảnh như cước, cao 3-8cm, màu lục đen hay nâu tía; chia nhánh bất quy tắc; phẫu thức ngang không có sợi căn-trạng, tế-bào tủy tròn to.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1868 : Tab. Phyc. XVIII : 17; Feldmann 1931 : Trav. Cryptog. : 156."
    },
    {
        "idx": 165, "name": "Gelidiopsis intricata", "author": "(C. Agardh) Vickers",
        "vn": "Rong Thạch-giả chằng-chịt", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Thạch-giả", "gen_lat": "Gelidiopsis",
        "p": 180, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_106.png",
        "morphology": "Tản mọc thành búi rối như mớ chỉ thép, cao 2-5cm, màu nâu lục; sợi cứng tròn đường kính 0,3-0,5mm; phân nhánh lưỡng phân chằng chịt.",
        "distribution": "Khắp các biển nhiệt đới thế giới. Rất phổ biến ở Việt Nam.",
        "status": "Mọc thành thảm rối dày bám chặt vào đá và san hô vùng triều.",
        "specimen": "Mẫu bãi đá Nha-trang và Vũng-Tàu.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 333; Vickers 1905 : Ann. Sci. Nat. Bot. IX : 61; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 423, fig. 34a-d."
    },
    {
        "idx": 166, "name": "Gelidiopsis scoparia", "author": "(Montagne & Millardet) De Toni",
        "vn": "Rong Thạch-giả chổi", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Thạch-giả", "gen_lat": "Gelidiopsis",
        "p": 181, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_107.png",
        "morphology": "Thân đứng thẳng cao 5-10cm, phần ngọn phân nhánh dẹp tập trung dày đặc như chiếc chổi xòe; màu nâu đỏ cứng cáp.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải trên đá gềnh.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Montagne & Millardet 1862 : Alg. Réunion : 20; De Toni 1900 : Syll. Alg. IV : 410."
    },
    {
        "idx": 167, "name": "Gelidiopsis variabilis", "author": "(Greville ex J. Agardh) Schmitz",
        "vn": "Rong Thạch-giả biến-thiên", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Thạch-giả", "gen_lat": "Gelidiopsis",
        "p": 182, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_108.png",
        "morphology": "Tản cao 6-12cm, hình thái biến thiên từ thân tròn đến dẹp; phân nhánh lưỡng phân hoặc so le; màu đỏ tía sẫm.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Việt Nam: Duyên hải Nam Trung bộ.",
        "status": "Bãi đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1851 : Sp. Alg. II : 468; Schmitz 1895 : Mar. Florid. Deutsch-Ostafrika : 148."
    },
    {
        "idx": 168, "name": "Gracilariopsis chorda", "author": "(Holmes) Ohmi",
        "vn": "Rong Câu-giả dây-đàn", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu-giả", "gen_lat": "Gracilariopsis",
        "p": 183, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_109.png",
        "morphology": "Tản hình sợi tròn dài như dây đàn, dài 20-50cm (đôi khi đến 1m), đường kính 1-2mm, màu đỏ nâu hay vàng lục; ít phân nhánh; trong quả-nang không có sợi dinh-dưỡng nối thể quả với vỏ nang (khác Gracilaria).",
        "distribution": "Nhật-bản, Trung-quốc, Việt Nam.",
        "status": "Nguồn nguyên liệu agar có giá trị kinh tế cao, mọc ở đầm phá và vịnh nông đáy cát bùn.",
        "specimen": "Mẫu đầm Cù-mông và vịnh Nha-trang.",
        "literature": "Holmes 1896 : New Mar. Alg. Japan : 253; Ohmi 1958 : Syst. Stud. Gracilaria : 16."
    },
    {
        "idx": 169, "name": "Gracilariopsis nganii", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Câu-giả Ngân", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu-giả", "gen_lat": "Gracilariopsis",
        "p": 184, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_110.png",
        "morphology": "Tản mềm hình sợi, dài 15-30cm, màu lục đỏ; phân nhánh nhiều lần xen kẽ; cấu trúc phẫu thức ngang chuyển tiếp từ từ từ vỏ sang tủy; quả-nang nhỏ không có sợi dinh dưỡng. Đặt theo tên nhà nghiên cứu Ngân.",
        "distribution": "Đặc hữu Việt Nam (vùng biển Phan-thiết, Nha-trang).",
        "status": "Mọc trong vịnh nước lợ tĩnh.",
        "specimen": "Holotype thu tại Phan-thiết.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 180, fig. 2.110."
    },
    {
        "idx": 170, "name": "Gracilariopsis phanthietensis", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Câu-giả Phan-thiết", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu-giả", "gen_lat": "Gracilariopsis",
        "p": 185, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_111.png",
        "morphology": "Tản mọc thành bụi dày, dài 10-20cm, nhánh hình sợi tròn hơi móp méo lúc khô; phân nhánh so le dày đặc ở phần ngọn. Loài mới cho khoa học.",
        "distribution": "Đặc hữu bờ biển Phan-thiết (Bình-thuận, Việt Nam).",
        "status": "Bám trên sỏi đá vũng triều cạn.",
        "specimen": "Holotype thu tại Phan-thiết.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 181, fig. 2.111."
    },
    {
        "idx": 171, "name": "Gracilaria verrucosa", "author": "(Hudson) Papenfuss",
        "vn": "Rong Câu chỉ", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 186, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_112.png",
        "morphology": "Tản hình sợi tròn như dây cước, dài 20-50cm, đường kính 1-2mm, màu nâu đỏ đến lục sẫm; phân nhánh so le nhiều cấp; trong quả-nang có nhiều sợi dinh-dưỡng nối liền thể quả với vách bao nang; phẫu thức ngang có ranh giới rõ rệt giữa tế-bào vỏ nhỏ và tế-bào tủy lớn.",
        "distribution": "Toàn cầu. Phân bố rộng khắp từ Bắc đến Nam ở các đầm phá, cửa sông ven biển Việt Nam.",
        "status": "Loài rong kinh tế quan trọng hàng đầu của Việt Nam, dùng nấu thạch đông, chiết thạch agar và chế biến món ăn bổ dưỡng.",
        "specimen": "Mẫu đầm Lăng-cô, phá Tam-giang, đầm Cù-mông, vịnh Nha-trang.",
        "literature": "Hudson 1762 : Fl. Angl. : 470; Papenfuss 1950 : Hydrobiologia II : 195; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438, fig. 49."
    },
    {
        "idx": 172, "name": "Gracilaria confervoides", "author": "(Linnaeus) Greville",
        "vn": "Rong Câu dạng-thủy-miên", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 187, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_113.png",
        "morphology": "Tản sợi thon dài, nhánh phụ ngắn mọc rải rác; màu đỏ tía nhạt; cấu trúc giải phẫu và quả nang tương tự G. verrucosa.",
        "distribution": "Các vùng biển nhiệt đới và ôn đới ấm.",
        "status": "Rong kinh tế chiết agar.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Linnaeus 1763 : Sp. Pl. ed. 2 : 1629; Greville 1830 : Alg. Brit. : 123."
    },
    {
        "idx": 173, "name": "Gracilaria bursapastoris", "author": "(S.G. Gmelin) P.C. Silva",
        "vn": "Rong Câu hầu-bao", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 188, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_114.png",
        "morphology": "Tản sụn dày mập, dẹp hoặc hơi tròn, phân nhánh lưỡng phân hoặc so le dày đặc; màu đỏ tươi đẹp mắt.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô tầng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Gmelin 1768 : Hist. Fuc. : 121; Silva 1952 : Univ. Calif. Publ. Bot. 25 : 265."
    },
    {
        "idx": 174, "name": "Gracilaria coronopifolia", "author": "J. Agardh",
        "vn": "Rong Câu vương-diệp", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 188, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_115.png",
        "morphology": "Tản bụi tròn hình bán cầu, cao 5-10cm, màu đỏ hồng sẫm; phân nhánh lưỡng phân nhiều lần sát nhau; các nhánh ngọn chẻ đôi ngắn như sừng hươu nhỏ.",
        "distribution": "Hawaii, Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Mọc ở vùng triều thấp nơi nước trong sạch.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1852 : Sp. Alg. II : 592; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438."
    },
    {
        "idx": 175, "name": "Gracilaria eucheumatoides", "author": "Harvey",
        "vn": "Rong Câu kỳ-lân", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 189, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_116.png",
        "morphology": "Tản sụn cực kỳ dày cứng mọc bò sát đá, màu lục đen hay nâu đỏ sẫm; thân dẹp rộng 5-10mm, dày 2-3mm; mép nhánh có nhiều răng cưa thô tù dạng mấu thịt giống như rong Kỳ-lân (Eucheuma); bám cực chặt vào đá.",
        "distribution": "Thái-bình-dương nhiệt đới, Biển Đông. Rất phong phú ở duyên hải miền Trung và hải đảo Việt Nam.",
        "status": "Mọc ở tầng hạ-duyên-hải và gờ rạn san hô nơi sóng đập dữ dội nhất.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, đảo Côn-đảo, Phú-quốc.",
        "literature": "Harvey 1860 : Proc. Amer. Acad. IV : 331; Okamura 1927 : Icones Jap. Alg. VI : 38, pl. 271; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438, fig. 48e."
    },
    {
        "idx": 176, "name": "Gracilaria crassa", "author": "Harvey ex J. Agardh",
        "vn": "Rong Câu dày", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Câu", "gen_lat": "Gracilaria",
        "p": 190, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_117.png",
        "morphology": "Tản sụn dày mọng nước, thân tròn mập mạp đường kính 2-4mm, màu vàng lục hay xanh ô-liu; các đốt thắt eo rõ rệt hình xúc xích hay chuỗi hạt; phân nhánh lưỡng phân hoặc tam phân; giòn dễ gãy.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến khắp duyên hải Việt Nam.",
        "status": "Rong thực phẩm ăn sống giòn ngon và nấu thạch; mọc trên rạn san hô chết vùng triều thấp.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "J. Agardh 1876 : Epicrisis : 417; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438, fig. 48b."
    },
    {
        "idx": 177, "name": "Ceratodictyon spongiosum", "author": "Zanardini",
        "vn": "Rong Hải-miên-võng", "fam_vn": "Họ Rong-câu", "fam_lat": "Gracilariaceae",
        "ord_vn": "Bộ Rong-câu", "ord_lat": "Gracilariales", "gen_vn": "Chi Rong Hải-miên-võng", "gen_lat": "Ceratodictyon",
        "p": 191, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_118.png",
        "morphology": "Loài cộng sinh đặc biệt giữa rong đỏ và hải miên (bọt biển); tản tạo thành khối xốp cứng lồi lõm hình sừng hươu hoặc ngón tay, màu lục xám hay nâu; các sợi rong phân nhánh đan lưới dày đặc bên trong khung xương hải miên.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phổ biến ở bờ biển miền Trung và Nam Việt Nam.",
        "status": "Mọc trên các rạn san hô nông tầng triều dưới nơi nước sạch và sóng vừa.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo.",
        "literature": "Zanardini 1878 : Phyc. Ind. : 37; Okamura 1909 : Icones Jap. Alg. II : 1, pl. 51; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438, fig. 48c."
    },
    {
        "idx": 178, "name": "Sarcodia ceylanica", "author": "Harvey",
        "vn": "Rong Nhục-phiến Tích-lan", "fam_vn": "Họ Nhục-phiến", "fam_lat": "Sarcodiaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Nhục-phiến", "gen_lat": "Sarcodia",
        "p": 192, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_119.png",
        "morphology": "Tản thịt dày sụn nạc, màu đỏ tươi sẫm; phiến xẻ thùy sâu hình ngón tay hoặc quạt dẹp; mép phiến dày nguyên hoặc có u lồi nhỏ; cơ cấu trong gồm các tế-bào tròn to chứa đầy chất dinh dưỡng.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Rong ăn được có giá trị, mọc ở tầng hạ-duyên-hải trên rạn đá san hô.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Harvey 1857 : Ceylon Alg. : no 26; J. Agardh 1876 : Epicrisis : 431; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436."
    },
    {
        "idx": 179, "name": "Sarcodia montagneana", "author": "(J. Agardh) J. Agardh",
        "vn": "Rong Nhục-phiến Mông-tanh", "fam_vn": "Họ Nhục-phiến", "fam_lat": "Sarcodiaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Nhục-phiến", "gen_lat": "Sarcodia",
        "p": 193, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_120.png",
        "morphology": "Tản phiến dẹp rất dày thịt sụn, cao 10-20cm, rộng 2-4cm, màu đỏ thắm; phiến phân nhánh lưỡng phân hoặc xẻ chân vịt; mép lượn sóng.",
        "distribution": "New Zealand, Úc, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở rạn san hô sâu 2-5m.",
        "specimen": "Mẫu đảo Hòn-tre, Nha-trang.",
        "literature": "J. Agardh 1852 : Sp. Alg. II : 601; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436."
    },
    {
        "idx": 180, "name": "Solieria mollis", "author": "(Harvey) Kylin",
        "vn": "Rong Xô-li-ê mềm", "fam_vn": "Họ Xô-li-ê", "fam_lat": "Solieriaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Xô-li-ê", "gen_lat": "Solieria",
        "p": 194, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_121.png",
        "morphology": "Tản sụn mềm nhầy mọng nước, cao 10-25cm, màu đỏ hồng tươi; thân hình trụ tròn đường kính 2-4mm, phân nhánh so le; các nhánh thon nhọn dần hai đầu; tủy gồm các sợi dài chìm trong chất keo.",
        "distribution": "Úc, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Chiết carrageenan chất lượng tốt; mọc ở tầng triều dưới trên cát sỏi rạn san hô.",
        "specimen": "Mẫu vịnh Nha-trang (Dawson 1954).",
        "literature": "Harvey 1863 : Phyc. Austr. V : pl. 270; Kylin 1932 : Florideenordn. Gigartinales : 18; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436, fig. 47."
    },
    {
        "idx": 181, "name": "Hypnea musciformis", "author": "(Wulfen) J.V. Lamouroux",
        "vn": "Rong Đùi-gà rêu", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 195, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_122.png",
        "morphology": "Tản hình bụi sụn dẻo dai cao 10-25cm, màu vàng lục hay đỏ nâu; phân nhánh chằng chịt; đặc trưng nổi bật là các đầu cành chính phồng to và cuốn cong hình móc câu rất khỏe để móc bám vào các cành rong khác; nhánh phủ đầy gai nhỏ.",
        "distribution": "Khắp các biển nhiệt đới và cận nhiệt đới thế giới. Rất phổ biến tại Việt Nam.",
        "status": "Nguyên liệu chính chiết xuất k-carrageenan phục vụ thực phẩm và y dược; mọc nhiều ở vùng triều thấp và đầm nước mặn.",
        "specimen": "Mẫu Nha-trang, Phan-thiết, Vũng-Tàu, Phú-quốc.",
        "literature": "Wulfen in Jacquin 1789 : Coll. Bot. III : 154, pl. 14; Lamouroux 1813 : Essai : 43; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436."
    },
    {
        "idx": 182, "name": "Hypnea valentiae", "author": "(Turner) Montagne",
        "vn": "Rong Đùi-gà Va-lăng", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 196, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_123.png",
        "morphology": "Tản mọc thành búi dày cao 10-20cm, màu nâu đỏ; thân chính hình sợi tròn đường kính 1-2mm, phủ đầy các nhánh gai phụ thẳng đứng hình que nhọn mọc tỏa đều các phía; không có cành móc câu.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Thái-bình-dương. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Nguồn nguyên liệu carrageenan quan trọng, mọc trên rạn san hô chết và đá vùng triều.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu.",
        "literature": "Turner 1809 : Fuci II : 17, pl. 78; Montagne 1841 : Pl. Cell. Canaries : 161; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436, fig. 46l."
    },
    {
        "idx": 183, "name": "Hypnea cervicornis", "author": "J. Agardh",
        "vn": "Rong Đùi-gà sừng-hươu", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 197, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_123b.png",
        "morphology": "Tản bụi xốp chằng chịt, màu vàng nâu hay hồng; phân nhánh lưỡng phân hoặc so le rẽ góc rộng giống gạc sừng hươu; nhánh thon nhọn dần.",
        "distribution": "Các vùng biển nhiệt đới ấm toàn cầu. Việt Nam: Duyên hải Trung và Nam bộ.",
        "status": "Mọc lẫn trong các rạn san hô tầng triều dưới.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1851 : Sp. Alg. II : 451; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 437, fig. 46d-g."
    },
    {
        "idx": 184, "name": "Hypnea cornuta", "author": "(Kützing) J. Agardh",
        "vn": "Rong Đùi-gà sừng", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 198, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_124.png",
        "morphology": "Tản cao 10-20cm, màu nâu vàng lục; đặc sắc nhờ các cành con hình sao hoặc hình chữ thập có 2-4 nhánh gai nhọn xòe ra (gọi là cành hình sao/sừng), rất dễ rụng làm phương tiện sinh sản sinh dưỡng.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Phổ biến ở các vịnh và đầm nước mặn Việt Nam.",
        "status": "Mọc nhiều trên đáy cát bùn sỏi ở vùng triều thấp và đầm nuôi trồng thủy sản.",
        "specimen": "Mẫu đầm Cù-mông và vịnh Cam-ranh.",
        "literature": "Kützing 1849 : Sp. Alg. : 758; J. Agardh 1851 : Sp. Alg. II : 449; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436, fig. 46c."
    },
    {
        "idx": 185, "name": "Hypnea esperi", "author": "Bory de Saint-Vincent",
        "vn": "Rong Đùi-gà Ét-pe", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 199, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_125.png",
        "morphology": "Búi tơ nhỏ chằng chịt, cao 2-4cm, màu đỏ hồng; nhánh rất mảnh đường kính dưới 0,5mm; gai ngắn thưa thớt.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc bám trên chân san hô và vỏ hàu.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Bory 1828 : Voy. Coquille Bot. : 157; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 436, fig. 46h-j."
    },
    {
        "idx": 186, "name": "Hypnea hamulosa", "author": "(Turner) Montagne",
        "vn": "Rong Đùi-gà móc-nhỏ", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 199, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_126.png",
        "morphology": "Tản bụi cứng, thân chính mang các nhánh phụ ngắn dày đặc cuốn cong hình móc nhỏ ở đầu.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Thái-bình-dương.",
        "status": "Trên rạn đá san hô vùng triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Turner 1809 : Fuci II : 19; Montagne 1844 : Fl. Algérie : 150."
    },
    {
        "idx": 187, "name": "Hypnea chordacea", "author": "Kützing",
        "vn": "Rong Đùi-gà dây", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 200, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_127.png",
        "morphology": "Tản gồm nhiều thân thẳng đứng hình trụ tròn mọc chụm từ một gốc, cao 5-12cm, ít phân nhánh dài; bề mặt phủ đầy các gai ngắn nhọn đều tăm tắp như chiếc bàn chải ống tròn; màu nâu đỏ.",
        "distribution": "Thái-bình-dương, Biển Đông. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Bám chắc vào đá nơi sóng to ở tầng trung-duyên-hải hạ.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Kützing 1849 : Sp. Alg. : 758; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 437, fig. 46t."
    },
    {
        "idx": 188, "name": "Hypnea pannosa", "author": "J. Agardh",
        "vn": "Rong Đùi-gà rách", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 201, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_128.png",
        "morphology": "Tản tạo thành đệm thảm cứng dày cộp dính sát vào đá, cao 2-4cm, màu tím biếc ánh kim quang lấp lánh dưới nước; nhánh phân chia góc rộng chằng chịt dính liền nhau; ngọn gai nhọn hoắt.",
        "distribution": "Khắp các biển nhiệt đới ấm thế giới. Phổ biến trên các rạn san hô Việt Nam.",
        "status": "Mọc bám cực chắc trên mặt đá và cành san hô nơi sóng đập dữ dội.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "J. Agardh 1847 : Öfv. K. Vet.-Akad. Förh. : 14; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 437, fig. 46k."
    },
    {
        "idx": 189, "name": "Hypnea cenomyce", "author": "J. Agardh",
        "vn": "Rong Đùi-gà địa-y", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 202, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_129.png",
        "morphology": "Tản bò lan tỏa tạo thành lớp vảy màng cứng giòn như địa y trên mặt đá, màu lục xám; nhánh con rất ngắn nhọn.",
        "distribution": "Úc, Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều cao có sóng văng ướt.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "J. Agardh 1851 : Sp. Alg. II : 452; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 437."
    },
    {
        "idx": 190, "name": "Hypnea nidulans", "author": "Setchell",
        "vn": "Rong Đùi-gà tổ-chim", "fam_vn": "Họ Rong-đùi-gà", "fam_lat": "Hypneaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đùi-gà", "gen_lat": "Hypnea",
        "p": 203, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_130.png",
        "morphology": "Tản bụi đệm chằng chịt uốn cong như tổ chim, cao 3-6cm; các nhánh đan bện vào nhau; ổ tứ-bào-tử-phòng phồng to ở một bên của các nhánh gai con nhỏ.",
        "distribution": "Samoa, Thái-bình-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Rạn san hô tầng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Setchell 1924 : Amer. Samoa : 161, fig. 30; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 438, fig. 46e."
    },
    {
        "idx": 191, "name": "Gigartina tenella", "author": "Harvey",
        "vn": "Rong Gi-ga mảnh", "fam_vn": "Họ Cự-tảo", "fam_lat": "Gigartinaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Cự-tảo", "gen_lat": "Gigartina",
        "p": 204, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_131.png",
        "morphology": "Tản sụn dẹp nhỏ, cao 2-4cm, màu đỏ tím sẫm; phân nhánh lông chim hoặc lưỡng phân hẹp; mép và mặt phiến phủ đầy các gai thịt nhỏ; quả-nang lồi to hình cầu trên mặt nhánh.",
        "distribution": "Nhật-bản, Trung-quốc, Việt Nam (Hải-phòng, Nha-trang).",
        "status": "Mọc trên đá vùng triều giữa nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Harvey 1860 : Proc. Amer. Acad. IV : 331; Okamura 1908 : Icones Jap. Alg. I : 159, pl. 33."
    },
    {
        "idx": 192, "name": "Gymnogongrus serenei", "author": "Dawson",
        "vn": "Rong Thể-cầu Xê-ren", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 205, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_132.png",
        "morphology": "Bụi màu vàng lục dính vào đá nhờ đĩa nhỏ; mang nhiều tản hình dải nẹp, đơn hay 1-2 lần lưỡng phân, cao 4-6cm, rộng 1-2mm, bìa nguyên, đầu tròn; phẫu thức ngang dày 300-400µ; tảo-quả rộng 100µ hình bán cầu. Đặt tên theo Viện trưởng Raoul Serène.",
        "distribution": "Đặc hữu vùng duyên hải Nha-trang (Việt Nam).",
        "status": "Ở Hòn-chồng (Nha-trang), làm thành một đai dày 30cm liên tục dưới Chnoospora minima và trên Tetraclita; trà trộn với Chaetomorpha antennina (tháng I-IV).",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vicin. Nha-trang : 441, fig. 52d; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 201, fig. 2.132."
    },
    {
        "idx": 193, "name": "Gymnogongrus quinhonensis", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Thể-cầu Qui-nhơn", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 206, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_133.png",
        "morphology": "Bụi cứng như sụn, đính vào đá nhờ một dĩa nhỏ, mang nhiều tản dài 10-13cm, rộng đến 4mm, 4-6 lần lưỡng phân, đầu tản tròn; màu nâu đỏ đậm; cấu trúc mô tủy đặc quánh. Loài mới phát hiện cho khoa học tại bờ biển Quy Nhơn.",
        "distribution": "Đặc hữu vùng biển Quy-nhơn (Bình-định, Việt Nam).",
        "status": "Mọc trên vách đá gềnh nơi sóng đánh dữ dội ở tầng hạ-duyên-hải.",
        "specimen": "Holotype thu tại bờ biển Quy-nhơn.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 202, fig. 2.133."
    },
    {
        "idx": 194, "name": "Gymnogongrus flabelliformis", "author": "Harvey",
        "vn": "Rong Thể-cầu hình-quạt", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 207, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_134.png",
        "morphology": "Tản hình quạt xòe rất đẹp, cao 4-8cm, màu tím đỏ sẫm; thân dẹp chia nhánh lưỡng phân liên tục sát nhau; các nhánh tỏa rộng cùng mặt phẳng; sụn cứng bóng.",
        "distribution": "Nhật-bản, Triều-tiên, Việt Nam (Đà-nẵng, Nha-trang).",
        "status": "Mọc trên đá vùng triều giữa nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Harvey 1857 : Proc. Amer. Acad. : 332; Okamura 1909 : Icones Jap. Alg. II : 44, pl. 61."
    },
    {
        "idx": 195, "name": "Gymnogongrus japonicus", "author": "Suringar",
        "vn": "Rong Thể-cầu Nhật-bản", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 208, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_135.png",
        "morphology": "Tản sụn cao 5-10cm, các nhánh dẹp dài, phân nhánh thưa hơn G. flabelliformis; đầu nhánh tày tròn.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Suringar 1867 : Alg. Jap. : 259; Okamura 1910 : Icones Jap. Alg. II : 115, pl. 81."
    },
    {
        "idx": 196, "name": "Gymnogongrus chnoosporoides", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Thể-cầu giả-nhiễu-bào", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 209, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_136.png",
        "morphology": "Tản sụn dai cao 4-7cm, màu vàng nâu; phân nhánh lưỡng phân nhiều lần tạo dạng búi tròn giống hệt rong nâu Chnoospora; mang nhiều ổ quả-bào-tử lồi tròn. Loài mới cho khoa học.",
        "distribution": "Đặc hữu bờ biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá vùng triều cao cùng với Chnoospora minima.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 205, fig. 2.136."
    },
    {
        "idx": 197, "name": "Gymnogongrus griffithsiae", "author": "(Turner) Martius",
        "vn": "Rong Thể-cầu Gơ-ríp-phít", "fam_vn": "Họ Diệp-tảo", "fam_lat": "Phyllophoraceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thể-cầu", "gen_lat": "Gymnogongrus",
        "p": 210, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_138.png",
        "morphology": "Bụi sụn nhỏ cao 2-5cm, màu nâu đỏ đen; thân sợi tròn ở gốc rồi dẹp dần lên trên; các nhánh ngọn chẻ đôi hình chữ V hẹp; nốt sinh sản lồi thành đai quanh nhánh.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Trên đá tầng trung-duyên-hải.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Turner 1808 : Fuci I : 80; Martius 1833 : Fl. Brasil. I : 27."
    },
    {
        "idx": 198, "name": "Weberella micans", "author": "Schmitz",
        "vn": "Rong Vê-be óng-ánh", "fam_vn": "Họ Cầm-phiến", "fam_lat": "Rhodymeniaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Vê-be", "gen_lat": "Weberella",
        "p": 211, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_139.png",
        "morphology": "Tản phiến dẹp màng mỏng hình bán cầu lồi lõm, màu xanh biếc ánh kim quang ngũ sắc rất rực rỡ dưới đáy biển; cơ cấu trong rỗng có vách ngăn tế bào lớn.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trong các hốc rạn san hô sâu 2-6m.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Schmitz in Murray 1895 : Phyc. Mem. III : 90; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434."
    },
    {
        "idx": 199, "name": "Catenella nipae", "author": "Zanardini",
        "vn": "Rong Xích-đoạn dừa-nước", "fam_vn": "Họ Xích-đoạn", "fam_lat": "Caulacanthaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Xích-đoạn", "gen_lat": "Catenella",
        "p": 212, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_140.png",
        "morphology": "Tản hình chuỗi xích nhỏ, cao 1-3cm, màu nâu tím sẫm; thân gồm các đốt hình thoi hoặc bầu dục dẹp thắt eo rõ rệt ở hai đầu; từ mỗi eo mọc ra các rễ bám hình trụ có đĩa dính; phân nhánh dích dắc.",
        "distribution": "Rừng ngập mặn nhiệt đới Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp vùng rừng sác ngập mặn Việt Nam.",
        "status": "Loài chỉ thị sinh thái rừng ngập mặn; bám dày đặc trên rễ thở cây đước, mắm và gốc cuống dừa nước (Nypa fruticans).",
        "specimen": "Mẫu rừng ngập mặn Cần-giờ, Vũng-Tàu, Cà-mau.",
        "literature": "Zanardini 1872 : Phyc. Ind. : 143, pl. 6; Post 1936 : Bostrychia-Caloglossa Assoc. : 14; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434, fig. 48a."
    },
    {
        "idx": 200, "name": "Catenella subumbellata", "author": "Tseng",
        "vn": "Rong Xích-đoạn cận-tán", "fam_vn": "Họ Xích-đoạn", "fam_lat": "Caulacanthaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Xích-đoạn", "gen_lat": "Catenella",
        "p": 213, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_141.png",
        "morphology": "Tản chuỗi đốt, các nhánh ngọn mọc chụm 3-5 nhánh từ một khớp eo tạo hình tán hoa nhỏ; màu đỏ tía.",
        "distribution": "Biển Đông (Hải Nam, Việt Nam).",
        "status": "Bám trên rễ đước rừng ngập mặn.",
        "specimen": "Mẫu rừng ngập mặn duyên hải miền Nam.",
        "literature": "Tseng 1942 : Mar. Alg. Hong Kong : 142; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 209."
    },
    {
        "idx": 201, "name": "Rhabdonia charoides", "author": "Harvey",
        "vn": "Rong Trượng-thảo dạng-xa-trục", "fam_vn": "Họ Trượng-thảo", "fam_lat": "Areschougiaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Trượng-thảo", "gen_lat": "Rhabdonia",
        "p": 214, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_142.png",
        "morphology": "Tản sụn hình trụ tròn cao 10-20cm, màu đỏ cam; các nhánh con mọc vòng quanh trục như rong Xa-trục (Chara).",
        "distribution": "Úc, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc dưới triều nơi rạn san hô sâu.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Harvey 1863 : Phyc. Austr. : pl. 296."
    },
    {
        "idx": 202, "name": "Caulacanthus ustulatus", "author": "(Mertens ex Turner) Kützing",
        "vn": "Rong Thoa-gai sém", "fam_vn": "Họ Thoa-gai", "fam_lat": "Caulacanthaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Thoa-gai", "gen_lat": "Caulacanthus",
        "p": 215, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_143.png",
        "morphology": "Tản hình bụi tơ gai dày đặc đan bện như nỉ, cao 1-3cm, màu nâu đỏ đen như bị cháy sém; thân hình sợi phân nhánh bất quy tắc, ngọn nhánh thon thành mũi gai nhọn hoắt; tế-bào ngọn duy nhất phân chia theo vách xiên.",
        "distribution": "Toàn cầu ở các bờ biển ấm. Rất phổ biến tại Việt Nam.",
        "status": "Mọc thành đai màu nâu đen ở tầng trung-duyên-hải thượng trên đá và vỏ hà bám đá.",
        "specimen": "Mẫu bãi đá Nha-trang, Qui-nhơn, Vũng-Tàu.",
        "literature": "Turner 1809 : Fuci II : 87; Kützing 1843 : Phyc. Gen. : 395; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434, fig. 48d."
    },
    {
        "idx": 203, "name": "Lomentaria corallicola", "author": "Boergesen",
        "vn": "Rong Tiết-bào san-hô", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Tiết-bào", "gen_lat": "Lomentaria",
        "p": 216, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_144.png",
        "morphology": "Tản hình ống rỗng mềm mại màu hồng tía, cao 1-3cm; thân chia nhánh dẹp, thắt eo ở các mấu khớp; vách ống do 1 lớp tế bào lớn bao quanh khoang rỗng chứa dịch nhầy; ổ tứ-bào-tử chìm trong vách lõm.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên rong San hô (Corallina, Jania) ở tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Boergesen 1939 : Ceylonese Mar. Alg. : 113, figs. 30-32; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 435, fig. 48f."
    },
    {
        "idx": 204, "name": "Lomentaria sinensis", "author": "Howe",
        "vn": "Rong Tiết-bào Trung-hoa", "fam_vn": "Họ Tản-sừng", "fam_lat": "Lomentariaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Tiết-bào", "gen_lat": "Lomentaria",
        "p": 217, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_145.png",
        "morphology": "Tản ống rỗng phân nhánh so le nhiều cấp, màu đỏ tươi; các nhánh con thon nhỏ hai đầu như chiếc suốt dệt vải.",
        "distribution": "Trung-quốc, Nhật-bản, Việt Nam.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Howe 1924 : Bull. Torrey Bot. Club LI : 137, pl. 1."
    },
    {
        "idx": 205, "name": "Champia vieillardii", "author": "Kützing",
        "vn": "Rong Xăm Vay-la", "fam_vn": "Họ Rong-xăm", "fam_lat": "Champiaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Xăm", "gen_lat": "Champia",
        "p": 218, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_148.png",
        "morphology": "Tản dẹp hình dải màng rỗng có vách ngăn ngang đều đặn như mắt tre gióng trúc, cao 3-6cm, rộng 2-4mm, màu tím hồng ánh kim quang rực rỡ; phân nhánh lông chim hoặc mọc đối; ổ quả-nang hình bình hoa nổi rõ trên mép phiến.",
        "distribution": "New Caledonia, Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Rất đẹp mắt, mọc bám trên đá và san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1866 : Tab. Phyc. XVI : 14, pl. 37; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434, fig. 46a."
    },
    {
        "idx": 206, "name": "Champia parvula", "author": "(C. Agardh) Harvey",
        "vn": "Rong Xăm nhỏ", "fam_vn": "Họ Rong-xăm", "fam_lat": "Champiaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Xăm", "gen_lat": "Champia",
        "p": 219, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_147.png",
        "morphology": "Tản hình bụi tơ nhầy mềm, cao 2-8cm, màu lục vàng hay hồng phớt; thân hình ống tròn đường kính 1-2mm, có các vách ngăn ngang chia thân thành từng lóng đều đặn rõ rệt; khoang trong rỗng chứa dịch nhầy; phân nhánh bất quy tắc chằng chịt.",
        "distribution": "Toàn cầu ở các biển ấm. Rất phổ biến khắp vùng biển Việt Nam.",
        "status": "Phụ sinh phổ biến trên cỏ biển và các loài rong lớn ở tầng triều thấp.",
        "specimen": "Mẫu bãi biển Nha-trang, Vũng-Tàu, Phú-quốc.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 207; Harvey 1853 : Nereis Bor. Amer. II : 76; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434."
    },
    {
        "idx": 207, "name": "Champia salicornioides", "author": "Harvey",
        "vn": "Rong Xăm dạng-diêm-phù", "fam_vn": "Họ Rong-xăm", "fam_lat": "Champiaceae",
        "ord_vn": "Bộ Cầm-phiến", "ord_lat": "Rhodymeniales", "gen_vn": "Chi Rong Xăm", "gen_lat": "Champia",
        "p": 220, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_149.png",
        "morphology": "Tản đứng cao 5-12cm, màu đỏ tươi; các lóng hình thùng phồng to thắt eo sâu trông giống cây Diêm-phù (Salicornia); phân nhánh đối xứng hoặc mọc vòng.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng triều dưới trên rạn san hô nơi sóng trong sạch.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Harvey 1853 : Nereis Bor. Amer. II : 76, pl. 19B; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 434."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH4_DATA)} figures for Batch 4...')
    for sp in BATCH4_DATA:
        p_num = sp['p']
        src_png = os.path.join(DPI300_DIR, f'page-{p_num:03d}.png')
        dst_png = os.path.join(IMAGE_DIR, sp['fig_name'])
        
        if not os.path.exists(src_png):
            print(f"Warning: source image {src_png} not found, skipping crop.")
            continue
            
        with Image.open(src_png) as img:
            w, h = img.size
            crop_box = sp['crop']
            x1 = max(0, min(crop_box[0], w - 10))
            y1 = max(0, min(crop_box[1], h - 10))
            x2 = max(x1 + 10, min(crop_box[2], w))
            y2 = max(y1 + 10, min(crop_box[3], h))
            cropped = img.crop((x1, y1, x2, y2))
            cropped.save(dst_png, 'PNG', optimize=True)
            print(f"  Cropped #{sp['idx']} -> {sp['fig_name']} ({cropped.size[0]}x{cropped.size[1]})")

def query_worms():
    print(f'Querying WoRMS API in chunks for {len(BATCH4_DATA)} species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH4_DATA), chunk_size):
        chunk = BATCH4_DATA[i:i+chunk_size]
        names = [sp['name'] for sp in chunk]
        names_query = '&'.join([f'scientificnames[]={n.replace(" ", "+")}' for n in names])
        url = f'https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?{names_query}&marine_only=false'
        req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results.extend(data)
        except Exception as e:
            print(f'WoRMS chunk error ({i}-{i+chunk_size}):', e)
            results.extend([None] * len(chunk))
        time.sleep(1.5)
        
    for sp, item in zip(BATCH4_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH4_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH4_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 4...')
    rows = []
    for sp in BATCH4_DATA:
        row = {
            "id": f"thucvat-tap2-species-{sp['idx']}",
            "collection_id": "thuc-vat-bien",
            "volume": 2,
            "species_index": sp['idx'],
            "vn_name": sp['vn'],
            "scientific_name": sp['name'],
            "authorship": sp['author'],
            "en_common_name": "",
            "vn_alternate_names": "",
            "tax_class_vn": "Lớp Tảo Đỏ",
            "tax_class_latin": "Rhodophyceae",
            "tax_order_vn": sp['ord_vn'],
            "tax_order_latin": sp['ord_lat'],
            "tax_family_vn": sp['fam_vn'],
            "tax_family_latin": sp['fam_lat'],
            "tax_genus_vn": sp['gen_vn'],
            "tax_genus_latin": sp['gen_lat'],
            "morphology_vn": sp['morphology'],
            "morphology_en": "",
            "photo_url": f"/images/species/thuc-vat-bien/v2/{sp['fig_name']}",
            "vn_distribution": sp['distribution'],
            "vn_specimen": sp['specimen'],
            "vn_status": sp['status'],
            "vn_literature": sp['literature'],
            "en_size": "",
            "en_distribution": "",
            "en_specimen": "",
            "en_status": "",
            "en_literature": "",
            "conservation_status": "unknown",
            "synonyms": "[]",
            "worms_id": sp.get('worms_id'),
            "worms_status": sp.get('worms_status', 'unverified'),
            "worms_accepted_name": sp.get('worms_accepted_name', sp['name'])
        }
        rows.append(row)

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch4.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 4 build completed successfully!')
