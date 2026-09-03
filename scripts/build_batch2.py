"""
build_batch2.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 40 loài Thanh-tảo (loài 28-67)
cho Volume 2 (Rong biển Việt Nam - GS. Phạm Hoàng Hộ, 1969).
Hoàn tất 100% PHẦN I (Cyanophyceae)!
"""
import os
import sys
import json
import urllib.request
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE, 'public', 'images', 'species', 'thuc-vat-bien', 'v2')
DPI300_DIR = os.path.join(BASE, 'scratch', 'phh_300dpi')
os.makedirs(IMAGE_DIR, exist_ok=True)

# 40 species of Batch 2 (Index 28 to 67)
BATCH2_DATA = [
    {
        "idx": 28, "name": "Lyngbya martensiana", "author": "Menegh. ex Gomont",
        "vn": "Rong Lương-ba Mác-ten", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 36, "crop": (150, 1100, 2200, 2600), "fig_name": "fig_1_28.png",
        "morphology": "Sợi dài nhiều mm, rộng 15µ; mao-tản vỏ-chai dợt, không eo ở vách ngang, rộng 10µ; tế-bào cao 2,5µ; vách ngang có hạt; bao dày, không màu; tế-bào chót không thon, đầu cắt ngang, không chóp.",
        "distribution": "Đại-tây-dương, Ấn-độ-dương, Thái-bình-dương. Gặp ở Phú-quốc (Việt Nam).",
        "status": "Nhiều trên vỏ hàu Ostrea forskalii ở Phú-quốc, nơi đây mọc lẫn với Oscillatoria simplicissima và Khuê-tảo. Thường gặp ở nước mặn và nước lợ.",
        "specimen": "Mẫu khảo sát tại Phú-quốc.",
        "literature": "Meneghini 1837 : Conspectus Algolog. Euganeae : 12; Gomont 1893 : Monogr. Oscillariées : 145, fig. 17, pl. 3; Frémy 1933 : Cyanoph. côtes d'Europe : 107, pl. 29, fig. 1."
    },
    {
        "idx": 29, "name": "Lyngbya semiplena", "author": "(C. Agardh) J. Agardh ex Gomont",
        "vn": "Rong Lương-ba bán-sung", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 37, "crop": (150, 1200, 2200, 2800), "fig_name": "fig_1_29.png",
        "morphology": "Mao-tản vàng hay nâu-nâu, rộng 15-20µ, dài 100µ đến vài mm; bao rất mỏng, trong, không màu; tế-bào dài 2,5µ; vách ngang có hạt, đầu hẹp không đều, có một chóp thường có lông.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Thường đi chung với Feldmannia breviarticulata làm thành những lọn dài 2-4cm, rộng cỡ 1cm, gặp ở tầng trung-duyên-hải thượng vào mùa đông trên bãi đá nơi sóng mạnh vùng Nha-trang.",
        "specimen": "Mẫu bãi đá Nha-trang mùa đông.",
        "literature": "J. Agardh 1842 : Alg. mar. Medit. et Adriat. : 11; Gomont 1893 : Monogr. Oscill. : 138, pl. 3, figs. 7-11; Frémy 1933 : Cyanop. côtes d'Europe : 108, pl. 28, fig. 3."
    },
    {
        "idx": 30, "name": "Lyngbya gracilis", "author": "Rabenhorst ex Gomont",
        "vn": "Rong Lương-ba mảnh", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 38, "crop": (150, 1400, 2200, 2800), "fig_name": "fig_1_30.png",
        "morphology": "Bụi mềm mịn như gòn, trơn, màu đỏ. Mao-tản mịn, rộng 6µ; tế-bào dài bằng hay ngắn hơn rộng; vách ngang khó thấy, bao rất mỏng. Đầu hơi thon, tế-bào chót tròn, không chóp.",
        "distribution": "Đại-tây-dương, Biển Đỏ, Ấn-độ-dương. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Tầng trung-duyên-hải, trên đá hoặc phụ sinh trên các loài rong lớn. Mọc thành đám nhung màu đỏ tía.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Rabenhorst 1865 : Flora Eur. Alg. II : 115; Gomont 1893 : Monogr. Oscill. II : 124, pl. 2, fig. 20; Frémy 1933 : Cyano. côtes d'Europe : 102, pl. 26, fig. 3."
    },
    {
        "idx": 31, "name": "Lyngbya sordida", "author": "(Zanardini) Gomont",
        "vn": "Rong Lương-ba bẩn", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 38, "crop": (150, 1800, 2200, 3100), "fig_name": "fig_1_31.png",
        "morphology": "Sợi mọc thành búi dày, màu lục bẩn hay vàng ô-liu; mao-tản rộng 14-30µ, tế-bào ngắn, rộng gấp 4-8 lần chiều cao (2-4µ); vách ngang không thắt, không có hạt; tế-bào ngọn tròn, không có chóp.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Thái-bình-dương. Gặp ở Vũng-Tàu, Nha-trang.",
        "status": "Phụ sinh trên đá, san hô chết hoặc bám vào các chân đế hải miên ở vùng triều giữa và triều dưới.",
        "specimen": "Mẫu khảo sát duyên hải Nha-trang.",
        "literature": "Gomont 1893 : Monogr. Oscillariées : 126, pl. 2, fig. 21; Frémy 1933 : Cyanophycées côtes d'Europe : 103, pl. 26, fig. 4."
    },
    {
        "idx": 32, "name": "Lyngbya confervoides", "author": "C. Agardh ex Gomont",
        "vn": "Rong Lương-ba dạng-thủy-miên", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 39, "crop": (150, 1300, 2200, 2900), "fig_name": "fig_1_32.png",
        "morphology": "Sợi dài 2-5cm, dính thành từng búi dày; mao-tản màu vàng nâu hay lục sẫm, rộng 10-18µ; tế-bào ngắn hơn rộng (cao 2-4µ); bao màng dày, phân lớp rõ rệt; tế-bào ngọn hơi tròn, không chóp.",
        "distribution": "Rộng khắp các vùng biển nhiệt đới và cận nhiệt đới thế giới. Khá phổ biến dọc bờ biển Việt Nam.",
        "status": "Mực trung-duyên-hải thượng trên đá, cọc gỗ, vỏ ốc hàu hoặc trôi nổi ven bờ triều yên sóng.",
        "specimen": "Mẫu thu thập tại bãi đá Nha-trang và Vũng-Tàu.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 73; Gomont 1893 : Monogr. Oscill. : 136, pl. 3, figs. 5-6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 380, figs. 3b, c."
    },
    {
        "idx": 33, "name": "Lyngbya majuscula", "author": "Harvey ex Gomont",
        "vn": "Rong Lương-ba to", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Lương-ba", "gen_lat": "Lyngbya",
        "p": 40, "crop": (150, 1200, 2200, 2800), "fig_name": "fig_1_33.png",
        "morphology": "Sợi rất to, dài tới 10-30cm, tạo thành búi tóc dày màu nâu sẫm, lục đen hay lục lam; mao-tản rộng 20-40µ (thường 25-35µ); tế-bào rất hẹp, cao chỉ 2-4µ; bao dày, không màu, không nhuộm tím với I-KI.",
        "distribution": "Khắp các biển nhiệt đới thế giới. Tại Việt Nam: Nha-trang, Vũng-Tàu, Côn-đảo, Phú-quốc.",
        "status": "Rất phổ biến ở tầng triều dưới và các rạn san hô nông, thường vướng vào cành san hô, rong khác hoặc trải rộng trên nền đáy cát sỏi.",
        "specimen": "Mẫu viện Hải dương học Nha-trang.",
        "literature": "Harvey in Hooker 1833 : English Flora V : 370; Gomont 1893 : Monogr. Oscillariées : 131, pl. 3, figs. 3-4; Desikachary 1959 : Cyanophyta : 313, pl. 48, fig. 7, pl. 49, fig. 12."
    },
    {
        "idx": 34, "name": "Oscillatoria tenuis", "author": "Agardh ex Gomont",
        "vn": "Rong Dao mảnh", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 41, "crop": (150, 1300, 2200, 2900), "fig_name": "fig_1_34.png",
        "morphology": "Mao-tản mỏng, màu lục lam, thẳng hay hơi lượn sóng, rộng 4-10µ; tế-bào cao bằng 1/3 đến 1/2 bề rộng; vách ngang có hạt mịn; tế-bào chót hình bán cầu tròn, vách mỏng, không có chóp.",
        "distribution": "Toàn cầu. Việt Nam: Gặp ở các vũng nước lợ và duyên hải Nha-trang, Quy-nhơn.",
        "status": "Tạo màng mỏng bao phủ bùn cát hoặc phụ sinh trên gốc rong khác ở vùng triều cao và vũng nước đọng.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Agardh 1813 : Disp. Alg. Suec. : 35; Gomont 1893 : Monogr. Oscillariées : 220, pl. 7, figs. 2-3; Desikachary 1959 : Cyanophyta : 222, pl. 42, fig. 15."
    },
    {
        "idx": 35, "name": "Oscillatoria nigroviridis", "author": "Thwaites ex Gomont",
        "vn": "Rong Dao đen-lục", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 42, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_35.png",
        "morphology": "Tản làm thành lớp màng nhầy màu lục đen hay lam sẫm; mao-tản rộng 7-11µ; tế-bào dài bằng 1/3 đến 1/2 bề rộng; vách ngang thắt nhẹ và có hạt lấm tấm; đầu ngọn cong và hơi thon nhẹ, tế-bào chót hơi có chóp tròn.",
        "distribution": "Biển nhiệt đới và ôn đới toàn cầu. Duyên hải miền Trung và Nam Việt Nam.",
        "status": "Mọc trên đá, bùn cát bẩn hoặc bám quanh các chân cọc ở tầng trung-duyên-hải.",
        "specimen": "Mẫu bãi biển Nha-trang (Dawson 1954).",
        "literature": "Thwaites in Harvey 1849 : Phyc. Brit. Syn. : 39, pl. 251A; Gomont 1893 : Monogr. Oscillariées : 217, pl. 6, fig. 20; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 380, fig. 3g."
    },
    {
        "idx": 36, "name": "Oscillatoria bonnemaisonii", "author": "(P. Crouan & H. Crouan) P. Crouan & H. Crouan ex Gomont",
        "vn": "Rong Dao Bon-mê-sông", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 43, "crop": (150, 1100, 2200, 2600), "fig_name": "fig_1_36.png",
        "morphology": "Mao-tản xoắn ốc đều đặn hoặc hơi lượn sóng, rộng 18-30µ, màu lục lam nhạt; tế-bào rất ngắn, dài bằng 1/3 đến 1/6 bề rộng; không thắt ở vách ngang, tế-bào chót tròn lồi, không chóp.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Thái-bình-dương. Việt Nam: Nha-trang, Vũng-Tàu.",
        "status": "Trên đá có bùn vào tầng trung-duyên-hải thượng; phụ sinh trên Carpopeltis formosana và nhiều rong khác ở vũng dựa biển.",
        "specimen": "Mẫu phụ sinh rong đỏ tại Nha-trang.",
        "literature": "Crouan 1858 : Florule Finistère : 115; Gomont 1893 : Monogr. Oscillariées : 215, pl. 6, figs. 17-18; Desikachary 1959 : Cyanophyta : 202, pl. 40, fig. 7."
    },
    {
        "idx": 37, "name": "Oscillatoria corallinae", "author": "Gomont",
        "vn": "Rong Dao san-hô", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 43, "crop": (150, 1900, 2200, 3100), "fig_name": "fig_1_37.png",
        "morphology": "Dề nhầy mỏng, màu đỏ hay gạch tươi. Mao-tản rộng 6-10µ, uốn lượn; tế-bào dài bằng 1/3 đến 1/2 bề rộng, vách ngang không thắt; đầu thon nhẹ, tế-bào ngọn có chóp hình nón cụt.",
        "distribution": "Các vùng biển nhiệt đới. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Phụ sinh trên các loài rong san hô (Corallina, Jania) ở tầng triều giữa nơi sóng vỗ vừa.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Gomont 1893 : Monogr. Oscillariées : 218, pl. 6, fig. 21; Frémy 1933 : Cyanop. côtes d'Europe : 121, pl. 30, fig. 9."
    },
    {
        "idx": 38, "name": "Oscillatoria margaritifera", "author": "Kützing ex Gomont",
        "vn": "Rong Dao trân-châu", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 44, "crop": (150, 1200, 2200, 2800), "fig_name": "fig_1_38.png",
        "morphology": "Tản màu lục đen hay lam sẫm; mao-tản rộng 18-28µ, thẳng, đầu cong; tế-bào ngắn, cao 3-6µ; vách ngang thắt nhẹ và có chuỗi hạt sáng như chuỗi ngọc (trân châu); tế-bào chót hơi phồng có chóp lồi.",
        "distribution": "Biển châu Âu, châu Phi, Ấn-độ-dương, Việt Nam.",
        "status": "Mọc trên bùn đáy rạn san hô và các vũng nước triều ấm có nhiều bùn hữu cơ.",
        "specimen": "Mẫu khảo sát vịnh Nha-trang.",
        "literature": "Kützing 1845 : Tab. Phyc. I : 31, pl. 43, fig. 10; Gomont 1893 : Monogr. Oscillariées : 216, pl. 6, fig. 19; Desikachary 1959 : Cyanophyta : 202, pl. 42, fig. 9."
    },
    {
        "idx": 39, "name": "Oscillatoria limosa", "author": "Agardh ex Gomont",
        "vn": "Rong Dao bùn", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 45, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_39.png",
        "morphology": "Mao-tản ngay hay hơi lượn sóng, dài 1-3mm, rộng 11-20µ (thường 13-16µ), làm thành những tấm thảm như nhung màu lam đậm, dày 2-3mm. Tế-bào rộng gấp 2-3 lần chiều cao, không thắt ở vách ngang; vách ngang có hạt rõ rệt; đầu không thon, tế-bào ngọn có vách hơi dày.",
        "distribution": "Toàn cầu, nước mặn và lợ. Duyên hải Việt Nam: Nha-trang, Phan-thiết, Vũng-Tàu.",
        "status": "Trong vũng nước ở mức trung-duyên-hải trung, thường sống chung với Chthamalus và ốc mút bám đá.",
        "specimen": "Mẫu bãi đá duyên hải miền Nam.",
        "literature": "Agardh 1812 : Disp. Alg. Suec. : 35; Gomont 1893 : Monogr. Oscillariées : 210, pl. 6, figs. 13-14; Desikachary 1959 : Cyanophyta : 206, pl. 42, fig. 11."
    },
    {
        "idx": 40, "name": "Oscillatoria laetevirens", "author": "P. Crouan & H. Crouan ex Gomont",
        "vn": "Rong Dao tươi", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 46, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_1_40.png",
        "morphology": "Tản màu lục tươi, nhầy mỏng; mao-tản rộng 3-5µ, thẳng, phần đầu hơi cong nhẹ và thon nhọn; tế-bào dài gần bằng hay ngắn hơn rộng (cao 2,5-4µ); vách ngang không có hạt; tế-bào chót nhọn không chóp.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Tầng trung-duyên-hải trên đá ẩm hoặc bám vào rong màng khác.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Crouan 1860 : Bull. Soc. Bot. France : 367; Gomont 1893 : Monogr. Oscillariées : 226, pl. 7, fig. 11; Desikachary 1959 : Cyanophyta : 226, pl. 37, fig. 9."
    },
    {
        "idx": 41, "name": "Oscillatoria agardhii", "author": "Gomont",
        "vn": "Rong Dao A-gạc", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 46, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_1_41.png",
        "morphology": "Mao-tản thẳng, màu lục lam nhạt, rộng 4-6µ; tế-bào hình chữ nhật thon, dài 2-4µ, vách ngang thường có hạt; đầu thon nhẹ, tế-bào chót có chóp lồi hoặc hơi tù tròn.",
        "distribution": "Các vùng nước mặn và lợ trên thế giới. Duyên hải Việt Nam.",
        "status": "Thường mọc lẫn giữa các bụi Oscillatoria limosa trong các vũng nước triều tĩnh.",
        "specimen": "Mẫu thu thập tại Nha-trang.",
        "literature": "Gomont 1893 : Monogr. Oscillariées : 205, pl. 6, fig. 7; Desikachary 1959 : Cyanophyta : 221."
    },
    {
        "idx": 42, "name": "Oscillatoria princeps", "author": "Vaucher ex Gomont",
        "vn": "Rong Dao chúa", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 48, "crop": (150, 1100, 2200, 2600), "fig_name": "fig_1_42.png",
        "morphology": "Mao-tản khổng lồ, rộng 30-60µ (thường 40-50µ), màu lam sẫm hay đen, thẳng tắp; tế-bào cực kỳ ngắn, cao chỉ 3,5-7µ (rộng gấp 8-10 lần chiều cao); không thắt ở vách ngang, tế-bào ngọn bằng phẳng hoặc hơi lồi nhẹ, có chóp dẹt.",
        "distribution": "Toàn cầu ở vùng nhiệt đới và cận nhiệt đới. Việt Nam: Gặp ở Nha-trang, Cà-mau, Phú-quốc.",
        "status": "Tạo màng trôi nổi hoặc bám trên nền bùn ở vùng cửa sông giáp biển và vũng triều giàu dinh dưỡng.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Vaucher 1803 : Hist. Conf. d'eau douce : 190, pl. 15, fig. 2; Gomont 1893 : Monogr. Oscillariées : 206, pl. 6, fig. 9; Desikachary 1959 : Cyanophyta : 210, pl. 37, figs. 1, 10, 11, 13, 14."
    },
    {
        "idx": 43, "name": "Oscillatoria salina", "author": "Biswas",
        "vn": "Rong Dao nước-mặn", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Dao", "gen_lat": "Oscillatoria",
        "p": 47, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_43.png",
        "morphology": "Mao-tản nhỏ, rộng 3-5µ, màu lục lam, uốn lượn nhẹ; tế-bào cao bằng 1/2 đến bằng bề rộng; vách ngang rõ; phần ngọn thon dần, uốn cong móc câu, tế-bào ngọn hơi nhọn không có chóp.",
        "distribution": "Vùng biển Ấn-độ, Đông Nam Á. Gặp ở Nha-trang.",
        "status": "Mọc thành đám màng mỏng trong ruộng muối và các vũng nước triều mặn cao.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Biswas 1926 : Jour. Dept. Sci. Calcutta Univ. : 3; Desikachary 1959 : Cyanophyta : 239."
    },
    {
        "idx": 44, "name": "Phormidium tenue", "author": "(Meneghini) Gomont",
        "vn": "Rong Nhập-đoàn mảnh", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Nhập-đoàn", "gen_lat": "Phormidium",
        "p": 48, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_1_44.png",
        "morphology": "Tản màng mỏng nhầy, màu lục lam nhạt; mao-tản rất mảnh, rộng 1-2µ; tế-bào dài gấp 2-3 lần bề rộng (dài 2,5-5µ); vách ngang không thắt hoặc hơi thắt nhẹ; bao màng rất mỏng, hòa tan nhanh; tế-bào chót nhọn hình nón.",
        "distribution": "Toàn cầu. Phổ biến ven biển Việt Nam.",
        "status": "Tạo lớp màng nhầy bám trên đá ẩm, bùn cát ven bờ biển và cửa lạch.",
        "specimen": "Mẫu duyên hải miền Trung.",
        "literature": "Meneghini 1837 : Conspectus Algolog. Euganeae : 8; Gomont 1893 : Monogr. Oscillariées : 169, pl. 4, figs. 23-25; Desikachary 1959 : Cyanophyta : 259, pl. 43, figs. 13-15."
    },
    {
        "idx": 45, "name": "Phormidium submembranaceum", "author": "(Ardissone & Strafforello) Gomont",
        "vn": "Rong Nhập-đoàn màng", "fam_vn": "Họ Dao-tảo", "fam_lat": "Oscillatoriaceae",
        "ord_vn": "Bộ Dao-tảo", "ord_lat": "Oscillatoriales", "gen_vn": "Chi Rong Nhập-đoàn", "gen_lat": "Phormidium",
        "p": 49, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_45.png",
        "morphology": "Tản dạng da màng dai, màu lục đen hay lục sẫm; mao-tản uốn lượn chằng chịt, rộng 5µ; tế-bào dài bằng hay hơi ngắn hơn rộng (cao 3-5µ); bao màng dai, không màu; tế-bào ngọn hơi tròn lồi.",
        "distribution": "Địa-trung-hải, Đại-tây-dương, Biển Đông. Gặp ở Vũng-Tàu, Nha-trang.",
        "status": "Bám chặt thành mảng màng dai trên các tảng đá bị sóng vỗ mạnh ở tầng trung-duyên-hải.",
        "specimen": "Mẫu bãi đá Vũng-Tàu.",
        "literature": "Ardissone & Strafforello 1877 : Enum. Alg. Liguria : 59; Gomont 1893 : Monogr. Oscillariées : 180, pl. 5, fig. 13; Frémy 1933 : Cyanophycées côtes d'Europe : 89, pl. 23, fig. 5."
    },
    {
        "idx": 46, "name": "Spirulina tenerrima", "author": "Kützing ex Gomont",
        "vn": "Rong Loa-tảo rất mảnh", "fam_vn": "Họ Loa-tảo", "fam_lat": "Spirulinaceae",
        "ord_vn": "Bộ Loa-tảo", "ord_lat": "Spirulinales", "gen_vn": "Chi Rong Loa-tảo", "gen_lat": "Spirulina",
        "p": 50, "crop": (150, 1200, 2200, 2400), "fig_name": "fig_1_46.png",
        "morphology": "Mao-tản hình sợi xoắn ốc cực kỳ mảnh, rộng chỉ 0,4-0,5µ; bước xoắn rất đều đặn, đường kính vòng xoắn 1-1,5µ, khoảng cách giữa các vòng xoắn 1-1,5µ; màu lam nhạt; không thấy vách ngăn tế bào.",
        "distribution": "Châu Âu, Bắc Mỹ, châu Á. Gặp ở Nha-trang.",
        "status": "Sống xen lẫn giữa các loài tảo lam khác trong các vũng nước triều trên rạn san hô.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Kützing 1843 : Phyc. Gen. : 183; Gomont 1893 : Monogr. Oscillariées : 252, pl. 7, fig. 28; Desikachary 1959 : Cyanophyta : 190, pl. 36, fig. 13."
    },
    {
        "idx": 47, "name": "Spirulina labyrinthiformis", "author": "(Meneghini) Gomont",
        "vn": "Rong Loa-tảo mê-cung", "fam_vn": "Họ Loa-tảo", "fam_lat": "Spirulinaceae",
        "ord_vn": "Bộ Loa-tảo", "ord_lat": "Spirulinales", "gen_vn": "Chi Rong Loa-tảo", "gen_lat": "Spirulina",
        "p": 50, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_1_47.png",
        "morphology": "Mao-tản xoắn ốc khít khao, rộng 1µ; vòng xoắn rộng 2-2,5µ, các bước xoắn áp sát nhau trông như lò xo đặc; màu lục lam sáng; chuyển động xoay tròn linh động.",
        "distribution": "Biển châu Âu, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tạo màng màu lam nhạt bám trên bùn đáy hoặc lẫn trong đám rong khác.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Meneghini 1837 : Conspectus Algolog. Euganeae : 16; Gomont 1893 : Monogr. Oscillariées : 255; Frémy 1933 : Cyanophycées côtes d'Europe : 131, pl. 31, fig. 18."
    },
    {
        "idx": 48, "name": "Spirulina major", "author": "Kützing ex Gomont",
        "vn": "Rong Loa-tảo lớn", "fam_vn": "Họ Loa-tảo", "fam_lat": "Spirulinaceae",
        "ord_vn": "Bộ Loa-tảo", "ord_lat": "Spirulinales", "gen_vn": "Chi Rong Loa-tảo", "gen_lat": "Spirulina",
        "p": 51, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_48.png",
        "morphology": "Mao-tản sợi xoắn đơn độc, rộng 1,2-1,7µ; đường kính vòng xoắn 2,5-4µ, bước xoắn tương đối thưa, cách nhau 2,7-5µ; màu lam sáng; chuyển động uốn lượn xoay trục nhanh.",
        "distribution": "Rộng khắp thế giới ở vùng nước mặn và lợ. Duyên hải miền Trung và Nam Việt Nam.",
        "status": "Mọc lẫn trong các lớp màng tảo lam trên đá, cát ẩm và các ao đầm nuôi thủy sản ven biển.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Kützing 1843 : Phyc. Gen. : 183; Gomont 1893 : Monogr. Oscillariées : 251, pl. 7, fig. 29; Desikachary 1959 : Cyanophyta : 196, pl. 36, fig. 13."
    },
    {
        "idx": 49, "name": "Spirulina subsalsa", "author": "Oersted ex Gomont",
        "vn": "Rong Loa-tảo lợ", "fam_vn": "Họ Loa-tảo", "fam_lat": "Spirulinaceae",
        "ord_vn": "Bộ Loa-tảo", "ord_lat": "Spirulinales", "gen_vn": "Chi Rong Loa-tảo", "gen_lat": "Spirulina",
        "p": 52, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_1_49.png",
        "morphology": "Tản màng màu lục sáng bóng hoặc lam tươi; mao-tản rộng 1-2µ; vòng xoắn rất sít sao, rộng 3-5µ, các vòng hầu như chạm vào nhau; sợi uốn lượn chằng chịt.",
        "distribution": "Khắp thế giới ở biển, nước lợ và suối nước nóng. Việt Nam: Nha-trang, Vũng-Tàu, Phan-thiết.",
        "status": "Tạo lớp màng nhung xanh biếc trên vỏ ốc, cọc cầu tàu và đá ẩm ở tầng triều trên.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Oersted 1842 : Naturhist. Tidsskr. IV : 17; Gomont 1893 : Monogr. Oscillariées : 253, pl. 7, fig. 32; Desikachary 1959 : Cyanophyta : 193, pl. 36, figs. 3-9."
    },
    {
        "idx": 50, "name": "Calothrix crustacea", "author": "Thuret ex Bornet & Flahault",
        "vn": "Rong Mỹ-mao vảy", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 52, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_1_50.png",
        "morphology": "Tản làm thành lớp vỏ cứng như vảy màu lục đen hay nâu sẫm trên đá; sợi mọc đứng thẳng khít khao, dài 1-2mm, rộng 12-40µ ở gốc; bao dày phân tầng, màu vàng hoặc nâu; tế-bào gốc rộng hơn cao; dị-bào (heterocyst) gốc từ 1-3 cái hình bán cầu hoặc chữ nhật.",
        "distribution": "Toàn cầu. Rất phổ biến khắp bờ biển Việt Nam từ Bắc vào Nam.",
        "status": "Tạo thành một đai màu đen đặc trưng (black zone) ở tầng trung-duyên-hải thượng và thượng-duyên-hải nơi sóng gió dữ dội.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang và Vũng-Tàu.",
        "literature": "Thuret in Bornet & Thuret 1878 : Notes Alg. I : 13, pl. 4; Bornet & Flahault 1886 : Revision Nostocacées : 359; Desikachary 1959 : Cyanophyta : 523."
    },
    {
        "idx": 51, "name": "Calothrix confervicola", "author": "(Roth) C. Agardh ex Bornet & Flahault",
        "vn": "Rong Mỹ-mao dạng-thủy-miên", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 53, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_51.png",
        "morphology": "Sợi mọc thành búi nhỏ hình sao hay túm lông cao 2-3mm, màu lục đen; gốc sợi rộng 18-30µ; bao trong suốt, không màu, loe hình phễu ở ngọn; dị-bào gốc 1-2 cái hình cầu hay bán cầu; ngọn sợi kéo dài thành sợi lông không màu.",
        "distribution": "Khắp các biển trên thế giới. Việt Nam: Nha-trang, Côn-đảo, Phú-quốc.",
        "status": "Phụ sinh phổ biến trên các rong biển lớn khác (như Chaetomorpha, Sargassum, Turbinaria) ở tầng triều giữa.",
        "specimen": "Mẫu phụ sinh trên rong Mơ tại Nha-trang.",
        "literature": "Roth 1797 : Catalecta Bot. I : 203; Bornet & Flahault 1886 : Revision Nostocacées : 349; Frémy 1933 : Cyanophycées côtes d'Europe : 140, pl. 33, fig. 2."
    },
    {
        "idx": 52, "name": "Calothrix pilosa", "author": "Harvey ex Bornet & Flahault",
        "vn": "Rong Mỹ-mao lông", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 56, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_52.png",
        "morphology": "Tản làm thành lớp đệm dày như nỉ (felt-like) màu nâu đen hay lục sẫm, cao 2-10mm; sợi uốn lượn chằng chịt, rộng 10-40µ; bao dày, màu vàng kim hay nâu sẫm, có thớ dọc; dị-bào mọc ở gốc hoặc nằm xen kẽ giữa sợi (intercalary); không có lông ngọn rõ.",
        "distribution": "Đặc trưng vùng nhiệt đới ấm (Thái-bình-dương, Ấn-độ-dương, Caribê). Việt Nam: Nha-trang, Vũng-Tàu, Hòn-yến.",
        "status": "Phủ kín mặt đá ở tầng trên triều và vùng văng sóng nơi nắng gắt, tạo thành lớp thảm dày chống khô hạn.",
        "specimen": "Mẫu bãi đá Hòn-yến (Khánh-hòa).",
        "literature": "Harvey 1858 : Nereis Bor. Amer. III : 106, pl. 48D; Bornet & Flahault 1886 : Rev. Nostocacées : 363; Setchell & Gardner 1919 : Mar. Alg. Flor. : 103, pl. 8, fig. 4."
    },
    {
        "idx": 53, "name": "Calothrix scopulorum", "author": "(Weber & Mohr) C. Agardh ex Bornet & Flahault",
        "vn": "Rong Mỹ-mao đá", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 57, "crop": (150, 1200, 2200, 2600), "fig_name": "fig_1_53.png",
        "morphology": "Tản dạng nhung dày, màu lục nhạt đến nâu ô-liu, cao 1mm; sợi uốn éo, gốc phồng rộng 10-18µ; bao mỏng nhầy, loe rộng phân tầng; tế-bào ngắn hơn rộng; 1-3 dị-bào ở gốc; ngọn sợi kéo dài thành lông mảnh.",
        "distribution": "Toàn cầu ở vùng duyên hải. Việt Nam: Nha-trang, Phan-thiết.",
        "status": "Tầng thượng và trung-duyên-hải trên vách đá đứng nơi sóng biển vỗ mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Weber & Mohr 1804 : Grossbritt. Konch. : 195; Bornet & Flahault 1886 : Rev. Nostocacées : 353; Frémy 1933 : Cyanop. côtes d'Europe : 143, pl. 35, fig. 2."
    },
    {
        "idx": 54, "name": "Calothrix parietina", "author": "(Nägeli) Thuret ex Bornet & Flahault",
        "vn": "Rong Mỹ-mao tường", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 57, "crop": (150, 2100, 2200, 3100), "fig_name": "fig_1_54.png",
        "morphology": "Tản làm thành lớp vỏ màu vàng nâu hay nâu đỏ, dày; sợi thẳng hoặc uốn lượn, rộng 10-15µ; bao rất dày, phân tầng rõ rệt, màu vàng mật ong; dị-bào ở gốc hoặc giữa sợi; ngọn vuốt nhọn.",
        "distribution": "Toàn cầu. Việt Nam: Ven biển miền Trung.",
        "status": "Trên vách đá ẩm có nước ngọt rỉ ra hòa với nước biển ở tầng trên triều.",
        "specimen": "Mẫu vách đá Nha-trang.",
        "literature": "Nägeli in Kützing 1849 : Sp. Alg. : 313; Bornet & Flahault 1886 : Rev. Nostocacées : 366; Fan 1956 : Rev. Calothrix : 159, fig. 1."
    },
    {
        "idx": 55, "name": "Calothrix contarenii", "author": "(Zanardini) Bornet & Flahault",
        "vn": "Rong Mỹ-mao Côn-ta-rê-ni", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Mỹ-mao", "gen_lat": "Calothrix",
        "p": 58, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_55.png",
        "morphology": "Tản màng cứng chắc, màu lục đen bóng như da; sợi xếp rất song song sít sao, dài 1mm, rộng 9-15µ; bao mỏng, màu vàng dợt, không loe ngọn; 1 dị-bào dẹt ở gốc; lông ngọn rụng sớm.",
        "distribution": "Địa-trung-hải, Ấn-độ-dương, Thái-bình-dương. Gặp ở Hòn-yến (Khánh-hòa).",
        "status": "Mọc trên đá nơi sóng rất mạnh. Ở Hòn-yến, tạo thành bớt màu đen đậm cao 3-4m trên mực triều.",
        "specimen": "Mẫu Hòn-yến, Khánh-hòa.",
        "literature": "Zanardini 1840 : Lettera al Barone Berlingieri : 134; Bornet & Flahault 1886 : Rev. Nostocacées : 355; Desikachary 1959 : Cyanophyta : 524, pl. 111, figs. 2, 5-8."
    },
    {
        "idx": 56, "name": "Isactis plana", "author": "(Harvey) Thuret ex Bornet & Flahault",
        "vn": "Rong Bình-thạch phẳng", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Bình-thạch", "gen_lat": "Isactis",
        "p": 59, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_56.png",
        "morphology": "Tản hình đệm phẳng dẹt, cứng, láng, màu lục tươi hay lam sẫm; sợi mọc đứng thẳng tắp song song ép sát nhau như cấu trúc mô giả nhu mô, cao 0,5-1mm; bao hẹp phân tầng; dị-bào nằm ở đáy sợi, hình bán cầu.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Thái-bình-dương. Việt Nam: Nha-trang, Vũng-Tàu.",
        "status": "Mọc thành từng vệt mảng dẹp bám cực chặt trên đá ở tầng trung-duyên-hải nơi sóng đánh liên hồi.",
        "specimen": "Mẫu bãi đá Hòn-chồng Nha-trang.",
        "literature": "Harvey in Hooker 1833 : British Flora V : 394; Bornet & Flahault 1886 : Rev. Nostocacées : 343; Frémy 1933 : Cyanop. côtes d'Europe : 151, pl. 40."
    },
    {
        "idx": 57, "name": "Rivularia australis", "author": "Harvey ex Bornet & Flahault",
        "vn": "Rong Khê-lưu nam", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Khê-lưu", "gen_lat": "Rivularia",
        "p": 60, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_57.png",
        "morphology": "Tản hình bán cầu nhỏ, chắc đặc, màu lục đen, đường kính 2-5mm, đôi khi hợp lại thành mảng lồi lõm; sợi tỏa tròn từ tâm ra ngoài; bao dày phân phiến màu vàng nâu; dị-bào ở gốc sợi, hình cầu.",
        "distribution": "Ấn-độ-dương, Úc-châu, Thái-bình-dương. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Mọc trên đá hoặc rạn san hô nông ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Harvey 1855 : Trans. Roy. Irish Acad. XXII : 566; Bornet & Flahault 1886 : Rev. Nostocacées : 362; Setchell & Gardner 1919 : Myxophyceae : 107, pl. 8, figs. 1-2."
    },
    {
        "idx": 58, "name": "Rivularia hemisphaerica", "author": "Bornet & Flahault",
        "vn": "Rong Khê-lưu bán cầu", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Khê-lưu", "gen_lat": "Rivularia",
        "p": 61, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_58.png",
        "morphology": "Tản nhầy hình bán cầu, màu lục đậm, to 2-3mm. Phẫu thức ngang cho thấy các sợi phân nhánh giả dạng tỏa tròn; tế-bào ở đáy rộng 6µ, kéo dài thành sợi lông mảnh ở ngọn; dị-bào đơn độc ở gốc sợi.",
        "distribution": "Ấn-độ-dương, Việt Nam (Nha-trang).",
        "status": "Bám trên vách đá đứng và các bậc thềm san hô nơi có sóng triều thường xuyên tạt ướt.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Bornet & Flahault 1886 : Rev. Nostocacées : 362; Desikachary 1959 : Cyanophyta : 518."
    },
    {
        "idx": 59, "name": "Rivularia atra", "author": "Roth ex Bornet & Flahault",
        "vn": "Rong Khê-lưu đen", "fam_vn": "Họ Khê-lưu", "fam_lat": "Rivulariaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Khê-lưu", "gen_lat": "Rivularia",
        "p": 62, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_59.png",
        "morphology": "Tản hình cầu hay bán cầu cứng như sụn, màu đen nhánh, to 1-4mm, mọc riêng rẽ hoặc kết hợp thành mảng vỏ; sợi xếp rất khít; bao mỏng không màu hoặc vàng nhạt ở gốc; dị-bào gốc hình cầu rộng 5-8µ.",
        "distribution": "Khắp các biển ôn đới và nhiệt đới thế giới. Việt Nam: Duyên hải Khánh-hòa, Ninh-thuận.",
        "status": "Trên đá, vỏ sò hàu ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "Roth 1806 : Catalecta Bot. III : 340; Bornet & Flahault 1886 : Rev. Nostocacées : 353; Desikachary 1959 : Cyanophyta : 515, pl. 106, figs. 1-6."
    },
    {
        "idx": 60, "name": "Nostoc commune", "author": "Vaucher ex Bornet & Flahault",
        "vn": "Rong Điền-tinh thường", "fam_vn": "Họ Niệm-châu", "fam_lat": "Nostocaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Điền-tinh", "gen_lat": "Nostoc",
        "p": 63, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_60.png",
        "morphology": "Tản chất keo nhầy dạng phiến lồi lõm gấp nếp, màu nâu ô-liu hay lam đậm, rộng vài cm; các chuỗi tế bào hình hạt cườm uốn khúc chằng chịt trong khối nhầy; tế-bào hình cầu hoặc mắt chim; dị-bào hình cầu nằm xen giữa sợi.",
        "distribution": "Toàn cầu. Việt Nam: Vùng duyên hải và các hải đảo.",
        "status": "Mọc trên đất ẩm pha cát hoặc các kẽ đá ven biển trên mức triều cao nhất (supralittoral).",
        "specimen": "Mẫu hải đảo ven bờ Nha-trang.",
        "literature": "Vaucher 1803 : Hist. Conf. d'eau douce : 222, pl. 16, fig. 1; Bornet & Flahault 1888 : Rev. Nostocacées : 203; Desikachary 1959 : Cyanophyta : 353, pl. 61, figs. 9-11."
    },
    {
        "idx": 61, "name": "Richelia intracellularis", "author": "Schmidt",
        "vn": "Rong Ri-sê nội-bào", "fam_vn": "Họ Niệm-châu", "fam_lat": "Nostocaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Ri-sê", "gen_lat": "Richelia",
        "p": 64, "crop": (150, 1100, 2200, 2300), "fig_name": "fig_1_61.png",
        "morphology": "Sợi ngắn gồm một chuỗi 5-15 tế bào, sống nội sinh trong tế bào của Khuê-tảo Rhizosolenia; tế-bào hình cầu hay dẹt, rộng 5-6µ; dị-bào hình cầu lớn nằm ở một đầu sợi.",
        "distribution": "Phù du thực vật phù dưỡng ở khắp các đại dương nhiệt đới. Vịnh Nha-trang.",
        "status": "Sống cộng sinh/nội sinh bên trong tế bào tảo Silic (Rhizosolenia styliformis) trôi nổi ngoài khơi.",
        "specimen": "Mẫu sinh vật phù du vịnh Nha-trang.",
        "literature": "Schmidt 1901 : Vidensk. Medd. dansk naturh. Foren. : 185; Lemmermann 1905 : Bot. Notiser : 148; Desikachary 1959 : Cyanophyta : 374, pl. 66, figs. 1-3."
    },
    {
        "idx": 62, "name": "Hormothamnion solutum", "author": "Bornet & Flahault",
        "vn": "Rong Chuỗi-nhánh rời", "fam_vn": "Họ Niệm-châu", "fam_lat": "Nostocaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Chuỗi-nhánh", "gen_lat": "Hormothamnion",
        "p": 64, "crop": (150, 2100, 2200, 3100), "fig_name": "fig_1_62.png",
        "morphology": "Sợi mọc thành búi nhầy nhỏ, màu lục lam, sợi uốn éo phân nhánh; tế-bào hình thùng tròn, rộng 6-7µ; dị-bào nằm xen giữa chuỗi tế bào; không làm thành màng liên kết dày.",
        "distribution": "Các vùng biển nhiệt đới. Gặp ở Hòn-chồng (Nha-trang).",
        "status": "Phụ sinh trên các loài rong khác ở đới triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Bornet & Flahault 1888 : Rev. Nostocacées : 259; Desikachary 1959 : Cyanophyta : 433."
    },
    {
        "idx": 63, "name": "Hormothamnion enteromorphoides", "author": "Grunow ex Bornet & Flahault",
        "vn": "Rong Chuỗi-nhánh ruột", "fam_vn": "Họ Niệm-châu", "fam_lat": "Nostocaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Chuỗi-nhánh", "gen_lat": "Hormothamnion",
        "p": 65, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_63.png",
        "morphology": "Tản dạng dải nhầy mềm, hình ống rỗng hay hình sợi dày giống rong Ruột (Enteromorpha), dài 1-3cm, màu lục lam; gồm rất nhiều chuỗi tế bào xếp dọc theo chiều dài ống; tế-bào dài bằng hay ngắn hơn rộng; dị-bào hình cầu xen kẽ.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương, Caribê. Việt Nam: Nha-trang, Vũng-Tàu.",
        "status": "Mọc trên đá, rạn san hô hoặc phụ sinh trên gốc rong lớn ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang (Dawson 1954).",
        "literature": "Grunow 1867 : Reise Novara Algen : 31; Bornet & Flahault 1888 : Rev. Nostocacées : 260; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 379, fig. 3n."
    },
    {
        "idx": 64, "name": "Microchaete vitiensis", "author": "Askenasy ex Bornet & Flahault",
        "vn": "Rong Vi-mao Phi-gi", "fam_vn": "Họ Vi-mao", "fam_lat": "Microchaetaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Vi-mao", "gen_lat": "Microchaete",
        "p": 66, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_64.png",
        "morphology": "Sợi mọc thành túm nhỏ hình sao, cao 0,5-1mm; gốc sợi phồng nhẹ dính vào giá thể, rộng 6-8µ; bao mỏng không màu; tế-bào hình chữ nhật hay vuông; 1 dị-bào ở gốc sợi hình bán cầu; đầu sợi thon nhẹ nhưng không có lông dài.",
        "distribution": "Thái-bình-dương, quần đảo Fiji, Việt Nam.",
        "status": "Phụ sinh trên các loài rong lớn ở tầng triều giữa.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Askenasy 1888 : Gazelle Bot. : 3, pl. 1, fig. 2; Bornet & Flahault 1887 : Rev. Nost. Hétéroc. : 85; Desikachary 1959 : Cyanophyta : 511."
    },
    {
        "idx": 65, "name": "Brachytrichia maculans", "author": "(Gomont) Umezaki",
        "vn": "Rong Đoản-mao đốm", "fam_vn": "Họ Đoản-mao", "fam_lat": "Brachytrichiaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Đoản-mao", "gen_lat": "Brachytrichia",
        "p": 67, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_1_65.png",
        "morphology": "Tản dạng đốm phẳng hay đệm nhầy mỏng, màu lục đen sẫm; sợi phân nhánh chữ V đặc trưng; các nhánh ngọn thon dần thành sợi lông ngắn; tế-bào tròn hay bầu dục; dị-bào nằm xen giữa sợi.",
        "distribution": "Biển Đông, Nhật-bản, Thái-bình-dương. Gặp ở bờ biển Nha-trang.",
        "status": "Mọc trên đá ở tầng trung-duyên-hải nơi có sóng vừa.",
        "specimen": "Mẫu thu thập tại Nha-trang.",
        "literature": "Gomont 1901 : Bull. Soc. Bot. France XLVIII : 210; Umezaki 1958 : Revision of Brachytrichia : 72; Desikachary 1959 : Cyanophyta : 580."
    },
    {
        "idx": 66, "name": "Brachytrichia quoyi", "author": "(C. Agardh) Bornet & Flahault",
        "vn": "Rong Đoản-mao Coi", "fam_vn": "Họ Đoản-mao", "fam_lat": "Brachytrichiaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Đoản-mao", "gen_lat": "Brachytrichia",
        "p": 68, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_66.png",
        "morphology": "Tản thịt nhầy lồi lõm gấp nếp, phồng bọng rỗng bên trong lúc già, màu lục sẫm đến nâu đen, rộng 1-5cm; cấu tạo gồm các sợi phân nhánh chữ V chằng chịt trong chất keo; ngọn sợi có lông ngắn; dị-bào xen kẽ hình cầu.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương nhiệt đới. Rất phổ biến tại Việt Nam: Nha-trang, Vũng-Tàu, Côn-đảo.",
        "status": "Bám trên mặt đá phơi nắng ở tầng trung-duyên-hải và thượng-duyên-hải, chịu đựng sóng to và nắng gắt.",
        "specimen": "Mẫu Hòn-chồng, Nha-trang.",
        "literature": "C. Agardh 1824 : Systema Algarum : 47; Bornet & Flahault 1886 : Rev. Nostocacées : 373; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 380, figs. 3k, l."
    },
    {
        "idx": 67, "name": "Mastigocoleus testarum", "author": "Lagerheim ex Bornet & Flahault",
        "vn": "Rong Tiên-bao mai", "fam_vn": "Họ Roi-tảo", "fam_lat": "Mastigocladaceae",
        "ord_vn": "Bộ Niệm-châu", "ord_lat": "Nostocales", "gen_vn": "Chi Rong Tiên-bao", "gen_lat": "Mastigocoleus",
        "p": 69, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_1_67.png",
        "morphology": "Tản vi thể sống khoan thủng vào vỏ vôi của động vật thân mềm và san hô; sợi phân nhánh tự do uốn lượn, rộng 6-10µ; bao mỏng không màu; tế-bào hình trụ tròn; dị-bào mọc ở đầu cành ngắn hoặc xen kẽ; ngọn cành thon thành lông dài.",
        "distribution": "Toàn cầu ở các vùng biển ấm. Khắp duyên hải Việt Nam.",
        "status": "Sống khoan thủng trong vỏ sò, vỏ ốc, hàu và san hô chết ở tầng triều giữa và triều dưới.",
        "specimen": "Mẫu vỏ sò thu tại vịnh Nha-trang.",
        "literature": "Lagerheim 1886 : Notarisia I : 65; Bornet & Flahault 1887 : Rev. Nost. Hétéroc. : 54; Taylor 1960 : Mar. Alg. Trop. Amer. : 50."
    }
]

