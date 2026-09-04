"""
build_batch5.py — Bóc tách, crop ảnh 300 DPI và chuẩn hóa 73 loài Hồng-tảo (Rhodophyceae - Đợt 5, loài 208-280)
cho Volume 2 (Rong biển Việt Nam - GS. Phạm Hoàng Hộ, 1969).
Hoàn tất 100% PHẦN II (Lớp Hồng-tảo / Rhodophyceae, tổng cộng 213 loài)!
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

BATCH5_DATA = [
    {
        "idx": 208, "name": "Asparagopsis taxiformis", "author": "(Delile) Trevisan",
        "vn": "Rong Măng dạng-thủy-tùng", "fam_vn": "Họ Măng-tảo", "fam_lat": "Bonnemaisoniaceae",
        "ord_vn": "Bộ Măng-tảo", "ord_lat": "Bonnemaisoniales", "gen_vn": "Chi Rong Măng-tảo", "gen_lat": "Asparagopsis",
        "p": 221, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_149.png",
        "morphology": "Tản đứng cao 10-25cm, mọc từ thân bò; thân chính mang các cành phân nhánh lông chim dày đặc như cây thông hay thủy tùng, màu hồng đỏ tươi; sinh kỳ dị hình xen kẽ với giai đoạn thể bào tử dạng sợi nhỏ hình bụi (Falkenbergia rufolanosa).",
        "distribution": "Các vùng biển nhiệt đới ấm toàn cầu. Rất phổ biến khắp bờ biển Việt Nam từ Quảng-ninh đến Kiên-giang.",
        "status": "Rong ăn được có hương vị cay thơm nồng nàn; hiện nay là đối tượng nghiên cứu hàng đầu thế giới để làm phụ gia thức ăn gia súc giảm khí metan.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "Delile 1813 : Fl. d'Égypte : 151, pl. 57; Trevisan 1845 : Nomencl. Alg. : 45; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 414, fig. 25b."
    },
    {
        "idx": 209, "name": "Gymnothamnion elegans", "author": "(Schousboe ex C. Agardh) J. Agardh",
        "vn": "Rong Khỏa-tùng đẹp", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Khỏa-tùng", "gen_lat": "Gymnothamnion",
        "p": 225, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_151.png",
        "morphology": "Tản vi thể hình lông chim thanh tú, cao 3-8mm, màu hồng đỏ; thân đứng mọc từ thân bò dính nhờ rễ giả; nhánh mọc đối ở mỗi tế bào trong cùng một mặt phẳng; tế bào ngọn nhọn.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên các loài rong lớn ở tầng triều giữa.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "C. Agardh 1828 : Sp. Alg. II : 162; J. Agardh 1892 : Analecta Algol. : 27; Tanaka 1952 : Protoflorideae : 12."
    },
    {
        "idx": 210, "name": "Antithamnion basisporum", "author": "Tokida & Inaba",
        "vn": "Rong Nghịch-tùng bào-tử-gốc", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Nghịch-tùng", "gen_lat": "Antithamnion",
        "p": 226, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_152.png",
        "morphology": "Tản sợi nhỏ mảnh mai, cao 5-15mm; các nhánh bên mọc đối đối xứng; tứ-bào-tử-phòng hình bầu dục mọc ở tế-bào gốc của nhánh bên; tế-bào tản đơn nhân.",
        "distribution": "Nhật-bản, Việt Nam (Nha-trang).",
        "status": "Phụ sinh trên rong Mơ (Sargassum).",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Tokida & Inaba 1950 : Sci. Pap. Inst. Alg. Res. Hokkaido III : 118; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 442."
    },
    {
        "idx": 211, "name": "Aglaothamnion neglectum", "author": "Feldmann-Mazoyer",
        "vn": "Rong Mỹ-tùng ẩn", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Mỹ-tùng", "gen_lat": "Aglaothamnion",
        "p": 228, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_154.png",
        "morphology": "Búi tơ màu hồng tươi cao 1-2cm; thân sợi đơn do một hàng tế-bào đơn nhân lớn; phân nhánh so le hình dích dắc; tứ-bào-tử không cuống gắn ở nách nhánh.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên vỏ ốc và đá tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Feldmann-Mazoyer 1940 : Rech. Céram. Médit. : 459, figs. 180-182."
    },
    {
        "idx": 212, "name": "Callithamnion cordatum", "author": "Boergesen",
        "vn": "Rong Mỹ-chi hình-tim", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Mỹ-chi", "gen_lat": "Callithamnion",
        "p": 229, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_155.png",
        "morphology": "Tản hình sợi lông mềm cao 1-3cm; tế-bào dài gấp 4-8 lần rộng; quả-nang (carposporophyte) chẻ đôi hai thùy hình trái tim đặc trưng.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Boergesen 1909 : Bot. Tidsskr. 30 : 10, figs. 5-6; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 442."
    },
    {
        "idx": 213, "name": "Callithamnion corymbosum", "author": "(Smith) Lyngbye",
        "vn": "Rong Mỹ-chi ngù", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Mỹ-chi", "gen_lat": "Callithamnion",
        "p": 230, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_156.png",
        "morphology": "Búi lông tơ cực kỳ mềm mịn như tơ tằm, cao 2-5cm, màu hồng tía; các nhánh ngọn phân nhánh tập trung xòe ngang cùng độ cao tạo hình ngù (corymb).",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên các loài rong lớn ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Smith 1811 : Engl. Bot. : pl. 2352; Lyngbye 1819 : Hydrophyt. Dan. : 125."
    },
    {
        "idx": 214, "name": "Centroceras clavulatum", "author": "(C. Agardh) Montagne",
        "vn": "Rong Trung-giác chùy", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Trung-giác", "gen_lat": "Centroceras",
        "p": 231, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_157.png",
        "morphology": "Tản sợi cứng tạo búi dày cao 3-8cm, màu đỏ tím đậm hay nâu đỏ; chia nhánh đôi đều đặn, ngọn nhánh cuốn cong như càng cua; thân có lớp vỏ tế bào nhỏ bao bọc hoàn toàn suốt chiều dài; ở mỗi mắt khớp có vòng gai nhỏ 1-2 tế bào tỏa tròn.",
        "distribution": "Toàn cầu ở vùng duyên hải nhiệt đới và cận nhiệt đới. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc phủ kín các bãi đá và chân rạn san hô ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Nha-trang, Vũng-Tàu, Côn-đảo, Phú-quốc.",
        "literature": "C. Agardh 1822 : Sp. Alg. I : 466; Montagne 1846 : Fl. Algérie : 140; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446, fig. 54b."
    },
    {
        "idx": 215, "name": "Centroceras inerme", "author": "Kützing",
        "vn": "Rong Trung-giác không-gai", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Trung-giác", "gen_lat": "Centroceras",
        "p": 232, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_158.png",
        "morphology": "Tương tự C. clavulatum với lớp vỏ bao kín thân nhưng các mắt khớp hoàn toàn không có gai nhỏ nhô ra; màu đỏ tía.",
        "distribution": "Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1841 : Linnaea XV : 731; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446."
    },
    {
        "idx": 216, "name": "Ceramium huysmansii", "author": "Weber van Bosse",
        "vn": "Rong Hồng-giác Huýt-xman", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 234, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_159.png",
        "morphology": "Tản nhỏ li ti phụ sinh, cao 3-8mm; vỏ chỉ bọc ở các mắt khớp tạo thành các ngấn đai hẹp, khoảng gian khớp hoàn toàn trong suốt trơ trụi; tế bào vỏ xếp sít sao.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Phú-quốc, Nha-trang.",
        "status": "Phụ sinh trên Centroceras và Sargassum.",
        "specimen": "Mẫu Phú-quốc.",
        "literature": "Weber van Bosse 1923 : Siboga Exped. : 322; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446."
    },
    {
        "idx": 217, "name": "Ceramium howei", "author": "Weber van Bosse",
        "vn": "Rong Hồng-giác Hao", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 235, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_160.png",
        "morphology": "Tản bò rồi đứng cao 5-10mm; đai vỏ mắt khớp mở rộng về phía dưới do các hàng tế bào xếp dọc; phân nhánh đôi rẽ góc hẹp.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên cỏ biển và rong lớn.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Weber van Bosse 1923 : Siboga : 323; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446."
    },
    {
        "idx": 218, "name": "Ceramium fimbriatum", "author": "Setchell & Gardner",
        "vn": "Rong Hồng-giác mép-lông", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 236, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_161.png",
        "morphology": "Tản cao 5-15mm; ở mỗi đai mắt khớp mang một hàng lông tơ cứng ngắn hoặc gai hình chùy đơn độc mọc thành vòng; ngọn nhánh cuốn hình càng cua.",
        "distribution": "Vịnh California, Thái-bình-dương nhiệt đới. Việt Nam: Nha-trang, Cà-ná.",
        "status": "Phụ sinh trên thân rong khác hoặc bám đá.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Setchell & Gardner 1924 : Mar. Alg. Revillagigedo : 725; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446, fig. 55a."
    },
    {
        "idx": 219, "name": "Ceramium gracillimum", "author": "(Kützing) Griffiths & Harvey",
        "vn": "Rong Hồng-giác rất-thanh", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 237, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_162.png",
        "morphology": "Tản tơ mảnh mai cao 1-3cm, màu hồng tía; đai vỏ hẹp gồm tế bào nhỏ ở trên và tế bào kéo dài ở dưới; ngọn nhánh chẻ đôi cuốn cong.",
        "distribution": "Toàn cầu ở vùng duyên hải. Rất phổ biến tại Việt Nam.",
        "status": "Phụ sinh trên nhiều loài rong lớn ở tầng triều giữa.",
        "specimen": "Mẫu bãi biển Nha-trang.",
        "literature": "Kützing 1841 : Linnaea XV : 733; Harvey 1848 : Phyc. Brit. II : pl. 206; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 448."
    },
    {
        "idx": 220, "name": "Ceramium procumbens", "author": "Setchell & Gardner",
        "vn": "Rong Hồng-giác nằm", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 238, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_164.png",
        "morphology": "Tản bò sát giá thể, các nhánh đứng rất ngắn chỉ cao 1-2mm; đai mắt khớp hẹp; rễ giả phát triển mạnh từ thân bò.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên rong khác.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Setchell & Gardner 1924 : Mar. Alg. Revillagigedo : 772, pl. 27; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446."
    },
    {
        "idx": 221, "name": "Ceramium cingulatum", "author": "Weber van Bosse",
        "vn": "Rong Hồng-giác đai", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 238, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_165.png",
        "morphology": "Tản bò mang nhánh đứng, các đai mắt khớp phân chia ranh giới rõ rệt như thắt đai lưng đều đặn; màu đỏ tươi.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Bám trên sỏi đá vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Weber van Bosse 1923 : Siboga : 332; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 446."
    },
    {
        "idx": 222, "name": "Ceramium mazatlanense", "author": "Dawson",
        "vn": "Rong Hồng-giác Ma-dát-lan", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 239, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_166.png",
        "morphology": "Tản sụn mềm phân nhánh đôi nhiều lần; đai vỏ mắt khớp do các tế bào tròn nhỏ xếp thành 3-4 hàng; tứ-bào-tử-phòng lồi tròn một bên đai.",
        "distribution": "Mexico, Thái-bình-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên rong Mơ (Sargassum).",
        "specimen": "Mẫu vịnh Nha-trang (Dawson 1954).",
        "literature": "Dawson 1950 : Amer. J. Bot. 37 : 148, pl. 2; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 448."
    },
    {
        "idx": 223, "name": "Ceramium clarionense", "author": "Setchell & Gardner",
        "vn": "Rong Hồng-giác Cơ-la-ri-ông", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 240, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_167.png",
        "morphology": "Tản cao 5-15mm, ngọn nhánh cuốn cong mạnh hình móng vuốt; đai vỏ mắt khớp rất đặc trưng với hàng tế bào dưới cùng kéo dài theo trục dọc.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở bờ biển Nha-trang.",
        "status": "Phụ sinh trên Turbinaria và Sargassum.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Setchell & Gardner 1930 : Mar. Alg. Revillagigedo : 170, pl. 7; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 448."
    },
    {
        "idx": 224, "name": "Ceramium aduncum", "author": "Nakamura",
        "vn": "Rong Hồng-giác móc", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 241, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_168.png",
        "morphology": "Tản có các nhánh ngọn cuốn cong thành hình móc câu rõ rệt; đai vỏ dày gồm nhiều hàng tế bào nhỏ; màu đỏ tía đậm.",
        "distribution": "Nhật-bản, Việt Nam (Nha-trang).",
        "status": "Phụ sinh trên rong khác ở tầng triều giữa.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Nakamura 1950 : New Ceramium Japan : 158; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 448."
    },
    {
        "idx": 225, "name": "Ceramium fastigiatum", "author": "Harvey",
        "vn": "Rong Hồng-giác thẳng", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 242, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_169.png",
        "morphology": "Búi tơ mảnh đứng thẳng cao 1-3cm; nhánh phân đôi góc nhọn vươn thẳng lên trên; đai mắt khớp hẹp chỉ gồm 2-3 hàng tế bào.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Harvey 1834 : Hook. Brit. Fl. II : 333; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 448."
    },
    {
        "idx": 226, "name": "Ceramium vietnamense", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Hồng-giác việtnam", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-giác", "gen_lat": "Ceramium",
        "p": 243, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_170.png",
        "morphology": "Tản nhỏ li ti cao 1-2mm; sợi bò mang nhánh đứng; đặc sắc ở cấu trúc đai mắt khớp chỉ gồm đúng 2 hàng tế bào xếp song song đều đặn; tứ-bào-tử-phòng lồi to ở mắt khớp. Loài mới do GS. Phạm Hoàng Hộ phát hiện và mô tả.",
        "distribution": "Đặc hữu bờ biển Việt Nam (Nha-trang).",
        "status": "Phụ sinh trên lá cỏ biển Halodule ở vũng triều nông.",
        "specimen": "Holotype thu tại Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 239, fig. 2.170."
    },
    {
        "idx": 227, "name": "Pleonosporium borrieri", "author": "(Smith) Nägeli",
        "vn": "Rong Đa-bào-tử Bô-rê", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-bào-tử", "gen_lat": "Pleonosporium",
        "p": 244, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_171.png",
        "morphology": "Tản lông chim màu hồng đỏ tía cao 2-5cm; thân đơn trục phân nhánh lông chim 2 lần; đặc trưng nổi bật là bào-tử-phòng chứa rất nhiều bào tử (đa-bào-tử-phòng, polysporangia chứa 16-32 bào tử) thay vì 4 bào tử như thông thường.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Smith 1811 : Engl. Bot. : pl. 2309; Nägeli 1861 : Ceramiac. : 381; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 444."
    },
    {
        "idx": 228, "name": "Griffithsia tenuis", "author": "C. Agardh",
        "vn": "Rong Gơ-ríp-phít mảnh", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Gơ-ríp-phít", "gen_lat": "Griffithsia",
        "p": 245, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_172.png",
        "morphology": "Tản sợi màu hồng tươi cao 1-3cm; do một hàng tế-bào khổng lồ hình trụ tròn mắt thấy rõ (dài 1-2mm, rộng 200-300µ); phân nhánh đôi thưa; tứ-bào-tử-phòng có cuống mọc thành vòng quanh khớp.",
        "distribution": "Khắp thế giới ở vùng biển ấm. Rất phổ biến tại Việt Nam.",
        "status": "Mọc trên đá và phụ sinh trên rong khác ở tầng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Vũng-Tàu.",
        "literature": "C. Agardh 1828 : Sp. Alg. II : 131; Okamura 1930 : Icones Jap. Alg. VI : pl. 271; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 444."
    },
    {
        "idx": 229, "name": "Griffithsia japonica", "author": "Okamura",
        "vn": "Rong Gơ-ríp-phít Nhật-bản", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Gơ-ríp-phít", "gen_lat": "Griffithsia",
        "p": 246, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_173.png",
        "morphology": "Tản sợi gồm các tế bào hình bầu dục hay hình chùy rất to mọng nước, màu đỏ hồng; các ổ tứ-bào-tử được bao bọc bởi một vòng lá bao ngắn bảo vệ.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng hạ-duyên-hải trên rạn san hô.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Okamura 1930 : Icones Jap. Alg. VI : 28, pl. 270."
    },
    {
        "idx": 230, "name": "Griffithsia metcalfii", "author": "Tseng",
        "vn": "Rong Gơ-ríp-phít Mét-kép", "fam_vn": "Họ Thao-bào", "fam_lat": "Ceramiaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Gơ-ríp-phít", "gen_lat": "Griffithsia",
        "p": 247, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_174.png",
        "morphology": "Tản cao 2-4cm, các tế bào ngọn phồng to hình cầu tròn như chuỗi bong bóng nhỏ li ti; màu đỏ vang.",
        "distribution": "Biển Đông (Hải Nam, Việt Nam).",
        "status": "Mọc ở tầng triều dưới nơi nước sạch.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Tseng 1942 : Chinese Spec. Griffithsia : 111, figs. 5-7; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 444."
    },
    {
        "idx": 231, "name": "Dasyopsis pilosa", "author": "Weber van Bosse",
        "vn": "Rong Giả-đa-si lông", "fam_vn": "Họ Đa-si", "fam_lat": "Dasyaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Giả-đa-si", "gen_lat": "Dasyopsis",
        "p": 248, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_175.png",
        "morphology": "Tản hình bụi màu đỏ nâu tía cao 3-8cm; thân chính dẹp có vỏ bao bọc, phủ đầy các nhánh lông tơ hình sợi mảnh chia nhánh đôi liên tục; ổ tứ-bào-tử hình mũi mác (stichidia).",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô tầng hạ-duyên-hải.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Weber van Bosse 1923 : Siboga : 377, pl. 7; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 451, fig. 56e-f."
    },
    {
        "idx": 232, "name": "Dasya pedicellata", "author": "(C. Agardh) C. Agardh",
        "vn": "Rong Đa-si có-cuống", "fam_vn": "Họ Đa-si", "fam_lat": "Dasyaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-si", "gen_lat": "Dasya",
        "p": 249, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_176.png",
        "morphology": "Tản tuyệt đẹp như một chiếc đuôi chồn màu đỏ tía rực rỡ, cao 10-25cm; trục chính to tròn có vỏ bao bọc, mang vô số nhánh lông tơ màu hồng mềm mại mọc tỏa tròn; quả-nang hình bình hoa có cuống rõ rệt.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc ở tầng hạ-duyên-hải sâu 2-8m trên đá và san hô nơi nước êm.",
        "specimen": "Mẫu lặn thu thập tại vịnh Nha-trang.",
        "literature": "C. Agardh 1824 : Syst. Alg. : 211; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 451, fig. 56a-c."
    },
    {
        "idx": 233, "name": "Dasya villosa", "author": "Harvey",
        "vn": "Rong Đa-si lông-dày", "fam_vn": "Họ Đa-si", "fam_lat": "Dasyaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-si", "gen_lat": "Dasya",
        "p": 250, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_177.png",
        "morphology": "Tản cao 8-15cm, thân chính phủ đầy lông nhung màu nâu đỏ sẫm dày đặc; các cành mang ổ túi bào-tử hình suốt thon dài.",
        "distribution": "Úc, Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Tầng triều dưới trên rạn đá.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Harvey 1844 : London J. Bot. III : 433; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 451."
    },
    {
        "idx": 234, "name": "Caloglossa leprieurii", "author": "(Montagne) G. Martens",
        "vn": "Rong Kiều-thiệt Lơ-pơ-ri-ơ", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Kiều-thiệt", "gen_lat": "Caloglossa",
        "p": 253, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_179.png",
        "morphology": "Tản phiến mỏng màu tím nâu hay đỏ sẫm, cao 1-3cm; thân dẹp chia thành từng lóng hình lưỡi thuyền hay mũi mác thắt eo ở các mấu khớp; có gân giữa rõ rệt chạy suốt chiều dài; từ các khớp mọc ra búi rễ giả dính chặt vào giá thể; phân nhánh lưỡng phân.",
        "distribution": "Khắp thế giới ở các vùng rừng ngập mặn và cửa sông nhiệt đới, cận nhiệt đới. Rất phong phú khắp bờ biển Việt Nam.",
        "status": "Loài đặc trưng của quần xã rừng ngập mặn (Bostrychietum); phủ kín rễ đước, rễ vẹt và cọc bến cảng.",
        "specimen": "Mẫu rừng ngập mặn Cần-giờ, Hải-phòng, Cà-mau.",
        "literature": "Montagne 1840 : Ann. Sci. Nat. Bot. XIII : 196; Martens 1869 : Flora : 234; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 451."
    },
    {
        "idx": 235, "name": "Caloglossa adnata", "author": "(Zanardini) De Toni",
        "vn": "Rong Kiều-thiệt dính", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Kiều-thiệt", "gen_lat": "Caloglossa",
        "p": 254, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_180.png",
        "morphology": "Tản bò dính sát hoàn toàn mặt dưới vào vỏ cây bằng hàng rễ giả dọc theo gân giữa; các phiến lá hình dải rộng màu nâu đỏ; không thắt eo sâu như C. leprieurii.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rừng sác ngập mặn Nam bộ Việt Nam.",
        "status": "Bám trên vỏ thân cây mắm, đước.",
        "specimen": "Mẫu Cần-giờ và Nhà-bè.",
        "literature": "Zanardini 1872 : Phyc. Ind. : 141; De Toni 1900 : Syll. Alg. IV : 731."
    },
    {
        "idx": 236, "name": "Caloglossa stipitata", "author": "Post",
        "vn": "Rong Kiều-thiệt có-cuống", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Kiều-thiệt", "gen_lat": "Caloglossa",
        "p": 254, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_181.png",
        "morphology": "Tản có phần cuống hình trụ tròn rõ rệt rồi mới loe ra thành phiến lá mỏng màu đỏ tía có gân giữa.",
        "distribution": "Biển Đông, Malaysia, Indonesia.",
        "status": "Vùng cửa sông rừng ngập mặn.",
        "specimen": "Mẫu cửa sông Đồng-tranh, Cần-giờ.",
        "literature": "Post 1936 : Bostrychia-Caloglossa Assoc. : 60; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 250."
    },
    {
        "idx": 237, "name": "Caloglossa saigonensis", "author": "Tanaka & Pham-hoang Ho nov. sp.",
        "vn": "Rong Kiều-thiệt Sài-gòn", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Kiều-thiệt", "gen_lat": "Caloglossa",
        "p": 255, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_182.png",
        "morphology": "Tản phiến mỏng dài 1,5cm rộng 1,3mm, màu đỏ tươi; gân giữa đơn độc rất rõ; đặc sắc nhờ các nhánh con mọc đối từ nách lá và cấu trúc ổ bào tử; sống trong vùng nước lợ cửa sông. Loài mới phát hiện ven sông Sài Gòn.",
        "distribution": "Đặc hữu vùng cửa sông Sài-gòn - Nhà-bè (Việt Nam).",
        "status": "Bám trên cọc gỗ và rễ dừa nước ở vùng hạ lưu sông nước lợ.",
        "specimen": "Holotype thu tại Nhà-bè, Sài-gòn.",
        "literature": "Tanaka & Phạm-hoàng Hộ 1962 : Notes Mar. Alg. Vietn. I : 38, fig. 13; Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 251."
    },
    {
        "idx": 238, "name": "Martensia denticulata", "author": "Harvey",
        "vn": "Rong Mác-tăng răng-cưa", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Mác-tăng", "gen_lat": "Martensia",
        "p": 256, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_183.png",
        "morphology": "Tản phiến mỏng màu hồng tía ánh ngũ sắc tuyệt đẹp, cao 3-6cm; phần gốc phiến liền, phần ngọn phát triển thành một tấm màng đan lưới thủng lỗ tổ ong đều tăm tắp rất kỳ diệu; mép phiến có răng cưa nhỏ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc ở rạn san hô sâu 2-8m nơi nước trong sạch.",
        "specimen": "Mẫu lặn thu tại Hòn-mun, Nha-trang.",
        "literature": "Harvey 1841 : Trans. R. Irish Acad. 22 : 537; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 452."
    },
    {
        "idx": 239, "name": "Claudea elegans", "author": "Lamouroux",
        "vn": "Rong Cơ-lốt đẹp", "fam_vn": "Họ Màng-tảo", "fam_lat": "Delesseriaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Cơ-lốt", "gen_lat": "Claudea",
        "p": 257, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_183b.png",
        "morphology": "Một trong những loài rong biển đẹp nhất thế giới; tản hình lông chim kép tạo mạng lưới ren đan hoa văn tinh xảo hình vòm cuốn như cánh quạt ren, màu đỏ hồng thắm rực rỡ.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Hiếm gặp, mọc ở vùng rạn san hô sâu tầng dưới triều.",
        "specimen": "Mẫu khảo sát Nha-trang.",
        "literature": "Lamouroux 1813 : Essai : 44, pl. 8; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 452."
    },
    {
        "idx": 240, "name": "Polysiphonia harlandii", "author": "Harvey",
        "vn": "Rong Đa-quản Hác-lan", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 258, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_184.png",
        "morphology": "Tản bụi màu nâu đỏ sẫm cao 3-8cm; thân hình sợi do 4 tế-bào chu-tâm bao quanh ống trục giữa (cơ cấu 4 quản); phần gốc có lớp tế bào vỏ bao phủ; phân nhánh so le đều.",
        "distribution": "Hồng Kông, Biển Đông. Phổ biến ven biển miền Trung Việt Nam.",
        "status": "Mọc trên đá và phụ sinh trên rong lớn vùng triều.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Harvey 1860 : Proc. Amer. Acad. IV : 330; Tseng 1944 : Mar. Alg. Hong Kong : 78; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454."
    },
    {
        "idx": 241, "name": "Polysiphonia subtilissima", "author": "Montagne",
        "vn": "Rong Đa-quản rất-mảnh", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 259, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_185.png",
        "morphology": "Búi tơ nhỏ mềm mại cao 1-2cm, màu nâu tím; cơ cấu 4 tế bào chu-tâm, hoàn toàn không có vỏ bao; các lóng dài gấp 3-4 lần đường kính.",
        "distribution": "Toàn cầu ở đầm lợ và duyên hải. Rất phổ biến tại Việt Nam.",
        "status": "Mọc trên bùn cát đầm phá và rừng ngập mặn.",
        "specimen": "Mẫu vịnh Cam-ranh và Nha-trang.",
        "literature": "Montagne 1840 : Ann. Sci. Nat. Bot. XIII : 199; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454."
    },
    {
        "idx": 242, "name": "Polysiphonia sparsa", "author": "(Setchell) Hollenberg",
        "vn": "Rong Đa-quản thưa", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 260, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_186.png",
        "morphology": "Tản sợi nhỏ phân nhánh thưa thớt, cao 1-1,5cm, màu đỏ sẫm; cơ cấu 4 tế bào chu-tâm không vỏ; lóng ngắn.",
        "distribution": "Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên rạn san hô.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Setchell 1926 : Tahitian Alg. : 101; Hollenberg 1968 : Pac. Sci. 22 : 87."
    },
    {
        "idx": 243, "name": "Polysiphonia fragilis", "author": "Suringar",
        "vn": "Rong Đa-quản giòn", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 261, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_187.png",
        "morphology": "Búi tơ giòn dễ gãy màu nâu đỏ, cao 1-2cm; thân sợi chia nhánh đôi đều; có 4 tế bào chu-tâm không vỏ; tứ-bào-tử hình xoan xếp thành chuỗi xoắn ốc ở ngọn cành.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Suringar 1870 : Alg. Jap. : 37, pl. 25; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454."
    },
    {
        "idx": 244, "name": "Polysiphonia ferulacea", "author": "Suhr ex J. Agardh",
        "vn": "Rong Đa-quản thìa-là", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 262, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_188.png",
        "morphology": "Tản tạo bụi dày cứng màu nâu đen, cao 3-6cm; cơ cấu gồm 12-16 tế bào chu-tâm (đa quản nhiều tế bào); không vỏ.",
        "distribution": "Đại-tây-dương, Thái-bình-dương. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên đá vùng triều thấp nơi sóng mạnh.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "J. Agardh 1863 : Sp. Alg. II : 980; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454."
    },
    {
        "idx": 245, "name": "Polysiphonia hawaiiensis", "author": "Hollenberg",
        "vn": "Rong Đa-quản Ha-oai", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 263, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_189.png",
        "morphology": "Tản sợi mảnh mềm, cao 1-3cm; cơ cấu gồm 8-10 tế bào chu-tâm; nhánh phụ mọc so le cách quãng.",
        "distribution": "Hawaii, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Phụ sinh trên Turbinaria ở rạn san hô.",
        "specimen": "Mẫu Hòn-tre Nha-trang.",
        "literature": "Hollenberg 1968 : Pac. Sci. 22 : 66, figs. 18-19."
    },
    {
        "idx": 246, "name": "Polysiphonia nhatrangensis", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Đa-quản Nha-trang", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đa-quản", "gen_lat": "Polysiphonia",
        "p": 264, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_190.png",
        "morphology": "Tản phụ sinh nhỏ cao 5-10mm; thân có 4 tế bào chu-tâm không vỏ; đặc sắc nhờ các nhánh ngọn mang chùm lông không màu xoắn ốc và tứ-bào-tử-phòng hình cầu lớn. Loài mới phát hiện tại Nha Trang.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Khánh-hòa, Việt Nam).",
        "status": "Phụ sinh trên rong Lỗ-năng (Laurencia) và trên vỏ tàu thuyền neo đậu.",
        "specimen": "Holotype thu tại cảng Cầu-đá, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 260, fig. 2.190."
    },
    {
        "idx": 247, "name": "Bryocladia cervicornis", "author": "(Kützing) Schmitz",
        "vn": "Rong Rêu-chi sừng-hươu", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Rêu-chi", "gen_lat": "Bryocladia",
        "p": 265, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_191.png",
        "morphology": "Tản mọc thành thảm nhung cứng cao 2-5cm, màu nâu đỏ sẫm; thân đứng phân nhánh lông chim dày đặc, các nhánh con cứng quăn cuốn ở ngọn như sừng hươu; có 8-10 tế bào chu-tâm.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang, Qui-nhơn.",
        "status": "Mọc trên đá vùng trung-duyên-hải nơi sóng to.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Kützing 1847 : Flora : 774; Schmitz in Falkenberg 1901 : Rhodomelaceen : 169; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454."
    },
    {
        "idx": 248, "name": "Bostrychia binderi", "author": "Harvey",
        "vn": "Rong Hồng-bách Bin-đơ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-bách", "gen_lat": "Bostrychia",
        "p": 266, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_192.png",
        "morphology": "Tản phủ thảm màu tím nâu xẫm cao 1-3cm; thân chia nhánh lông chim 2-3 lần đều đặn; nhánh con có ngọn cuốn móc; cơ cấu trục có lớp vỏ tế bào nhỏ bao bọc bên ngoài các tế bào chu-tâm.",
        "distribution": "Toàn cầu ở rừng ngập mặn và duyên hải đá ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Mọc bám trên rễ thở cây ngập mặn và trên vách đá râm mát tầng trung-duyên-hải thượng.",
        "specimen": "Mẫu Nha-trang, Cần-giờ, Vũng-Tàu.",
        "literature": "Harvey 1847 : Nereis Austr. : 68, pl. 28; Post 1936 : Bostrychia-Caloglossa : 28; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 452."
    },
    {
        "idx": 249, "name": "Bostrychia tenella", "author": "(Vahl) J. Agardh",
        "vn": "Rong Hồng-bách mảnh", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-bách", "gen_lat": "Bostrychia",
        "p": 267, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_193.png",
        "morphology": "Tản hình bụi tơ mịn như nhung màu nâu xám lúc khô, màu sô-cô-la lúc ướt; các nhánh ngọn mảnh khảnh do các tế bào đơn trục không có vỏ bao bọc; nhánh uốn lượn mềm mại.",
        "distribution": "Biển nhiệt đới toàn cầu. Phổ biến tại Việt Nam.",
        "status": "Bám vách đá dốc đứng ở mực triều cao.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Vahl 1802 : Skr. Naturh.-Selsk. V : 45; J. Agardh 1863 : Sp. Alg. II : 869; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 453."
    },
    {
        "idx": 250, "name": "Bostrychia radicans", "author": "(Montagne) Montagne",
        "vn": "Rong Hồng-bách ra-rễ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-bách", "gen_lat": "Bostrychia",
        "p": 268, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_194.png",
        "morphology": "Tản bò lan tỏa mang vô số rễ bám hình trụ (cladosiphons) đâm xuống giá thể; thân đứng phân nhánh thưa; hoàn toàn không có lớp vỏ ngoài (ecorticate).",
        "distribution": "Các vùng rừng ngập mặn nhiệt đới ấm toàn cầu. Việt Nam: Nam bộ.",
        "status": "Bám trên rễ đước, vẹt ở rừng ngập mặn nước lợ.",
        "specimen": "Mẫu rừng sác Cần-giờ.",
        "literature": "Montagne 1840 : Ann. Sci. Nat. Bot. XIII : 198; Post 1936 : Bostrychia-Caloglossa : 13."
    },
    {
        "idx": 251, "name": "Bostrychia kelanensis", "author": "Mobius ex De Toni",
        "vn": "Rong Hồng-bách Kê-lan", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Hồng-bách", "gen_lat": "Bostrychia",
        "p": 269, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_195.png",
        "morphology": "Tản tạo thảm sát giá thể màu đỏ sẫm; thân bò có móc to; nhánh đứng đơn giản; không vỏ bọc ngoài.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Rừng ngập mặn Việt Nam.",
        "status": "Mọc trên thân cây ngập mặn ở vùng triều cao.",
        "specimen": "Mẫu Cần-giờ và Cà-mau.",
        "literature": "De Toni 1903 : Syll. Alg. IV : 1152; Post 1936 : Bostrychia-Caloglossa : 22."
    },
    {
        "idx": 252, "name": "Herposiphonia tenella", "author": "(C. Agardh) Ambronn",
        "vn": "Rong Bò-quản mảnh", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Bò-quản", "gen_lat": "Herposiphonia",
        "p": 271, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_196.png",
        "morphology": "Tản bò chằng chịt, từ mỗi mắt của thân bò mọc ra các nhánh đứng có giới hạn sinh trưởng (short shoots) và nhánh bò dài vô hạn (long shoots) luân phiên nhau theo một trật tự toán học nghiêm ngặt; màu đỏ nâu; cơ cấu 8-10 tế bào chu-tâm.",
        "distribution": "Toàn cầu ở vùng biển ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Phụ sinh trên các loài rong lớn và bám trên đá tầng triều giữa.",
        "specimen": "Mẫu bãi biển Nha-trang và Vũng-Tàu.",
        "literature": "C. Agardh 1828 : Sp. Alg. II : 105; Ambronn 1880 : Ber. Bot. Ges. : 197; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 452, fig. 59a."
    },
    {
        "idx": 253, "name": "Herposiphonia vietnamica", "author": "Pham-hoang Ho nov. sp.",
        "vn": "Rong Bò-quản việtnam", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Bò-quản", "gen_lat": "Herposiphonia",
        "p": 272, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_197.png",
        "morphology": "Tản phụ sinh nhỏ nhắn; nhánh đứng rất ngắn chỉ gồm 8-12 lóng; đặc sắc ở cấu trúc 6-8 tế bào chu-tâm và ngọn nhánh cuốn hình xoắn ốc mang chùm lông tơ lớn. Loài mới cho khoa học do GS. Phạm Hoàng Hộ phát hiện tại Nha Trang.",
        "distribution": "Đặc hữu vùng biển Nha-trang (Khánh-hòa, Việt Nam).",
        "status": "Phụ sinh trên Dictyota và Sargassum ở tầng triều thấp.",
        "specimen": "Holotype thu tại Hòn-chồng, Nha-trang.",
        "literature": "Phạm-hoàng Hộ 1969 : Rong biển Việt Nam : 268, fig. 2.197."
    },
    {
        "idx": 254, "name": "Lophosiphonia villum", "author": "(J. Agardh) Setchell & Gardner",
        "vn": "Rong Quoa-quản đỏ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Quoa-quản", "gen_lat": "Lophosiphonia",
        "p": 273, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_198.png",
        "morphology": "Tản tạo thảm lông màu nâu đỏ dày cộm trên đá, cao 5-10mm; thân bò mang các nhánh đứng đơn không phân nhánh xếp thành hàng dày đặc; có 4 tế bào chu-tâm; ngọn nhánh hơi uốn cong lưng.",
        "distribution": "Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều cao nơi sóng đập.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1863 : Sp. Alg. II : 941; Setchell & Gardner 1903 : Alg. N. Amer. : 329; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 451, fig. 58f-g."
    },
    {
        "idx": 255, "name": "Lophosiphonia reptabunda", "author": "(Suhr) Kylin",
        "vn": "Rong Quoa-quản bò", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Quoa-quản", "gen_lat": "Lophosiphonia",
        "p": 274, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_199.png",
        "morphology": "Tản bò chằng chịt, thân đứng cao 5-12mm; cơ cấu gồm 6-8 tế bào chu-tâm; nhánh đứng uốn cong hình lưỡi liềm ở ngọn.",
        "distribution": "Địa-trung-hải, Biển Đỏ, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng trung-duyên-hải.",
        "specimen": "Mẫu bờ biển Nha-trang.",
        "literature": "Suhr 1831 : Flora : 685; Kylin 1956 : Gatt. Rhodophyc. : 539; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 452."
    },
    {
        "idx": 256, "name": "Roschera glomerulata", "author": "(C. Agardh) Weber van Bosse",
        "vn": "Rong Rốt-se chùm", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Rốt-se", "gen_lat": "Roschera",
        "p": 275, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_200.png",
        "morphology": "Tản hình bụi sụn dẻo dai màu nâu đỏ, cao 5-12cm; thân tròn mang các cụm nhánh con ngắn hình cầu mọc vòng quanh trục như những quả bông nhỏ đan lưới; có 4 tế bào chu-tâm.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Rất phong phú ở miền Trung và hải đảo Việt Nam.",
        "status": "Mọc trên rạn san hô chết và đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "C. Agardh 1822 : Sp. Alg. : 343; Weber van Bosse 1923 : Siboga : 359; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 454, fig. 59b-c."
    },
    {
        "idx": 257, "name": "Tolypiocladia calodictyon", "author": "(Harvey ex Kützing) P.C. Silva",
        "vn": "Rong Cuộn-chi lưới-đẹp", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Cuộn-chi", "gen_lat": "Tolypiocladia",
        "p": 275, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_201.png",
        "morphology": "Tản dạng bụi xốp, các nhánh con liên kết đan cài thành một mạng lưới mắt cáo hình trụ rỗng màu đỏ nâu rất thanh nhã.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Rạn san hô tầng triều dưới.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "Kützing 1864 : Tab. Phyc. XIV : 20; Silva 1952 : Univ. Calif. Publ. Bot. 25 : 308."
    },
    {
        "idx": 258, "name": "Acanthophora spicifera", "author": "(Vahl) Boergesen",
        "vn": "Rong Cứt-đài gai", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Cứt-đài", "gen_lat": "Acanthophora",
        "p": 276, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_202.png",
        "morphology": "Tản sụn dai giòn mọc thành bụi cao 10-25cm, màu vàng lục, nâu hay đỏ sẫm; thân chính hình trụ tròn đường kính 2-3mm, trơn nhẵn; các nhánh phụ ngắn phủ đầy các gai nhọn nhỏ mọc tỏa tròn như bông lúa (spicifera); cơ cấu trong có 5 tế bào chu-tâm được bao bọc bởi mô vỏ dày.",
        "distribution": "Khắp các vùng biển nhiệt đới và cận nhiệt đới thế giới. Cực kỳ phong phú ở toàn bộ duyên hải Việt Nam.",
        "status": "Rong kinh tế ăn được, làm gỏi, nấu canh thanh nhiệt và chiết lambda-carrageenan; mọc dày đặc trên rạn san hô nông và bãi đá.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu, Phú-quốc.",
        "literature": "Vahl 1802 : Skr. Naturh.-Selsk. V : 44; Boergesen 1918 : Mar. Alg. Dan. W. Ind. II : 259; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 456, fig. 61a-b."
    },
    {
        "idx": 259, "name": "Leveillea jungermannioides", "author": "(Hering & G. Martens) Harvey",
        "vn": "Rong Lơ-ve rêu", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lơ-ve", "gen_lat": "Leveillea",
        "p": 277, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_203.png",
        "morphology": "Tản bò màu đỏ tươi tuyệt đẹp, trông giống hệt cây Rêu gan (Jungermannia); thân bò mang 2 hàng vảy lá mọc xếp lợp xen kẽ sít sao; ngọn vảy lá mang chùm lông tơ mịn; đĩa dính bám chặt vào rong chủ.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương, Biển Đỏ. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Phụ sinh phổ biến trên thân rong Mơ (Sargassum), Turbinaria và Padina ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Côn-đảo.",
        "literature": "Martens & Hering 1836 : Flora XIX : 481; Harvey 1855 : Trans. R. Irish Acad. 22 : 539; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 456, fig. 60a."
    },
    {
        "idx": 260, "name": "Amansia glomerata", "author": "C. Agardh",
        "vn": "Rong A-măng chùm", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong A-măng", "gen_lat": "Amansia",
        "p": 278, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_204.png",
        "morphology": "Tản đứng cao 5-12cm, màu đỏ nâu sẫm hay tía; thân hình trụ trơ trụi ở phần dưới, phần trên mang các chùm lá dẹp mọc tỏa tròn thành hình bông hoa hồng nhiều cánh; mép lá có răng cưa nhỏ và ngọn cuốn cong vào trong.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương nhiệt đới. Việt Nam: Nam Trung bộ và hải đảo.",
        "status": "Mọc bám trên gờ đá san hô nơi sóng đập dữ dội ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu đảo Hòn-chồng và Hòn-mun, Nha-trang.",
        "literature": "C. Agardh 1822 : Sp. Alg. I : 194; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 456, fig. 60b-c."
    },
    {
        "idx": 261, "name": "Neurymenia fraxinifolia", "author": "(Mertens ex Turner) J. Agardh",
        "vn": "Rong Mạch-mạc lá-tro", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Mạch-mạc", "gen_lat": "Neurymenia",
        "p": 279, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_205.png",
        "morphology": "Tản hình phiến lá dẹp màu đỏ nâu ánh đồng, cao 8-15cm; phiến có gân giữa nổi rõ và các gân phụ mọc đối xứng chạy song song ra mép lá giống hệt chiếc lá cây Tro (Fraxinus); mép lá có răng cưa nhọn.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương nhiệt đới. Gặp ở Nha-trang.",
        "status": "Mọc ở vùng rạn san hô sâu 10-15m nơi nước trong tại Hòn-yến (Khánh-hòa).",
        "specimen": "Mẫu lặn thu thập tại Hòn-yến, Nha-trang.",
        "literature": "Turner 1819 : Fuci IV : pl. 193; J. Agardh 1863 : Sp. Alg. II : 1135; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 456."
    },
    {
        "idx": 262, "name": "Laurencia parvipapillata", "author": "Tseng",
        "vn": "Rong Lỗ-năng nhú-nhỏ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 281, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_206.png",
        "morphology": "Tản sụn dày cứng dẹp mọc bò sát mặt đá, màu đỏ nâu đen; thân dẹp rộng 2-4mm, mép và mặt trên phủ đầy các nốt nhú thịt nhỏ hình chùy tù.",
        "distribution": "Biển Đông (Hải Nam, Việt Nam). Phổ biến ở miền Trung.",
        "status": "Bám cực chắc trên mặt đá phẳng nơi sóng vỗ mạnh ở tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Tseng 1943 : Mar. Alg. Hong Kong IV : 204, pl. 4; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458, fig. 61g."
    },
    {
        "idx": 263, "name": "Laurencia thyroidea", "author": "Kützing",
        "vn": "Rong Lỗ-năng hình-khiên", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 281, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_207.png",
        "morphology": "Tản sụn cao 4-8cm, nhánh dẹp phân nhánh lông chim; ngọn nhánh có các nốt lõm mang bao sinh sản.",
        "distribution": "Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1865 : Tab. Phyc. XV : pl. 74."
    },
    {
        "idx": 264, "name": "Laurencia articulata", "author": "Tseng",
        "vn": "Rong Lỗ-năng có-đốt", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 282, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_207b.png",
        "morphology": "Tản sụn mềm hình trụ tròn cao 3-6cm, màu vàng lục; các nhánh thắt eo rõ rệt thành từng đốt hình thoi hoặc bầu dục.",
        "distribution": "Hồng Kông, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc kẽ đá san hô dưới triều.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Tseng 1943 : Mar. Alg. Hong Kong IV : 196, pl. 2."
    },
    {
        "idx": 265, "name": "Laurencia corymbosa", "author": "J. Agardh",
        "vn": "Rong Lỗ-năng tản-phòng", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 283, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_208.png",
        "morphology": "Tản sụn mọc thành bụi tròn cao 5-10cm, màu tím đỏ sẫm; các nhánh con ở ngọn tập trung dày đặc tạo thành mặt phẳng hình ngù (tản phòng); tế bào biểu bì ngoài cùng không lồi lồi.",
        "distribution": "Ấn-độ-dương, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "J. Agardh 1863 : Sp. Alg. II : 747; Yamada 1931 : Laurencia : 208; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 266, "name": "Laurencia tropica", "author": "Yamada",
        "vn": "Rong Lỗ-năng nhiệt-đới", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 284, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_209.png",
        "morphology": "Tản đứng cao 6-12cm, màu lục đỏ; thân hình trụ tròn, phân nhánh so le nhiều cấp; các nhánh con hình chùy ngắn đầu tù lõm giữa.",
        "distribution": "Thái-bình-dương nhiệt đới. Việt Nam: Duyên hải Trung bộ.",
        "status": "Bãi rạn san hô vùng triều.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Yamada 1931 : Laurencia : 233, pl. 20; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 267, "name": "Laurencia cartilaginea", "author": "Yamada",
        "vn": "Rong Lỗ-năng sụn", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 284, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_210.png",
        "morphology": "Tản sụn cực kỳ chắc cứng và dai, cao 5-10cm, màu nâu đỏ ánh đen; nhánh phân chia lưỡng phân hoặc so le dày đặc; chịu sóng rất tốt.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang, Côn-đảo.",
        "status": "Mọc trên vách đá gềnh tầng trung-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Yamada 1931 : Laurencia : 230, pl. 19; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 268, "name": "Laurencia tenera", "author": "Tseng",
        "vn": "Rong Lỗ-năng mềm", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 285, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_211.png",
        "morphology": "Tản mềm mại thanh mảnh cao 2-4cm, màu đỏ hồng tươi; nhánh hình sợi tròn nhỏ đường kính dưới 0,8mm; nhánh con thưa ngắn.",
        "distribution": "Biển Đông (Hải Nam, Việt Nam).",
        "status": "Mọc trong các vũng nước triều êm sóng.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Tseng 1943 : Mar. Alg. Hong Kong IV : 200, pl. 1; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458, fig. 61b-c."
    },
    {
        "idx": 269, "name": "Laurencia microclada", "author": "Kützing",
        "vn": "Rong Lỗ-năng nhánh-nhỏ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 286, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_212.png",
        "morphology": "Tản mọc thành búi dày, các nhánh con li ti mọc tua tủa dày đặc quanh trục chính; màu nâu đỏ.",
        "distribution": "Tây Ấn, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều giữa.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1865 : Tab. Phyc. XV : 22, pl. 60."
    },
    {
        "idx": 270, "name": "Laurencia brachyclados", "author": "Pilger",
        "vn": "Rong Lỗ-năng cành-ngắn", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 287, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_213.png",
        "morphology": "Tản cao 3-6cm, thân mang các cành con rất ngắn chỉ dài 1-2mm hình núm thịt mọc đều quanh trục; màu lục xám hay đỏ sẫm.",
        "distribution": "Châu Phi, Biển Đông. Gặp ở Nha-trang.",
        "status": "Bám trên đá và vỏ hào nơi sóng mạnh.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Pilger 1920 : Bot. Jahrb. 57 : 466; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 271, "name": "Laurencia obtusa", "author": "(Hudson) J.V. Lamouroux",
        "vn": "Rong Lỗ-năng đầu-tù", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 288, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_214.png",
        "morphology": "Tản sụn mềm mọng nước, cao 8-20cm, màu vàng lục hay hồng phớt; phân nhánh so le hoặc mọc đối; các nhánh con hình trụ ngắn đầu tù tròn lõm một chấm ở đỉnh.",
        "distribution": "Toàn cầu ở các vùng biển nhiệt đới và ôn đới ấm. Rất phổ biến khắp bờ biển Việt Nam.",
        "status": "Rong ăn sống rất ngon giòn ngọt; chứa nhiều hoạt chất sinh học chống vi khuẩn; mọc trên rạn san hô và đá vùng triều thấp.",
        "specimen": "Mẫu Nha-trang, Qui-nhơn, Vũng-Tàu, Phú-quốc.",
        "literature": "Hudson 1778 : Fl. Angl. ed. 2 : 586; Lamouroux 1813 : Essai : 42; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 272, "name": "Laurencia nidifica", "author": "J. Agardh",
        "vn": "Rong Lỗ-năng tổ-chim", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 289, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_215.png",
        "morphology": "Tản tạo bụi rối đan bện chằng chịt uốn lượn như tổ chim, cao 4-8cm, màu đỏ nâu; các nhánh dính vào nhau ở điểm tiếp xúc.",
        "distribution": "Hawaii, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá rạn san hô tầng triều thấp.",
        "specimen": "Mẫu đảo Hòn-mun, Nha-trang.",
        "literature": "J. Agardh 1852 : Sp. Alg. II : 749; Yamada 1931 : Laurencia : 202; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 273, "name": "Laurencia papillosa", "author": "(C. Agardh) Greville",
        "vn": "Rong Lỗ-năng có-nhú", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 290, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_216.png",
        "morphology": "Tản sụn dày cứng như da, cao 5-15cm, màu lục ô-liu hay nâu đen; thân chính phủ kín mít bởi vô số các nốt nhú thịt hình chùy ngắn xếp chen chúc sít sao; phẫu thức ngang cho thấy tế bào biểu bì xếp nghiêng hình hàng rào.",
        "distribution": "Toàn cầu ở các vùng biển nhiệt đới. Cực kỳ phong phú ở toàn bộ bờ biển miền Trung và hải đảo Việt Nam.",
        "status": "Rong thực phẩm ăn sống và làm gỏi giòn thơm; mọc phủ kín thềm đá san hô ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang, Côn-đảo, Phú-quốc.",
        "literature": "C. Agardh 1822 : Sp. Alg. I : 344; Greville 1830 : Alg. Brit. : LII; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 274, "name": "Laurencia pygmaea", "author": "Weber van Bosse",
        "vn": "Rong Lỗ-năng lùn", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 291, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_217.png",
        "morphology": "Tản lùn nhỏ li ti cao chỉ 5-10mm, mọc thành thảm nhung đỏ dính chặt trên đá; thân bò mang các nhánh đứng ngắn hình chùy.",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều cao nơi sóng đập.",
        "specimen": "Mẫu bãi đá Nha-trang.",
        "literature": "Weber van Bosse 1913 : Siboga : 268; Yamada 1931 : Laurencia : 248; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 275, "name": "Laurencia perforata", "author": "(Bory de Saint-Vincent) Montagne",
        "vn": "Rong Lỗ-năng thủng", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 292, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_218.png",
        "morphology": "Tản sụn cứng hình sợi cong queo, mọc thành bụi đệm cao 2-4cm, màu nâu đỏ; nhánh chính cong cuốn mang các nhánh con ngắn dạng gai tù; tế bào vỏ xếp hàng rào.",
        "distribution": "Đại-tây-dương, Địa-trung-hải, Biển Đông. Gặp ở Nha-trang.",
        "status": "Bám chặt kẽ đá vùng triều nơi sóng dữ.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Bory 1803 : Voy. Iles Afr. I : 305; Montagne 1840 : Pl. Cell. Canaries : 155; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 276, "name": "Laurencia heteroclada", "author": "Harvey",
        "vn": "Rong Lỗ-năng dị-chi", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Lỗ-năng", "gen_lat": "Laurencia",
        "p": 293, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_219.png",
        "morphology": "Tản đứng cao 5-10cm, màu lục vàng sẫm; thân mang các nhánh con có hình thái khác nhau rõ rệt (dị chi); tế bào biểu bì ngoài có màng trong suốt lồi ra ngoài dạng hạt.",
        "distribution": "Úc, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều thấp.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Harvey 1855 : Trans. R. Irish Acad. 22 : 544; Yamada 1931 : Laurencia : 238; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 458."
    },
    {
        "idx": 277, "name": "Chondria baileyana", "author": "(Montagne) Harvey",
        "vn": "Rong Sụn-thảo Bay-lơ", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Sụn-thảo", "gen_lat": "Chondria",
        "p": 295, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_221.png",
        "morphology": "Tản bụi mềm mại cao 7-12cm, màu đỏ tái hay hồng phớt; thân hình sợi tròn, các nhánh con thon nhỏ thắt eo ở gốc và nhọn ở ngọn; ổ tứ-bào-tử-phòng chìm trong mô ngọn nhánh.",
        "distribution": "Bắc Mỹ, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên đá và vỏ sò ốc ở vùng nước êm.",
        "specimen": "Mẫu vịnh Nha-trang.",
        "literature": "Montagne 1849 : Ann. Sci. Nat. Bot. : 63; Harvey 1853 : Nereis Bor. Amer. II : 20, pl. 18; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 460."
    },
    {
        "idx": 278, "name": "Chondria repens", "author": "Boergesen",
        "vn": "Rong Sụn-thảo bò", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Sụn-thảo", "gen_lat": "Chondria",
        "p": 296, "crop": (150, 1200, 2200, 2500), "fig_name": "fig_2_222.png",
        "morphology": "Tản bò chằng chịt trên san hô chết, cao 1-2cm, màu đỏ tía; thân hình sợi dẹp hẹp; quả-nang hình cầu lồi rõ trên mặt lưng nhánh.",
        "distribution": "Ấn-độ-dương, Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Mọc trên san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Boergesen 1924 : Kew Bull. : 272; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 460, fig. 62d-e."
    },
    {
        "idx": 279, "name": "Chondria armata", "author": "(Kützing) Okamura",
        "vn": "Rong Sụn-thảo trang-bị", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Sụn-thảo", "gen_lat": "Chondria",
        "p": 296, "crop": (150, 2000, 2200, 3100), "fig_name": "fig_2_223.png",
        "morphology": "Tản sụn cứng hình chùy mập cao 3-6cm, màu nâu đỏ đen; các nhánh mang gai nhọn ngắn cứng như chiếc áo giáp gai; chứa hợp chất có hoạt tính diệt giun sán đường ruột.",
        "distribution": "Nhật-bản, Biển Đông. Gặp ở Nha-trang.",
        "status": "Mọc trên đá vùng triều nơi sóng dữ.",
        "specimen": "Mẫu Nha-trang.",
        "literature": "Kützing 1866 : Tab. Phyc. XVI : 2; Okamura 1907 : Icones Jap. Alg. I : pl. 14."
    },
    {
        "idx": 280, "name": "Acrocystis nana", "author": "Zanardini",
        "vn": "Rong Đỉnh-nang lùn", "fam_vn": "Họ Đa-quản", "fam_lat": "Rhodomelaceae",
        "ord_vn": "Bộ Thao-bào", "ord_lat": "Ceramiales", "gen_vn": "Chi Rong Đỉnh-nang", "gen_lat": "Acrocystis",
        "p": 297, "crop": (150, 1300, 2200, 2800), "fig_name": "fig_2_224.png",
        "morphology": "Tản tạo thành bụi đệm hình bán cầu nhỏ cao 1-3cm, màu nâu đỏ sẫm; thân gồm các nhánh hình chùy mập phồng to ở ngọn như chiếc bọc nhỏ; trên đỉnh lõm chứa các cơ quan sinh sản được bao bọc kín. Loài kết thúc toàn bộ Phần II (Lớp Hồng-tảo).",
        "distribution": "Ấn-độ-Tây Thái-bình-dương. Gặp ở Nha-trang.",
        "status": "Bám chặt trên mặt đá và cành san hô chết ở tầng hạ-duyên-hải.",
        "specimen": "Mẫu Hòn-chồng Nha-trang.",
        "literature": "Zanardini 1872 : Phyc. Ind. : 145, pl. 8; Okamura 1931 : Icones Jap. Alg. VI : pl. 269; Dawson 1954 : Mar. Pl. Vic. Nha-trang : 461, fig. 63."
    }
]

def crop_figures():
    print(f'Cropping {len(BATCH5_DATA)} figures for Batch 5...')
    for sp in BATCH5_DATA:
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
    print(f'Querying WoRMS API in chunks for {len(BATCH5_DATA)} species...')
    results = []
    chunk_size = 20
    for i in range(0, len(BATCH5_DATA), chunk_size):
        chunk = BATCH5_DATA[i:i+chunk_size]
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
        
    for sp, item in zip(BATCH5_DATA, results):
        if item:
            rec = item[0]
            sp['worms_id'] = rec.get('AphiaID')
            sp['worms_status'] = rec.get('status')
            sp['worms_accepted_name'] = rec.get('valid_name')
        else:
            sp['worms_id'] = None
            sp['worms_status'] = 'unverified'
            sp['worms_accepted_name'] = sp['name']
            
    matched = len([s for s in BATCH5_DATA if s.get('worms_id')])
    print(f"WoRMS lookup finished: {matched}/{len(BATCH5_DATA)} verified.")

def build_json():
    print('Generating Supabase flat schema JSON for Batch 5...')
    rows = []
    for sp in BATCH5_DATA:
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

    out_file = os.path.join(BASE, 'data', 'ocr_batches', 'thuc-vat-bien_batch5.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} records to {out_file}")

if __name__ == '__main__':
    crop_figures()
    query_worms()
    build_json()
    print('Batch 5 build completed successfully!')
