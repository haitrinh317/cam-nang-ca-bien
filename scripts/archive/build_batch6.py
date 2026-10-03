"""
build_batch6.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 82 loài Cát-tảo / Tảo nâu (Phaeophyceae - Đợt 6, loài 281-362)
cho Volume 2 (Rong biển Việt Nam - GS. Phạm Hoàng Hộ, 1969).
Hoàn tất 100% PHẦN III (Lớp Cát-tảo / Phaeophyceae, tổng cộng 82 loài)!
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

BATCH6_DATA = [
    {
        "idx": 281, "name": "Feldmannia breviarticulata", "author": "(J. Agardh) Kuckuck",
        "vn": "Rong Hải-tu lóng-ngắn", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 300, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_1.png",
        "morphology": "Tản tạo thành những búp sợi bện tròn xơ xác như búi dây thừng nhỏ cao 2-4cm, màu nâu vàng; các sợi chính uốn lượn chằng chịt, tế-bào ngắn hơn hoặc dài bằng đường kính; các nhánh phụ ngắn hình móc câu quấn chặt vào nhau; túi đa-bào-tử hình trứng hay bầu dục có cuống.",
        "distribution": "Toàn cầu ở vùng duyên hải nhiệt đới và cận nhiệt đới. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc bám trên đá dốc đứng nơi sóng vỗ cực mạnh ở tầng trung-duyên-hải thượng.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Vũng-Tàu.",
        "literature": "J. Agardh 1847 : Nya Alger : 7; Kuckuck 1954 : Ectocarp. : 179; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 398, fig. 14a-b."
    },
    {
        "idx": 282, "name": "Feldmannia irregularis", "author": "(Kützing) Hamel",
        "vn": "Rong Hải-tu bất-quy", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 301, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_3_2.png",
        "morphology": "Búi sợi nhỏ mềm mại cao 1-2cm, phân nhánh bất quy tắc; vùng sinh trưởng nằm ở gốc các nhánh; túi đa-bào-tử hình nón dài thon nhọn ở đỉnh.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên Sargassum và cỏ biển.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "Kützing 1845 : Phyc. Germ. : 234; Hamel 1939 : Phéophyc. Fr. : 67; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 398."
    },
    {
        "idx": 283, "name": "Feldmannia elachistaeformis", "author": "(Heydrich) P.H. Hô",
        "vn": "Rong Hải-tu sát", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 302, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_3.png",
        "morphology": "Tản phụ sinh hình chùm lông nhỏ cao 1-3mm; gốc chìm bán nội sinh trong mô tế bào chủ; sợi đứng đơn giản mang vùng sinh trưởng phân chia mạnh ở gốc; túi đa-bào-tử hình bầu dục mọc sát cuống.",
        "distribution": "Biển Đỏ, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên Padina và Sargassum.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Heydrich 1892 : Ber. Bot. Ges. X : 470; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 301, fig. 3.3."
    },
    {
        "idx": 284, "name": "Feldmannia filifera", "author": "Boergesen",
        "vn": "Rong Hải-tu dạng-chỉ", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 303, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_4.png",
        "morphology": "Sợi mọc đứng mảnh mai như sợi chỉ tơ, cao 5-10mm; túi đa-bào-tử hình trụ dài đỉnh có lông tơ.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Boergesen 1937 : South Ind. Mar. Alg. : 315; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 399."
    },
    {
        "idx": 285, "name": "Feldmannia enhali", "author": "Boergesen",
        "vn": "Rong Hải-tu cỏ-gương", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 304, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_5.png",
        "morphology": "Tản phụ sinh chuyên biệt tạo thành đốm lông màu nâu vàng trên lá cây Cỏ-gương (Enhalus acoroides); sợi đứng cao 2-5mm; túi đa-bào-tử hình thoi hẹp.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở bãi cỏ biển Nha-trang.",
        "status": "Phụ sinh đặc hiệu trên lá cỏ biển Enhalus.",
        "specimen": "Mẫu bãi biển Cầu-đá, Nha-trang.",
        "literature": "Boergesen 1937 : South Ind. Mar. Alg. : 317; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 399."
    },
    {
        "idx": 286, "name": "Feldmannia indica", "author": "(Sonder) Womersley & Bailey",
        "vn": "Rong Hải-tu Ấn-độ", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Hải-tu", "gen_lat": "Feldmannia",
        "p": 305, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_6.png",
        "morphology": "Búi tơ màu nâu vàng óng ánh cao 1-3cm; thân sợi phân nhánh nhiều lần; túi đa-bào-tử hình trụ tròn hai đầu tù, không cuống mọc một bên cành.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ven biển Việt Nam.",
        "status": "Phụ sinh trên Turbinaria, Sargassum và cọc gỗ ven biển.",
        "specimen": "Mẫu Nha-trang và Phan-thiết.",
        "literature": "Sonder 1854 : Zoll. Verz. : 3; Womersley & Bailey 1970 : Solomons : 288; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 399."
    },
    {
        "idx": 287, "name": "Giffordia mitchellae", "author": "(Harvey) Hamel",
        "vn": "Rong Hải-tu Mít-sơn", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Ghíp-pho", "gen_lat": "Giffordia",
        "p": 305, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_3_7.png",
        "morphology": "Tản hình bụi tơ mịn cao 2-5cm, màu nâu lục nhạt; túi đa-bào-tử hình trụ thon dài hai đầu tròn, mọc thành chuỗi dọc theo mặt trên của các nhánh phụ.",
        "distribution": "Toàn cầu ở vùng duyên hải ấm. Rất phổ biến tại Việt Nam.",
        "status": "Mọc trên đá, cọc bến cảng và phụ sinh trên rong lớn.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Harvey 1852 : Nereis Bor. Amer. I : 142; Hamel 1939 : Phéophyc. Fr. : 66; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 288, "name": "Pylaiella littoralis", "author": "(Linnaeus) Kjellman",
        "vn": "Rong Phì-lai duyên-hải", "fam_vn": "Họ Hải-tu", "fam_lat": "Acinetosporaceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Phì-lai", "gen_lat": "Pylaiella",
        "p": 307, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_8.png",
        "morphology": "Tản sợi nâu mềm cao 2-6cm; phân nhánh đối xứng hoặc so le; đặc trưng nổi bật là các túi đa-bào-tử và đơn-bào-tử hình thành ngay trong thân sợi (xen giữa chuỗi tế bào dinh dưỡng).",
        "distribution": "Toàn cầu. Gặp ở vùng duyên hải miền Trung Việt Nam.",
        "status": "Mọc trên đá và phụ sinh trên rong Fucus, Sargassum.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Linnaeus 1753 : Sp. Pl. : 1165; Kjellman 1872 : Skand. Ectocarp. : 99; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 289, "name": "Myrionema strangulans", "author": "Greville",
        "vn": "Rong Thiên-mao thắt", "fam_vn": "Họ Thiên-mao", "fam_lat": "Myrionemataceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Thiên-mao", "gen_lat": "Myrionema",
        "p": 309, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_9.png",
        "morphology": "Tản vi thể hình đĩa tròn nhỏ đường kính 1-3mm, màu nâu; cấu tạo gồm một tầng đáy bò sát tỏa tròn và các sợi đứng rất ngắn mang túi bào tử và sợi lông có vỏ.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Phụ sinh phổ biến trên màng lá rong Diếp biển (Ulva) và Enteromorpha.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Greville 1827 : Scott. Crypt. Fl. : pl. 300; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 290, "name": "Chilionema ocellata", "author": "(Kützing) Kuckuck",
        "vn": "Rong Thần-mục có-đốm", "fam_vn": "Họ Thiên-mao", "fam_lat": "Myrionemataceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Thần-mục", "gen_lat": "Chilionema",
        "p": 310, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_3_10.png",
        "morphology": "Tản đĩa nhỏ màu nâu đậm; các sợi đứng phân nhánh ở gốc mang túi đơn bào tử hình chùy to.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên rong khác.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1843 : Phyc. Gen. : 329; Kuckuck 1953 : Ectocarp. : 325."
    },
    {
        "idx": 291, "name": "Petroderma vietnamense", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Thạch-bì việtnam", "fam_vn": "Họ Thạch-bì", "fam_lat": "Petrodermataceae",
        "ord_vn": "Bộ Hải-tu", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Thạch-bì", "gen_lat": "Petroderma",
        "p": 310, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_3_11.png",
        "morphology": "Tản dạng vỏ màng mỏng màu nâu đen bám chặt trên đá như một lớp sơn bóng cứng; phẫu thức ngang gồm các chuỗi tế-bào đứng sít sao; túi đơn bào tử sinh ra từ tế bào ngọn. Loài mới phát hiện cho khoa học.",
        "distribution": "Đặc hữu vùng duyên hải Việt Nam (Hòn-chồng, Nha-trang).",
        "status": "Mọc trên đá vùng trung-duyên-hải thượng chịu sóng to và nắng gắt.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 310, fig. 3.11."
    },
    {
        "idx": 292, "name": "Sphacelaria novaehollandiae", "author": "Sonder",
        "vn": "Rong A-chi Tân-hòa-lan", "fam_vn": "Họ A-chi", "fam_lat": "Sphacelariaceae",
        "ord_vn": "Bộ A-chi", "ord_lat": "Sphacelariales", "gen_vn": "Chi Rong A-chi", "gen_lat": "Sphacelaria",
        "p": 312, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_12.png",
        "morphology": "Búi tơ nâu cứng cao 1-2cm; thân sợi do nhiều hàng tế bào xếp dọc với 1 tế-bào ngọn to màu đen; đặc trưng nhờ mầm cầu-hành sinh sản (propagules) hình nêm rộng hai sừng cùn ngắn.",
        "distribution": "Úc, Ấn-độ-Tây Thái-bình-dương. Phổ biến ven biển Việt Nam.",
        "status": "Mọc trên đá và rạn san hô chết vùng triều giữa.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Sonder 1845 : Bot. Zeit. : 52; Sauvageau 1901 : Sphacelaria : 137; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 293, "name": "Sphacelaria tribuloides", "author": "Meneghini",
        "vn": "Rong A-chi ú", "fam_vn": "Họ A-chi", "fam_lat": "Sphacelariaceae",
        "ord_vn": "Bộ A-chi", "ord_lat": "Sphacelariales", "gen_vn": "Chi Rong A-chi", "gen_lat": "Sphacelaria",
        "p": 313, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_13.png",
        "morphology": "Búi tơ cao 5-15mm, màu nâu sẫm; mầm cầu-hành hình tam giác ú mập với 3 sừng tù ngắn xòe ra như chiếc quả tật lê (Tribulus).",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc bám trên đá, vỏ sò và rạn san hô tầng triều giữa.",
        "specimen": "Mẫu bãi đá Nha-trang, Qui-nhơn.",
        "literature": "Meneghini 1840 : Lettera Corinaldi : 2; Sauvageau 1901 : Sphacelaria : 123; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400, fig. 14i-j."
    },
    {
        "idx": 294, "name": "Sphacelaria furcigera", "author": "Kützing",
        "vn": "Rong A-chi chẻ", "fam_vn": "Họ A-chi", "fam_lat": "Sphacelariaceae",
        "ord_vn": "Bộ A-chi", "ord_lat": "Sphacelariales", "gen_vn": "Chi Rong A-chi", "gen_lat": "Sphacelaria",
        "p": 314, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_14.png",
        "morphology": "Búi sợi mảnh cao 5-10mm; mầm cầu-hành chẻ đôi hai sừng hình chữ V thon dài như chiếc chạc chĩa (furcate).",
        "distribution": "Khắp thế giới. Rất phong phú ở vùng duyên hải Việt Nam.",
        "status": "Phụ sinh phổ biến trên Sargassum, Turbinaria và san hô chết.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Vũng-Tàu.",
        "literature": "Kützing 1855 : Tab. Phyc. V : 27, pl. 90; Sauvageau 1901 : Sphacelaria : 145; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400, fig. 14h."
    },
    {
        "idx": 295, "name": "Sphacelaria ceylanica", "author": "Sauvageau",
        "vn": "Rong A-chi Tích-lan", "fam_vn": "Họ A-chi", "fam_lat": "Sphacelariaceae",
        "ord_vn": "Bộ A-chi", "ord_lat": "Sphacelariales", "gen_vn": "Chi Rong A-chi", "gen_lat": "Sphacelaria",
        "p": 315, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_15.png",
        "morphology": "Tản cao 3-8mm; mầm cầu-hành hình thoi dài với cuống đơn và 3 nhánh sừng thon nhỏ ở đỉnh.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên vỏ ốc và đá vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Sauvageau 1901 : Sphacelaria : 144; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 296, "name": "Mesospora schmidtii", "author": "Weber van Bosse",
        "vn": "Rong Trung-bào Xơ-mít", "fam_vn": "Họ Cái-nhung", "fam_lat": "Ralfsiaceae",
        "ord_vn": "Bộ Cái-nhung", "ord_lat": "Ralfsiales", "gen_vn": "Chi Rong Trung-bào", "gen_lat": "Mesospora",
        "p": 316, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_16.png",
        "morphology": "Tản dạng vỏ nhung mỏng trơn nhớt màu nâu gạch bám trên đá; phẫu thức ngang gồm tầng hạ tản tỏa tròn và các sợi đứng tự do không dính sát nhau; túi đơn bào tử mọc ở giữa sợi đứng.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Mọc trên đá vùng triều giữa nơi sóng vỗ.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Weber van Bosse 1911 : Ann. Jard. Bot. Buitenzorg IX : 27; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 297, "name": "Ralfsia expansa", "author": "(J. Agardh) J. Agardh",
        "vn": "Rong Cái-nhung nở", "fam_vn": "Họ Cái-nhung", "fam_lat": "Ralfsiaceae",
        "ord_vn": "Bộ Cái-nhung", "ord_lat": "Ralfsiales", "gen_vn": "Chi Rong Cái-nhung", "gen_lat": "Ralfsia",
        "p": 317, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_17.png",
        "morphology": "Tản dạng vỏ cứng chắc như đá màu nâu đen hay lục sẫm bám cực chặt vào mặt đá phẳng; bề mặt có các vòng sinh trưởng đồng tâm; phẫu thức ngang gồm các hàng tế-bào xếp nghiêng cong lên trên; túi bào tử sinh ra trong các nốt lồi (sori).",
        "distribution": "Toàn cầu ở vùng biển nhiệt đới. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Phủ kín các gờ đá tầng trung-duyên-hải thượng nơi sóng đập liên tục.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Cà-ná, Vũng-Tàu.",
        "literature": "J. Agardh 1847 : Nya Alger : 7; J. Agardh 1848 : Sp. Alg. I : 63; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 400."
    },
    {
        "idx": 298, "name": "Dictyota beccariana", "author": "Zanardini",
        "vn": "Rong Võng Béc-ca-ri", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 320, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_18.png",
        "morphology": "Tản phiến dẹp mỏng màu nâu vàng, cao 8-15cm; phân nhánh lưỡng phân đều đặn rẽ góc nhọn; mép phiến phủ đầy các răng gai nhọn nhỏ; phẫu thức gồm 1 lớp tế bào tủy lớn hình chữ nhật bao quanh bởi 1 lớp tế bào vỏ nhỏ chứa diệp lục.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ở miền Trung Việt Nam.",
        "status": "Mọc trên rạn san hô và đá ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Zanardini 1872 : Phyc. Ind. : 132; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 299, "name": "Dictyota patens", "author": "J. Agardh",
        "vn": "Rong Võng xòe", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 321, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_19.png",
        "morphology": "Tản phân nhánh lưỡng phân rẽ góc rộng xòe ngang, các nhánh dẹp rộng 2-4mm, mép nguyên không có răng; đầu nhánh tù tròn.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc kẽ đá san hô vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1882 : Till Alg. Syst. II : 93; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 300, "name": "Dictyota dichotoma", "author": "(Hudson) J.V. Lamouroux",
        "vn": "Rong Võng chẻ-đôi", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 322, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_20.png",
        "morphology": "Tản mọc thành bụi tròn màu nâu vàng ánh xanh lấp lánh dưới nước, cao 5-15cm; chia nhánh lưỡng phân hoàn toàn đều đặn nhiều lần; nhánh rộng 2-5mm, đầu nhánh chẻ đôi đối xứng; ổ tứ-bào-tử rải rác khắp mặt phiến.",
        "distribution": "Toàn cầu ở các vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Loài điển hình của bộ Võng-tảo, mọc nhiều ở vùng triều thấp và đầm nước mặn.",
        "specimen": "Mẫu Nha-trang, Vũng-Tàu, Phú-quốc.",
        "literature": "Hudson 1762 : Fl. Angl. : 476; Lamouroux 1809 : Desv. J. Bot. II : 42; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 301, "name": "Dictyota indica", "author": "Sonder ex Kützing",
        "vn": "Rong Võng Ấn-độ", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 323, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_21.png",
        "morphology": "Tản dài 10-20cm, màu nâu sáng mềm mại; nhánh hình dải hẹp rộng 1-2mm, lóng dài; chia nhánh lưỡng phân góc nhọn.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải nơi nước êm.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Kützing 1859 : Tab. Phyc. IX : pl. 17; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 302, "name": "Dictyota bartayresiana", "author": "Lamouroux",
        "vn": "Rong Võng Bác-tay-rê", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 324, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_22.png",
        "morphology": "Tản giòn dễ gãy, tạo bụi tròn màu vàng lục, cao 5-10cm; phân nhánh lưỡng phân đều; đầu nhánh tù tròn; mép nhánh có rễ giả dính vào nhau.",
        "distribution": "Biển nhiệt đới toàn cầu. Phổ biến tại Việt Nam.",
        "status": "Mọc trên rạn san hô nông tầng triều thấp.",
        "specimen": "Mẫu Hòn-mun Nha-trang.",
        "literature": "Lamouroux 1809 : Desv. J. Bot. II : 43; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 303, "name": "Dictyota divaricata", "author": "Lamouroux",
        "vn": "Rong Võng giẽ", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 325, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_23.png",
        "morphology": "Tản tạo thảm rối dày đan bện, cao 3-6cm, màu nâu ánh xanh ngũ sắc rất sáng; các nhánh chia đôi rẽ góc rất rộng (90-120°); nhánh ngọn thon nhỏ nhọn hoắt.",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phong phú ở các rạn san hô Việt Nam.",
        "status": "Phủ kín mặt rạn san hô chết và đá vùng triều.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Lamouroux 1809 : Desv. J. Bot. II : 43; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401, fig. 18b."
    },
    {
        "idx": 304, "name": "Dictyota ceylanica", "author": "Kützing",
        "vn": "Rong Võng Tích-lan", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 326, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_24.png",
        "morphology": "Tản nhỏ mảnh mai cao 2-5cm; thân dẹp hẹp rộng dưới 1mm; các nhánh tiếp xúc tự nối liền với nhau (anastomosing) tạo thành mạng lưới dẹt.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô ngầm.",
        "specimen": "Mẫu đảo Hòn-tre Nha-trang.",
        "literature": "Kützing 1859 : Tab. Phyc. IX : 11, pl. 25; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 305, "name": "Dictyota friabilis", "author": "Setchell",
        "vn": "Rong Võng bở", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 327, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_25.png",
        "morphology": "Tản bò xếp lớp chồng lên nhau tạo thảm mỏng dính chặt vào đá nhờ nhiều rễ giả đa bào; chất giòn bở cực kỳ dễ gãy vụn khi gỡ; màu xanh lục ánh kim quang.",
        "distribution": "Tahiti, Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Bám trên mặt san hô chết tầng triều dưới.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Setchell 1926 : Tahitian Alg. : 91, pl. 13; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401, fig. 16a-b."
    },
    {
        "idx": 306, "name": "Dictyota submaritima", "author": "Tanaka & Pham-hoang Ho nov. sp.",
        "vn": "Rong Võng cận-hải", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-tảo", "gen_lat": "Dictyota",
        "p": 328, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_26.png",
        "morphology": "Tản dẹp bò lan rồi dựng đứng cao 3-6cm, màu nâu đậm; đặc sắc ở các ổ tứ-bào-tử-phòng chỉ tập trung thành 1-2 hàng dọc sát mép bìa mặt dưới của tản. Loài mới cho khoa học.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Tanaka & Phạm-hoàng Hộ 1962 : Notes Mar. Alg. Vietn. I : 30, fig. 5; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 326, fig. 3.26."
    },
    {
        "idx": 307, "name": "Spatoglossum vietnamense", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đại-võng việtnam", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Đại-võng", "gen_lat": "Spatoglossum",
        "p": 329, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_27.png",
        "morphology": "Tản phiến dẹp lớn cao 10-25cm, dày 400-500µ, chất dai như da, màu nâu sẫm; phân nhánh ngón tay hoặc xẻ thùy không đều; phẫu thức ngang gồm 2-4 lớp tế bào tủy lớn không đều; túi bào tử rải rác chìm trong vỏ. Loài mới phát hiện tại Nha Trang.",
        "distribution": "Đặc hữu bờ biển Việt Nam (Nha-trang).",
        "status": "Mọc ở tầng hạ-duyên-hải sâu 2-6m trên đá rạn san hô.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 327, fig. 3.27."
    },
    {
        "idx": 308, "name": "Padina commersonii", "author": "Bory de Saint-Vincent",
        "vn": "Rong Quạt Côm-méc-xông", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Quạt", "gen_lat": "Padina",
        "p": 331, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_28.png",
        "morphology": "Tản hình quạt tròn xòe rộng, cao 5-12cm, tẩm vôi mỏng màu trắng phấn ở mặt lưng, mặt bụng màu nâu vàng; mép phiến cuốn tròn vào trong; có các vòng lông tơ và nốt túi bào tử xếp thành hàng đồng tâm đều đặn; cấu tạo gồm 2 lớp tế bào suốt chiều dài phiến.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Loài rong quạt phong phú nhất trên các bãi rạn san hô nông và thềm đá vùng triều.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Côn-đảo, Phú-quốc.",
        "literature": "Bory 1828 : Voy. Coquille Bot. : 144, pl. 21; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 309, "name": "Padina boryana", "author": "Thivy",
        "vn": "Rong Quạt Bô-ri", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Quạt", "gen_lat": "Padina",
        "p": 331, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_29.png",
        "morphology": "Tản quạt xòe rộng, tẩm vôi vừa phải; hàng túi bào tử mọc ngay sát phía trên của các đai lông tơ đồng tâm; phiến gồm 2 lớp tế bào.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Phổ biến tại Việt Nam.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Thivy in Taylor 1966 : Pacific Sci. 20 : 355; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 310, "name": "Padina tetrastromatica", "author": "Hauck",
        "vn": "Rong Quạt bốn-lớp", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Quạt", "gen_lat": "Padina",
        "p": 332, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_30.png",
        "morphology": "Tản quạt to dày chắc chắn, cao 8-15cm; đặc trưng bởi cấu trúc giải phẫu gồm 4 lớp tế-bào ở phần giữa và gốc tản (chỉ có 2 lớp ở sát mép ngọn); túi bào tử có màng bao (indusium) che chở.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Khắp bờ biển miền Trung và Nam Việt Nam.",
        "status": "Rất giàu alginate và mannitol; mọc thành dải lớn ở vùng triều thấp.",
        "specimen": "Mẫu Nha-trang, Vũng-Tàu, Hà-tiên.",
        "literature": "Hauck 1887 : Hedwigia XXVI : 43; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 311, "name": "Padina australis", "author": "Hauck",
        "vn": "Rong Quạt nam", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Quạt", "gen_lat": "Padina",
        "p": 333, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_31.png",
        "morphology": "Tản quạt xẻ thùy sâu, cao 10-20cm, màu trắng phấn dày ở cả hai mặt; phẫu thức gồm 2 lớp tế bào ở toàn bộ phiến, tế bào lớp trên to gấp đôi lớp dưới; túi bào tử trần không có màng bao.",
        "distribution": "Úc, Thái-bình-dương nhiệt đới, Biển Đông. Rất phong phú tại Việt Nam.",
        "status": "Nguồn sinh khối alginate dồi dào, mọc ở tầng hạ-duyên-hải sâu đến 5-6m.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Hauck 1887 : Hedwigia XXVI : 44; Yamada 1931 : Mar. Alg. Mutsu Bay : 70; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 401."
    },
    {
        "idx": 312, "name": "Dictyopteris delicatula", "author": "Lamouroux",
        "vn": "Rong Võng-dực thanh", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-dực", "gen_lat": "Dictyopteris",
        "p": 335, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_32.png",
        "morphology": "Tản hình dải dẹp màu nâu vàng tươi, cao 4-10cm, rộng 1-2mm; có một đường gân giữa nổi rõ chạy dọc tản và hai đường gân phụ sát mép phiến; phân nhánh lưỡng phân.",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc bò chằng chịt bám trên đá và san hô ở tầng trung-duyên-hải hạ.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo.",
        "literature": "Lamouroux 1809 : J. de Bot. II : 332, pl. 6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 402."
    },
    {
        "idx": 313, "name": "Dictyopteris membranacea", "author": "(Stackhouse) Batters",
        "vn": "Rong Võng-dực màng", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-dực", "gen_lat": "Dictyopteris",
        "p": 336, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_33.png",
        "morphology": "Tản phiến màng to lớn, cao 10-25cm, rộng 4-8mm; gân giữa đơn độc rất đậm và lồi cao; mép phiến mỏng nguyên hoặc lượn sóng; có mùi hương biển nồng nàn đặc trưng.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng rạn san hô dưới triều sâu 2-8m nơi nước sạch.",
        "specimen": "Mẫu lặn vịnh Nha-trang.",
        "literature": "Stackhouse 1795 : Nereis Brit. : 13; Batters 1902 : Cat. Brit. Mar. Alg. : 54; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 402."
    },
    {
        "idx": 314, "name": "Dictyopteris repens", "author": "(Okamura) Boergesen",
        "vn": "Rong Võng-dực bò", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Võng-dực", "gen_lat": "Dictyopteris",
        "p": 337, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_34.png",
        "morphology": "Tản nhỏ li ti bò lan trên san hô, dài 1-3cm, rộng 1mm; gân giữa mờ; bám nhờ các chùm rễ giả mọc từ mặt dưới gân lá.",
        "distribution": "Nhật-bản, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc phụ sinh trên chân các khóm san hô chết.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Okamura 1916 : List Mar. Alg. Caroline Isl. : 8; Boergesen 1924 : Kew Bull. : 271; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 403."
    },
    {
        "idx": 315, "name": "Zonaria stipitata", "author": "Tanaka & Nozawa",
        "vn": "Rong Đới-tảo có-cuống", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Đới-tảo", "gen_lat": "Zonaria",
        "p": 338, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_3_35.png",
        "morphology": "Tản phiến dẹp hình quạt xẻ thùy sâu, cao 5-10cm, có cuống hình trụ tròn rõ rệt phủ đầy lông mịn; phiến có các dải màu đồng tâm; phẫu thức ngang gồm 4-6 lớp tế bào.",
        "distribution": "Biển Đông (Việt Nam, Nhật-bản).",
        "status": "Mọc ở rạn san hô sâu 12-45m ngoài khơi đảo Hòn-thu (Khánh-hòa).",
        "specimen": "Mẫu nạo vét ở độ sâu ngoài khơi Khánh-hòa.",
        "literature": "Tanaka & Nozawa 1962 : Gen. Padina and Zonaria : 183, fig. 4; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 336."
    },
    {
        "idx": 316, "name": "Lobophora variegata", "author": "(Lamouroux) Womersley",
        "vn": "Rong Thùy-đài loang-lổ", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Thùy-đài", "gen_lat": "Lobophora",
        "p": 338, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_3_36.png",
        "morphology": "Tản hình quạt mỏng dẹp màu nâu cam loang lổ, cao 4-10cm; mọc bò xếp lớp như nấm hoặc đứng xòe hình quạt; phẫu thức ngang đặc trưng gồm đúng 1 lớp tế bào tủy lớn ở giữa và mỗi bên có 2 lớp tế bào vỏ nhỏ đối xứng đều.",
        "distribution": "Khắp các biển nhiệt đới ấm toàn cầu. Cực kỳ phong phú ở các rạn san hô Việt Nam.",
        "status": "Loài chiếm ưu thế trên rạn san hô ngầm, cạnh tranh không gian sống mạnh mẽ với san hô cứng.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Lamouroux 1809 : Desv. J. Bot. II : 40; Womersley 1967 : Austral. J. Bot. 15 : 221; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 403, fig. 18c."
    },
    {
        "idx": 317, "name": "Chlanidophora repens", "author": "Okamura",
        "vn": "Rong Y-đài bò", "fam_vn": "Họ Võng-tảo", "fam_lat": "Dictyotaceae",
        "ord_vn": "Bộ Võng-tảo", "ord_lat": "Dictyotales", "gen_vn": "Chi Rong Y-đài", "gen_lat": "Chlanidophora",
        "p": 340, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_37.png",
        "morphology": "Tản phiến mỏng màu nâu vàng, mép tròn cuốn; phẫu thức ngang gồm 2 lớp tế bào có kích thước bằng nhau; túi bào tử có lớp màng áo che chở.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Okamura 1899 : Bot. Mag. Tokyo XIII : 11, pl. 1; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 403."
    },
    {
        "idx": 318, "name": "Hydroclathrus clathratus", "author": "(C. Agardh) M. Howe",
        "vn": "Rong Ruột-heo", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Ruột-heo", "gen_lat": "Hydroclathrus",
        "p": 341, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_38.png",
        "morphology": "Tản sụn mềm xốp màu nâu vàng hay cam gạch, tạo thành khối đệm tròn cao 5-20cm; cấu tạo tản thủng vô số lỗ tròn lớn nhỏ đan bện như một tấm lưới mạng hoặc bọt biển ruột heo thủng lỗ chỗ; mọc bám trên san hô và đá.",
        "distribution": "Toàn cầu ở các vùng biển nhiệt đới ấm. Cực kỳ phong phú ở toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Rong thực phẩm ăn sống giải nhiệt rất ngon giòn; xuất hiện với sinh khối khổng lồ vào mùa xuân hè trên các rạn san hô nông.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 412; Howe 1920 : Bahama Flora : 590; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 403, fig. 18b."
    },
    {
        "idx": 319, "name": "Colpomenia sinuosa", "author": "(Mertens ex Roth) Derbès & Solier",
        "vn": "Rong Bao-tử lượn-sóng", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Bao-tử", "gen_lat": "Colpomenia",
        "p": 341, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_39.png",
        "morphology": "Tản hình bóng cầu rỗng mọng nước, đường kính 3-10cm (đôi khi đến 15cm), màu vàng nâu hay lục đồng; bề mặt lồi lõm gấp nếp uốn lượn; vách màng mỏng giòn bóp vỡ kêu lép bép; ổ bào tử rải rác trên mặt ngoài.",
        "distribution": "Khắp các biển nhiệt đới và ôn đới ấm toàn cầu. Cực kỳ phong phú tại Việt Nam.",
        "status": "Xuất hiện rộ vào mùa đông và xuân, phủ kín các thềm đá và rạn san hô vùng triều.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu.",
        "literature": "Roth 1806 : Catal. Bot. III : 327; Derbès & Solier 1851 : Suppl. Compt. Rend. : 95; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 402."
    },
    {
        "idx": 320, "name": "Colpomenia bullosa", "author": "(Saunders) Yamada",
        "vn": "Rong Bao-tử phồng", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Bao-tử", "gen_lat": "Colpomenia",
        "p": 343, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_40.png",
        "morphology": "Tản hình túi ngón tay dài thon hẹp ở gốc và phồng to ở ngọn, rỗng ruột chứa khí, cao 5-10cm, mọc thành cụm nhiều túi; màu nâu vàng.",
        "distribution": "Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Saunders 1898 : Proc. Calif. Acad. Sci. I : 163; Yamada 1948 : Icon. Mar. Alg. Japan : 110."
    },
    {
        "idx": 321, "name": "Rosenvingea intricata", "author": "(J. Agardh) Boergesen",
        "vn": "Rong Đỗ-quyên rối", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Đỗ-quyên", "gen_lat": "Rosenvingea",
        "p": 344, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_41.png",
        "morphology": "Tản mọc thành búi đệm xốp mềm màu nâu vàng ánh xanh, cao 5-12cm; thân hình ống rỗng đường kính 1-3mm, phân nhánh chằng chịt đan cài vào nhau; vách màng mỏng do vài lớp tế bào.",
        "distribution": "Vùng biển nhiệt đới toàn cầu. Phổ biến ven biển miền Trung và Nam Việt Nam.",
        "status": "Mọc trên đá và san hô ở các vũng nước triều êm sóng.",
        "specimen": "Mẫu Nha-trang, Vũng-Tàu, Phú-quốc.",
        "literature": "J. Agardh 1847 : Nya Alger : 7; Boergesen 1914 : Mar. Alg. Dan. W. Ind. I : 26; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 404, fig. 19a-b."
    },
    {
        "idx": 322, "name": "Rosenvingea orientalis", "author": "(J. Agardh) Boergesen",
        "vn": "Rong Đỗ-quyên đông-phương", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Đỗ-quyên", "gen_lat": "Rosenvingea",
        "p": 345, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_42.png",
        "morphology": "Tản đứng cao 10-20cm, các nhánh ống rỗng to đường kính 3-5mm, phân nhánh so le vươn dài đứng thẳng; đầu nhánh thon nhỏ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở tầng hạ-duyên-hải trên cát sỏi.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 68; Boergesen 1914 : Mar. Alg. Dan. W. Ind. I : 26."
    },
    {
        "idx": 323, "name": "Rosenvingea nhatrangensis", "author": "Dawson",
        "vn": "Rong Đỗ-quyên Nha-trang", "fam_vn": "Họ Đốm-tảo", "fam_lat": "Scytosiphonaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Đỗ-quyên", "gen_lat": "Rosenvingea",
        "p": 346, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_43.png",
        "morphology": "Tản ống nhỏ mảnh khảnh cao 3-6cm, chia nhánh chữ V nhiều lần; các ổ sinh sản hình đĩa tròn nhỏ rải rác khắp thân ống. Loài đặt tên theo địa danh Nha Trang.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Khánh-hòa, Việt Nam).",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Holotype thu tại Cầu-đá, Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 404, fig. 19c-d; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 344."
    },
    {
        "idx": 324, "name": "Chnoospora minima", "author": "(Hering) Papenfuss",
        "vn": "Rong Mao-tử nhỏ", "fam_vn": "Họ Mao-tử", "fam_lat": "Chnoosporaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Mao-tử", "gen_lat": "Chnoospora",
        "p": 348, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_44.png",
        "morphology": "Tản sụn đặc dai cứng như cao su, cao 5-15cm, màu nâu sẫm hay đen; thân dẹp chia nhánh lưỡng phân dày đặc tạo bụi hình quạt tròn; bề mặt phủ đầy các chùm lông tơ nhỏ li ti xuất phát từ các lỗ huyệt lõm; chịu sóng đập dữ dội.",
        "distribution": "Toàn cầu ở vùng biển nhiệt đới ấm. Cực kỳ phong phú ở miền Trung Việt Nam.",
        "status": "Tạo thành một đai sinh thái ưu thế nổi bật ở tầng trung-duyên-hải thượng trên các vách đá sóng gió dữ dội nhất.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, mũi Cà-ná, Qui-nhơn.",
        "literature": "Hering 1841 : Ann. Mag. Nat. Hist. VIII : 180; Papenfuss 1956 : J. S. Afr. Bot. 22 : 69; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 405, fig. 20b."
    },
    {
        "idx": 325, "name": "Chnoospora implexa", "author": "J. Agardh",
        "vn": "Rong Mao-tử rối", "fam_vn": "Họ Mao-tử", "fam_lat": "Chnoosporaceae",
        "ord_vn": "Bộ Đốm-tảo", "ord_lat": "Ectocarpales", "gen_vn": "Chi Rong Mao-tử", "gen_lat": "Chnoospora",
        "p": 349, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_46.png",
        "morphology": "Tản tạo thành búi xốp mềm chằng chịt uốn lượn, cao 10-20cm, màu nâu vàng lục; nhánh hình trụ tròn hoặc hơi dẹp, chia nhánh đôi không đều rẽ góc rộng.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Thái-bình-dương. Việt Nam: Nam Trung bộ.",
        "status": "Mọc trên rạn san hô tầng triều dưới nơi nước sạch.",
        "specimen": "Mẫu đảo Hòn-tre Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 172; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 405, fig. 20a."
    },
    {
        "idx": 326, "name": "Hormophysa articulata", "author": "(Forsskål) Zanardini",
        "vn": "Rong Cán-nang có-đốt", "fam_vn": "Họ Cán-nang", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Cán-nang", "gen_lat": "Hormophysa",
        "p": 350, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_47.png",
        "morphology": "Tản sụn dai cứng màu nâu vàng lục, cao 20-50cm; thân có 3 cánh thịt lượn sóng chạy dọc tạo hình tam giác; mép cánh có răng cưa tù; các lóng phồng to ở giữa tạo thành các túi phao khí hình bầu dục nằm ngay bên trong trục tản.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở miền Trung và hải đảo Việt Nam.",
        "status": "Loài đặc sắc của rạn san hô, giàu alginate; mọc ở tầng hạ-duyên-hải sâu 1-4m.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 192; Zanardini 1860 : Pl. Mar. Rubr. : 244; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406."
    },
    {
        "idx": 327, "name": "Turbinaria ornata", "author": "(Turner) J. Agardh",
        "vn": "Rong Chùy-diệp đẹp", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Chùy-diệp", "gen_lat": "Turbinaria",
        "p": 353, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_49.png",
        "morphology": "Tản sụn cực kỳ dày cứng chắc như da thuộc hoặc gỗ sừng, cao 10-30cm, màu nâu sẫm hay vàng đồng; trục đứng mang các lá hình nón ngược hay hình chùy tam giác cụt đầu rất lạ mắt; mặt ngọn phẳng lõm giữa mang 1 túi phao khí hình cầu; mép ngọn viền 1 hàng răng gai nhọn cứng cáp và thường có thêm 1 vòng gai ở tâm.",
        "distribution": "Khắp các rạn san hô nhiệt đới Ấn-độ-Tây Thái-bình-dương. Cực kỳ phong phú tại toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Loài chủ đạo thống soái trên các bãi rạn san hô nông; nguyên liệu chiết xuất sodium alginate chất lượng cao và các hợp chất chống oxy hóa, kháng khuẩn.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Hoàng-sa, Trường-sa, Côn-đảo, Phú-quốc.",
        "literature": "Turner 1808 : Fuci I : 50, pl. 24; J. Agardh 1848 : Sp. Alg. I : 266; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 405, fig. 21."
    },
    {
        "idx": 328, "name": "Turbinaria gracilis", "author": "Sonder",
        "vn": "Rong Chùy-diệp mảnh", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Chùy-diệp", "gen_lat": "Turbinaria",
        "p": 355, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_52.png",
        "morphology": "Tản cao 15-25cm, thân mảnh dẻo hơn T. ornata; các lá hình chùy có cuống dài thanh mảnh, mép lá có răng cưa nhỏ thưa.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá san hô ở vùng nước sâu 2-5m.",
        "specimen": "Mẫu đảo Hòn-tre Nha-trang.",
        "literature": "Sonder 1845 : Bot. Zeit. : 52; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406."
    },
    {
        "idx": 329, "name": "Turbinaria conoides", "author": "(J. Agardh) Kützing",
        "vn": "Rong Chùy-diệp chùy", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Chùy-diệp", "gen_lat": "Turbinaria",
        "p": 356, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_3_53.png",
        "morphology": "Tản cao 15-40cm, màu nâu vàng; lá hình nón dài thon, mặt ngọn tròn phồng lồi mang phao khí to ở tâm; mép lá có răng cưa sắc bén không đều.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp vùng biển miền Trung và hải đảo Việt Nam.",
        "status": "Chiết alginate công nghiệp; mọc thành bụi lớn trên rạn san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu vịnh Nha-trang, Qui-nhơn, Côn-đảo.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 267; Kützing 1860 : Tab. Phyc. X : 24, pl. 66; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 405."
    },
    {
        "idx": 330, "name": "Turbinaria decurrens", "author": "Bory de Saint-Vincent",
        "vn": "Rong Chùy-diệp xuôi", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Chùy-diệp", "gen_lat": "Turbinaria",
        "p": 356, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_3_54.png",
        "morphology": "Tản hình cột tháp cao 10-25cm; lá hình tam giác đều có 3 cánh sắc cạnh chạy xuôi dọc theo cuống lá; mặt ngọn phẳng hình tam giác viền gờ không có gai; rất đặc trưng.",
        "distribution": "Biển Đỏ, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên rạn san hô kín sóng ở độ sâu 1-3m.",
        "specimen": "Mẫu rạn san hô đảo Hòn-mun Nha-trang.",
        "literature": "Bory 1828 : Voy. Coquille Bot. : 119; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406, fig. 21f."
    },
    {
        "idx": 331, "name": "Sargassum tortile", "author": "(C. Agardh) C. Agardh",
        "vn": "Rong Lá-mơ quấn", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 360, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_55.png",
        "morphology": "Tản to lớn dài 50-100cm; trục chính xoắn vặn uốn lượn; lá dày hình dải hẹp, mép nguyên hoặc có răng nhỏ; phao khí hình bầu dục có cánh hẹp.",
        "distribution": "Nhật-bản, Triều-tiên, Biển Đông. Gặp ở miền Bắc và Trung Việt Nam.",
        "status": "Khai thác làm phân bón hữu cơ, chiết alginate và chế biến thức ăn chăn nuôi.",
        "specimen": "Mẫu thu tại đảo Cát-bà và Quy-nhơn.",
        "literature": "C. Agardh 1820 : Sp. Alg. : 15; J. Agardh 1848 : Sp. Alg. I : 339."
    },
    {
        "idx": 332, "name": "Sargassum horneri", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ Hóc-nơ", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 361, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_56.png",
        "morphology": "Tản khổng lồ dài 1-3m; lá xẻ thùy sâu hình lông chim đều đặn như chiếc lược; phao khí hình trụ thon dài có chóp nhọn như hạt thóc; đế sinh sản hình trụ dài.",
        "distribution": "Nhật-bản, Triều-tiên, Trung-quốc, Việt Nam (Quảng-ninh, Hải-phòng, Đà-nẵng).",
        "status": "Rong mùa đông xuân, tạo rừng rong ngầm khổng lồ là bãi đẻ của cá mực; ăn được và chiết fucoidan.",
        "specimen": "Mẫu thu thập tại vịnh Hạ-long và Cát-bà.",
        "literature": "Turner 1808 : Fuci I : 34, pl. 17; C. Agardh 1820 : Sp. Alg. : 38; Yamada 1942 : Sargassum Japan : 559."
    },
    {
        "idx": 333, "name": "Sargassum hemiphyllum", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ bán-diệp", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 363, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_57.png",
        "morphology": "Tản cao 30-60cm; lá có hình phản tay hoặc nửa hình tam giác bất đối xứng (bán diệp) rất đặc trưng; mép trên có răng cưa, mép dưới thẳng trơn trơ trụi.",
        "distribution": "Nhật-bản, Trung-quốc, Việt Nam (Quảng-ninh đến Bình-định).",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Qui-nhơn và Đà-nẵng.",
        "literature": "Turner 1811 : Fuci III : 85, pl. 169; C. Agardh 1820 : Sp. Alg. : 39; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406."
    },
    {
        "idx": 334, "name": "Sargassum kjellmanianum", "author": "Yendo",
        "vn": "Rong Lá-mơ Ki-en-man", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 364, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_58.png",
        "morphology": "Tản dài 40-80cm, phân nhánh dày; lá nhỏ hình mũi mác hẹp dài 1-2cm; phao khí nhỏ li ti hình cầu mọc thành chùm.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở bờ biển miền Trung.",
        "status": "Mọc trên đá ngầm ven bờ.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Yendo 1905 : Prelim. List Jap. Fuc. : 158; Yendo 1907 : Fucac. Japan : 102, pl. 15."
    },
    {
        "idx": 335, "name": "Sargassum nipponicum", "author": "Yendo",
        "vn": "Rong Lá-mơ Nhật-bản", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 365, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_59.png",
        "morphology": "Tản thanh nhã dài 30-60cm; lá hình dải hẹp dài, mép nguyên trơn không răng; phao khí hình bầu dục có cánh nhọn ở đỉnh.",
        "distribution": "Nhật-bản, Triều-tiên, Biển Đông. Gặp ở Quy-nhơn, Nha-trang.",
        "status": "Mọc ở vùng triều thấp nơi nước sạch.",
        "specimen": "Mẫu Qui-nhơn.",
        "literature": "Yendo 1907 : Fucac. Japan : 153, pl. 17."
    },
    {
        "idx": 336, "name": "Sargassum confusum", "author": "C. Agardh",
        "vn": "Rong Lá-mơ lẫn-lộn", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 366, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_60.png",
        "morphology": "Tản dài 50-100cm; trục chính hơi dẹp; lá ở gốc to rộng lượn sóng, lá ở ngọn hẹp có răng cưa nhỏ; phao khí hình cầu tròn có cuống dẹp.",
        "distribution": "Đông Á, Biển Đông. Gặp ở miền Trung Việt Nam.",
        "status": "Mọc trên đá vùng triều dưới.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "C. Agardh 1820 : Sp. Alg. : 23; Yendo 1907 : Fucac. Japan : 106, pl. 14."
    },
    {
        "idx": 337, "name": "Sargassum mcclurei", "author": "Setchell",
        "vn": "Rong Lá-mơ Mác-cơ-lua", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 367, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_61.png",
        "morphology": "Tản sụn dai cao 40-80cm; lá hình ngọn giáo thắt hẹp ở cuống, có cánh chạy dọc; phao khí hình cầu có vương miện gai nhỏ ở chóp.",
        "distribution": "Hồng Kông, Biển Đông. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên gờ rạn san hô nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Setchell 1933 : Hong Kong Seaweeds III : 44, pls. 15-17; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406."
    },
    {
        "idx": 338, "name": "Sargassum carpophyllum", "author": "J. Agardh",
        "vn": "Rong Lá-mơ chụm", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 368, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_62.png",
        "morphology": "Tản dài 30-70cm; lá mỏng mềm hình mũi mác, gân lá mờ; các đế sinh sản mọc thành chùm dày đặc ở nách lá xen lẫn phao khí.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ở miền Trung Việt Nam.",
        "status": "Mọc ở vùng triều thấp trên đáy cát pha sỏi.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 304; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 406."
    },
    {
        "idx": 339, "name": "Sargassum flavicans", "author": "(Mertens) C. Agardh",
        "vn": "Rong Lá-mơ vàng-vàng", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 369, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_63.png",
        "morphology": "Tản to màu nâu vàng tươi sáng, cao 40-90cm; lá mỏng dài 3-5cm rộng 5-8mm, mép có răng cưa nhỏ đều; phao khí hình cầu trơn bóng.",
        "distribution": "Úc, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải trên rạn san hô chết.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Mertens 1819 : Mém. Mus. Hist. Nat. V : 180; C. Agardh 1820 : Sp. Alg. : 18."
    },
    {
        "idx": 340, "name": "Sargassum aemulum", "author": "Sonder",
        "vn": "Rong Lá-mơ nhại", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 371, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_65.png",
        "morphology": "Tản dài 30-60cm; lá hình bầu dục thon, mép có răng cưa thô; các đế sinh sản có gai nhọn nhỏ.",
        "distribution": "Úc, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Sonder 1852 : Linnaea 25 : 672; J. Agardh 1889 : Sp. Sarg. Austr. : 95."
    },
    {
        "idx": 341, "name": "Sargassum tenerrimum", "author": "J. Agardh",
        "vn": "Rong Lá-mơ mềm", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 372, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_66.png",
        "morphology": "Tản mềm mại thanh mảnh dài 40-80cm, màu nâu vàng nhạt; lá rất mỏng trong suốt khi tươi, hình mũi mác mép lượn răng cưa mịn; phao khí tròn nhỏ cuống mảnh.",
        "distribution": "Ấn-độ-dương, Biển Đông. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc ở các đầm nước mặn tĩnh sóng và vũng triều cạn.",
        "specimen": "Mẫu Cam-ranh và Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 305; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 342, "name": "Sargassum glaucescens", "author": "J. Agardh",
        "vn": "Rong Lá-mơ hơi-mốc", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 373, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_3_67.png",
        "morphology": "Tản dài 30-70cm, bề mặt phủ lớp phấn mốc xám nhạt; lá hình bầu dục thon, gân lá mờ; phao khí có mấu gai nhỏ ở ngọn.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 306; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 343, "name": "Sargassum swartzii", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ Xoát", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 373, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_3_68.png",
        "morphology": "Tản to lớn dài 50-120cm; trục dẹp có sóng gờ giữa rõ rệt rộng 3-5mm; lá dẹp hẹp dài 3-8cm, mép nguyên; phao khí hình bầu dục cuống dẹp có cánh.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở bờ biển Việt Nam.",
        "status": "Loài rong mơ kinh tế quan trọng hàng đầu, nguồn khai thác alginate chủ lực của miền Trung.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Turner 1819 : Fuci IV : 110, pl. 248; C. Agardh 1820 : Sp. Alg. : 11; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 344, "name": "Sargassum binderi", "author": "Sonder ex J. Agardh",
        "vn": "Rong Lá-mơ Bin-đơ", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 375, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_69.png",
        "morphology": "Tản đứng cao 40-80cm, trục dẹp; lá dày sụn màu nâu sẫm, mép có răng cưa thô; phao khí hình tròn có gờ cánh hẹp; đế sinh sản phân nhánh dày đặc.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc dày đặc ở vùng triều thấp và dưới triều trên đá gềnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 328; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 345, "name": "Sargassum feldmannii", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Lá-mơ Phe-man", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 376, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_70.png",
        "morphology": "Tản cao 30-50cm, trục dẹp mang nhánh song đính hai bên; lá dày hình dải hẹp dài 4-6cm; đặc sắc nhờ các đế sinh sản hình chùy ngắn xếp thành cụm dày ở nách lá. Đặt tên vinh danh GS. Jean Feldmann.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá tầng hạ-duyên-hải.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1967 : Contrib. Sargass. Vietn. : 301, fig. 17; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 374, fig. 3.70."
    },
    {
        "idx": 346, "name": "Sargassum cristaefolium", "author": "C. Agardh",
        "vn": "Rong Lá-mơ có-răng", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 377, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_71.png",
        "morphology": "Tản sụn dày cứng như da, cao 30-70cm; lá hình bầu dục dày cộp, đỉnh lá chẻ đôi tạo thành 2 gờ răng cưa song song (lá mào đôi); phao khí hình cầu có vương miện gai nhọn.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú tại bờ biển miền Trung Việt Nam.",
        "status": "Mọc bám trên đá nơi sóng to gió lớn ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, đảo Côn-đảo.",
        "literature": "C. Agardh 1820 : Sp. Alg. : 13; J. Agardh 1848 : Sp. Alg. I : 325; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 347, "name": "Sargassum duplicatum", "author": "J. Agardh",
        "vn": "Rong Lá-mơ bìa-đôi", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 378, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_72.png",
        "morphology": "Tản sụn dày cao 30-60cm; lá dày cứng có mép gấp đôi tạo thành viền răng kép chạy quanh đầu lá; phao khí tròn có gai nhỏ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến tại Việt Nam.",
        "status": "Mọc trên rạn san hô vùng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1889 : Sp. Sarg. Austr. : 90; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 348, "name": "Sargassum crassifolium", "author": "J. Agardh",
        "vn": "Rong Lá-mơ lá-dày", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 379, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_73.png",
        "morphology": "Tản cực kỳ dày thịt và cứng cáp, màu nâu lục đen; lá dày mập thịt hình bầu dục tròn, gân lá chìm sâu; mép lá có răng cưa thô tù; chịu sóng đánh cực mạnh.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phong phú ở các hải đảo Việt Nam.",
        "status": "Bám chắc trên gờ rạn san hô ngoài khơi nơi sóng đập dữ dội nhất.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 326; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 349, "name": "Sargassum turbinarioides", "author": "Grunow",
        "vn": "Rong Lá-mơ hình-chùy", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 380, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_74.png",
        "morphology": "Tản có lá biến đổi đặc sắc phồng to thành hình nón cụt giống như lá rong Chùy-diệp (Turbinaria); phao khí chìm trong lá thịt; sụn rất cứng.",
        "distribution": "Biển Đỏ, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá san hô vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Grunow 1915 : Addit. Cog. Sargass. : 395; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 379."
    },
    {
        "idx": 350, "name": "Sargassum ilicifolium", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ ô-rô", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 381, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_75.png",
        "morphology": "Tản cao 40-90cm; lá dày cứng hình bầu dục mép có răng cưa nhọn uốn lượn như lá cây Ô-rô (Ilex); phao khí hình cầu trơn bóng.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phổ biến tại Việt Nam.",
        "status": "Nguồn nguyên liệu khai thác alginate quan trọng của vùng biển miền Trung.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu.",
        "literature": "Turner 1808 : Fuci I : 113, pl. 51; C. Agardh 1820 : Sp. Alg. : 11; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 351, "name": "Sargassum heterocystum", "author": "Montagne",
        "vn": "Rong Lá-mơ dị-nang", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 382, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_76.png",
        "morphology": "Tản cao 30-60cm; phao khí có nhiều hình dạng khác nhau trên cùng một tản (dị nang): phao ở dưới hình bầu dục có cánh, phao ở trên hình cầu nhỏ trơn.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Montagne 1842 : Cent. Pl. Cell. : 17; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 352, "name": "Sargassum microcystum", "author": "J. Agardh",
        "vn": "Rong Lá-mơ phao-nhỏ", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 384, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_77.png",
        "morphology": "Tản to lớn dài 50-100cm; mang vô số phao khí nhỏ li ti hình cầu đường kính chỉ 1-2mm mọc dày đặc thành chùm che khuất cả cành lá; lá nhỏ hình mũi mác.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Tạo rừng rong ngầm dày đặc ở tầng hạ-duyên-hải sâu 1-3m.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Phú-quốc.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 323; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 353, "name": "Sargassum armatum", "author": "J. Agardh",
        "vn": "Rong Lá-mơ nhọn", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 383, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_78.png",
        "morphology": "Trục chính và các nhánh phủ đầy gai nhọn cứng cáp; lá hình ngọn giáo mép có răng cưa sắc bén; phao khí có gai nhọn ở đỉnh.",
        "distribution": "Thái-bình-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 313; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 354, "name": "Sargassum polycystum", "author": "C. Agardh",
        "vn": "Rong Lá-mơ nhiều-phao", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 386, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_79.png",
        "morphology": "Tản cao 50-150cm, màu nâu đỏ sẫm; đặc trưng nổi bật ở gốc tản phát triển thành các cành bò biến đổi thành rễ bò phân nhánh đâm chồi bò lan trên đá; trục phủ đầy gai nhỏ; mang vô số phao khí nhỏ li ti.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Cực kỳ phong phú ở toàn bộ duyên hải và hải đảo Việt Nam.",
        "status": "Loài rong mơ phổ biến nhất Việt Nam, tạo thành sinh khối khổng lồ; nguyên liệu sản xuất alginate công nghiệp và phân bón sinh học.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc, Cát-bà.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 304; J. Agardh 1848 : Sp. Alg. I : 310; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407, fig. 22."
    },
    {
        "idx": 355, "name": "Sargassum gracile", "author": "J. Agardh",
        "vn": "Rong Lá-mơ mảnh", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 387, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_80.png",
        "morphology": "Tản mảnh mai thanh nhã dài 40-70cm; trục tròn nhẵn; lá hẹp dài, mép có răng cưa nhỏ thưa; phao khí tròn nhỏ cuống dài.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng triều dưới nơi nước sạch.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 310; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 356, "name": "Sargassum baccularia", "author": "(Mertens) C. Agardh",
        "vn": "Rong Lá-mơ trái-nhỏ", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 388, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_81.png",
        "morphology": "Tản cao 50-100cm; phao khí hình cầu đường kính 5-6mm mọc đơn độc trên cuống ngắn; lá hình mũi mác rộng, gân lá rõ; đế sinh sản mọc thưa không gai.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ven biển miền Trung.",
        "status": "Khai thác lấy alginate.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Mertens 1819 : Mém. Mus. Hist. Nat. V : 177; C. Agardh 1824 : Syst. Alg. : 305; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 357, "name": "Sargassum parvifolium", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ lá-nhỏ", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 388, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_82.png",
        "morphology": "Tản phân nhánh dày đặc; lá rất nhỏ dài dưới 1,5cm rộng 2-3mm, mép có răng cưa nhọn; phao khí nhỏ li ti.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Turner 1819 : Fuci IV : 93, pl. 236; C. Agardh 1820 : Sp. Alg. : 30."
    },
    {
        "idx": 358, "name": "Sargassum bacciferum", "author": "(Turner) C. Agardh",
        "vn": "Rong Lá-mơ mang-trái", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 389, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_83.png",
        "morphology": "Tản trôi nổi tự do trên biển mở (loài rong biển Sargasso); lá dài hẹp mép có răng cưa nhọn; phao khí tròn có cuống mang gai nhọn; sinh sản hoàn toàn bằng phương thức sinh dưỡng gãy nhánh.",
        "distribution": "Đại-tây-dương, Thái-bình-dương, Biển Đông. Trôi dạt vào bờ biển miền Trung Việt Nam.",
        "status": "Rong trôi nổi tự do ngoài đại dương dạt vào bờ sau các cơn bão.",
        "specimen": "Mẫu vớt tại vịnh Nha-trang.",
        "literature": "Turner 1808 : Fuci I : 120, pl. 57; C. Agardh 1820 : Sp. Alg. : 6."
    },
    {
        "idx": 359, "name": "Sargassum henslowianum", "author": "C. Agardh ex J. Agardh",
        "vn": "Rong Lá-mơ Hen-xlo", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 390, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_84.png",
        "morphology": "Tản đa niên to lớn dài 1-2m; trục hình trụ tròn như sợi dây; lá hình dải hẹp dài 5-12cm, rộng 3-6mm, chất màng dai, mép có răng cưa sắc; phao khí hình cầu trơn; đế sinh sản hình trụ dài phân nhánh.",
        "distribution": "Trung-quốc, Biển Đông. Rất phong phú ở vùng biển miền Trung và Nam Việt Nam.",
        "status": "Nguồn nguyên liệu khai thác alginate quan trọng của nước ta.",
        "specimen": "Mẫu Quy-nhơn, Nha-trang, Vũng-Tàu.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 315; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 407."
    },
    {
        "idx": 360, "name": "Sargassum congkinhii", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Lá-mơ Cồng-Kính", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 391, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_85.png",
        "morphology": "Tản cao 40-80cm; trục tròn; lá gần như không cuống, dài 5-7cm, rộng 8-12mm, mép có răng cưa nhỏ; phao khí hình xoan có cánh hẹp; đế sinh sản hình trụ ngắn có gai nhọn. Đặt tên vinh danh nhà thực vật học Nguyễn Cồng Kính.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá rạn san hô tầng hạ-duyên-hải.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1967 : Contrib. Sargass. Vietn. : 318, fig. 24; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 389, fig. 3.85."
    },
    {
        "idx": 361, "name": "Sargassum bicorne", "author": "J. Agardh",
        "vn": "Rong Lá-mơ hai-sừng", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 393, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_86.png",
        "morphology": "Tản nhỏ mịn cao 20-40cm; trục như chỉ rộng 0,2-0,5mm; lá nhỏ hẹp; đặc sắc nhờ các phao khí ở ngọn mang 2 sừng nhọn hoắt như sừng trâu nhỏ.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên rạn san hô nông.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "J. Agardh 1848 : Sp. Alg. I : 315; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 408."
    },
    {
        "idx": 362, "name": "Sargassum kuetzingii", "author": "Setchell",
        "vn": "Rong Lá-mơ Cút-dinh", "fam_vn": "Họ Rong-mơ", "fam_lat": "Sargassaceae",
        "ord_vn": "Bộ Rong-mơ", "ord_lat": "Fucales", "gen_vn": "Chi Rong Mơ", "gen_lat": "Sargassum",
        "p": 394, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_3_87.png",
        "morphology": "Tản mịn đẹp cao 30-60cm; trục như sợi chỉ; lá mỏng nhỏ thon hẹp; phao khí tròn nhỏ có cuống mảnh; đế sinh sản nhỏ mọc ở nách lá. Loài kết thúc toàn bộ Phần III (Lớp Cát-tảo / Tảo nâu).",
        "distribution": "Hồng Kông, Biển Đông. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc trên đá và rạn san hô tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Setchell 1931 : Hong Kong Seaweeds II : 249, pl. 38; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 408."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH6_DATA)} figures for Batch 6...')
    for sp in BATCH6_DATA:
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
    print(f'Querying WoRMS API in chunks for {len(BATCH6_DATA)} species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH6_DATA), chunk_size):
        chunk = BATCH6_DATA[i:i+chunk_size]
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
        
    for sp, item in zip(BATCH6_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH6_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH6_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 6...')
    rows = []
    for sp in BATCH6_DATA:
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
            "tax_class_vn": "Lớp Tảo Nâu",
            "tax_class_latin": "Phaeophyceae",
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch6.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 6 build completed successfully!')
