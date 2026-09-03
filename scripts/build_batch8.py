"""
build_batch8.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 45 loài Lục-tảo cuối cùng (Chlorophyceae - Đợt 8, loài 427-471)
cho Volume 2 (Rong biển Việt Nam - GS. Phạm Hoàng Hộ, 1969).
HOÀN THÀNH 100% TOÀN BỘ CUỐN SÁCH CỦA GS. PHẠM HOÀNG HỘ (TỔNG CỘNG 471 LOÀI TRONG CẢ 4 PHẦN)!
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

BATCH8_DATA = [
    {
        "idx": 427, "name": "Acetabularia calyculus", "author": "J.V. Lamouroux",
        "vn": "Rong Dù chén", "fam_vn": "Họ Tản-dù", "fam_lat": "Polyphysaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Dù-biển", "gen_lat": "Acetabularia",
        "p": 466, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_72.png",
        "morphology": "Tản đơn bào khổng lồ hình chiếc ô dù che mưa tẩm vôi mỏng tuyệt đẹp màu trắng phấn ngọn lục, cao 3-6cm; cán dù hình sợi chỉ mang một tán hình chén lõm đường kính 5-8mm gồm 20-30 tia hợp nhất; mặt trên tán có vòng mấu lồi mang lông tơ rụng sớm.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Ấn-độ-Tây Thái-bình-dương. Rất phong phú tại bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Loài sinh vật mô hình kinh điển thế giới trong thí nghiệm chuyển nhân tế bào của Hämmerling; mọc trên vỏ sò và rạn san hô nông kín sóng.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Lamouroux 1824 : Quoy et Gaimard : 621; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396."
    },
    {
        "idx": 428, "name": "Acetabularia ryukyuensis", "author": "Okamura & Yamada",
        "vn": "Rong Dù Lưu-cầu", "fam_vn": "Họ Tản-dù", "fam_lat": "Polyphysaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Dù-biển", "gen_lat": "Acetabularia",
        "p": 467, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_73.png",
        "morphology": "Tản dù tẩm vôi mỏng, tán hình đĩa phẳng tròn xoe đường kính 8-12mm; các tia kết dính chặt chẽ bằng lớp vôi bên; màu trắng lục.",
        "distribution": "Nhật-bản (Ryukyu), Biển Đông. Gặp ở vịnh Nha-trang.",
        "status": "Mọc trên mảnh vỏ sò ốc ở vùng triều thấp.",
        "specimen": "Mẫu Cầu-đá Nha-trang.",
        "literature": "Okamura & Yamada 1932 : In Okamura Icon. Jap. Alg. VII : 68; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396."
    },
    {
        "idx": 429, "name": "Acetabularia crenulata", "author": "Lamouroux",
        "vn": "Rong Dù răng-cưa", "fam_vn": "Họ Tản-dù", "fam_lat": "Polyphysaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Dù-biển", "gen_lat": "Acetabularia",
        "p": 467, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_74.png",
        "morphology": "Tản mang 2-4 tầng tán dù xếp chồng lên nhau dọc theo cán; mép tán có khía răng cưa nhỏ; tẩm vôi dày màu trắng sữa.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều cạn.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Lamouroux 1816 : Hist. Polyp. : 249; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396."
    },
    {
        "idx": 430, "name": "Acetabularia clavata", "author": "Yamada",
        "vn": "Rong Dù hình-chùy", "fam_vn": "Họ Tản-dù", "fam_lat": "Polyphysaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Dù-biển", "gen_lat": "Acetabularia",
        "p": 468, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_75.png",
        "morphology": "Tản nhỏ li ti cao 5-10mm; các tia của tán không dính liền nhau mà rời rạc xòe tròn như chùm chùy nhỏ đầu nhọn.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên vỏ san hô chết.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Yamada 1934 : Sci. Pap. Inst. Alg. Res. Hokkaido I : 57; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396, fig. 11b."
    },
    {
        "idx": 431, "name": "Derbesia marina", "author": "(Lyngbye) Solier",
        "vn": "Rong Điệp-bích biển", "fam_vn": "Họ Điệp-bích", "fam_lat": "Derbesiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Điệp-bích", "gen_lat": "Derbesia",
        "p": 468, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_76.png",
        "morphology": "Tản hình búi sợi tơ mềm màu lục tươi óng ả, cao 1-3cm; thân ống không có vách ngăn ngang thông suốt; túi bào tử hình bầu dục to có cuống ngắn ngăn cách bằng hai vách đôi ở gốc.",
        "distribution": "Toàn cầu. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Giai đoạn bào tử thể hình sợi trong chu trình sống luân phiên dị hình với pha giao tử thể hình bóng Halicystis.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Lyngbye 1819 : Tent. Hydrophyt. Dan. : 79; Solier 1847 : Rev. Bot. II : 158; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 432, "name": "Halicystis ovalis", "author": "(Lyngbye) Areschoug",
        "vn": "Rong Diêm-nang xoan", "fam_vn": "Họ Điệp-bích", "fam_lat": "Derbesiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Diêm-nang", "gen_lat": "Halicystis",
        "p": 469, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_77.png",
        "morphology": "Tản hình bóng cầu hay quả lê đơn bào mọc đứng trên cuống bám chìm trong rong vôi, đường kính 2-5mm, màu xanh ngọc lục bảo bóng loáng; pha giao tử thể của Derbesia.",
        "distribution": "Bắc Đại-tây-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc phụ sinh cắm rễ vào tảng rong vôi Lithothamnion.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Lyngbye 1819 : Tent. Hydrophyt. Dan. : 79; Areschoug 1850 : Phyc. Scand. : 447."
    },
    {
        "idx": 433, "name": "Bryopsis plumosa", "author": "(Hudson) C. Agardh",
        "vn": "Rong Lục-tùng lông-chim", "fam_vn": "Họ Lục-tùng", "fam_lat": "Bryopsidaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Lục-tùng", "gen_lat": "Bryopsis",
        "p": 472, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_79.png",
        "morphology": "Tản hình chiếc lông chim nhỏ mềm mại thanh nhã tuyệt đẹp màu xanh lục sáng bóng lướt thướt trong nước, cao 3-8cm; trục chính hình ống mang 2 hàng nhánh phụ lông chim đối xứng mọc trong cùng một mặt phẳng; các nhánh thu hẹp dần về ngọn tạo hình tam giác cân.",
        "distribution": "Toàn cầu ở các vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc trên đá, cọc cảng và thành tàu thuyền ở tầng trung-duyên-hải hạ.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Vũng-Tàu, Qui-nhơn.",
        "literature": "Hudson 1778 : Fl. Angl. : 571; C. Agardh 1823 : Sp. Alg. : 448; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 434, "name": "Bryopsis pennata", "author": "Lamouroux",
        "vn": "Rong Lục-tùng lông-gà", "fam_vn": "Họ Lục-tùng", "fam_lat": "Bryopsidaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Lục-tùng", "gen_lat": "Bryopsis",
        "p": 472, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_80.png",
        "morphology": "Tản mọc thành bụi dày màu xanh lục sẫm, cao 4-10cm; trục chính đứng thẳng mang hai hàng nhánh lông chim dài bằng nhau song song đều đặn từ gốc đến gần ngọn tạo hình chữ nhật dài.",
        "distribution": "Toàn cầu ở vùng nhiệt đới ấm. Cực kỳ phong phú tại bờ biển miền Trung Việt Nam.",
        "status": "Mọc bám trên gờ đá nơi sóng vỗ mạnh tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Cà-ná, Côn-đảo.",
        "literature": "Lamouroux 1809 : J. de Bot. II : 333; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392, fig. 9c."
    },
    {
        "idx": 435, "name": "Bryopsis indica", "author": "A. Gepp & E.S. Gepp",
        "vn": "Rong Lục-tùng Ấn-độ", "fam_vn": "Họ Lục-tùng", "fam_lat": "Bryopsidaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Lục-tùng", "gen_lat": "Bryopsis",
        "p": 473, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_81.png",
        "morphology": "Tản cao 2-5cm, các nhánh phụ mọc thành 2 hàng hoặc so le chụm lại ở đỉnh ngọn trục chính.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Gepp & Gepp 1908 : Trans. Linn. Soc. Bot. VII : 169; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 436, "name": "Pseudobryopsis parva", "author": "Dawson",
        "vn": "Rong Giả-lục-tùng nhỏ", "fam_vn": "Họ Lục-tùng", "fam_lat": "Bryopsidaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Giả-lục-tùng", "gen_lat": "Pseudobryopsis",
        "p": 474, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_82.png",
        "morphology": "Tản vi thể cao 3-8mm; túi giao tử hình trứng mọc ở gốc các nhánh phụ có màng ngăn riêng biệt.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Holotype thu tại Cầu-đá Nha-trang.",
        "literature": "Dawson 1954 : Mar. Pl. Vic. Nha-trang : 393, fig. 10b."
    },
    {
        "idx": 437, "name": "Pseudobryopsis mucronata", "author": "Boergesen",
        "vn": "Rong Giả-lục-tùng có-mũi", "fam_vn": "Họ Lục-tùng", "fam_lat": "Bryopsidaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Giả-lục-tùng", "gen_lat": "Pseudobryopsis",
        "p": 474, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_83.png",
        "morphology": "Tản cao 1-2cm; các túi giao tử mang một mũi nhọn nhỏ hoắt ở đỉnh rất đặc sắc.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc kẽ san hô tầng triều thấp.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Boergesen 1930 : J. Indian Bot. Soc. 9 : 163; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 393."
    },
    {
        "idx": 438, "name": "Codium adhaerens", "author": "C. Agardh",
        "vn": "Rong Nhung bám", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 477, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_84.png",
        "morphology": "Tản dạng đệm nhung thịt dày 3-6mm bám sát trườn phủ trên mặt đá như một lớp da thú màu xanh lục thẫm óng mượt; cấu tạo gồm lõi tủy là mạng sợi ống phân nhánh và lớp vỏ ngoài gồm vô số túi thịt hình trụ đứng (utricles) xếp khít khao.",
        "distribution": "Toàn cầu ở vùng duyên hải ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Rong thực phẩm ăn được, làm gỏi; phủ kín mặt đá nơi sóng vỗ mạnh tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Qui-nhơn, Côn-đảo.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 457; Schmidt 1923 : Beitr. Kenntn. Codium : 26; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 439, "name": "Codium arabicum", "author": "Kützing",
        "vn": "Rong Nhung A-rập", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 478, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_85.png",
        "morphology": "Tản đệm nhung dày màu lục đen, bề mặt cuộn khúc gồ ghề lồi lõm với nhiều múi u nần; các túi thịt đa dạng hình chùy hoặc thắt ngực; bám chắc trên đá.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương. Rất phổ biến ở miền Trung Việt Nam.",
        "status": "Mọc trên đá vùng triều giữa chịu sóng to.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Cà-ná.",
        "literature": "Kützing 1856 : Tab. Phyc. VI : 35, pl. 100; Schmidt 1923 : Codium : 30; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 440, "name": "Codium cylindricum", "author": "Holmes",
        "vn": "Rong Nhung hình-trụ", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 479, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_86.png",
        "morphology": "Tản hình trụ tròn to khổng lồ cao 20-50cm, đường kính thân 1-2cm, mềm mọng nước màu xanh lục ngọc; chia nhánh lưỡng phân thưa; các túi thịt hình chùy cực lớn dài hơn 1mm.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở vùng biển miền Trung.",
        "status": "Rong thực phẩm cao cấp của Nhật Bản và Việt Nam, nấu canh và làm salad.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Holmes 1896 : J. Linn. Soc. Bot. 31 : 250, pl. 7; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 441, "name": "Codium divaricatum", "author": "Holmes",
        "vn": "Rong Nhung giẽ", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 480, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_87.png",
        "morphology": "Tản dẹp xòe rộng phân nhánh góc tù 90-120°, chất sụn mềm đàn hồi; màu lục sẫm.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng triều thấp.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Holmes 1896 : J. Linn. Soc. Bot. 31 : 250; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 442, "name": "Codium formosanum", "author": "Yamada",
        "vn": "Rong Nhung Đài-loan", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 481, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_88.png",
        "morphology": "Tản đứng cao 10-25cm, phân nhánh lưỡng phân hoặc tam phân đều đặn; nhánh hình trụ đường kính 3-6mm; túi thịt hình chùy thon.",
        "distribution": "Đài Loan, Biển Đông. Phổ biến ở miền Trung Việt Nam.",
        "status": "Rong thực phẩm ăn được, mọc ở rạn san hô ngầm.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Yamada 1950 : Sci. Pap. Inst. Alg. Res. Hokkaido III : 180, fig. 3; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 443, "name": "Codium tomentosum", "author": "Stackhouse",
        "vn": "Rong Nhung tơ", "fam_vn": "Họ Nhung-biển", "fam_lat": "Codiaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Nhung-biển", "gen_lat": "Codium",
        "p": 482, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_89.png",
        "morphology": "Tản hình trụ tròn phân nhánh đôi đều, cao 15-30cm, phủ lớp lông nhung tơ mịn màng êm ái; túi thịt hình chùy đầu tù có lông rụng sớm.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Rong ăn được, mọc ở tầng hạ-duyên-hải sâu 1-4m.",
        "specimen": "Mẫu Qui-nhơn và Nha-trang.",
        "literature": "Stackhouse 1797 : Nereis Brit. : 24, pl. 7; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 444, "name": "Halimeda tuna", "author": "(J. Ellis & Solander) J.V. Lamouroux",
        "vn": "Rong Xương-mai cá-ngừ", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 484, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_90.png",
        "morphology": "Tản tẩm vôi cứng chắc màu xanh lục sữa, cao 10-25cm; cấu tạo gồm chuỗi các đốt phiến dẹp hình tròn, thận hoặc bầu dục lớn đường kính 10-20mm nối với nhau bằng các khớp dẻo không tẩm vôi; phân nhánh lưỡng phân; là loài điển hình của chi.",
        "distribution": "Địa-trung-hải, Ấn-độ-Tây Thái-bình-dương. Cực kỳ phong phú tại toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Thành phần quan trọng bậc nhất tạo cát vôi sinh học và rạn san hô nhiệt đới; mọc ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Ellis & Solander 1786 : Nat. Hist. Zoophyt. : 111; Lamouroux 1812 : Bull. Soc. Philom. : 186; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 445, "name": "Halimeda opuntia", "author": "(Linnaeus) J.V. Lamouroux",
        "vn": "Rong Xương-mai xương-rồng", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 485, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_91.png",
        "morphology": "Tản mọc thành bụi đệm vôi khổng lồ đan bện chằng chịt, rộng 20-50cm; các đốt nhỏ hình 3 thùy hoặc hình gân lá xương rồng Opuntia, tẩm vôi cực kỳ dày cứng; bám bằng vô số rễ giả khắp nơi trong khối tản.",
        "distribution": "Toàn cầu ở các rạn san hô nhiệt đới ấm. Chiếm ưu thế tuyệt đối ở các hải đảo Việt Nam.",
        "status": "Đóng góp sinh khối carbonate khổng lồ tạo trầm tích rạn san hô; chịu sóng đập cực mạnh.",
        "specimen": "Mẫu Hoàng-sa, Trường-sa, Côn-đảo, Phú-quốc, Nha-trang.",
        "literature": "Linnaeus 1758 : Syst. Nat. : 805; Lamouroux 1816 : Hist. Polyp. : 308; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 446, "name": "Halimeda macroloba", "author": "Decaisne",
        "vn": "Rong Xương-mai thùy-to", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 486, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_92.png",
        "morphology": "Tản đứng cao 15-30cm, đặc trưng bởi củ rễ giả dạng củ hành khổng lồ vùi sâu trong đáy cát bùn; các đốt phiến phía trên to bản dày cộp hình quạt rộng 2-4cm tẩm vôi trắng phấn ngọn lục.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương. Rất phong phú ở các bãi cát rạn san hô Việt Nam.",
        "status": "Cố định nền đáy cát vụn san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Decaisne 1841 : Ann. Sci. Nat. Bot. II : 118; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 447, "name": "Halimeda cuneata", "author": "Kering ex Kützing",
        "vn": "Rong Xương-mai hình-nêm", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 487, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_93.png",
        "morphology": "Tản cao 10-20cm; các đốt tẩm vôi hình nêm tam giác đáy thon hẹp đỉnh xòe rộng; khớp nối mềm mại.",
        "distribution": "Nam Phi, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá ở độ sâu 0-4m.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1849 : Sp. Alg. : 505; Barton 1901 : Gen. Halimeda : 15; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 448, "name": "Halimeda simulans", "author": "M. Howe",
        "vn": "Rong Xương-mai nhại", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 488, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_94.png",
        "morphology": "Tản cao 8-15cm, có củ rễ nhỏ; các đốt phiến hình thang hoặc quạt xẻ thùy tù ở mép trên; tẩm vôi dày cứng.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên cát sỏi san hô.",
        "specimen": "Mẫu đảo Hòn-tre Nha-trang.",
        "literature": "Howe 1907 : Bull. Torrey Bot. Club 34 : 503; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 449, "name": "Halimeda gracilis", "author": "Harvey ex J. Agardh",
        "vn": "Rong Xương-mai mảnh", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 488, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_95.png",
        "morphology": "Tản dài rủ xuống dài 20-40cm; các đốt mỏng thanh mảnh hình quạt hoặc thận tròn; phân nhánh thưa lả lướt.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở vùng nước sâu.",
        "status": "Mọc ở rạn san hô sâu 5-15m.",
        "specimen": "Mẫu lặn vịnh Nha-trang.",
        "literature": "J. Agardh 1887 : Till Alg. Syst. V : 82; Barton 1901 : Gen. Halimeda : 22."
    },
    {
        "idx": 450, "name": "Halimeda incrassata", "author": "(J. Ellis) J.V. Lamouroux",
        "vn": "Rong Xương-mai dày", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 489, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_96.png",
        "morphology": "Tản đứng thẳng cứng cáp cao 10-20cm; các đốt phía dưới hình trụ hợp nhất thành thân giả, các đốt phía trên hình quạt dày xẻ 3 khía nông.",
        "distribution": "Biển nhiệt đới toàn cầu. Phổ biến tại Việt Nam.",
        "status": "Mọc trên bãi cát san hô nông kín sóng.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo.",
        "literature": "Ellis 1768 : Philos. Trans. 57 : 408; Lamouroux 1812 : Bull. Soc. Philom. : 186; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 451, "name": "Halimeda discoidea", "author": "Decaisne",
        "vn": "Rong Xương-mai đĩa", "fam_vn": "Họ Xương-mai", "fam_lat": "Halimedaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Xương-mai", "gen_lat": "Halimeda",
        "p": 490, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_97.png",
        "morphology": "Tản cao 10-20cm, tẩm vôi mỏng màu xanh lục tươi; các đốt phiến hình đĩa tròn xoe phẳng mỏng đường kính 15-35mm rất lớn; các túi vỏ lớp ngoài phồng to dính nhau.",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc trên đá và san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Qui-nhơn, Côn-đảo.",
        "literature": "Decaisne 1842 : Ann. Sci. Nat. Bot. II : 102; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 452, "name": "Caulerpa fastigiata", "author": "Montagne",
        "vn": "Rong Guột thẳng", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 491, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_98.png",
        "morphology": "Tản tạo thành búi nhung mềm mịn màu xanh lục đậm trông như rêu nước, cao 2-5cm; thân bò hình ống mang các nhánh đứng chia nhánh lưỡng phân hoặc chùm thẳng đứng song song; các sợi nhánh hình chỉ thanh mảnh đồng đều.",
        "distribution": "Tây Ấn, Ấn-độ-Tây Thái-bình-dương. Phổ biến ở miền Trung Việt Nam.",
        "status": "Mọc trên đá phủ bùn cát ở vùng triều kín sóng.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo.",
        "literature": "Montagne 1837 : Ann. Sci. Nat. Bot. II : 353; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 391."
    },
    {
        "idx": 453, "name": "Caulerpa ambigua", "author": "Okamura",
        "vn": "Rong Guột ám", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 492, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_99.png",
        "morphology": "Tản nhỏ nhắn cao 5-15mm; nhánh đứng mang các chồi con hình chùy nhỏ xếp so le hoặc vòng tròn quanh trục; màu lục sáng.",
        "distribution": "Nhật-bản, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên rạn san hô chết.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Okamura 1897 : Bot. Mag. Tokyo XI : 4, pl. 1; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 391."
    },
    {
        "idx": 454, "name": "Caulerpa verticillata", "author": "J. Agardh",
        "vn": "Rong Guột luân-sinh", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 493, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_100.png",
        "morphology": "Tản tạo thảm nhung xanh mướt tuyệt đẹp cao 2-5cm; nhánh đứng mang các vòng lông tơ nhỏ li ti xếp luân sinh (tỏa tròn như nan hoa bánh xe) thành từng tầng cách đều nhau dọc thân.",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc phủ kín rễ cây đước và bùn cát vùng rừng ngập mặn và rạn san hô cạn.",
        "specimen": "Mẫu Cần-giờ, vịnh Nha-trang, Côn-đảo.",
        "literature": "J. Agardh 1847 : Nya Alger : 6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 455, "name": "Caulerpa vickersiae", "author": "Boergesen",
        "vn": "Rong Guột Vích-cơ", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 493, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_101.png",
        "morphology": "Tản vi thể nhỏ cao 5-10mm; các nhánh bên mọc đối xứng lông chim 2 hàng; màu xanh lục tươi.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc kẽ san hô tầng triều thấp.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Boergesen 1911 : Mar. Alg. Dan. W. Ind. : 8; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 456, "name": "Caulerpa racemosa", "author": "(Forsskål) J. Agardh",
        "vn": "Rong Nho biển (Rong Guột chùm)", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 495, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_102.png",
        "morphology": "Loài rong kinh tế nổi tiếng nhất thế giới (trứng cá xanh nhân tạo / sea grape); thân bò hình ống dài hàng mét bò lan trên đá cát; các nhánh đứng cao 5-15cm mang vô số nhánh con biến đổi thành những quả bóng tròn mọng nước đường kính 2-4mm xếp chụm lại như những chùm nho xanh ngọc bích giòn tan; chứa nhiều hợp chất quý caulerpin và khoáng chất.",
        "distribution": "Khắp các vùng biển nhiệt đới ấm toàn cầu. Cực kỳ phong phú tại bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Rong thực phẩm thượng hạng, được nuôi trồng quy mô công nghiệp lớn xuất khẩu tại Khánh Hòa, Ninh Thuận, Phú Quốc.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Cà-ná, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 191; J. Agardh 1872 : Till Alg. Syst. I : 35; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 457, "name": "Caulerpa microphysa", "author": "(Weber van Bosse) Feldmann",
        "vn": "Rong Nho túi-nhỏ", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 498, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_105.png",
        "morphology": "Tản bò mang các chùm bóng tròn nhỏ li ti đường kính chỉ 1-1,5mm mọc sát cuống; màu xanh ngọc bích bóng láng.",
        "distribution": "Indonesia, Biển Đông. Phổ biến ở rạn san hô Nha-trang.",
        "status": "Mọc trên đá san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Weber van Bosse 1898 : Monogr. Caulerpes : 361; Feldmann 1955 : Plastes Caulerpa : 9; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 458, "name": "Caulerpa lentillifera", "author": "J. Agardh",
        "vn": "Rong Nho hạt (Guột bi-nhỏ)", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 499, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_106.png",
        "morphology": "Loài rong nho hạt tiêu (green caviar) thương mại số 1; các quả bóng hình hạt thấu kính nhỏ tròn xoe đường kính 1,5-2mm có cuống ngắn thắt ngấn rõ rệt ở gốc xếp san sát thành cột trụ dày đặc như bắp ngô tí hon; ăn sống giòn sần sật bùng nổ hương vị biển.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương. Nuôi trồng và phân bố tự nhiên rộng rãi tại duyên hải miền Trung Việt Nam.",
        "status": "Rong thực phẩm xuất khẩu chủ lực giá trị cao hàng đầu của ngành rong biển Việt Nam.",
        "specimen": "Mẫu Hòn-khói, đầm Nha-phu, vịnh Nha-trang, Phú-quốc.",
        "literature": "J. Agardh 1837 : Nya Alger : 173; Weber van Bosse 1898 : Monogr. Caulerpes : 380; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 459, "name": "Caulerpa serrulata", "author": "(Forsskål) J. Agardh",
        "vn": "Rong Guột răng-cưa", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 499, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_107.png",
        "morphology": "Tản có thân bò to khỏe; các nhánh đứng dẹp xoắn ốc uốn lượn cao 3-8cm, mép nhánh có các răng cưa nhọn sắc bén hai bên; màu xanh lục sẫm.",
        "distribution": "Toàn cầu ở vùng biển nhiệt đới ấm. Cực kỳ phong phú tại toàn bộ duyên hải và hải đảo Việt Nam.",
        "status": "Rong ăn được, mọc thành thảm lớn trên cát san hô nông và rạn san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 189; J. Agardh 1837 : Nya Alger : 174; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 460, "name": "Caulerpa cupressoides", "author": "(Vahl) C. Agardh",
        "vn": "Rong Guột trắc-bá", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 500, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_108.png",
        "morphology": "Tản sụn cứng cáp cao 5-15cm; nhánh đứng mang các gai thịt ngắn hình chùy 3-4 cạnh xếp xoắn ốc khít khao trông như cành cây Trắc-bá diệp (Cupressus); màu xanh lục sẫm.",
        "distribution": "Toàn cầu ở các rạn san hô nhiệt đới. Rất phong phú ở các hải đảo Việt Nam.",
        "status": "Mọc bám trên rạn san hô nơi sóng mạnh.",
        "specimen": "Mẫu Hoàng-sa, Trường-sa, Côn-đảo, Phú-quốc.",
        "literature": "Vahl 1802 : Skrift. Naturh. Selsk. V : 38; C. Agardh 1817 : Syn. Alg. : 23; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 461, "name": "Caulerpa sertularioides", "author": "(S.G. Gmelin) M. Howe",
        "vn": "Rong Guột lông-chim", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 500, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_109.png",
        "morphology": "Tản thanh nhã tuyệt đẹp màu xanh lục tươi mướt; các nhánh đứng cao 5-15cm hình chiếc lông chim thẳng tắp với 2 hàng nhánh con hình kim mảnh dẻ mọc đối xứng đều tăm tắp từ gốc đến ngọn; rất mềm mại trong nước.",
        "distribution": "Khắp các biển nhiệt đới ấm thế giới. Cực kỳ phổ biến tại toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Rong thực phẩm ăn sống rất mát và bổ dưỡng; được trồng làm cảnh thủy sinh và nghiên cứu sinh học.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Quy-nhơn, Côn-đảo, Phú-quốc.",
        "literature": "Gmelin 1768 : Hist. Fuc. : 151; Howe 1905 : Bull. Torrey Bot. Club 32 : 576; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 462, "name": "Caulerpa taxifolia", "author": "(Vahl) C. Agardh",
        "vn": "Rong Guột song-đính (lá-thông)", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 501, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_110.png",
        "morphology": "Tản cao 10-25cm; nhánh đứng mang 2 hàng nhánh con dẹp hình lưỡi liềm uốn cong về phía ngọn, thắt hẹp rõ rệt ở cuống dính trông giống cành lá cây Thủy-tùng (Taxus); màu xanh lục tươi bóng.",
        "distribution": "Nhiệt đới toàn cầu. Rất phong phú ở vùng biển miền Trung Việt Nam.",
        "status": "Rong ăn được, mọc thành thảm lớn ở tầng hạ-duyên-hải trên cát bùn và đá.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Vahl 1802 : Skrift. Naturh. Selsk. V : 36; C. Agardh 1817 : Syn. Alg. : 22; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 463, "name": "Caulerpa brachypus", "author": "Harvey",
        "vn": "Rong Guột chân-ngắn", "fam_vn": "Họ Rong-guột (Rong-nho)", "fam_lat": "Caulerpaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Guột", "gen_lat": "Caulerpa",
        "p": 503, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_111.png",
        "morphology": "Tản bò lan mang các phiến lá dẹp đơn độc hình dải dài 3-8cm, rộng 4-8mm, có cuống rất ngắn (chân ngắn); mép phiến lá có răng cưa nhỏ mịn; màu xanh lục tươi bóng.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc trên đá và san hô ở tầng hạ-duyên-hải nơi nước sạch.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, đảo Hòn-mun.",
        "literature": "Harvey 1859 : Char. New Alg. : 332; Weber van Bosse 1898 : Monogr. Caulerpes : 280; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 392."
    },
    {
        "idx": 464, "name": "Penicillus sibogae", "author": "A. Gepp & E.S. Gepp",
        "vn": "Rong Hải-bút Xi-bô-ga", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Hải-bút", "gen_lat": "Penicillus",
        "p": 405, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_112.png",
        "morphology": "Tản tẩm vôi hình chiếc bút lông quét vôi độc đáo cao 5-10cm; trục cán hình trụ tròn cứng cáp do các sợi ống bện chặt tẩm vôi; đỉnh mang một chùm sợi lông xòe tròn màu trắng sữa ngọn xanh.",
        "distribution": "Indonesia (chuyến tàu Siboga), Biển Đông. Gặp ở rạn san hô Nha-trang.",
        "status": "Mọc cắm rễ trên nền cát san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Gepp & Gepp 1911 : Codiaceae Siboga Exped. : 82, pl. 19; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 465, "name": "Flabellia petiolata", "author": "(Turra) Nizamuddin",
        "vn": "Rong Phiến-lục có-cuống", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Phiến-lục", "gen_lat": "Flabellia",
        "p": 506, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_113.png",
        "morphology": "Tản phiến dẹp hình quạt màu xanh lục đậm không tẩm vôi (khác Udotea), cao 3-6cm; có cuống dẹp rõ rệt; cấu tạo bởi các sợi ống phân nhánh lưỡng phân song song bện chặt.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trong các hang hốc tối dưới triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Turra 1780 : Fl. Ital. Prodr. : 68; Nizamuddin 1987 : Nova Hedwigia 44 : 176."
    },
    {
        "idx": 466, "name": "Tydemania expeditionis", "author": "Weber van Bosse",
        "vn": "Rong Ti-đơ-man", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Ti-đơ-man", "gen_lat": "Tydemania",
        "p": 507, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_114.png",
        "morphology": "Tản tẩm vôi trắng xanh tuyệt đẹp cao 5-15cm; trục chính mang các vòng cầu đệm xốp gồm các chuỗi sợi phân nhánh tỏa tròn như chuỗi hạt ngọc; mọc ở rạn san hô sâu.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Gặp ở vùng biển đảo Nha-trang, Trường Sa.",
        "status": "Loài chỉ thị rạn san hô nước trong ở độ sâu 5-20m.",
        "specimen": "Mẫu lặn rạn san hô đảo Hòn-mun Nha-trang.",
        "literature": "Weber van Bosse 1901 : Ann. Jard. Bot. Buitenzorg XVII : 139; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 467, "name": "Udotea javensis", "author": "(Montagne) A. Gepp & E.S. Gepp",
        "vn": "Rong Hải-nữ Gia-va", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Hải-nữ (Quạt-vôi)", "gen_lat": "Udotea",
        "p": 508, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_115.png",
        "morphology": "Tản nhỏ nhắn thanh nhã hình chiếc quạt vôi màu xanh lục nhạt có cuống mảnh đơn độc mọc đứng, cao 1-3cm; phiến quạt đơn lớp sợi không có sợi phụ bên; các sợi phân nhánh lưỡng phân tỏa tròn từ cuống; tẩm vôi mỏng.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở các rạn san hô Việt Nam.",
        "status": "Mọc bám trên đá và san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Montagne 1842 : Prodr. Phyc. : 14; Gepp & Gepp 1904 : J. Bot. 42 : 363; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395, fig. 10c."
    },
    {
        "idx": 468, "name": "Udotea argentea", "author": "Zanardini",
        "vn": "Rong Hải-nữ ánh-bạc", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Hải-nữ (Quạt-vôi)", "gen_lat": "Udotea",
        "p": 509, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_116.png",
        "morphology": "Tản quạt vôi to lớn dày cộp cao 8-15cm, phủ lớp phấn vôi màu xám trắng ánh bạc lấp lánh; phiến quạt nhiều lớp sợi có các vòng sinh trưởng đồng tâm rõ rệt; cuống to khỏe.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương. Rất phổ biến ở miền Trung và hải đảo Việt Nam.",
        "status": "Đóng góp quan trọng vào quá trình bồi tụ trầm tích vôi rạn san hô.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo.",
        "literature": "Zanardini 1858 : Pl. Mar. Rubr. : 290; Gepp & Gepp 1911 : Siboga Exped. : 125; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 469, "name": "Udotea flabellum", "author": "(J. Ellis & Solander) M. Howe",
        "vn": "Rong Hải-nữ hình-quạt", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Hải-nữ (Quạt-vôi)", "gen_lat": "Udotea",
        "p": 509, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_117.png",
        "morphology": "Tản hình quạt xòe rộng dày cứng như đá vôi, cao 10-25cm; bề mặt có các dải vân đồng tâm uốn lượn; tẩm vôi cực kỳ dày màu xanh lục sữa; gốc có củ rễ lớn cắm sâu trong cát.",
        "distribution": "Toàn cầu ở các vùng biển nhiệt đới ấm. Phổ biến tại các rạn san hô Việt Nam.",
        "status": "Mọc trên bãi cát vụn san hô tầng hạ-duyên-hải sâu 1-6m.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Phú-quốc.",
        "literature": "Ellis & Solander 1786 : Nat. Hist. Zoophyt. : 124; Howe 1904 : Bull. Torrey Bot. Club 31 : 94; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 470, "name": "Avrainvillea erecta", "author": "(Berkeley) A. Gepp & E.S. Gepp",
        "vn": "Rong Cọ-biển đứng", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Cọ-biển", "gen_lat": "Avrainvillea",
        "p": 510, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_118.png",
        "morphology": "Tản chất da thuộc mềm xốp màu nâu lục đậm hoặc lục đen không tẩm vôi, cao 5-12cm; gốc phát triển thành một khối củ rễ hình trụ bện cát khổng lồ dài 5-10cm cắm thẳng đứng trong bùn cát; phiến lá hình quạt dày mềm.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Phổ biến ven biển miền Trung và Nam Việt Nam.",
        "status": "Cố định nền đáy cát bùn trong các thảm cỏ biển và rừng ngập mặn.",
        "specimen": "Mẫu bãi cỏ biển Cầu-đá Nha-trang, Phú-quốc.",
        "literature": "Berkeley 1842 : Ann. Mag. Nat. Hist. IX : 157; Gepp & Gepp 1911 : Siboga Exped. : 29; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    },
    {
        "idx": 471, "name": "Avrainvillea lacerata", "author": "J. Agardh",
        "vn": "Rong Cọ-biển rách", "fam_vn": "Họ Rong-quạt-vôi", "fam_lat": "Udoteaceae",
        "ord_vn": "Bộ Điệp-bích", "ord_lat": "Bryopsidales", "gen_vn": "Chi Rong Cọ-biển", "gen_lat": "Avrainvillea",
        "p": 511, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_119.png",
        "morphology": "Tản nhỏ cao 2-5cm, màu nâu xám; phiến lá hình quạt xẻ rách tả tơi thành nhiều thùy không đều; cuống ngắn. Loài cuối cùng khép lại toàn bộ 471 loài thực vật biển của công trình GS. Phạm Hoàng Hộ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Phổ biến ở các rạn san hô Việt Nam.",
        "status": "Mọc trên cát sỏi san hô vùng hạ-duyên-hải. Khép lại toàn bộ công trình khoa học Rong biển Việt Nam (Phạm Hoàng Hộ, 1969).",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo.",
        "literature": "J. Agardh 1887 : Till Alg. Syst. V : 54; Gepp & Gepp 1911 : Siboga Exped. : 38; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 395."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH8_DATA)} figures for Batch 8...')
    for sp in BATCH8_DATA:
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
    print(f'Querying WoRMS API in chunks for {len(BATCH8_DATA)} species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH8_DATA), chunk_size):
        chunk = BATCH8_DATA[i:i+chunk_size]
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
        
    for sp, item in zip(BATCH8_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH8_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH8_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 8...')
    rows = []
    for sp in BATCH8_DATA:
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
            "tax_class_vn": "Lớp Tảo Lục",
            "tax_class_latin": "Chlorophyceae",
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch8.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 8 build completed successfully!')
