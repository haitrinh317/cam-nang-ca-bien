"""
build_batch3.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 66 loài Hồng-tảo (Rhodophyceae - Đợt 3, loài 68-133)
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

BATCH3_DATA = [
    {
        "idx": 68, "name": "Erythrotrichia carnea", "author": "(Dillwyn) J. Agardh",
        "vn": "Rong Hồng-tiết thịt", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-tiết", "gen_lat": "Erythrotrichia",
        "p": 72, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_1.png",
        "morphology": "Sợi mọc phụ sinh, cao 2-8mm, màu hồng đỏ tươi; sợi đơn không phân nhánh, do một hàng tế-bào tạo thành, rộng 15-25µ; tế-bào ngắn hơn rộng hay dài bằng rộng; hồng-lạp hình sao có 1 hạch-lạp ở giữa; bám nhờ tế-bào đáy chia nhánh hình đĩa.",
        "distribution": "Toàn cầu ở các vùng biển ấm. Việt Nam: Nha-trang, Vũng-Tàu, Phú-quốc.",
        "status": "Phụ sinh trên các loài rong lớn khác như Grateloupia ramosissima, Enteromorpha kylinii.",
        "specimen": "Mẫu khảo sát Nha-trang (V-VIII).",
        "literature": "Dillwyn 1809 : Brit. Conf. : 54; J. Agardh 1883 : Till Alg. Syst. VI : 15; Tanaka 1952 : Syst. Stud. Jap. Protoflorideae : 14, fig. 7."
    },
    {
        "idx": 69, "name": "Erythrotrichia parietalis", "author": "Tanaka",
        "vn": "Rong Hồng-tiết vách", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-tiết", "gen_lat": "Erythrotrichia",
        "p": 73, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_2.png",
        "morphology": "Tản phụ sinh, cao 1,5mm, hình sợi, chia nhánh như lưỡng phân, rộng 15-18µ; đáy tản do tế-bào dài cao, tế-bào đáy phù thành đĩa dính; tế-bào dài bằng rộng, hồng-lạp hình sao, vách rất dày.",
        "distribution": "Nhật-bản, Việt Nam (Hòn-chồng Nha-trang).",
        "status": "Phụ sinh trên thân các loài rong đỏ lớn ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Tanaka 1952 : Syst. Stud. Jap. Protoflorideae : 18, fig. 10."
    },
    {
        "idx": 70, "name": "Erythrotrichia boryana", "author": "(Montagne) Berthold",
        "vn": "Rong Hồng-tiết Bô-ri", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-tiết", "gen_lat": "Erythrotrichia",
        "p": 75, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_3.png",
        "morphology": "Tản hình dải dẹp màu đỏ tía, cao 2-5mm, do nhiều hàng tế-bào tạo thành ở phần trên; phần gốc hình trụ hẹp; tế-bào sắp xếp thành hàng ngang đều đặn.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên lá cỏ biển và các loài rong cọng cứng vùng triều thấp.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "Montagne 1846 : Fl. Algérie : 150; Berthold 1882 : Bangiaceen : 25; Tanaka 1952 : Protoflorideae : 17."
    },
    {
        "idx": 71, "name": "Bangiopsis humphreyi", "author": "(Collins) Hamel",
        "vn": "Rong Giả-xích-phát Hâm-phri", "fam_vn": "Họ Xích-phát", "fam_lat": "Bangiaceae",
        "ord_vn": "Bộ Xích-phát", "ord_lat": "Bangiales", "gen_vn": "Chi Rong Giả-xích-phát", "gen_lat": "Bangiopsis",
        "p": 78, "crop": (150, 1500, 2200, 2900), "fig_name": "fig_2_6.png",
        "morphology": "Cỏ thê đỏ đậm hay tươi; tản do sợi đơn, cao 1,5mm, rộng 15-70µ, do tế-bào sắp không thành hàng đều, đẵng-kính, rộng 6-10µ, với hồng-lạp hình sao có hạch-lạp ở giữa. Dính nhờ một dĩa nhỏ do vài tế-bào.",
        "distribution": "Vùng nhiệt đới châu Mỹ, Nhật-bản, Việt Nam (Phan-thiết).",
        "status": "Trên đá, mực trung-duyên-hải trung vào mùa đông (tháng XII).",
        "specimen": "Mẫu khảo sát tại Phan-thiết.",
        "literature": "Collins 1898 : Phyc. Bor. Amer. : no 421; Hamel 1925 : Floridées de France : 45; Tanaka 1952 : Protoflorideae : 8, fig. 4."
    },
    {
        "idx": 72, "name": "Bangia fuscopurpurea", "author": "(Dillwyn) Lyngbye",
        "vn": "Rong Xích-phát tía", "fam_vn": "Họ Xích-phát", "fam_lat": "Bangiaceae",
        "ord_vn": "Bộ Xích-phát", "ord_lat": "Bangiales", "gen_vn": "Chi Rong Xích-phát", "gen_lat": "Bangia",
        "p": 79, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_7.png",
        "morphology": "Sợi như tóc, dài 8-15cm, màu đỏ vàng hay đỏ đậm, rộng 75-90µ. Phần đáy cho thấy nhiều căn-trạng trong tản đài. Tế-bào sắp thành hoàn-sinh đẳng-kính, to cỡ 25-30µ; hồng-lạp hình sao, hạch-lạp to ở giữa. Tản đực đỏ dợt hay vàng; tản cái màu đỏ to hơn tản đực.",
        "distribution": "Khắp các biển ôn đới và nhiệt đới thế giới. Việt Nam: Duyên hải Trung bộ.",
        "status": "Rong mùa đông (Phạm-Hoàng Hộ 1961) ở những nơi sóng rất mạnh, đi chung với Porphyra (XII-I).",
        "specimen": "Mẫu Qui-nhơn và Nha-trang.",
        "literature": "Dillwyn 1809 : Brit. Conferv. : 92; Lyngbye 1819 : Hydrophyt. Dan. : 83, tab. 24c; Okamura 1916 : Icones Jap. Alg. IV : 87, pl. 171, figs. 6-12."
    },
    {
        "idx": 73, "name": "Bangia tanakai", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Xích-phát Ta-na-ca", "fam_vn": "Họ Xích-phát", "fam_lat": "Bangiaceae",
        "ord_vn": "Bộ Xích-phát", "ord_lat": "Bangiales", "gen_vn": "Chi Rong Xích-phát", "gen_lat": "Bangia",
        "p": 80, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_8.png",
        "morphology": "Tản dài 1-2cm, rộng 60-75µ ở phần rộng nhất. Đáy cho thấy nhiều căn-trạng nội-tản. Tế-bào thường sắp một dọc, rộng hơn cao, chứa một hồng-lạp hình sao với 1-2 hạch-lạp trung-trục. Quả-bào-tử-phòng với 8-16 bào-tử to cỡ 14-18µ màu đỏ thắm. Loài mới do GS. Phạm Hoàng Hộ phát hiện và mô tả.",
        "distribution": "Đặc hữu Việt Nam: Hòn-tre (Nha-trang).",
        "status": "Làm thành cỏ thê đỏ, mực trung-duyên-hải thượng cạnh Porphyra crispata ở Hòn-tre (Nha-trang); tháng I.",
        "specimen": "Holotype thu tại Hòn-tre, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 76, fig. 2.8."
    },
    {
        "idx": 74, "name": "Porphyra crispata", "author": "Kjellman",
        "vn": "Rong Mứt dúng", "fam_vn": "Họ Xích-phát", "fam_lat": "Bangiaceae",
        "ord_vn": "Bộ Xích-phát", "ord_lat": "Bangiales", "gen_vn": "Chi Rong Mứt", "gen_lat": "Porphyra",
        "p": 81, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_9.png",
        "morphology": "Phiến xoan hay hình thận, nhăn nhiều, rộng 2-4cm, dày 60µ, màu đỏ vàng hay đậm, bìa thường xẻ và có răng nhỏ; phần đáy tản cho thấy căn-trạng nội-tản; đáy tản nhọn. Tế-bào dinh-dưỡng rộng 15-20µ; hồng-lạp hình sao. Tảo-quả với 32 quả-bào-tử.",
        "distribution": "Nhật-bản, Trung-quốc, Việt Nam (Đà-nẵng, Qui-nhơn, Nha-trang).",
        "status": "Rong ăn được có giá trị kinh tế cao, mọc thành dải dày trên đá nơi sóng to vào mùa đông.",
        "specimen": "Mẫu thu tại Hòn-chồng, Nha-trang.",
        "literature": "Kjellman 1897 : Jap. Arter af slagt. Porphyra : 15, t. 1, figs. 4-5; Tanaka 1952 : Protoflorideae : 34, fig. 14; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 412, fig. 24."
    },
    {
        "idx": 75, "name": "Porphyra vietnamensis", "author": "Tanaka & Pham-hoang Ho nov. sp.",
        "vn": "Rong Mứt việtnam", "fam_vn": "Họ Xích-phát", "fam_lat": "Bangiaceae",
        "ord_vn": "Bộ Xích-phát", "ord_lat": "Bangiales", "gen_vn": "Chi Rong Mứt", "gen_lat": "Porphyra",
        "p": 82, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_10.png",
        "morphology": "Tản mỏng manh, dài 5-15cm, rộng 1-3cm, dày chỉ 20-25µ, màu đỏ tươi; bìa có răng nhỏ mịn; phẫu thức ngang gồm 1 lớp tế-bào; quả-bào-tử-phòng chia 64 bào-tử; tinh-phòng chia 128 tinh-trùng. Loài mới phát hiện cho khoa học tại bờ biển Việt Nam.",
        "distribution": "Đặc hữu vùng duyên hải Việt Nam và Biển Đông.",
        "status": "Mọc trên đá vùng triều cao nơi sóng đánh mạnh, xuất hiện từ tháng XI đến tháng III hàng năm.",
        "specimen": "Holotype thu tại Vũng-Tàu và Nha-trang.",
        "literature": "Tanaka & Phạm-hoàng Hộ 1962 : Notes Mar. Alg. Vietn. I : 34, fig. 10; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 78, fig. 2.10."
    },
    {
        "idx": 76, "name": "Erythrocladia irregularis", "author": "Rosenvinge",
        "vn": "Rong Hồng-bì bất-quy", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-bì", "gen_lat": "Erythrocladia",
        "p": 83, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_11.png",
        "morphology": "Tản vi thể hình đĩa nhỏ, màu hồng nhạt, đường kính 50-100µ; sợi bò phân nhánh bất quy tắc, các sợi không áp sát nhau hoàn toàn; tế-bào uốn lượn; độc-bào-tử hình cầu sinh ra từ tế-bào tản.",
        "distribution": "Toàn cầu. Việt Nam: Gặp ở Nha-trang, Vũng-Tàu.",
        "status": "Phụ sinh trên màng cutin của các loài rong lục và rong nâu lớn.",
        "specimen": "Mẫu phụ sinh tại vịnh Nha-trang.",
        "literature": "Rosenvinge 1909 : Mar. Alg. Denm. I : 72, figs. 11-12; Tanaka 1952 : Protoflorideae : 4, fig. 2."
    },
    {
        "idx": 77, "name": "Erythrocladia subintegra", "author": "Rosenvinge",
        "vn": "Rong Hồng-bì nguyên", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-bì", "gen_lat": "Erythrocladia",
        "p": 84, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_12.png",
        "morphology": "Tản hình đĩa tròn đều đặn, mép nguyên hoặc xẻ răng cưa rất nông; các sợi tỏa tròn từ tâm ra mép ngoài ép sát vào nhau thành màng liên tục; tế-bào mép chẻ đôi ở đầu ngọn.",
        "distribution": "Khắp thế giới. Rất phổ biến ở Việt Nam.",
        "status": "Phụ sinh trên Bryopsis, Chaetomorpha, Valonia và vỏ thủy sinh động vật.",
        "specimen": "Mẫu Nha-trang và Phan-thiết.",
        "literature": "Rosenvinge 1909 : Mar. Alg. Denm. I : 73, figs. 13-14; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 411, fig. 23."
    },
    {
        "idx": 78, "name": "Erythrocladia chaetomorphae", "author": "Tanaka & Pham-hoang Ho",
        "vn": "Rong Hồng-bì mao-hình", "fam_vn": "Họ Hồng-tiết", "fam_lat": "Erythrotrichiaceae",
        "ord_vn": "Bộ Hồng-tiết", "ord_lat": "Erythropeltidales", "gen_vn": "Chi Rong Hồng-bì", "gen_lat": "Erythrocladia",
        "p": 85, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_13.png",
        "morphology": "Tản đĩa bao quanh tế bào sợi rong Chaetomorpha; sợi phân nhánh tỏa tròn sít sao; tế-bào hình chữ nhật hay đa giác, rộng 4-8µ; độc-bào-tử-phòng hình cầu đường kính 4µ tạo thành ở trung tâm đĩa.",
        "distribution": "Đặc hữu Việt Nam: Nha-trang, Cà-ná.",
        "status": "Phụ sinh đặc hiệu trên vách tế bào Chaetomorpha antennina nơi sóng to.",
        "specimen": "Holotype thu tại Cà-ná (Ninh-thuận).",
        "literature": "Tanaka & Phạm-hoàng Hộ 1962 : Notes Mar. Alg. Vietn. I : 28, fig. 3; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 81, fig. 2.13."
    },
    {
        "idx": 79, "name": "Acrochaetium colaconemoides", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đỉnh-mao giả-thúc", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 88, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_14.png",
        "morphology": "Tản vi thể sống bán nội sinh trong màng của rong khác; sợi bò phân nhánh ngang trong vách ký chủ, cho ra các nhánh đứng rất ngắn cao 50-100µ; tế-bào dài gấp 2-4 lần rộng; độc-bào-tử không cọng ở ngọn nhánh.",
        "distribution": "Đặc hữu bờ biển Việt Nam (Nha-trang).",
        "status": "Nội sinh một phần trong vách tế bào của Grateloupia và Halymenia.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 84, fig. 2.14."
    },
    {
        "idx": 80, "name": "Acrochaetium gracile", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao thanh", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 86, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_15.png",
        "morphology": "Sợi đứng mảnh mai, cao 1-2mm; tế-bào hình trụ dài gấp 3-5 lần đường kính (rộng 5-7µ); phân nhánh thưa; độc-bào-tử-phòng hình bầu dục mọc đơn độc hoặc từng đôi ở nách nhánh.",
        "distribution": "Tây Ấn, Ấn-độ-dương, Việt Nam.",
        "status": "Phụ sinh trên Dictyota và Turbinaria ở tầng triều dưới.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Boergesen 1915 : Mar. Alg. Dan. W. Ind. II : 26, fig. 19; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 413."
    },
    {
        "idx": 81, "name": "Acrochaetium crassipes", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao chân-mập", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 87, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_16.png",
        "morphology": "Tản cực nhỏ, cao chỉ 50-120µ; gốc dính gồm duy nhất một tế-bào đáy hình cầu to mập đường kính 12-15µ; từ tế-bào này mọc lên 1-3 nhánh đứng ngắn; độc-bào-tử-phòng hình xoan ở đỉnh nhánh.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên sợi Cladophora và Chaetomorpha.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "Boergesen 1915 : Mar. Alg. Dan. W. Ind. II : 20, fig. 11; Tanaka 1952 : Protoflorideae : 89."
    },
    {
        "idx": 82, "name": "Acrochaetium pseuderectum", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đỉnh-mao đứng-giả", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 90, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_17.png",
        "morphology": "Tản sợi đứng thẳng tắp, cao 0,5-1mm; tế-bào đáy duy nhất hình bàn chân dính chặt vào ký chủ; sợi chính chia nhánh cách quãng; tế-bào hình trụ dài gấp 2-3 lần rộng; bào-tử-phòng mọc thành hàng một bên.",
        "distribution": "Đặc hữu Việt Nam: Hòn-chồng (Nha-trang).",
        "status": "Phụ sinh trên Padina và Sargassum.",
        "specimen": "Holotype thu tại Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 86, fig. 2.17."
    },
    {
        "idx": 83, "name": "Acrochaetium catenulatum", "author": "M. Howe",
        "vn": "Rong Đỉnh-mao dày", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 89, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_18.png",
        "morphology": "Tản cao đến 150µ, dính vào ký chủ nhờ một tế-bào đáy nhọn. Tế-bào mập, rộng 10µ, dài hơn cỡ một lần rưỡi; không lông; hồng-lạp với hạch-lạp ở giữa. Sợi chánh cong queo, mang nhánh đơn trục từ tế-bào thứ 3 hay 4; độc-bào-tử-phòng ở ngọn hoặc bên cạnh.",
        "distribution": "Thái-bình-dương (Peru, Nhật-bản, Việt Nam).",
        "status": "Phụ sinh trên Sphacelaria, Padina ở tầng triều giữa.",
        "specimen": "Mẫu phụ sinh tại bờ biển Nha-trang.",
        "literature": "Howe 1914 : Mar. Alg. Peru : 84, pl. 31, figs. 12-18; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 414."
    },
    {
        "idx": 84, "name": "Acrochaetium robustum", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao cứng", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 91, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_19.png",
        "morphology": "Búi sợi nhỏ cứng cáp, màu đỏ hồng sẫm, cao 1-3mm; sợi đứng rộng 8-12µ; vách tế bào dày; phân nhánh đơn phương; tế-bào gốc nhiều chia thành đĩa dính; độc-bào-tử hình bầu dục to.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Biển Đông. Gặp ở Qui-nhơn, Nha-trang.",
        "status": "Phụ sinh trên Sargassum và Turbinaria.",
        "specimen": "Mẫu thu tại vịnh Qui-nhơn.",
        "literature": "Boergesen 1915 : Mar. Alg. Dan. W. Ind. II : 40, figs. 38-40."
    },
    {
        "idx": 85, "name": "Acrochaetium occidentale", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao tây", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 92, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_20.png",
        "morphology": "Sợi cao 1-2mm, sống trên Liagora; bào-tử mọc cho ra một sợi xoi tản rong này, rộng 16µ. Sợi đứng mang nhánh càng cao càng ngắn, tế-bào rộng 10-11µ, dài 27-40µ; hồng-lạp hình sao với 1 hạch-lạp. Độc-bào-tử không cọng hình xoan 9-12 x 18-20µ, gắn một bên nhánh.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Sống nội sinh/phụ sinh trên Liagora ceranoides.",
        "specimen": "Mẫu Nha-trang (Dawson 1954).",
        "literature": "Boergesen 1915 : Mar. Alg. Dan. W. Ind. : 44, figs. 42-43; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 414, fig. 25 d-e."
    },
    {
        "idx": 86, "name": "Acrochaetium ryukyuense", "author": "Nakamura",
        "vn": "Rong Đỉnh-mao Lưu-cầu", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 93, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_21.png",
        "morphology": "Sợi mọc phụ sinh, cao 0,5-1mm; tế-bào đáy đơn hình cầu dính trên màng tế bào chủ; sợi đứng phân nhánh so le; tế-bào rộng 7-9µ, dài gấp 2-3 lần rộng; độc-bào-tử mọc ở nách nhánh.",
        "distribution": "Nhật-bản (quần đảo Ryukyu), Việt Nam (Nha-trang).",
        "status": "Phụ sinh trên Galaxaura và Liagora.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Nakamura 1941 : Sci. Pap. Inst. Algol. Res. Hokkaido Univ. II : 279, fig. 6."
    },
    {
        "idx": 87, "name": "Acrochaetium kuckuckianum", "author": "Hamid",
        "vn": "Rong Đỉnh-mao Cúc-cúc", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 94, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_22.png",
        "morphology": "Tản sợi nhỏ bám nhờ tế-bào đáy tròn; sợi phân nhánh dích dắc; tế-bào hình chữ nhật thon; độc-bào-tử có cuống ngắn 1 tế bào.",
        "distribution": "Ấn-độ-dương, Biển Đông.",
        "status": "Phụ sinh trên rong Mơ (Sargassum) vùng triều thấp.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Hamid 1954 : Bull. Karachi Univ. : 12; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 90."
    },
    {
        "idx": 88, "name": "Acrochaetium subseriatum", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao cận-chuỗi", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 95, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_23.png",
        "morphology": "Sợi mọc đứng cao 1-2mm, rộng 6-8µ; độc-bào-tử sắp thành hàng chuỗi một bên ở các nhánh ngọn; tế-bào ngọn thon thành sợi lông không màu dài.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Việt Nam: Nha-trang.",
        "status": "Phụ sinh trên các loài rong đỏ khác.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Boergesen 1932 : Some Ind. Rhodophyceae : 6, figs. 1-2."
    },
    {
        "idx": 89, "name": "Acrochaetium daviesii", "author": "(Dillwyn) Nägeli",
        "vn": "Rong Đỉnh-mao Đa-vít", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 96, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_24.png",
        "morphology": "Bụi tơ dày màu đỏ tía, cao 2-4mm; sợi đứng rộng 9-12µ; phân nhánh chùm sít sao; bào-tử-phòng mọc thành từng cụm hình chùm ở nách nhánh.",
        "distribution": "Toàn cầu. Việt Nam: Duyên hải miền Trung.",
        "status": "Phụ sinh trên mép lá rong Mơ và rong Cầm.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Dillwyn 1809 : Brit. Conf. : 73; Nägeli 1861 : Beitr. Morph. Ceramiac. : 405; Frémy 1933 : Cyanop. côtes d'Europe : 54."
    },
    {
        "idx": 90, "name": "Acrochaetium trichogloeae", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đỉnh-mao mao-giao", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 97, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_25.png",
        "morphology": "Sợi vi thể sống nội sinh hoàn toàn trong chất keo nhớt của tản Trichogloea requienii; sợi phân nhánh ngang rồi mọc hướng tâm ra ngoài; độc-bào-tử hình xoan nhỏ.",
        "distribution": "Đặc hữu Việt Nam (Nha-trang).",
        "status": "Nội sinh đặc hiệu trong tản rong Trichogloea.",
        "specimen": "Holotype thu tại Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 93, fig. 2.25."
    },
    {
        "idx": 91, "name": "Acrochaetium seriatum", "author": "Boergesen",
        "vn": "Rong Đỉnh-mao chuỗi", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 98, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_26.png",
        "morphology": "Sợi đứng cao 1-1,5mm, rộng 8-10µ; các độc-bào-tử-phòng mọc thành một chuỗi dài liên tục dọc theo mặt lưng của các nhánh bên; tế-bào ngọn tròn.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Việt Nam.",
        "status": "Phụ sinh trên Hypnea và Gracilaria.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Boergesen 1915 : Mar. Alg. Dan. W. Ind. II : 32, figs. 25-26."
    },
    {
        "idx": 92, "name": "Acrochaetium phuquocense", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đỉnh-mao Phú-quốc", "fam_vn": "Họ Đỉnh-mao", "fam_lat": "Acrochaetiaceae",
        "ord_vn": "Bộ Đỉnh-mao", "ord_lat": "Acrochaetiales", "gen_vn": "Chi Rong Đỉnh-mao", "gen_lat": "Acrochaetium",
        "p": 99, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_27.png",
        "morphology": "Tản phụ sinh hình bụi nhỏ cao 1mm; tế-bào gốc hình củ hành ăn sâu vào màng ký chủ; sợi phân nhánh chữ V; tế-bào chứa hồng-lạp hình dải dài; bào-tử-phòng hình bầu dục không cuống.",
        "distribution": "Đặc hữu Việt Nam: Đảo Phú-quốc.",
        "status": "Phụ sinh trên rong Guột (Caulerpa) tại Phú-quốc.",
        "specimen": "Holotype thu tại bãi Cây-Dừa, Phú-quốc.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 95, fig. 2.27."
    },
    {
        "idx": 93, "name": "Liagora orientalis", "author": "J. Agardh",
        "vn": "Rong Hải-giác đông-phương", "fam_vn": "Họ Hải-giác", "fam_lat": "Liagoraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Hải-giác", "gen_lat": "Liagora",
        "p": 101, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_28.png",
        "morphology": "Tản tẩm vôi mềm dẻo, cao 5-10cm, màu hồng trắng hay xám phấn; chia nhánh lưỡng phân đều đặn; nhánh hình trụ đường kính 1-1,5mm; cơ cấu gồm trục tủy hình sợi và vỏ ngoài do các chuỗi tế bào đồng hóa tỏa tròn.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Mọc trên đá và rạn san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "J. Agardh 1896 : Analecta Algol. Cont. III : 99; Yamada 1938 : Spec. Liagora Japan : 18, pl. 5, fig. 1."
    },
    {
        "idx": 94, "name": "Liagora farinosa", "author": "Lamouroux",
        "vn": "Rong Hải-giác phấn", "fam_vn": "Họ Hải-giác", "fam_lat": "Liagoraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Hải-giác", "gen_lat": "Liagora",
        "p": 102, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_29.png",
        "morphology": "Tản cao 8-15cm, tẩm vôi xốp như bột phấn, màu trắng xám hay hồng nhạt; nhánh phân đôi cách quãng, rộng 1,5-2mm; các sợi vỏ ngoài dài, tế-bào ngọn hình cầu to mang chùm lông tơ mịn.",
        "distribution": "Vùng biển nhiệt đới toàn cầu. Phổ biến khắp duyên hải Nam Trung bộ Việt Nam.",
        "status": "Rất phổ biến trên rạn san hô nông và bãi đá ven đảo.",
        "specimen": "Mẫu Nha-trang và Côn-đảo.",
        "literature": "Lamouroux 1816 : Hist. Polyp. Corall. : 240; Boergesen 1915 : Mar. Alg. Dan. W. Ind. II : 67; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 415, fig. 26."
    },
    {
        "idx": 95, "name": "Liagora ceranoides", "author": "Lamouroux",
        "vn": "Rong Hải-giác sừng", "fam_vn": "Họ Hải-giác", "fam_lat": "Liagoraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Hải-giác", "gen_lat": "Liagora",
        "p": 103, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_30.png",
        "morphology": "Tản hình bụi tròn bán cầu, cao 4-8cm, tẩm vôi vừa phải, màu hồng tía; chia nhánh lưỡng phân khít khao; ngọn cành hơi thon nhọn như sừng hươu.",
        "distribution": "Khắp các biển nhiệt đới. Việt Nam: Nha-trang, Ninh-thuận, Bình-thuận.",
        "status": "Tầng triều thấp trên nền đá san hô nơi sóng trong.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Lamouroux 1816 : Hist. Polyp. Corall. : 239; Yamada 1938 : Spec. Liagora Japan : 20, pl. 6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 416."
    },
    {
        "idx": 96, "name": "Liagora divaricata", "author": "Tseng",
        "vn": "Rong Hải-giác giẽ", "fam_vn": "Họ Hải-giác", "fam_lat": "Liagoraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Hải-giác", "gen_lat": "Liagora",
        "p": 104, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_31.png",
        "morphology": "Tản cao 6-10cm, các nhánh chia đôi rẽ góc rất rộng (divaricate); tẩm vôi đều, bề mặt láng mịn; màu trắng ngà pha phớt hồng; cấu trúc sợi vỏ ngoài ngắn.",
        "distribution": "Biển Đông (Hải Nam, Việt Nam).",
        "status": "Mọc ở mực hạ-duyên-hải trên rạn san hô nơi nước chảy mạnh.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Tseng 1941 : Bull. Fan Mem. Inst. Biol. Bot. X : 268, figs. 2-4; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 100."
    },
    {
        "idx": 97, "name": "Liagora pinnata", "author": "Harvey",
        "vn": "Rong Hải-giác lông-chim", "fam_vn": "Họ Hải-giác", "fam_lat": "Liagoraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Hải-giác", "gen_lat": "Liagora",
        "p": 105, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_32.png",
        "morphology": "Tản dài 10-20cm, khác biệt các loài Liagora khác nhờ lối phân nhánh lông chim rõ rệt (pinnate); trục chính to rõ, tẩm vôi xốp, nhánh bên mọc đối hoặc so le đối xứng.",
        "distribution": "Tây Ấn, Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Đới dưới triều trên đá san hô sâu 2-5m.",
        "specimen": "Mẫu lặn thu thập tại vịnh Nha-trang.",
        "literature": "Harvey 1853 : Nereis Bor. Amer. II : 138; Yamada 1938 : Spec. Liagora Japan : 27; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 416."
    },
    {
        "idx": 98, "name": "Dermonema frappieri", "author": "(Montagne & Millardet) Boergesen",
        "vn": "Rong Bì-tơ Phơ-ráp-pi-ê", "fam_vn": "Họ Bì-tơ", "fam_lat": "Dermonemataceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Bì-tơ", "gen_lat": "Dermonema",
        "p": 106, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_33.png",
        "morphology": "Tản sụn dai như cao su, không tẩm vôi, cao 4-8cm, màu nâu đỏ sẫm hay tía; chia nhánh lưỡng phân nhiều lần; nhánh tròn hình trụ rộng 1,5-2mm; tế-bào vỏ ngoài hình chùy xếp sít sao.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Cà-ná.",
        "status": "Bám chặt trên đá dốc đứng nơi sóng gió dữ dội nhất ở tầng trung-duyên-hải thượng.",
        "specimen": "Mẫu mũi Cà-ná và Hòn-chồng Nha-trang.",
        "literature": "Montagne & Millardet 1862 : Alg. Réunion : 22; Boergesen 1942 : Mar. Alg. Mauritius III : 42; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 414, fig. 25a."
    },
    {
        "idx": 99, "name": "Actinotrichia fragilis", "author": "(Forsskål) Boergesen",
        "vn": "Rong Xạ-mao giòn", "fam_vn": "Họ Xạ-mao", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Xạ-mao", "gen_lat": "Actinotrichia",
        "p": 107, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_34.png",
        "morphology": "Tản hình bụi bán cầu tròn, cao 4-8cm, màu đỏ hồng hay cam gạch; tẩm vôi cứng nhưng rất giòn, dễ gãy; chia nhánh lưỡng phân dày đặc; nhánh tròn mang các vòng lông tơ cứng tỏa tròn đặc trưng.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương, Biển Đỏ. Khắp bờ biển miền Trung và Nam Việt Nam.",
        "status": "Rất phổ biến trên các rạn san hô nông vùng triều thấp.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 190; Boergesen 1932 : Dansk Bot. Arkiv VIII : 6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 416, fig. 28b."
    },
    {
        "idx": 100, "name": "Galaxaura clavigera", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch chùy", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 108, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_35.png",
        "morphology": "Tản tẩm vôi cứng, cao 5-8cm, màu đỏ hồng; nhánh dẹp có bìa dày; phẫu thức ngang cho thấy lớp biểu bì gồm các tế-bào hình chùy hoặc chữ nhật mang cuống.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Rạn san hô sâu 1-3m nơi nước trong.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 76, pl. 13; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 417."
    },
    {
        "idx": 101, "name": "Galaxaura vietnamensis", "author": "Dawson",
        "vn": "Rong Đĩnh-thạch việtnam", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 109, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_36.png",
        "morphology": "Tản cao 6-10cm, tẩm vôi nhẵn bóng; chia nhánh lưỡng phân đều; các lóng hình trụ tròn hoặc hơi thắt eo ở khớp; màu hồng phấn tươi; cơ cấu giải phẫu vỏ ngoài đặc trưng.",
        "distribution": "Đặc hữu vùng duyên hải Việt Nam (Nha-trang).",
        "status": "Mọc trên nền đá san hô ở tầng hạ-duyên-hải.",
        "specimen": "Holotype thu tại Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 417, fig. 28c-e; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 105."
    },
    {
        "idx": 102, "name": "Galaxaura veprecula", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch gai", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 110, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_37.png",
        "morphology": "Tản dẹp rõ rệt, cao 5-8cm, màu đỏ nâu; mép nhánh có gờ răng cưa nhỏ; tẩm vôi chắc.",
        "distribution": "Thái-bình-dương, Ấn-độ-dương.",
        "status": "Mọc kẽ đá san hô dưới triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 80, pl. 16; Tanaka 1936 : Galaxaura Japan : 169."
    },
    {
        "idx": 103, "name": "Galaxaura ventricosa", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch phồng", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 110, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_38.png",
        "morphology": "Tản cao 6-10cm, các lóng phồng to hình bọng rỗng ở giữa, thắt hẹp ở hai đầu khớp nối; màu hồng nhạt.",
        "distribution": "Vùng biển nhiệt đới ấm.",
        "status": "Dưới triều, rạn san hô kín sóng.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 81, pl. 16."
    },
    {
        "idx": 104, "name": "Galaxaura obtusata", "author": "(Ellis & Solander) Lamouroux",
        "vn": "Rong Đĩnh-thạch đầu-tù", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 111, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_39.png",
        "morphology": "Tản tẩm vôi láng bóng, phân nhánh lưỡng phân; các lóng hình trụ tròn ngắn, mập, đầu lóng tù tròn; màu hồng san hô rất đẹp.",
        "distribution": "Khắp thế giới ở biển nhiệt đới. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Rạn san hô sâu 2-6m, vùng nước trong sạch.",
        "specimen": "Mẫu thu tại Hòn-mun, Nha-trang.",
        "literature": "Ellis & Solander 1786 : Nat. Hist. Zooph. : 113; Lamouroux 1816 : Hist. Polyp. Corall. : 262; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 418."
    },
    {
        "idx": 105, "name": "Galaxaura oblongata", "author": "(Solander) Lamouroux",
        "vn": "Rong Đĩnh-thạch thon-dài", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 112, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_40.png",
        "morphology": "Tản phân nhánh lưỡng phân nhiều lần tạo bụi tròn; lóng hình trụ thon dài, rộng 1-2mm, tẩm vôi đều; màu trắng hồng.",
        "distribution": "Toàn cầu ở vùng nhiệt đới. Rất phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc trên đá rạn san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang và Vũng-Tàu.",
        "literature": "Solander in Ellis & Solander 1786 : Nat. Hist. Zooph. : 114; Lamouroux 1816 : Hist. Polyp. Corall. : 262; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 417, fig. 27."
    },
    {
        "idx": 106, "name": "Galaxaura glabriuscula", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch nhẵn", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 113, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_41.png",
        "morphology": "Tản hình bụi cao 5-8cm; bề mặt nhẵn bóng không có lông cứng; các lóng hình trụ tròn dài; tẩm vôi xốp đều.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Tầng triều thấp ven đảo.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 56, pl. 7; Tanaka 1936 : Galaxaura Japan : 151."
    },
    {
        "idx": 107, "name": "Galaxaura fasciculata", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch chùm", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 114, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_42.png",
        "morphology": "Tản phủ đầy lông tơ dài màu đỏ nâu hay hung đỏ; các sợi lông mọc thành từng chùm dày đặc che khuất lớp vôi bên trong.",
        "distribution": "Ấn-độ-dương, Biển Đông, Thái-bình-dương. Gặp ở Hòn-tre, Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp nơi có sóng vỗ mạnh.",
        "specimen": "Mẫu Hòn-tre, Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 53, pl. 5; Tanaka 1936 : Galaxaura Japan : 147, pl. 34."
    },
    {
        "idx": 108, "name": "Galaxaura rudis", "author": "Kjellman",
        "vn": "Rong Đĩnh-thạch thô", "fam_vn": "Họ Đĩnh-thạch", "fam_lat": "Galaxauraceae",
        "ord_vn": "Bộ Hải-giác", "ord_lat": "Nemaliales", "gen_vn": "Chi Rong Đĩnh-thạch", "gen_lat": "Galaxaura",
        "p": 116, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_43.png",
        "morphology": "Tản xù xì thô ráp, phủ đầy lông cứng ngắn màu nâu xám; nhánh tròn to rộng 2mm, chia nhánh lưỡng phân.",
        "distribution": "Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Côn-đảo.",
        "status": "Bãi rạn san hô dưới triều.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Kjellman 1900 : Galaxaura : 43, pl. 2; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 417."
    },
    {
        "idx": 109, "name": "Gelidiella pannosa", "author": "(Feldmann) Feldmann & Hamel",
        "vn": "Rong Dực-thạch rách", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiellaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-thạch", "gen_lat": "Gelidiella",
        "p": 118, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_44.png",
        "morphology": "Tản nhỏ li ti, cao 2-5mm; thân bò mang các nhánh đứng hình sợi mảnh, rộng chỉ 50-100µ; cơ cấu trong không có sợi căn-trạng (hyphae); màu đỏ tía.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Tạo lớp nhung đỏ mịn bám trên vỏ ốc và đá ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Feldmann 1931 : Trav. Cryptog. : 157; Feldmann & Hamel 1934 : Observ. Gelid. : 11; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 422."
    },
    {
        "idx": 110, "name": "Gelidiella acerosa", "author": "(Forsskål) Feldmann & Hamel",
        "vn": "Rong Câu gai", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiellaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-thạch", "gen_lat": "Gelidiella",
        "p": 119, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_45.png",
        "morphology": "Tản sụn dai cứng, mọc thành bụi cao 5-10cm, màu vàng lục hay nâu đỏ; thân bò cho ra các thân đứng; nhánh bên mọc xếp thành 2 hàng sít sao như lông chim, ngọn nhọn như gai; không có căn-trạng trong tủy.",
        "distribution": "Toàn cầu ở các vùng biển nhiệt đới. Rất phong phú ở bờ biển Việt Nam từ Quảng-ninh đến Kiên-giang.",
        "status": "Rong kinh tế quan trọng dùng nấu thạch (agar-agar), mọc bám chặt trên rạn san hô và đá vùng triều.",
        "specimen": "Mẫu thu thập tại Nha-trang, Vũng-Tàu, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 190; Feldmann & Hamel 1934 : Observ. Gelid. : 9; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 422, fig. 33g."
    },
    {
        "idx": 111, "name": "Gelidiella myrioclada", "author": "(Boergesen) Feldmann & Hamel",
        "vn": "Rong Dực-thạch vạn-chi", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiellaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-thạch", "gen_lat": "Gelidiella",
        "p": 120, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_46.png",
        "morphology": "Bụi tơ mảnh chằng chịt, cao 1-2cm; nhánh đứng phân chia rất nhiều nhánh con ngắn tỏa ra các phía; màu đỏ sẫm.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá trong các hang hốc tối ở vùng triều.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Boergesen 1934 : Some Ind. Rhodophyceae IV : 5; Feldmann & Hamel 1934 : Observ. Gelid. : 10."
    },
    {
        "idx": 112, "name": "Gelidiella lubrica", "author": "(Kützing) Feldmann & Hamel",
        "vn": "Rong Dực-thạch trơn", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiellaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-thạch", "gen_lat": "Gelidiella",
        "p": 121, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_47.png",
        "morphology": "Tản bò chằng chịt, thân dẹp rộng 0,5-1mm, trơn láng; nhánh đứng cao 1-3cm; màu đỏ nâu bóng.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Trên đá ở mực trung-duyên-hải hạ.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Kützing 1843 : Phyc. Gen. : 405; Feldmann & Hamel 1934 : Observ. Gelid. : 10; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 422."
    },
    {
        "idx": 113, "name": "Gelidiella adnata", "author": "Dawson",
        "vn": "Rong Dực-thạch dính", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiellaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-thạch", "gen_lat": "Gelidiella",
        "p": 122, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_48.png",
        "morphology": "Tản bò sát dính chặt hoàn toàn vào đá bằng các rễ giả ngắn; nhánh đứng gần như tiêu giảm; các chùm tứ-bào-tử-phòng hình bầu dục mọc đứng trên thân bò.",
        "distribution": "Đặc hữu vùng duyên hải Việt Nam (Nha-trang).",
        "status": "Bám sát mặt đá vùng triều nơi sóng đánh mạnh.",
        "specimen": "Holotype thu tại Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 422, fig. 33f; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 118."
    },
    {
        "idx": 114, "name": "Pterocladia capillacea", "author": "(S.G. Gmelin) Bornet",
        "vn": "Rong Dực-tiết tóc", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-tiết", "gen_lat": "Pterocladia",
        "p": 123, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_49.png",
        "morphology": "Tản hình lông chim nhiều lần, cao 5-15cm, màu đỏ thẫm; thân dẹp, nhánh bên mọc đối xứng; phẫu thức ngang có sợi căn-trạng tập trung ở vùng tủy giữa; quả-nang chỉ có 1 lỗ thoát (khác Gelidium có 2 lỗ).",
        "distribution": "Khắp các biển ôn đới và nhiệt đới ấm thế giới. Việt Nam: Miền Trung.",
        "status": "Nguồn nguyên liệu agar chất lượng cao, mọc ở tầng hạ-duyên-hải trên đá gềnh.",
        "specimen": "Mẫu thu tại Qui-nhơn và Nha-trang.",
        "literature": "Gmelin 1768 : Hist. Fuc. : 146, pl. 15; Bornet in Bornet & Thuret 1876 : Notes Algol. I : 57, pl. 20; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 420."
    },
    {
        "idx": 115, "name": "Pterocladia parva", "author": "Dawson",
        "vn": "Rong Dực-tiết nhỏ", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-tiết", "gen_lat": "Pterocladia",
        "p": 124, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_50.png",
        "morphology": "Tản nhỏ cao chỉ 1-2cm, thân dẹp rộng 0,3-0,5mm; chia nhánh lông chim đơn giản; sợi căn-trạng ở tủy thưa thớt.",
        "distribution": "Biển Đông (Nha-trang).",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu Nha-trang (Dawson 1954).",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 420, fig. 31g-h."
    },
    {
        "idx": 116, "name": "Pterocladia pinnata", "author": "(Hudson) Papenfuss",
        "vn": "Rong Dực-tiết lông-chim", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Dực-tiết", "gen_lat": "Pterocladia",
        "p": 124, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_51.png",
        "morphology": "Tản hình lông chim 1-2 lần, cao 4-8cm, màu đỏ nâu; các nhánh thẳng, thon hai đầu; quả-nang đơn khoang mở 1 lỗ.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Trên đá vùng triều thấp.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Hudson 1762 : Fl. Angl. : 474; Papenfuss 1950 : Hydrobiologia II : 208."
    },
    {
        "idx": 117, "name": "Gelidium crinale", "author": "(Turner) Gaillon",
        "vn": "Rong Thạch lông", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 126, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_52.png",
        "morphology": "Tản mọc thành búi dày như bàn chải lông, cao 2-5cm, màu nâu đỏ sẫm; thân đứng hình sợi chỉ tròn hoặc hơi dẹp ở ngọn; căn-trạng dày đặc ở vùng vỏ trong; quả-nang có 2 lỗ thoát đối diện.",
        "distribution": "Toàn cầu. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc trên vách đá đứng và các bậc thềm đá ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang và Vũng-Tàu.",
        "literature": "Turner 1808 : Fuci I : 87; Gaillon 1828 : Dict. Sci. Nat. 53 : 362; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 420, fig. 31e."
    },
    {
        "idx": 118, "name": "Gelidium spathulatum", "author": "(Kützing) Bornet",
        "vn": "Rong Thạch hình-muỗng", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 128, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_53.png",
        "morphology": "Tản nhỏ cao 1-2cm; nhánh đứng dẹp, phần ngọn loe rộng ra thành hình muỗng hay hình thìa đặc trưng; màu đỏ tía đậm.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc bám trên đá ở vùng triều cao có sóng vỗ.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Kützing 1843 : Phyc. Gen. : 405; Bornet in Bornet & Thuret 1876 : Notes Algol. I : 58."
    },
    {
        "idx": 119, "name": "Gelidium pusillum", "author": "(Stackhouse) Le Jolis",
        "vn": "Rong Thạch nhỏ", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 129, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_54.png",
        "morphology": "Tản bò chằng chịt tạo thảm màu đỏ đen dày đặc trên đá, cao 0,5-1,5cm; thân bò hình trụ tròn; nhánh đứng dẹp hình bầu dục hay hình mũi mác; căn-trạng nhiều ở vùng vỏ.",
        "distribution": "Toàn cầu ở vùng duyên hải. Rất phổ biến tại Việt Nam.",
        "status": "Phủ kín mặt đá ở tầng trung-duyên-hải thượng nơi sóng mạnh.",
        "specimen": "Mẫu Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Stackhouse 1795 : Nereis Brit. : 16; Le Jolis 1863 : Liste Alg. Mar. Cherbourg : 139; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 420, fig. 31a-c."
    },
    {
        "idx": 120, "name": "Gelidium vietnamense", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Thạch việtnam", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 130, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_55.png",
        "morphology": "Tản cao 2-4cm, thân dẹp rộng 1-1,5mm; phân nhánh lưỡng phân hoặc so le; đặc sắc ở cấu trúc đáy tản và đầu ngọn phân nhánh hình quạt; quả-nang có 2 lỗ rõ rệt. Loài mới phát hiện cho khoa học.",
        "distribution": "Đặc hữu bờ biển Việt Nam (Khánh-hòa, Bình-thuận).",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Holotype thu tại Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 126, fig. 2.55."
    },
    {
        "idx": 121, "name": "Gelidium pulchellum", "author": "(Turner) Kützing",
        "vn": "Rong Thạch đẹp", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 131, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_56.png",
        "morphology": "Tản hình lông chim thanh nhã, cao 3-7cm, màu đỏ vang; thân chính dẹp, nhánh bên mọc đối đều đặn thon nhỏ dần về phía ngọn.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải trên đá san hô.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Turner 1819 : Fuci IV : 97; Kützing 1868 : Tab. Phyc. XVIII : 18; Feldmann & Hamel 1936 : Gelid. : 119."
    },
    {
        "idx": 122, "name": "Gelidium divaricatum", "author": "Martens",
        "vn": "Rong Thạch giẽ", "fam_vn": "Họ Thạch-hoa", "fam_lat": "Gelidiaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Thạch-hoa", "gen_lat": "Gelidium",
        "p": 132, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_57.png",
        "morphology": "Tản bò dính chặt trên đá tạo thảm mỏng dẹt; nhánh đứng dẹp, ngắn chỉ 3-8mm, rẽ góc rất rộng sang hai bên; màu đỏ nâu sẫm.",
        "distribution": "Nhật-bản, Trung-quốc, Việt Nam (Hải-phòng, Nha-trang).",
        "status": "Mọc thành mảng dày đặc trên đá ở tầng thượng-duyên-hải nơi sóng dữ.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Martens 1866 : Preuss. Exped. Ost-Asien : 30, pl. 8; Okamura 1914 : Icones Jap. Alg. III : 14, pl. 106."
    },
    {
        "idx": 123, "name": "Wurdemannia miniata", "author": "(Sprengel) Feldmann & Hamel",
        "vn": "Rong Vua-đờ-man chu-sa", "fam_vn": "Họ Vua-đờ-man", "fam_lat": "Wurdemanniaceae",
        "ord_vn": "Bộ Thạch-hoa", "ord_lat": "Gelidiales", "gen_vn": "Chi Rong Vua-đờ-man", "gen_lat": "Wurdemannia",
        "p": 133, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_58.png",
        "morphology": "Tản sụn hình sợi tròn hay hơi dẹp, cao 2-5cm, màu đỏ chu sa hay cam gạch; chia nhánh bất quy tắc; cơ cấu trong gồm các tế-bào tủy dài bao quanh bởi các tế-bào nhỏ chứa chất màu; không có sợi căn-trạng.",
        "distribution": "Các vùng biển nhiệt đới ấm toàn cầu. Việt Nam: Nha-trang, Vũng-Tàu, Phú-quốc.",
        "status": "Mọc xen lẫn trong các rạn san hô và thảm rong khác ở tầng triều dưới.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Sprengel 1827 : Syst. Veg. IV : 340; Feldmann & Hamel 1934 : Observ. Gelid. : 13; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 424, fig. 35."
    },
    {
        "idx": 124, "name": "Gloiopeltis minuta", "author": "Kylin",
        "vn": "Rong Keo-phiến nhỏ", "fam_vn": "Họ Nhầy-bì", "fam_lat": "Endocladiaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Keo-phiến", "gen_lat": "Gloiopeltis",
        "p": 134, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_59.png",
        "morphology": "Tản nhầy mềm hình sợi ống rỗng nhỏ, cao 1-2cm, màu nâu đỏ; phân nhánh lưỡng phân hoặc so le; lớp vỏ ngoài gồm các chuỗi tế-bào tỏa tròn dính chặt trong chất nhầy.",
        "distribution": "Nhật-bản, Việt Nam (Nha-trang).",
        "status": "Mọc trên đá ở tầng trung-duyên-hải.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Kylin 1956 : Gatt. Rhodophyc. : 202; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 130."
    },
    {
        "idx": 125, "name": "Desmia hornemannii", "author": "Lyngbye",
        "vn": "Rong Đét-mi Hóoc-nơ-man", "fam_vn": "Họ Băng-tảo", "fam_lat": "Rhizophyllidaceae",
        "ord_vn": "Bộ Ẩn-khách", "ord_lat": "Gigartinales", "gen_vn": "Chi Rong Đét-mi", "gen_lat": "Desmia",
        "p": 135, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_60.png",
        "morphology": "Tản hình dải dẹp màu đỏ cam tươi rất rực rỡ, cao 5-10cm; chia nhánh lông chim nhiều lần trong cùng một mặt phẳng; các nhánh con cuốn cong hình móc câu ở ngọn; có mùi tanh nồng đặc trưng do chứa các hợp chất halogenua hữu cơ chống ăn thực vật.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương nhiệt đới. Việt Nam: Duyên hải Khánh-hòa, Ninh-thuận, Bình-thuận.",
        "status": "Rất đẹp mắt, mọc bám trên gờ đá san hô nơi sóng vỗ mạnh ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang và Côn-đảo.",
        "literature": "Lyngbye 1819 : Hydrophyt. Dan. : 35, tab. 7b; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 426, fig. 37."
    },
    {
        "idx": 126, "name": "Peyssonnelia calcea", "author": "Heydrich",
        "vn": "Rong Bôi-sơn vôi", "fam_vn": "Họ Bôi-sơn", "fam_lat": "Peyssonneliaceae",
        "ord_vn": "Bộ Bôi-sơn", "ord_lat": "Peyssonneliales", "gen_vn": "Chi Rong Bôi-sơn", "gen_lat": "Peyssonnelia",
        "p": 137, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_61.png",
        "morphology": "Tản dạng vỏ tẩm vôi dày cứng chắc, màu hồng phấn hay trắng xám; bám chặt như lớp men trên san hô chết và đá; mặt dưới có lớp rễ tẩm vôi bám chắc vào giá thể.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Góp phần quan trọng vào quá trình tạo rạn và gắn kết khung xương san hô.",
        "specimen": "Mẫu rạn san hô Nha-trang (Dawson 1954).",
        "literature": "Heydrich 1897 : Bibl. Bot. VII : 12; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 425, fig. 36."
    },
    {
        "idx": 127, "name": "Peyssonnelia rubra", "author": "(Greville) J. Agardh",
        "vn": "Rong Bôi-sơn đỏ", "fam_vn": "Họ Bôi-sơn", "fam_lat": "Peyssonneliaceae",
        "ord_vn": "Bộ Bôi-sơn", "ord_lat": "Peyssonneliales", "gen_vn": "Chi Rong Bôi-sơn", "gen_lat": "Peyssonnelia",
        "p": 138, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_62.png",
        "morphology": "Tản hình phiến màng mỏng tẩm vôi ở mặt dưới, màu đỏ thẫm tươi; mép phiến lượn sóng và không dính sát hoàn toàn vào đá; mặt dưới mang nhiều rễ giả đơn bào.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Khắp duyên hải miền Trung Việt Nam.",
        "status": "Mọc trong hang hốc tối và mặt dưới các khối san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-mun, Nha-trang.",
        "literature": "Greville in Linnaea 1827 : 298; J. Agardh 1851 : Sp. Alg. II : 502; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 424."
    },
    {
        "idx": 128, "name": "Peyssonnelia gunniana", "author": "J. Agardh",
        "vn": "Rong Bôi-sơn Gân", "fam_vn": "Họ Bôi-sơn", "fam_lat": "Peyssonneliaceae",
        "ord_vn": "Bộ Bôi-sơn", "ord_lat": "Peyssonneliales", "gen_vn": "Chi Rong Bôi-sơn", "gen_lat": "Peyssonnelia",
        "p": 139, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_63.png",
        "morphology": "Tản hình vỏ dày tẩm vôi, màu đỏ gạch; cấu trúc phẫu thức ngang gồm tầng đáy tỏa tròn và các hàng tế bào đứng phân chia đều; nốt sinh sản (nemathecia) lồi rõ trên mặt tản.",
        "distribution": "Úc-châu, Ấn-độ-dương, Biển Đông. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Trên đá và vỏ ốc biển ở tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1876 : Epicrisis : 387; Weber van Bosse 1921 : Siboga : 272."
    },
    {
        "idx": 129, "name": "Hildenbrandia prototypus", "author": "Nardo",
        "vn": "Rong Hân-đơn nguyên-hình", "fam_vn": "Họ Hân-đơn", "fam_lat": "Hildenbrandiaceae",
        "ord_vn": "Bộ Hân-đơn", "ord_lat": "Hildenbrandiales", "gen_vn": "Chi Rong Hân-đơn", "gen_lat": "Hildenbrandia",
        "p": 140, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_64.png",
        "morphology": "Tản dạng vỏ màng mỏng như sơn quét lên đá, màu đỏ máu tươi hay nâu đỏ, không tẩm vôi; bám cực kỳ chặt vào đá không thể cạo ra nguyên vẹn; phẫu thức ngang gồm các hàng tế-bào nhỏ xếp thẳng đứng; ổ bào-tử (conceptacles) chìm trong tản.",
        "distribution": "Toàn cầu. Phổ biến khắp bờ biển Việt Nam.",
        "status": "Phủ kín mặt đá ở tầng trung-duyên-hải và thượng-duyên-hải, chịu đựng sóng đập và nắng gắt liên tục.",
        "specimen": "Mẫu bãi đá Nha-trang và Vũng-Tàu.",
        "literature": "Nardo 1834 : Isis : 675; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 424, fig. 36a-b."
    },
    {
        "idx": 130, "name": "Amphiroa fragilissima", "author": "(Linnaeus) J.V. Lamouroux",
        "vn": "Rong San-hô giòn", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong Lưỡng-thoa", "gen_lat": "Amphiroa",
        "p": 142, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_65.png",
        "morphology": "Tản tẩm vôi cứng như đá san hô, cao 3-8cm, màu trắng hồng; chia nhánh lưỡng phân hoặc tam phân dày đặc; nhánh gồm các đốt vôi hình trụ tròn dài 2-4mm, ngăn cách bởi các khớp nối hữu cơ không tẩm vôi rất dẻo nhưng nhánh giòn dễ gãy khi khô; các ổ khái-bao (conceptacles) lồi thành nốt bên hông đốt.",
        "distribution": "Khắp các vùng biển nhiệt đới trên thế giới. Rất phong phú ở các rạn san hô Việt Nam.",
        "status": "Thành phần quan trọng tạo rạn san hô, tạo thành những búi đệm dày đặc ở vùng triều thấp và dưới triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Linnaeus 1758 : Syst. Nat. ed. 10 : 815; Lamouroux 1816 : Hist. Polyp. Corall. : 298; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430, fig. 40g-h."
    },
    {
        "idx": 131, "name": "Jania ungulata", "author": "(Yendo) Yendo",
        "vn": "Rong San-hô hình-móng", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong San-hô-tơ", "gen_lat": "Jania",
        "p": 143, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_66.png",
        "morphology": "Tản nhỏ nhắn thanh mảnh, cao 1-3cm, tẩm vôi màu hồng phấn; phân nhánh lưỡng phân rẽ góc hẹp; các đốt ngọn dẹp phồng ra hình móng ngựa hoặc hình quạt đặc trưng.",
        "distribution": "Nhật-bản, Biển Đông, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Phụ sinh phổ biến trên Turbinaria, Sargassum và rạn san hô nông.",
        "specimen": "Mẫu phụ sinh tại vịnh Nha-trang.",
        "literature": "Yendo 1902 : Corall. Jap. : 27, pl. 3, figs. 7-8; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430, fig. 40e."
    },
    {
        "idx": 132, "name": "Jania adhaerens", "author": "J.V. Lamouroux",
        "vn": "Rong San-hô dính", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong San-hô-tơ", "gen_lat": "Jania",
        "p": 144, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_67.png",
        "morphology": "Búi tơ vôi hình bán cầu dày đặc, cao 1-4cm, màu hồng tươi; chia nhánh đôi rẽ góc rộng (60-90°); các đốt vôi hình sợi chỉ tròn, dài gấp 4-8 lần đường kính (rộng 100-150µ); các nhánh tự dính vào nhau bằng đĩa dính nhỏ.",
        "distribution": "Biển nhiệt đới và cận nhiệt đới toàn cầu. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc bám trên đá, san hô hoặc phụ sinh trên các loài rong lớn ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu bãi đá Nha-trang và Vũng-Tàu.",
        "literature": "Lamouroux 1816 : Hist. Polyp. Corall. : 270; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430, fig. 40a."
    },
    {
        "idx": 133, "name": "Jania rubens", "author": "(Linnaeus) J.V. Lamouroux",
        "vn": "Rong San-hô đỏ", "fam_vn": "Họ San-hô", "fam_lat": "Corallinaceae",
        "ord_vn": "Bộ San-hô", "ord_lat": "Corallinales", "gen_vn": "Chi Rong San-hô-tơ", "gen_lat": "Jania",
        "p": 145, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_68.png",
        "morphology": "Tản hình bụi tơ vôi cao 2-5cm, màu đỏ hồng tía; phân nhánh lưỡng phân rẽ góc nhọn (30-45°); các đốt vôi hình trụ thon đều, các nhánh ngọn nhọn dần; ổ khái-bao mọc ở chót đốt ngọn mang 2 sừng nhỏ.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đỏ, Biển Đông. Việt Nam: Miền Trung.",
        "status": "Phụ sinh trên rong Cladostephus, Cystoseira và đá rạn san hô tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Linnaeus 1758 : Syst. Nat. ed. 10 : 806; Lamouroux 1816 : Hist. Polyp. Corall. : 272; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 430."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH3_DATA)} figures for Batch 3...')
    for sp in BATCH3_DATA:
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
    print('Querying WoRMS API in chunks for 66 species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH3_DATA), chunk_size):
        chunk = BATCH3_DATA[i:i+chunk_size]
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
        
    for sp, item in zip(BATCH3_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH3_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH3_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 3...')
    rows = []
    for sp in BATCH3_DATA:
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch3.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 3 build completed successfully!')