def crop_figures():
    print('Cropping 40 figures for Batch 2...')
    for sp in BATCH2_DATA:
        p_num = sp['p']
        src_png = os.path.join(DPI300_DIR, f'page-{p_num:03d}.png')
        dst_png = os.path.join(IMAGE_DIR, sp['fig_name'])
        
        if not os.path.exists(src_png):
            print(f"Warning: source image {src_png} not found, skipping crop.")
            continue
            
        with Image.open(src_png) as img:
            w, h = img.size
            crop_box = sp['crop']
            # Bound check
            x1 = max(0, min(crop_box[0], w - 10))
            y1 = max(0, min(crop_box[1], h - 10))
            x2 = max(x1 + 10, min(crop_box[2], w))
            y2 = max(y1 + 10, min(crop_box[3], h))
            cropped = img.crop((x1, y1, x2, y2))
            cropped.save(dst_png, 'PNG', optimize=True)
            print(f"  Cropped #{sp['idx']} -> {sp['fig_name']} ({cropped.size[0]}x{cropped.size[1]})")

def query_worms():
    print('Querying WoRMS API for 40 species...')
    names = [sp['name'] for sp in BATCH2_DATA]
    names_query = '&'.join([f'scientificnames[]={n.replace(" ", "+")}' for n in names])
    url = f'https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?{names_query}&marine_only=false'
    req = urllib.request.Request(url, headers={'User-Agent': 'CamNangCaBien/1.0'})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for sp, item in zip(BATCH2_DATA, data):
            if item:
                rec = item[0]
                sp['worms_id'] = rec.get('AphiaID')
                sp['worms_status'] = rec.get('status')
                sp['worms_accepted_name'] = rec.get('valid_name')
            else:
                sp['worms_id'] = None
                sp['worms_status'] = 'unverified'
                sp['worms_accepted_name'] = sp['name']
    matched = len([s for s in BATCH2_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH2_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON...')
    rows = []
    for sp in BATCH2_DATA:
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
            "tax_class_vn": "Lớp Tảo Lam",
            "tax_class_latin": "Cyanophyceae",
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch2.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 2 build completed successfully!')
