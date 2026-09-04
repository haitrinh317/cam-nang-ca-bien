"""
build_batch7.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 64 loài Lục-tảo (Chlorophyceae - Đợt 7, loài 363-426)
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

BATCH7_DATA = [
    {
        "idx": 363, "name": "Ulothrix subflaccida", "author": "Wille",
        "vn": "Rong Ba-phát mềm", "fam_vn": "Họ Ba-phát", "fam_lat": "Ulotrichaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Ba-phát", "gen_lat": "Ulothrix",
        "p": 397, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_1.png",
        "morphology": "Tản hình sợi đơn không phân nhánh màu lục sáng bóng, cao 1-3cm; tế-bào rộng 8-15µ, dài bằng hoặc ngắn hơn rộng; lục-lạp hình vòng đai mở bao quanh tế bào với 1-3 hạch-lạp; tạo thành đám tơ xanh mượt trên đá.",
        "distribution": "Toàn cầu ở các vùng duyên hải. Việt Nam: Duyên hải miền Trung.",
        "status": "Mọc phủ kín mặt đá ở tầng thượng-duyên-hải và trung-duyên-hải thượng vào mùa đông xuân.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Wille 1901 : Studien : 27; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 364, "name": "Monostroma nitidum", "author": "Wittrock",
        "vn": "Rong Đơn-mạc bóng", "fam_vn": "Họ Đơn-mạc", "fam_lat": "Monostromataceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Đơn-mạc", "gen_lat": "Monostroma",
        "p": 398, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_2.png",
        "morphology": "Tản phiến mỏng manh màu lục tươi bóng loáng, cao 3-8cm; bề mặt nhăn nheo gợn sóng; phẫu thức ngang gồm đúng 1 lớp tế bào đơn độc (khác Ulva có 2 lớp); tế bào hình đa giác hay góc tròn.",
        "distribution": "Đông Á, Biển Đông. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Rong ăn được rất thơm ngon, mọc thành dải xanh mướt trên đá vào mùa đông và đầu xuân.",
        "specimen": "Mẫu Qui-nhơn và Nha-trang.",
        "literature": "Wittrock 1866 : Monostroma : 41, pl. 2; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 365, "name": "Enteromorpha intestinalis", "author": "(Linnaeus) Nees",
        "vn": "Rong Bún ruột", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 400, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_3.png",
        "morphology": "Tản hình ống rỗng mềm mại màu lục tươi, dài 10-30cm, đường kính 3-10mm; ống đơn không phân nhánh, thường phồng to thắt eo lồi lõm ngoằn ngoèo giống ruột động vật; vách ống do 1 lớp tế bào sắp xếp không theo hàng lối đều.",
        "distribution": "Toàn cầu. Rất phổ biến khắp các vùng cửa sông, đầm phá và bờ biển Việt Nam.",
        "status": "Rong thực phẩm ăn được, làm rau sống, nấu canh và chiết polysaccharide; thích nghi dải độ mặn rất rộng.",
        "specimen": "Mẫu phá Tam-giang, đầm Cù-mông, vịnh Nha-trang.",
        "literature": "Linnaeus 1753 : Sp. Pl. : 1163; Nees 1820 : Hor. Phys. Berol. :  indeks; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 366, "name": "Enteromorpha tubulosa", "author": "(Kützing) Kützing",
        "vn": "Rong Bún hình-ống", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 400, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_4.png",
        "morphology": "Tản hình ống tròn đều tăm tắp, dài 5-15cm, không phân nhánh; các tế bào sắp xếp thành những hàng dọc rất thẳng hàng và ngay ngắn.",
        "distribution": "Toàn cầu ở vùng nước lợ và mặn.",
        "status": "Mọc trên đá và cọc gỗ vùng cửa sông.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Kützing 1845 : Phyc. Germ. : 247; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 367, "name": "Enteromorpha flexuosa", "author": "(Wulfen) J. Agardh",
        "vn": "Rong Bún uốn-lượn", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 401, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_5.png",
        "morphology": "Tản ống rỗng uốn lượn mềm mại mọc thành bụi dày, cao 10-25cm; chỉ phân nhánh ở phần sát gốc; các tế bào xếp thành hàng dọc và hàng ngang rõ rệt.",
        "distribution": "Biển ấm toàn cầu. Rất phổ biến tại Việt Nam.",
        "status": "Rong ăn được, mọc ở tầng trung-duyên-hải và đầm nước mặn.",
        "specimen": "Mẫu Nha-trang, Vũng-Tàu, Phú-quốc.",
        "literature": "Wulfen 1803 : Crypt. Aquat. : 1; J. Agardh 1883 : Till Alg. Syst. VI : 126; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 368, "name": "Enteromorpha kylinii", "author": "Bliding",
        "vn": "Rong Bún Ki-lin", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 402, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_6.png",
        "morphology": "Tản sợi nhỏ thanh mảnh dài 5-15cm, đường kính dưới 1mm; phân nhánh nhiều lần từ gốc đến ngọn; tế bào hình chữ nhật nhỏ sắp xếp thành hàng dọc.",
        "distribution": "Châu Âu, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá và vỏ tàu thuyền.",
        "specimen": "Mẫu cảng Cầu-đá Nha-trang.",
        "literature": "Bliding 1939 : Bot. Notiser : 134, figs. 1-3; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 369, "name": "Enteromorpha clathrata", "author": "(Roth) Greville",
        "vn": "Rong Bún mạng", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 403, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_7.png",
        "morphology": "Tản màu lục sáng phân nhánh rất nhiều lần chằng chịt; các nhánh con nhỏ li ti hình sợi lông; tế bào xếp thành hàng dọc thẳng tắp; mỗi tế bào có 2-5 hạch-lạp.",
        "distribution": "Toàn cầu. Phổ biến khắp các đầm nuôi trồng thủy sản ven biển Việt Nam.",
        "status": "Rong ăn được, thức ăn ưa thích của tôm cua và cá biển.",
        "specimen": "Mẫu đầm Cù-mông và vịnh Nha-trang.",
        "literature": "Roth 1806 : Catal. Bot. III : 175; Greville 1830 : Alg. Brit. : 181; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 384."
    },
    {
        "idx": 370, "name": "Enteromorpha ralfsii", "author": "Harvey",
        "vn": "Rong Bún Ráp", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 404, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_8.png",
        "morphology": "Tản hình sợi nhỏ li ti bò lan và đứng, thân gồm 2-4 hàng tế bào dọc; tế bào gốc phát triển thành rễ giả dài; màu xanh đậm.",
        "distribution": "Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đất bùn vùng triều cao rừng ngập mặn.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Harvey 1850 : Phyc. Brit. : pl. 282; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 371, "name": "Enteromorpha chaetomorphoides", "author": "Boergesen",
        "vn": "Rong Bún mao-hình", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Bún", "gen_lat": "Enteromorpha",
        "p": 405, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_9.png",
        "morphology": "Tản sợi mảnh trông giống như rong Chaetomorpha, nhưng cấu tạo rỗng ruột với các tế bào xếp thành 2-3 hàng dọc.",
        "distribution": "Tây Ấn, Ấn-độ-dương, Biển Đông. Gặp ở cửa sông miền Trung.",
        "status": "Mọc ở cửa sông và đầm nước lợ.",
        "specimen": "Mẫu cửa sông Cái, Nha-trang.",
        "literature": "Boergesen 1911 : Mar. Alg. Dan. W. Ind. : 5; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 372, "name": "Ulva reticulata", "author": "Forsskål",
        "vn": "Rong Lục-võng", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Diếp-biển", "gen_lat": "Ulva",
        "p": 406, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_10.png",
        "morphology": "Tản phiến mỏng màu lục tươi bóng, phát triển thành tấm lưới ren đan thủng vô số lỗ tròn méo lớn nhỏ khác nhau như một chiếc mạng lưới cá; phiến gồm 2 lớp tế bào ép sát nhau; thường quấn vào các loài rong khác.",
        "distribution": "Biển Đỏ, Ấn-độ-Tây Thái-bình-dương nhiệt đới. Cực kỳ phong phú tại toàn bộ bờ biển miền Trung và Nam Việt Nam.",
        "status": "Rong thực phẩm ăn được, làm gỏi và phơi khô nấu thạch; nguồn thức ăn quan trọng của rùa biển và cá ăn rong.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 187; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386, fig. 7."
    },
    {
        "idx": 373, "name": "Ulva lactuca", "author": "Linnaeus",
        "vn": "Rong Sa-lách (Diếp-biển)", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Diếp-biển", "gen_lat": "Ulva",
        "p": 406, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_11.png",
        "morphology": "Tản phiến rộng hình lá xà lách màu lục tươi mướt, cao 10-30cm; mép phiến lượn sóng nhăn nheo; phẫu thức ngang gồm 2 lớp tế bào hình vuông hay chữ nhật đứng; bám vào đá nhờ đĩa dính nhỏ ở gốc.",
        "distribution": "Toàn cầu khắp các đại dương. Rất phổ biến khắp duyên hải Việt Nam từ Bắc vào Nam.",
        "status": "Rong thực phẩm phổ biến nhất thế giới (sea lettuce), ăn sống, làm salad, nấu canh, chiết xuất ulvan chống virus và dùng xử lý ô nhiễm nước biển.",
        "specimen": "Mẫu Cô-tô, Đồ-sơn, Đà-nẵng, Nha-trang, Vũng-Tàu.",
        "literature": "Linnaeus 1753 : Sp. Pl. : 1163; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 374, "name": "Ulva papenfussii", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Diếp-biển Pa-pen-phút", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Diếp-biển", "gen_lat": "Ulva",
        "p": 408, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_12.png",
        "morphology": "Tản to lớn tự do trôi dạt trong vịnh, rộng 20-40cm, màu lục thẫm; phẫu thức ngang gồm 2 lớp tế bào cao hình chữ nhật thuôn dài đặc sắc (cao gấp đôi rộng); màng cutin dày. Loài mới do GS. Phạm Hoàng Hộ đặt tên vinh danh nhà phycology George F. Papenfuss.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trôi nổi tự do trong vịnh kín sóng ở tầng hạ-duyên-hải.",
        "specimen": "Holotype thu tại vịnh Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 408, fig. 4.12."
    },
    {
        "idx": 375, "name": "Ulva fasciata", "author": "Delile",
        "vn": "Rong Sa-lách bó", "fam_vn": "Họ Rong-bún", "fam_lat": "Ulvaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Diếp-biển", "gen_lat": "Ulva",
        "p": 409, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_13.png",
        "morphology": "Tản xẻ sâu thành nhiều dải dẹp dài hình băng dải, cao 20-50cm, rộng 1-3cm; mép dải lượn sóng gợn lăn tăn; chất màng dai chắc hơn U. lactuca; màu lục sẫm.",
        "distribution": "Toàn cầu ở vùng biển ấm nhiệt đới. Rất phong phú tại bờ biển miền Trung Việt Nam.",
        "status": "Mọc bám trên đá nơi sóng vỗ mạnh ở tầng trung-duyên-hải; rong thực phẩm giàu khoáng chất.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Quy-nhơn, Vũng-Tàu.",
        "literature": "Delile 1813 : Fl. d'Égypte : 153, pl. 58; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 376, "name": "Entocladia viridis", "author": "Reinke",
        "vn": "Rong Lục-tiên xanh", "fam_vn": "Họ Lục-tiên", "fam_lat": "Ulvellaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Lục-tiên", "gen_lat": "Entocladia",
        "p": 410, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_14.png",
        "morphology": "Tản vi thể sống nội sinh trong màng cutin của rong khác; sợi phân nhánh bất quy tắc bò len lỏi giữa các tế bào chủ; tế bào hình đa giác uốn lượn; mỗi tế bào có 1 lục-lạp hình phiến và 1 hạch-lạp.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Nội sinh trong màng tế bào của Cladophora, Chaetomorpha và Bryopsis.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Reinke 1879 : Bot. Zeit. 37 : 476, pl. 6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 377, "name": "Ulvella lens", "author": "Prouho",
        "vn": "Rong Giả-diếp hình-thấu-kính", "fam_vn": "Họ Lục-tiên", "fam_lat": "Ulvellaceae",
        "ord_vn": "Bộ Ba-phát", "ord_lat": "Ulotrichales", "gen_vn": "Chi Rong Giả-diếp", "gen_lat": "Ulvella",
        "p": 411, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_15.png",
        "morphology": "Tản vi thể hình đĩa tròn đơn lớp tế bào tỏa tròn như thấu kính, đường kính 0,5-1mm, màu xanh lục; mép đĩa có các tế bào chẻ đôi hình chữ V ép sát nhau.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên đá, vỏ sò và màng rong khác.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Prouho 1891 : Ann. Sci. Nat. Zool. IX : 255; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 378, "name": "Rhizoclonium grande", "author": "Boergesen",
        "vn": "Rong Căn-chi to", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Căn-chi", "gen_lat": "Rhizoclonium",
        "p": 413, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_17.png",
        "morphology": "Tản sợi to cứng cáp màu xanh lục đậm, đường kính sợi 200-400µ; sợi bò lan tỏa trên đá mang nhiều nhánh rễ giả đa bào ngắn hình chùy dính chặt vào kẽ đá; vách tế bào cực kỳ dày xếp tầng.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang, Cà-ná.",
        "status": "Mọc bám trên đá nơi sóng vỗ mạnh ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Boergesen 1935 : List Mar. Alg. Bombay : 14, figs. 5-6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 379, "name": "Rhizoclonium riparium", "author": "(Roth) Harvey",
        "vn": "Rong Căn-chi ven-bờ", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Căn-chi", "gen_lat": "Rhizoclonium",
        "p": 414, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_18.png",
        "morphology": "Tản tạo búi sợi mềm màu xanh lục sáng như mớ tóc rối; sợi mảnh đường kính 20-35µ; mang các nhánh rễ giả đơn bào hoặc đa bào ngắn phân bố rải rác.",
        "distribution": "Toàn cầu. Rất phổ biến khắp bờ biển và rừng ngập mặn Việt Nam.",
        "status": "Phủ thành thảm xanh trên bùn đất và rễ cây ngập mặn ở tầng triều cao.",
        "specimen": "Mẫu Cần-giờ, Hải-phòng, Nha-trang.",
        "literature": "Roth 1806 : Catal. Bot. III : 216; Harvey 1849 : Phyc. Brit. : pl. 238; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 380, "name": "Rhizoclonium kochianum", "author": "Kützing",
        "vn": "Rong Căn-chi Cốc", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Căn-chi", "gen_lat": "Rhizoclonium",
        "p": 415, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_19.png",
        "morphology": "Sợi sợi đơn thẳng tắp hầu như không có nhánh rễ giả, đường kính 10-15µ; tế bào dài gấp 2-4 lần rộng.",
        "distribution": "Châu Âu, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên các loài rong khác.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "Kützing 1845 : Phyc. Germ. : 206; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 381, "name": "Chaetomorpha linum", "author": "(O.F. Müller) Kützing",
        "vn": "Rong Mao-hình chỉ", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 417, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_22.png",
        "morphology": "Tản hình sợi cước cứng dài 20-50cm, đường kính sợi 150-250µ, màu lục tươi; sợi cuộn xoắn thành mớ bùi nhùi tự do trôi dạt không bám gốc; tế bào dài bằng hoặc gấp đôi rộng.",
        "distribution": "Toàn cầu. Cực kỳ phong phú ở các đầm phá, cửa sông và ao đầm nuôi thủy sản Việt Nam.",
        "status": "Rong thích nghi cao, xuất hiện sinh khối lớn trong các đầm nuôi tôm cá.",
        "specimen": "Mẫu đầm Lăng-cô, Tam-giang, vịnh Nha-trang.",
        "literature": "Müller 1778 : Fl. Dan. : pl. 771; Kützing 1845 : Phyc. Germ. : 204; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 382, "name": "Chaetomorpha antennina", "author": "(Bory de Saint-Vincent) Kützing",
        "vn": "Rong Mao-hình râu", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 418, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_23.png",
        "morphology": "Tản mọc thành búi cứng thẳng đứng như bàn chải màu xanh lục đậm, cao 5-15cm; sợi cứng như dây cước to đường kính 400-600µ; đặc trưng nổi bật là tế-bào đáy đơn độc khổng lồ dài 5-10mm với vách có nhiều ngấn xoắn vòng dính chặt vào đá; chịu sóng đập cực mạnh.",
        "distribution": "Toàn cầu ở bờ biển đá nhiệt đới. Cực kỳ phong phú tại toàn bộ duyên hải miền Trung Việt Nam.",
        "status": "Tạo thành một đai xanh thẫm đặc trưng ở tầng trung-duyên-hải thượng trên các vách đá sóng gió dữ dội nhất.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, mũi Cà-ná, Qui-nhơn, Vũng-Tàu.",
        "literature": "Bory 1828 : Voy. Coquille : 161; Kützing 1847 : Bot. Zeit. : 166; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 383, "name": "Chaetomorpha aerea", "author": "(Dillwyn) Kützing",
        "vn": "Rong Mao-hình đứng", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 419, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_24.png",
        "morphology": "Tản mọc thành cụm sợi đứng thẳng tắp, cao 5-15cm, màu lục sáng; đường kính sợi tăng dần từ gốc (100µ) lên ngọn (300-400µ); tế bào ngọn phồng hình cầu sinh sản.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Mọc trên đá và trong các vũng nước triều cạn.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Dillwyn 1806 : Brit. Conf. : pl. 80; Kützing 1849 : Sp. Alg. : 379; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 384, "name": "Chaetomorpha indica", "author": "Kützing",
        "vn": "Rong Mao-hình Ấn-độ", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 420, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_25.png",
        "morphology": "Sợi mọc dính vào đá, đường kính 100-150µ; tế bào dài gấp 1,5-2 lần rộng; màu xanh lục tươi.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Kützing 1849 : Sp. Alg. : 376; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 385, "name": "Chaetomorpha spiralis", "author": "Okamura",
        "vn": "Rong Mao-hình xoắn", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 420, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_26.png",
        "morphology": "Tản sợi đơn rất to cứng như sợi cước cá đường kính 500-800µ; sợi cuộn xoắn ốc thành vòng tròn đều đặn; màu xanh lục sẫm.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng triều thấp nơi nước chảy mạnh.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Okamura 1903 : Alg. Jap. Exsicc. : no 94; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 386, "name": "Chaetomorpha brachygona", "author": "Harvey",
        "vn": "Rong Mao-hình đốt-ngắn", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Mao-hình", "gen_lat": "Chaetomorpha",
        "p": 421, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_27.png",
        "morphology": "Tản sợi cứng đan rối; tế bào ngắn hơn rộng hoặc dài bằng rộng (đốt ngắn), đường kính sợi 80-150µ; vách dày.",
        "distribution": "Tây Ấn, Thái-bình-dương. Phổ biến ven biển miền Trung.",
        "status": "Mọc trên đá và đầm nuôi trồng thủy sản.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Harvey 1858 : Nereis Bor. Amer. III : 87; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 387, "name": "Cladophora papenfussii", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Chi-đài Pa-pen-phút", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 424, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_29.png",
        "morphology": "Búi sợi màu xanh lục tươi cao 3-8cm; phân nhánh đối xứng hoặc chùm 3-4 nhánh ở mắt khớp; tế bào hình trụ dài thon; cấu trúc vách tế bào dày sọc. Loài mới do GS. Phạm Hoàng Hộ mô tả.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Việt Nam).",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 424, fig. 4.29."
    },
    {
        "idx": 388, "name": "Cladophora glaucescens", "author": "(Griffiths ex Harvey) Harvey",
        "vn": "Rong Chi-đài mốc", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 425, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_30.png",
        "morphology": "Búi tơ màu lục mốc ánh bạc cao 5-10cm; đặc sắc ở các lóng ngắn tế bào dài chỉ gấp 1,5-2 lần rộng; phân nhánh dày đặc ở ngọn.",
        "distribution": "Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Harvey 1848 : Phyc. Brit. : pl. 196; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 389, "name": "Cladophora patentiramea", "author": "(Montagne) Kützing",
        "vn": "Rong Chi-đài nhánh-thưa", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 427, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_32.png",
        "morphology": "Tản mọc thành búi mềm xốp màu lục nhạt, cao 5-12cm; các nhánh chia đôi rẽ góc rất rộng xòe ngang (patent); tế bào ngọn thon tròn.",
        "distribution": "Thái-bình-dương, Biển Đông. Phổ biến tại miền Trung.",
        "status": "Mọc trong các vũng triều cạn và bãi rạn san hô nông.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Montagne 1842 : Cent. Pl. Cell. : 15; Kützing 1849 : Sp. Alg. : 416; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 390, "name": "Cladophora fuliginosa", "author": "Kützing",
        "vn": "Rong Chi-đài đen", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 428, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_33.png",
        "morphology": "Búi sợi cứng đệm dày màu lục đen hay nâu sẫm, cao 2-5cm; thường cộng sinh với một loài nấm tạo thành các đốm đen cứng trên thân sợi; phân nhánh chùm sát gốc.",
        "distribution": "Tây Ấn, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều cao nơi sóng đập mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1849 : Sp. Alg. : 415; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 391, "name": "Cladophora coelothrix", "author": "Kützing",
        "vn": "Rong Chi-đài liên-phát", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 429, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_34.png",
        "morphology": "Tản tạo thảm đệm cứng dày cộm màu lục sẫm, cao 3-6cm; các nhánh đan bện chằng chịt dính vào nhau bằng các rễ bám nhỏ; chịu hạn và sóng dữ.",
        "distribution": "Địa-trung-hải, Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Phủ kín mặt đá trong các hang hốc tối tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo.",
        "literature": "Kützing 1843 : Phyc. Gen. : 272; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 392, "name": "Cladophora crispula", "author": "Vickers",
        "vn": "Rong Chi-đài quắn", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 430, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_35.png",
        "morphology": "Búi tơ nhỏ màu xanh đậm, các sợi chính và sợi phụ uốn xoăn quăn queo như tóc uốn; tế bào ngắn.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên thân các loài rong lớn.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Vickers 1905 : Ann. Sci. Nat. Bot. : 56; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 393, "name": "Cladophora rugulosa", "author": "Martens",
        "vn": "Rong Chi-đài nhám", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 431, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_36.png",
        "morphology": "Tản sụn cứng màu xanh lục đậm, cao 5-10cm; vách tế bào ngoài cùng có nhiều gờ nếp nhăn nhám thô ráp.",
        "distribution": "Nam Phi, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Martens 1866 : Preuss. Exped. Ost-Asien : 112; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 394, "name": "Cladophora inserta", "author": "Dickie",
        "vn": "Rong Chi-đài hở", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 432, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_37.png",
        "morphology": "Búi sợi mềm cao 4-8cm, các nhánh uốn cong hình móc câu ở ngọn; góc phân nhánh mở rộng.",
        "distribution": "Đại-tây-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc kẽ đá san hô vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Dickie 1874 : J. Linn. Soc. Bot. 14 : 359; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 395, "name": "Cladophora fascicularis", "author": "(Mertens ex C. Agardh) Kützing",
        "vn": "Rong Chi-đài bó", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 433, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_38.png",
        "morphology": "Tản to lớn cao 10-30cm, màu lục sáng óng ánh; các nhánh con ở phần ngọn mọc chụm lại thành từng bó dày đặc như ngọn bút lông; thân chính to rõ.",
        "distribution": "Toàn cầu ở vùng duyên hải ấm. Rất phong phú tại Việt Nam.",
        "status": "Mọc phủ trên đá và rạn san hô nông tầng triều thấp.",
        "specimen": "Mẫu Qui-nhơn, Nha-trang, Vũng-Tàu.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 114; Kützing 1843 : Phyc. Gen. : 268; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388, fig. 8b."
    },
    {
        "idx": 396, "name": "Cladophora gracilis", "author": "(Griffiths ex Harvey) Kützing",
        "vn": "Rong Chi-đài mảnh", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 435, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_39.png",
        "morphology": "Búi tơ mảnh mai mềm mại cao 5-15cm, màu lục nhạt bóng loáng; phân nhánh so le vươn dài thanh thoát; lóng dài gấp 4-8 lần rộng.",
        "distribution": "Bắc Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng nước lợ êm sóng.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Harvey 1841 : Man. Brit. Alg. : 137; Kützing 1845 : Phyc. Germ. : 215."
    },
    {
        "idx": 397, "name": "Cladophora glomerata", "author": "(Linnaeus) Kützing",
        "vn": "Rong Chi-đài lọn", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 436, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_40.png",
        "morphology": "Tản dài 10-30cm, màu lục tươi; các nhánh con tập trung thành từng lọn dày đặc ở ngọn cành; thích nghi cả nước ngọt, lợ và ven biển.",
        "distribution": "Toàn cầu. Phổ biến ở các cửa sông ven biển Việt Nam.",
        "status": "Mọc bám trên đá và kè đê ven cửa sông.",
        "specimen": "Mẫu cửa sông miền Trung.",
        "literature": "Linnaeus 1753 : Sp. Pl. : 1167; Kützing 1843 : Phyc. Gen. : 266."
    },
    {
        "idx": 398, "name": "Cladophora albida", "author": "(Nees) Kützing",
        "vn": "Rong Chi-đài trăng-trắng", "fam_vn": "Họ Mao-hình", "fam_lat": "Cladophoraceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài", "gen_lat": "Cladophora",
        "p": 437, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_41.png",
        "morphology": "Búi tơ nhỏ mịn như tơ tằm màu lục nhạt ánh trắng, cao 2-5cm; sợi rất mảnh đường kính 15-30µ; phân nhánh dày đặc.",
        "distribution": "Toàn cầu. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Nees 1820 : Hor. Phys. Berol. : 41; Kützing 1843 : Phyc. Gen. : 267; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 386."
    },
    {
        "idx": 399, "name": "Microdictyon okamurae", "author": "Setchell",
        "vn": "Rong Vi-võng Ô-ca-mu-ra", "fam_vn": "Họ Hải-nga", "fam_lat": "Anadyomenaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Vi-võng", "gen_lat": "Microdictyon",
        "p": 439, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_42.png",
        "morphology": "Tản phiến mỏng màu xanh lục đậm, cấu tạo thành một tấm lưới phẳng tinh xảo gồm các sợi phân nhánh trong cùng một mặt phẳng; các nhánh tự hàn liền đầu lại tạo thành mắt lưới hình đa giác đều đặn; tế-bào dính có vòng đệm đặc sắc.",
        "distribution": "Nhật-bản, Biển Đông. Rất phong phú ở các rạn san hô Việt Nam.",
        "status": "Mọc bám trên đá và san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Setchell 1925 : Univ. Calif. Publ. Bot. 13 : 107; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390, fig. 9a."
    },
    {
        "idx": 400, "name": "Microdictyon japonicum", "author": "Setchell",
        "vn": "Rong Vi-võng Nhật-bản", "fam_vn": "Họ Hải-nga", "fam_lat": "Anadyomenaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Vi-võng", "gen_lat": "Microdictyon",
        "p": 440, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_43.png",
        "morphology": "Tản lưới phẳng mỏng manh màu lục sáng, mắt lưới hình thoi hoặc lục giác thưa; các nhánh phụ mọc đối xứng đều.",
        "distribution": "Nhật-bản, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở rạn san hô sâu 2-6m.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Setchell 1925 : Univ. Calif. Publ. Bot. 13 : 107; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 401, "name": "Anadyomene wrightii", "author": "Harvey ex J.E. Gray",
        "vn": "Rong Hải-nga Rai", "fam_vn": "Họ Hải-nga", "fam_lat": "Anadyomenaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Hải-nga", "gen_lat": "Anadyomene",
        "p": 441, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_44.png",
        "morphology": "Tản phiến dẹp hình quạt xòe tròn màu xanh lục ngọc bích tuyệt đẹp, cao 3-8cm; cấu trúc giải phẫu hiển vi gồm các gân lá hình xương sườn tỏa tròn từ gốc, giữa các gân là các tế bào hình bầu dục xếp song song khít khao tạo thành phiến lá đặc kín không thủng lỗ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phổ biến ở miền Trung và hải đảo Việt Nam.",
        "status": "Mọc bám trên đá và san hô ở tầng hạ-duyên-hải nơi nước trong sạch.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Harvey in Gray 1866 : J. Bot. IV : 48, pl. 44; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390, fig. 9b."
    },
    {
        "idx": 402, "name": "Anadyomene plicata", "author": "C. Agardh",
        "vn": "Rong Hải-nga xếp", "fam_vn": "Họ Hải-nga", "fam_lat": "Anadyomenaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Hải-nga", "gen_lat": "Anadyomene",
        "p": 442, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_45.png",
        "morphology": "Tản phiến dày gấp nếp uốn lượn hình quạt gợn sóng, màu lục đậm; các gân sườn to rõ phân nhánh chùm 4-6 nhánh.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Bám trên rạn san hô chết.",
        "specimen": "Mẫu đảo Hòn-tre Nha-trang.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 400; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 403, "name": "Cladophoropsis herpestica", "author": "(Montagne) M. Howe",
        "vn": "Rong Chi-đài-hình bò", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài-hình", "gen_lat": "Cladophoropsis",
        "p": 445, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_49.png",
        "morphology": "Tản tạo đệm cứng màu lục sáng cao 2-4cm; sợi ống lớn đường kính 300-500µ; phân nhánh một bên; đặc trưng của chi là nhánh bên không có vách ngăn ở gốc nối liền thông suốt với tế bào trục mẹ.",
        "distribution": "New Zealand, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều nơi sóng vỗ mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Montagne 1842 : Prodr. Phyc. : 15; Howe 1914 : Mar. Alg. Peru : 35; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 404, "name": "Cladophoropsis sundanensis", "author": "Reinbold",
        "vn": "Rong Chi-đài-hình Sun-đa", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài-hình", "gen_lat": "Cladophoropsis",
        "p": 446, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_50.png",
        "morphology": "Tản hình đệm nhung dày cộm màu lục sáng, cao 1-3cm; sợi mảnh hơn C. herpestica đường kính 100-150µ; nhánh không vách đáy mọc tỏa tròn chằng chịt.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rất phổ biến khắp vùng biển Việt Nam.",
        "status": "Mọc thành thảm dày trên đá ở tầng trung-duyên-hải thượng.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu.",
        "literature": "Reinbold 1905 : Nuova Notarisia XVI : 147; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390, fig. 8e."
    },
    {
        "idx": 405, "name": "Cladophoropsis adhaerens", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Chi-đài-hình dính", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài-hình", "gen_lat": "Cladophoropsis",
        "p": 447, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_51.png",
        "morphology": "Tản tạo khối đệm đặc xốp sống cộng sinh chặt chẽ với hải miên (bọt biển), màu vàng lục; các sợi dính sát nhau bằng đĩa dính con ở đầu nhánh. Loài mới do GS. Phạm Hoàng Hộ mô tả.",
        "distribution": "Đặc hữu vùng duyên hải Nha-trang (Việt Nam).",
        "status": "Cộng sinh với hải miên trên đá vùng triều.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 447, fig. 4.51."
    },
    {
        "idx": 406, "name": "Cladophoropsis zollingeri", "author": "(Kützing) Reinbold",
        "vn": "Rong Chi-đài-hình Giô-linh", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Chi-đài-hình", "gen_lat": "Cladophoropsis",
        "p": 447, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_52.png",
        "morphology": "Tản búi cứng cao 3-6cm, sợi to đường kính 200-300µ; phân nhánh một bên, các nhánh con uốn cong.",
        "distribution": "Mã Lai, Indonesia, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1849 : Sp. Alg. : 415; Reinbold 1905 : Nuova Notarisia XVI : 147."
    },
    {
        "idx": 407, "name": "Boodlea composita", "author": "(Harvey) F. Brand",
        "vn": "Rong Búp đều", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Búp", "gen_lat": "Boodlea",
        "p": 449, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_53.png",
        "morphology": "Tản tạo thành búi xốp mềm hình bán cầu màu xanh lục tươi mướt, cao 3-10cm; cấu tạo tản là một mạng lưới không gian 3 chiều chằng chịt gồm các sợi phân nhánh đối xứng hoặc chùm; các đầu nhánh tự hàn dính vào nhánh đối diện bằng các đĩa dính nhỏ (haptera).",
        "distribution": "Khắp các biển nhiệt đới ấm thế giới. Rất phong phú ở toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Rất phổ biến trên các rạn san hô nông và bãi đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Harvey in Hooker 1834 : J. Bot. I : 157; Brand 1904 : Beih. Bot. Centralbl. 18 : 187; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 408, "name": "Boodlea siamensis", "author": "Reinbold",
        "vn": "Rong Búp Thái-lan", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Búp", "gen_lat": "Boodlea",
        "p": 449, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_54.png",
        "morphology": "Tản đệm xốp màu vàng lục; các nhánh con không phân chia lông chim đều đặn mà đan mạng lưới bất quy tắc; sợi mảnh hơn B. composita.",
        "distribution": "Vịnh Thái Lan, Biển Đông. Gặp ở Phú-quốc, Nha-trang.",
        "status": "Mọc trên rạn san hô tầng triều dưới.",
        "specimen": "Mẫu đảo Phú-quốc.",
        "literature": "Reinbold 1901 : Bot. Tidsskr. 24 : 191; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 409, "name": "Boodlea struveoides", "author": "M. Howe",
        "vn": "Rong Búp có-phiến", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Búp", "gen_lat": "Boodlea",
        "p": 450, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_55.png",
        "morphology": "Tản kết hợp giữa dạng mạng 3 chiều ở gốc và các phiến lưới phẳng có cuống ở ngọn giống như rong Trụ-đèn (Struvea).",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Howe 1918 : Torrey Bot. Club Mem. 15 : 494; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 410, "name": "Struvea delicatula", "author": "Kützing",
        "vn": "Rong Trụ-đèn thanh", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Trụ-đèn", "gen_lat": "Struvea",
        "p": 451, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_56.png",
        "morphology": "Tản thanh nhã tuyệt đẹp hình chiếc quạt lưới ren có cuống đơn độc mọc thẳng, cao 2-5cm, màu lục sáng; phiến lá hình bầu dục tạo thành bởi các nhánh phân chia lông chim đối xứng hàn liền đầu nhau thành mắt lưới đều tăm tắp.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá và san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1866 : Tab. Phyc. XVI : 1, pl. 2; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 411, "name": "Struvea anastomosans", "author": "(Harvey) Piccone & Grunow",
        "vn": "Rong Trụ-đèn liền-nhánh", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Trụ-đèn", "gen_lat": "Struvea",
        "p": 451, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_57.png",
        "morphology": "Tản mọc thành cụm nhiều phiến quạt lưới màu xanh lục, cuống có vách ngăn; phiến lá hình tam giác phân nhánh lông chim 2-3 lần hàn dính liền nhau.",
        "distribution": "Toàn cầu ở vùng biển ấm. Phổ biến tại bờ biển miền Trung Việt Nam.",
        "status": "Mọc trên đá ngầm vùng triều thấp nơi nước sạch.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Harvey 1858 : Nereis Bor. Amer. III : 123; Piccone 1884 : Croc. Corsaro : 20; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 412, "name": "Struvea tenuis", "author": "Zanardini",
        "vn": "Rong Trụ-đèn mỏng", "fam_vn": "Họ Rong-búp", "fam_lat": "Boodleaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Trụ-đèn", "gen_lat": "Struvea",
        "p": 452, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_58.png",
        "morphology": "Tản rất mỏng manh nhỏ nhắn cao 1-2cm; cuống không phân vách; phiến lá lưới hình trái tim xẻ thùy.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc kẽ đá san hô dưới triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Zanardini 1878 : Phyc. Ind. : 38; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 390."
    },
    {
        "idx": 413, "name": "Valonia ventricosa", "author": "J. Agardh",
        "vn": "Rong Bóng (Đại-bào phồng)", "fam_vn": "Họ Đại-bào", "fam_lat": "Valoniaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Đại-bào", "gen_lat": "Valonia",
        "p": 453, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_59.png",
        "morphology": "Một trong những tế-bào đơn độc khổng lồ lớn nhất hành tinh; tản là một bọng hình cầu hay trứng đơn bào đa nhân duy nhất, đường kính 1-4cm (đôi khi đến 5cm), màu xanh lục đậm bóng láng như viên ngọc bích soi gương; bám trên san hô nhờ các rễ giả vi thể li ti ở gốc; chứa đầy dịch bào trong suốt.",
        "distribution": "Khắp các rạn san hô nhiệt đới toàn cầu (Sailor's eyeball). Cực kỳ phong phú ở toàn bộ duyên hải miền Trung và hải đảo Việt Nam.",
        "status": "Đối tượng nghiên cứu kinh điển thế giới về sinh lý màng tế bào và thẩm thấu ion; mọc trong các hốc rạn san hô nông tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Hoàng-sa, Trường-sa, Côn-đảo, Phú-quốc.",
        "literature": "J. Agardh 1887 : Till Alg. Syst. V : 96; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 414, "name": "Valonia fastigiata", "author": "Harvey ex J. Agardh",
        "vn": "Rong Đại-bào thẳng", "fam_vn": "Họ Đại-bào", "fam_lat": "Valoniaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Đại-bào", "gen_lat": "Valonia",
        "p": 453, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_60.png",
        "morphology": "Tản tạo thành khối đệm tròn đặc xốp rất cứng màu xanh lục bóng, cao 3-8cm; gồm vô số tế bào hình chùy dài thon mọc thẳng đứng chụm lại sát nhau; các nhánh phân chia ở ngọn tế bào.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phổ biến khắp các rạn san hô Việt Nam.",
        "status": "Phủ kín các gờ đá san hô ở tầng hạ-duyên-hải nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo.",
        "literature": "J. Agardh 1887 : Till Alg. Syst. V : 101; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388, fig. 8d."
    },
    {
        "idx": 415, "name": "Valonia aegagropila", "author": "C. Agardh",
        "vn": "Rong Đại-bào lọn", "fam_vn": "Họ Đại-bào", "fam_lat": "Valoniaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Đại-bào", "gen_lat": "Valonia",
        "p": 454, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_61.png",
        "morphology": "Tản hình búi đệm tròn màu lục đậm, gồm các tế bào hình trụ ngón tay dài 5-10mm xếp đan cài chằng chịt nhiều tầng; các tế bào con mọc ra từ hông và ngọn tế bào mẹ.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Ấn-độ-Thái-bình-dương. Rất phong phú tại Việt Nam.",
        "status": "Mọc bám trên đá và san hô chết ở tầng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang, Qui-nhơn, Côn-đảo.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 429; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388, fig. 8j."
    },
    {
        "idx": 416, "name": "Valonia utricularis", "author": "(Roth) C. Agardh",
        "vn": "Rong Đại-bào bọng", "fam_vn": "Họ Đại-bào", "fam_lat": "Valoniaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Đại-bào", "gen_lat": "Valonia",
        "p": 455, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_62.png",
        "morphology": "Tản bò lan tỏa tạo thảm, các tế bào hình quả lê hay bọng uốn cong uốn lượn; phân nhánh bất quy tắc; màu lục sẫm.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trong các hốc đá tối nơi sóng vỗ.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Roth 1797 : Catal. Bot. I : 160; C. Agardh 1822 : Sp. Alg. : 428; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 417, "name": "Boergesenia forbesii", "author": "(Harvey) Feldmann",
        "vn": "Rong Boóc-gơ-xen Bô-bét", "fam_vn": "Họ Rong-búp", "fam_lat": "Siphonocladaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Boóc-gơ-xen", "gen_lat": "Boergesenia",
        "p": 456, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_63.png",
        "morphology": "Tản hình túi bọng đơn bào khổng lồ hình chùy cong uốn lượn, cao 2-6cm, đường kính 1-2cm, màu vàng lục trong suốt lấp lánh; mọc thành từng chùm nhiều túi từ một gốc rễ bám; bên trong chứa đầy dịch nhầy và khí; vách màng mỏng dẻo dai.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Cực kỳ phong phú ở toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Loài chỉ thị tuyệt đẹp của rạn san hô, mọc dày đặc trong các vũng nước triều cạn và thềm đá san hô nông.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Harvey 1859 : Char. New Alg. : 333; Feldmann 1938 : Rev. Gén. Bot. 50 : 588; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388, fig. 8h."
    },
    {
        "idx": 418, "name": "Dictyosphaeria cavernosa", "author": "(Forsskål) Boergesen",
        "vn": "Rong Võng-cầu bộng", "fam_vn": "Họ Rong-búp", "fam_lat": "Siphonocladaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Võng-cầu", "gen_lat": "Dictyosphaeria",
        "p": 457, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_64.png",
        "morphology": "Tản hình khối cầu rỗng bộng ruột ở giữa, đường kính 2-8cm, chất sụn giòn cứng màu xanh lục ngọc; cấu tạo bởi 1 lớp tế bào khổng lồ hình đa giác đường kính 1-3mm mắt thường thấy rất rõ, liên kết với nhau bằng các gai nhỏ li ti ở vách bên như xếp gạch tổ ong; khi già vỡ toác thành hình chén lõm.",
        "distribution": "Toàn cầu ở các rạn san hô nhiệt đới. Cực kỳ phong phú tại toàn bộ duyên hải và hải đảo Việt Nam.",
        "status": "Thành phần quan trọng tạo rạn san hô, mọc phủ kín thềm đá san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Forsskål 1775 : Fl. Aegypt.-Arab. : 187; Boergesen 1932 : Dansk Bot. Arkiv VIII : 2; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388, fig. 8i."
    },
    {
        "idx": 419, "name": "Dictyosphaeria versluysii", "author": "Weber van Bosse",
        "vn": "Rong Võng-cầu Véc-luýt", "fam_vn": "Họ Rong-búp", "fam_lat": "Siphonocladaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Võng-cầu", "gen_lat": "Dictyosphaeria",
        "p": 458, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_65.png",
        "morphology": "Tản hình khối đặc hoàn toàn (không rỗng bộng ruột như D. cavernosa), màu xanh lục xám rất cứng chắc; các vách tế bào bên trong mọc các gai nhọn tẩm silic đâm vào khoang tế bào.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phổ biến tại Việt Nam.",
        "status": "Mọc bám trên đá rạn san hô nơi sóng mạnh.",
        "specimen": "Mẫu vịnh Nha-trang, Côn-đảo.",
        "literature": "Weber van Bosse 1905 : Nuova Notarisia XVI : 144; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 420, "name": "Dictyosphaeria setchellii", "author": "Boergesen",
        "vn": "Rong Võng-cầu Xét-xen", "fam_vn": "Họ Rong-búp", "fam_lat": "Siphonocladaceae",
        "ord_vn": "Bộ Ống-tảo", "ord_lat": "Cladophorales", "gen_vn": "Chi Rong Võng-cầu", "gen_lat": "Dictyosphaeria",
        "p": 459, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_66.png",
        "morphology": "Tản khối đặc màu xanh đậm, tế bào đa giác cực lớn đường kính 3-5mm; gai liên kết ở vách rất dài.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Rạn san hô sâu 2-5m.",
        "specimen": "Mẫu Hòn-mun Nha-trang.",
        "literature": "Boergesen 1940 : Mar. Alg. Mauritius I : 12; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 388."
    },
    {
        "idx": 421, "name": "Bornetella oligospora", "author": "Solms-Laubach",
        "vn": "Rong Biệt-nang ít-bào-tử", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Biệt-nang", "gen_lat": "Bornetella",
        "p": 460, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_67.png",
        "morphology": "Tản sụn mềm tẩm vôi mỏng hình chùy cong màu lục sáng, cao 2-4cm, đường kính 4-8mm; trục chính hình trụ mang các vòng nhánh túa tròn bên trong; vỏ ngoài do các đầu nhánh loe rộng hình lục giác ép sát nhau như vảy rắn; mỗi nhánh bên mang 4-8 túi bào tử hình cầu.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Mọc trên đá và rạn san hô chết ở tầng hạ-duyên-hải nơi nước trong sạch.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Solms-Laubach 1892 : Ann. Jard. Bot. Buitenzorg XI : 87, pl. 9; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394, fig. 11c."
    },
    {
        "idx": 422, "name": "Bornetella sphaerica", "author": "(Zanardini) Solms-Laubach",
        "vn": "Rong Biệt-nang tròn", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Biệt-nang", "gen_lat": "Bornetella",
        "p": 461, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_68.png",
        "morphology": "Tản hình cầu tròn xoe hoặc hình quả trứng nhỏ đường kính 5-10mm, có cuống ngắn dính vào đá, màu lục tươi; mỗi nhánh bên chỉ mang đúng 1-2 túi bào tử to.",
        "distribution": "Mã Lai, Thái-bình-dương. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên san hô chết tầng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Zanardini 1878 : Phyc. Ind. : 37; Solms-Laubach 1892 : Ann. Jard. Bot. Buitenzorg XI : 80; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394."
    },
    {
        "idx": 423, "name": "Bornetella nitida", "author": "(Harvey) Munier-Chalmas",
        "vn": "Rong Biệt-nang bóng", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Biệt-nang", "gen_lat": "Bornetella",
        "p": 461, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_69.png",
        "morphology": "Tản hình trụ dài uốn cong, cao 3-6cm, màu lục bóng; mỗi nhánh bên mang 20-30 túi bào tử nhỏ xếp xung quanh.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Phổ biến ven biển miền Trung.",
        "status": "Rạn san hô nông kín sóng.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Harvey 1857 : Ceylon Alg. : no 87; Munier-Chalmas 1877 : Compt. Rend. 85 : 816; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 394, fig. 11a-b."
    },
    {
        "idx": 424, "name": "Neomeris bilimbata", "author": "Koster",
        "vn": "Rong Tân-tiết hai-viền", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Tân-tiết", "gen_lat": "Neomeris",
        "p": 463, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_4_70.png",
        "morphology": "Tản tẩm vôi trắng như chiếc ngón tay nhỏ hình sâu đo, cao 1-3cm, đỉnh ngọn mang chùm lông xanh mướt; bề mặt phủ lớp vỏ vôi nhẵn có các lỗ nhỏ đa giác; đặc trưng bởi các túi bào tử hình cầu được bọc trong lớp vôi dày có 2 gờ viền đối xứng.",
        "distribution": "Indonesia, Biển Đông. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Mọc bám trên đá và san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Koster 1937 : Blumea II : 221, pl. 15; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396."
    },
    {
        "idx": 425, "name": "Neomeris vanbosseae", "author": "M. Howe",
        "vn": "Rong Tân-tiết Van Bosse", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Tân-tiết", "gen_lat": "Neomeris",
        "p": 464, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_4_71.png",
        "morphology": "Tản tẩm vôi hình trụ cong cao 1,5-3cm, màu trắng sữa ngọn xanh; các túi bào tử hình bầu dục không dính liền nhau mà rời rạc hoàn toàn trong lớp vôi.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên đá san hô chết tầng triều thấp.",
        "specimen": "Mẫu đảo Hòn-mun Nha-trang.",
        "literature": "Howe 1909 : Bull. Torrey Bot. Club 36 : 80, pl. 1; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396, fig. 11e-f."
    },
    {
        "idx": 426, "name": "Neomeris annulata", "author": "Dickie",
        "vn": "Rong Tân-tiết có-vòng", "fam_vn": "Họ Tản-dù", "fam_lat": "Dasycladaceae",
        "ord_vn": "Bộ Tản-dù", "ord_lat": "Dasycladales", "gen_vn": "Chi Rong Tân-tiết", "gen_lat": "Neomeris",
        "p": 464, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_4_72.png",
        "morphology": "Tản tẩm vôi màu trắng có các vòng ngấn ngang rõ rệt quanh thân; các túi bào tử liên kết dính liền nhau thành từng vòng đai ngang 10-15 túi đều đặn.",
        "distribution": "Toàn cầu ở vùng biển nhiệt đới. Phổ biến tại các rạn san hô Việt Nam.",
        "status": "Mọc trên san hô chết và đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Dickie 1874 : J. Linn. Soc. Bot. 14 : 198; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 396, fig. 11d."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH7_DATA)} figures for Batch 7...')
    for sp in BATCH7_DATA:
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
    print(f'Querying WoRMS API in chunks for {len(BATCH7_DATA)} species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH7_DATA), chunk_size):
        chunk = BATCH7_DATA[i:i+chunk_size]
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
        
    for sp, item in zip(BATCH7_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH7_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH7_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 7...')
    rows = []
    for sp in BATCH7_DATA:
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch7.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 7 build completed successfully!')
