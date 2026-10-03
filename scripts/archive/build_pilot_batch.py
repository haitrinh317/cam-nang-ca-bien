import json
import os
import time
import urllib.request
import urllib.parse

SPECIES_DATA = [
    {
        "index": 1,
        "vn_name": "Rong Lam-quả",
        "scientific_name": "Entophysalis conferta",
        "authorship": "(Kuetz.) Dr. and Dail.",
        "order": "Chroococcales",
        "family": "Entophysalidaceae",
        "genus": "Entophysalis",
        "morphology": "Tản phụ-sinh, làm thành khối nhầy, mềm, có thể thấy với mắt thường được. Tế-bào hình cầu hay xoan sắp thành hàng ly-tâm đo được 3-6µ bề kính, nội-dung làm nội-bào-tử.",
        "status": "Phụ-sinh trên Lyngbya aestuarii, Lyngbya confervoides, Chaetomorpha, Bostrychia.",
        "distribution": "Vùng biển duyên hải Việt Nam.",
        "literature": "Drouet and Daily, 1948 : Nom. Transf. among Cocc. Alg. : 79; Dawson 1954 : Mar. Pl. Vicin. Nha-trang : 379, fig. 3c; Palmella conferta Kuetzing 1845 : Phyc. germ. : 149.",
        "synonyms": [
            "Palmella conferta Kuetzing 1845 : Phyc. germ. : 149."
        ],
        "fig": "fig_1_1.png"
    },
    {
        "index": 2,
        "vn_name": "Rong Lục nội sinh",
        "scientific_name": "Chlorogloea endophytica",
        "authorship": "Howe 1914",
        "order": "Chroococcales",
        "family": "Entophysalidaceae",
        "genus": "Chlorogloea",
        "morphology": "Tản trên Cladophora, có vẻ nội-sinh làm thành một lớp hay nhiều lớp phủ thành khối không đều. Tế-bào kích-thước không đều, có hàng đứng rõ-rệt. Tế-bào ở đáy cao; có tế-bào kích-thước nhỏ.",
        "status": "Nội sinh / phụ sinh trên Cladophora.",
        "distribution": "Vùng duyên hải Nam Việt Nam.",
        "literature": "Dangeard 1952 : Alg. Presqu'île Cap Vert : 201, pl. 11, fig. A-D.",
        "synonyms": [],
        "fig": "fig_1_2.png"
    },
    {
        "index": 3,
        "vn_name": "Rong Thủy-bào",
        "scientific_name": "Hydrococcus rivularis",
        "authorship": "Kuetz.",
        "order": "Chroococcales",
        "family": "Entophysalidaceae",
        "genus": "Hydrococcus",
        "morphology": "Tản làm ra khối không đều, có u-nần, dày 30-60µ, bao quanh tản Chaetomorpha javanica. Tế-bào từng cặp làm thành khối hình xoan, dài 5µ, rộng 3,5-4µ.",
        "status": "Phụ sinh bao quanh tản Chaetomorpha javanica.",
        "distribution": "Vùng nước lợ và bờ biển duyên hải Việt Nam.",
        "literature": "Kuetzing 1846 : Tab. Phyc. I : pl. 32; Oncobyrsa rivularis (Kuetz.) Meneghini 1843 : Monogr. Nost. Ital. : 96; Frémy 1933 : Cyanop. côtes d'Europe : 41 pl. 9, figs. 1-2; Desikachary 1959 : Cyanophyta : 181, pl. 30, figs. 10-11.",
        "synonyms": [
            "Oncobyrsa rivularis (Kuetz.) Meneghini 1843 : Monogr. Nost. Ital. : 96."
        ],
        "fig": "fig_1_3.png"
    },
    {
        "index": 4,
        "vn_name": "Rong Vô-bì-cầu bờ",
        "scientific_name": "Aphanocapsa littoralis",
        "authorship": "Hansg.",
        "order": "Chroococcales",
        "family": "Chroococcaceae",
        "genus": "Aphanocapsa",
        "morphology": "Tản nhầy, không hình-thể rõ-rệt, màu lục gạch-tôm; tế-bào hình cầu hay hơi xoan, đường kính 4-5µ, nội-dung màu ten đồng hay vàng-vàng, cô-độc hay nhóm thành cặp.",
        "status": "Loài thường gặp ở các vũng mực thượng-duyên-hải có thể chứa toàn nước mưa hay nước muối rất mặn.",
        "distribution": "Nha Trang, Vũng Tàu. Tứ xứ.",
        "literature": "Hansgirg 1892 : Beitr. zur Kenntnis der Meersalg. und Bact. : 229; Forti in De Toni 1907 : Syll. Alg. V : 70; Frémy 1933 : Cyan. côtes d'Europe : 15, pl. 3, fig. 1; Desikachary 1959 : Cyanophyta : 131, pl. 21, fig. 1.",
        "synonyms": [],
        "fig": "fig_1_4.png"
    },
    {
        "index": 5,
        "vn_name": "Rong Vô-bì-cầu biển",
        "scientific_name": "Aphanocapsa marina",
        "authorship": "Hansg.",
        "order": "Chroococcales",
        "family": "Chroococcaceae",
        "genus": "Aphanocapsa",
        "morphology": "Khối không hình-thể rõ-rệt, nhầy; màu lục đợt hay đậm. Tế-bào hình cầu, rộng 0,4-0,5µ, cô-độc hay từng cặp, vách mỏng không màu; chất nhầy không màu.",
        "status": "Nước lợ và bờ biển, mực trung-duyên-hải; phụ sinh trên Lyngbya lutea.",
        "distribution": "Âu châu, bờ biển Việt Nam.",
        "literature": "Hansgirg 1890 : Alg. of Norway : 169; Frémy 1926-33 : Cyanop. côtes d'Europe : 16, pl. 3, fig. 2.",
        "synonyms": [],
        "fig": "fig_1_5.png"
    },
    {
        "index": 6,
        "vn_name": "Rong Lam-cầu nhỏ",
        "scientific_name": "Chroococcus minor",
        "authorship": "(Kuetz.) Naeg.",
        "order": "Chroococcales",
        "family": "Chroococcaceae",
        "genus": "Chroococcus",
        "morphology": "Tản nhầy, gần như hình cầu, đường kính đo 25-40µ; chất nhầy chung gần như đều-hòa, nâu. Tế-bào hình hơi xoan, dài 6µ, rộng 4-5µ, với một bao riêng, không màu. Vách bao không có lớp, tế-bào rộng 3-4µ không kể bao.",
        "status": "Ở cửa sông nhỏ làm thành lớp màu lục lam trên mặt đất, trà trộn với Lyngbya aestuarii và Microcoleus chthonoplastes; vũng dựa biển, rừng sát.",
        "distribution": "Bờ biển duyên hải Việt Nam; tứ xứ.",
        "literature": "Naegeli 1849 : Gatt. einz. Alg. : 47, pl. I, fig. 4; W.van Bosse 1913-18 : Liste des Alg. Siboga : 4; Frémy 1929 : Myx. Afrique Éq. Fr. : 45, fig. 50; Geitler 1932 : Kryptogamenflora : 240, fig. 116g; Desikachary 1959 : Cyanophyta : 105, pl. 24, fig. 1; Protococcus minor Kuetzing 1849 : Sp. Alg. : 198.",
        "synonyms": [
            "Protococcus minor Kuetzing 1849 : Sp. Alg. : 198."
        ],
        "fig": "fig_1_6.png"
    },
    {
        "index": 7,
        "vn_name": "Rong Lam-cầu nước ngọt",
        "scientific_name": "Chroococcus limneticus",
        "authorship": "Lemm.",
        "order": "Chroococcales",
        "family": "Chroococcaceae",
        "genus": "Chroococcus",
        "morphology": "Tản hình cầu, chất nhầy không màu. Tế-bào hình cầu hay hơi hình xoan, dài 6-12µ, bao riêng khó nhận, không có phiến, nội-dung đều, màu lục-vàng hay màu ve-chai.",
        "status": "Vũng dựa bờ biển; mặt đất ở nước ngọt.",
        "distribution": "Đại Tây Dương, Ấn Độ Dương, duyên hải Việt Nam.",
        "literature": "Lemmermann 1898 : Beitr. Kenntn. Planktonalg. II : 153; Forti in De Toni 1907 : Syll. Alg. V : 16; Frémy 1929 : Myx. d'Afr. Éq. franç. : 40, fig. 44; 1933 : Cyan. côtes d'Europe : 23, pl. 4, fig. 3; Desikachary 1959 : Cyanophyta : 107, pl. 26, fig. 2.",
        "synonyms": [],
        "fig": "fig_1_7.png"
    },
    {
        "index": 8,
        "vn_name": "Rong Vi-phòng",
        "scientific_name": "Microcystis Reinboldii",
        "authorship": "(Richter) Forti",
        "order": "Chroococcales",
        "family": "Chroococcaceae",
        "genus": "Microcystis",
        "morphology": "Tế-bào làm thành tập-chủng gần như hình cầu, đường kính to đến 75µ, trong một chất nhầy, không màu. Tế-bào màu nâu-nâu khi già, lam ở tập chủng non, cô-độc có vách dày và hình xoan, đo 5x7µ; ở tập chủng dày đo 3µ.",
        "status": "Trên các khối đá-vôi 'beach-rock' làm thành dề, trộn với Microcoleus chthonoplastes và Calothrix crustacea.",
        "distribution": "Hòn Thu (Poulo-Cecir de mer), Bình Thuận.",
        "literature": "Forti in De Toni 1907 : Syll. Alg. Myx. : 91; Frémy 1933 : Cyanop. côtes d'Europe : pl. 1, fig 8.",
        "synonyms": [],
        "fig": "fig_1_8.png"
    },
    {
        "index": 9,
        "vn_name": "Rong Tiêu-bì-quả bán cầu",
        "scientific_name": "Dermocarpella hemisphaerica",
        "authorship": "Setc. và Gardner in Gardner",
        "order": "Chamaesiphonales",
        "family": "Dermocarpellaceae",
        "genus": "Dermocarpella",
        "morphology": "Tế-bào hình bán-cầu, cô-độc. Bào-tử-phòng dính vào đài-vật bằng đáy phẳng, rộng 20µ, cao 13µ, màu lam nâu-nâu, vách dày 2,5µ, trong, nở ở đỉnh.",
        "status": "Phụ-sinh trên Chaetomorpha linum ở mực trung-duyên-hải.",
        "distribution": "Nha Trang. California, Ấn Độ.",
        "literature": "Gardner 1918 : New Pac. Coast. Mar. Alg : 438, pl. 37 fig. 21; Setchell and Gardner, 1919 : Mar. Alg. of the Pacific Coast of North Am. : 22, pl. 3, fig. 21; Desikachary 1959 : Cyanophyta : 173, pl. 33, figs. 11-12; Ginsburg-Ardré F. 1966 : Dermocarpa, Xenococcus, Dermocarpella : 362-67.",
        "synonyms": [],
        "fig": "fig_1_9.png"
    },
    {
        "index": 10,
        "vn_name": "Rong Tiêu-bì-quả chùy",
        "scientific_name": "Dermocarpella clavata",
        "authorship": "(Setc. and Gardn.) Pham-hoang nov. comb.",
        "order": "Chamaesiphonales",
        "family": "Dermocarpellaceae",
        "genus": "Dermocarpella",
        "morphology": "Tản hình dùi cao 20-28µ, rộng 8-12µ, thường hơi cong-cong; vách dày, nội-dung đều-hòa, màu lam hay tim-tím. Khi tạo nội-bào-tử, một phần nguyên-sinh-chất còn lại ở đáy.",
        "status": "Phụ-sinh trên Cladophora.",
        "distribution": "Bắc Thái Bình Dương, duyên hải Việt Nam.",
        "literature": "Chamaesiphon clavatus Setc. and Gardner 1925 : Mar. Alg. Revillagigedo Isl. 11 : 118; pl. 4, fig. 1; Dermocarpa clavata Geitler, 1932 : Kryptogamenflora : 406, fig. 235.",
        "synonyms": [
            "Chamaesiphon clavatus Setc. and Gardner 1925 : Mar. Alg. Revillagigedo Isl. 11 : 118.",
            "Dermocarpa clavata Geitler, 1932 : Kryptogamenflora : 406, fig. 235."
        ],
        "fig": "fig_1_10.png"
    },
    {
        "index": 11,
        "vn_name": "Rong Bì-quả cầu",
        "scientific_name": "Dermocarpa sphaerica",
        "authorship": "Setc. và Gardn. in Gardner",
        "order": "Pleurocapsales",
        "family": "Scopulonemataceae",
        "genus": "Dermocarpa",
        "morphology": "Tế-bào to 13µ, cô-độc hay thành tập-đoàn phụ-sinh trên rong khác, hình cầu với bao trong, mỏng, có khi dày bằng 1/3 hay 1/2 bán-kính. Bào-tử-phòng với sự phân vách đa giác rõ-rệt, đặc sắc.",
        "status": "Phụ-sinh trên Lyngbya lutea gặp ở Cà Ná (tháng 6), Phan Thiết và Vũng Tàu (tháng 10).",
        "distribution": "Đại Tây Dương, Ấn Độ Dương, Thái Bình Dương.",
        "literature": "Gardner 1918 : New Pac. Coast. Mar. Alg. 6 : 457; Frémy 1933 : Cyan. côtes d'Europe : 58, pl. 16, fig. 2; Desikachary 1959 : Cyanophyta : 174.",
        "synonyms": [],
        "fig": "fig_1_11.png"
    },
    {
        "index": 12,
        "vn_name": "Rong Bì-quả dài",
        "scientific_name": "Dermocarpa prasina",
        "authorship": "(Reinsch) Born. et Thur.",
        "order": "Pleurocapsales",
        "family": "Scopulonemataceae",
        "genus": "Dermocarpa",
        "morphology": "Tế-bào làm thành dề nhỏ, hình xoan tròn-dài hay hình dùi, rộng 15-18µ, cao 20-30µ; vách dày cỡ 2µ; nội-dung đều.",
        "status": "Phụ-sinh trên Gelidiopsis variabilis.",
        "distribution": "Nha Trang. Đại Tây Dương, Địa Trung Hải.",
        "literature": "Bornet et Thuret, 1880 : Notes algologiques II : 75-77, tab. 26, figs. 6-9; Geitler 1932 : Kryptogamenflora : 394, fig. 219; Frémy 1933 : Cyanop. côtes d'Europe : 58, pl. 16, fig. 3; Sphaenosiphon prasinus Reinsch 1874-5 : Contr. ad alg.",
        "synonyms": [
            "Sphaenosiphon prasinus Reinsch 1874-5 : Contr. ad alg."
        ],
        "fig": "fig_1_12.png"
    },
    {
        "index": 13,
        "vn_name": "Rong Bì-quả tụ",
        "scientific_name": "Dermocarpa acervata",
        "authorship": "(Setc. and Gardn.) Pham-hoang nov. comb.",
        "order": "Pleurocapsales",
        "family": "Scopulonemataceae",
        "genus": "Dermocarpa",
        "morphology": "Tập-chủng thường do một lớp tế-bào rải-rác song có khi lớp dày. Tế-bào tròn khi rời nhau, có thể có cạnh khi gần nhau, to 3-6µ, vách mỏng; nội-dung lam, đều-hòa.",
        "status": "Phụ-sinh trên nhiều loài Lyngbya như L. majuscula.",
        "distribution": "Ấn Độ Dương, Thái Bình Dương, duyên hải Việt Nam.",
        "literature": "Xenococcus acervatus Setchell and Gardner, 1918 : New Pacif. Coast Alg. : 459, tab. 39, fig. 13; Geitler, 1932 : Kryptogam. : 333, fig. 168; Desikachary, 1959 : Cyanophyta : 182, pl. 31, fig. 38.",
        "synonyms": [
            "Xenococcus acervatus Setchell and Gardner, 1918 : New Pacif. Coast Alg. : 459."
        ],
        "fig": "fig_1_13.png"
    },
    {
        "index": 14,
        "vn_name": "Rong Tiêu-ngạch",
        "scientific_name": "Hyella caespitosa",
        "authorship": "Born. et Flah.",
        "order": "Pleurocapsales",
        "family": "Hyellaceae",
        "genus": "Hyella",
        "morphology": "Tản nhầy, lúc đầu hình dĩa mỏng hay hình đốm, rộng 1-2mm, sau dính nhau thành đốm to màu lam hay nâu-nâu trên vỏ chứa vôi. Sợi nằm trên mặt vỏ do tế-bào gần hình cầu; sợi xoi dài đến 100-200µ do tế-bào rộng 4-10µ; tế-bào chót rất dài; bao không màu, có phiến.",
        "status": "Gặp trên vỏ nhu-thể sống hay chết, trên san-hô chết.",
        "distribution": "Bắc bán cầu, duyên hải Việt Nam.",
        "literature": "Bornet et Flahault 1888 : Note sur 2 nouv. genres d'Algues perforantes : 163; W. Van Bosse 1913 : Liste Alg. Siboga : 9; Geitler 1932 : Kryptogamenflora : 369, fig. 198; Frémy 1933 : Cyanop. côtes d'Europe : 49, pl. 12, figs. 1-10; Desikachary 1959 : Cyanophyta : 183, pl. 34.",
        "synonyms": [],
        "fig": "fig_1_14.png"
    },
    {
        "index": 15,
        "vn_name": "Rong Vi-bao mảnh",
        "scientific_name": "Microcoleus tenerrimus",
        "authorship": "Gomont",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Microcoleus",
        "morphology": "Tản màu lam đậm; mao-tản rộng 1,5-2µ, hơi eo ở vách ngang, tế-bào dài hơn ngang 1-2 lần; đầu tản hơi nhỏ, nhọn; nội-dung tế-bào hơi có hạt.",
        "status": "Trên bùn, trong vũng dựa biển.",
        "distribution": "Duyên hải Việt Nam; tứ xứ.",
        "literature": "Gomont 1893 : Monog. Oscillatoriées : 93, pl. 14, fig. 9-11; Velasquez 1962 : Blue-green Alg. Phil. : 331, pl. 6, fig. 85.",
        "synonyms": [],
        "fig": "fig_1_15.png"
    },
    {
        "index": 16,
        "vn_name": "Rong Vi-bao màng đất",
        "scientific_name": "Microcoleus chthonoplastes",
        "authorship": "Thur. ex. Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Microcoleus",
        "morphology": "Dề nhầy, màu sét hay nâu đậm. Mao-tản tụ trong một bao chung không màu, cong-queo, rộng 200-300µ, dài vài mm; bao dày 7-8µ. Mao-tản rộng 2,5 đến 6µ, hơi thắt ở vách ngang; đính thon, không có chóp.",
        "status": "Thông thường trên đáy cát hay bùn, ở các cửa sông, vũng nhỏ dọc duyên hải. Đi chung với L. aestuarii hay Oscillatoria tenuis.",
        "distribution": "Khắp duyên hải Việt Nam; tứ xứ.",
        "literature": "Thuret 1875 : Ann. Sc. Nat. : 378; Gomont 1892 : Monographie des Oscill. I : 353, pl. 14, figs. 5-8; Frémy 1933 : Cyanoph. côtes d'Europe : 67, pl. 17, fig. 7; Chthonoblastus salinus Kuetzing, 1843 : Phyc. Gener : 197; Chthonoblastus Lyngbyei Kuetzing, ibid. : 197.",
        "synonyms": [
            "Chthonoblastus salinus Kuetzing, 1843 : Phyc. Gener : 197.",
            "Chthonoblastus Lyngbyei Kuetzing 1843 : ibid. : 197."
        ],
        "fig": "fig_1_16.png"
    },
    {
        "index": 17,
        "vn_name": "Rong Thủy-bao lương-ba",
        "scientific_name": "Hydrocoleum lyngbyaceum",
        "authorship": "Kuetz. ex Gomont",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Hydrocoleum",
        "morphology": "Mao-tản hình bụi, lam đậm hay đen-đen, nhầy. Sợi không nhánh ở đáy, có nhánh ở phần trên trong bao chung rộng, nhầy; mao-tản xoắn-ốc, rộng 8-16µ, vách ngang có hạt; tế-bào rộng 3-6 lần hơn cao; tế-bào ngọn có chóp.",
        "status": "Trên bùn hay phụ-sinh trên rong khác như Hypnea.",
        "distribution": "Nha Trang, duyên hải Việt Nam; tứ xứ.",
        "literature": "Kuetzing 1849 : Sp. Alg. : 259; Gomont 1893 : Monog. Oscillat. : 337, pl. 12, figs. 8-10; Frémy 1933 : Cyanop. côtes d'Europe : 72, pl. 19, fig. 1; Dawson 1954 : Mar. pl. Vic. Nha-trang : 380, fig. 39.",
        "synonyms": [],
        "fig": "fig_1_17.png"
    },
    {
        "index": 18,
        "vn_name": "Rong Thủy-bao bọ hung",
        "scientific_name": "Hydrocoleum cantharidosum",
        "authorship": "(Mont.) Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Hydrocoleum",
        "morphology": "Mao-tản dài hơn 1cm, làm thành như lông the trên san-hô chết; thường tự-do, có khi tụ 2-5 trong bao màu nâu sô-cô-la. Tế-bào rộng 33µ, dài 2-3µ; bao dày 5-6µ; tế-bào ngọn có chóp.",
        "status": "Tầng hạ-duyên-hải; làm thành lông the màu lam hay sô-cô-la trên các khúc san-hô chết.",
        "distribution": "Đại Tây Dương, Thái Bình Dương, Mã Lai Á, duyên hải Việt Nam.",
        "literature": "Gomont 1890 : Essai class. Nostocacées Homocystées : 353; 1893 : Monogr. Oscillatoriées : 336, pl. 12, figs. 6-7; Forti in De Toni 1907 : Syll. Alg. V : 316; W. van Bosse 1913 : Liste Alg. Siboga : 17; Desikachary 1959 : Cyanoph.: 347, pl. 46, fig. 4-5.",
        "synonyms": [],
        "fig": "fig_1_18.png"
    },
    {
        "index": 19,
        "vn_name": "Rong Nhập-đoàn nhầy",
        "scientific_name": "Symploca hydnoides",
        "authorship": "Kuetzing ex. Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Symploca",
        "morphology": "Bụi hay phiến cô-độc hay nhóm 2-3, dài 1-3cm, nhớt nhầy, với một trục trăng-trắng và rìa lam đậm hay tím. Mao-tản dài hơn 1mm, rộng 6-14µ, bao dễ thấy, dày cỡ 0,5µ; vách ngang khó nhận; tế-bào có hạt, dài hai lần hơn ngang; tế-bào ngọn không chóp.",
        "status": "Trên đá, cát hay bùn từ trung-duyên-hải thượng đến hạ-duyên-hải, thường ở nơi hơi được che nắng; trong đồng cỏ Đơn-tử-diệp thủy-sinh.",
        "distribution": "Nha Trang, bờ biển Việt Nam.",
        "literature": "Gomont 1893 : Monogr. Oscillariées : 106, pl. 2. figs. 1-4; W. Van Bosse, 1913 : Liste Algues Siboga : 16; Frémy 1933 : Cyanop. côtes d'Europe : 81, pl. 21, fig. 3; Dawson 1954 : Mar. Pl. Vic. Nha-trang. : 380, fig. 30p; Desikachary 1959 : Cyanophyta : 335, pl. 60, figs. 2,3,6.",
        "synonyms": [],
        "fig": "fig_1_19.png"
    },
    {
        "index": 20,
        "vn_name": "Rong Nhập-đoàn tây dương",
        "scientific_name": "Symploca atlantica",
        "authorship": "Gomont",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Symploca",
        "morphology": "Phiến lục đậm, đứng, có thể cao đến 1cm. Sợi uốn-éo, bao mỏng, cứng; mao-tản dày 4-6µ, hơi eo ở vách ngang; tế-bào cao bằng rộng hay hơi dài hơn; tế-bào ngọn có vách ngọn dày hình chùy.",
        "status": "Trên đá, thực-vật dựa biển.",
        "distribution": "Bờ biển Việt Nam; tứ xứ.",
        "literature": "Gomont 1892 : Monogr. Oscill. II : 109; pl. 11, fig. 5; Frémy 1926-33 : Cyan. côtes d'Europe : 82, pl. 22, fig. 1.",
        "synonyms": [],
        "fig": "fig_1_20.png"
    },
    {
        "index": 21,
        "vn_name": "Rong Lương-ba phụ sinh",
        "scientific_name": "Lyngbya epiphytica",
        "authorship": "Hieron.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Mao-tản không eo ở vách ngang, mọc trên bao của rong khác, xoắn-ốc đều hay không đều; tế-bào màu lục ten-đồng, rộng 1-1,5µ, cao cũng như vậy; vách ngang khó nhận; bao mỏng không màu; tế-bào ngọn hình bán-cầu, không chóp.",
        "status": "Phụ-sinh trên Lyngbya lutea gặp ở Hòn Yến (Khánh Hòa).",
        "distribution": "Phi châu, Ấn Độ Dương, Hòn Yến (Khánh Hòa).",
        "literature": "Hieronymus in Kirchner 1898 : Schizophyceae, in Engler and Prantl : 67; Frémy 1929 : Myx. Afr. équat. franç. : 195, fig. 162; Desikachary 1959 : Cyanophyta : 284, pl. 53, fig. 7.",
        "synonyms": [],
        "fig": "fig_1_21.png"
    },
    {
        "index": 22,
        "vn_name": "Rong Lương-ba khe",
        "scientific_name": "Lyngbya rivulariarum",
        "authorship": "Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Mao-tản rất mịn, rộng 0,70-0,8µ; tế-bào hơi dài hơn ngang hay dài hơn đến 4 lần, eo ở vách ngang; bao rất mỏng; tế-bào ngọn không chóp.",
        "status": "Nội-sinh, đặc-sắc sống trong bao của rong khác như Lyngbya majuscula, Lyngbya lutea.",
        "distribution": "Bờ biển Việt Nam; có lẽ tứ xứ.",
        "literature": "Gomont 1893 : Monogr. Oscill. : 148; Frémy 1933 : Cyano. côtes d'Europe : 112, pl. 29, fig. 6.",
        "synonyms": [],
        "fig": "fig_1_22.png"
    },
    {
        "index": 23,
        "vn_name": "Rong Lương-ba Me-ne-ghi-ni",
        "scientific_name": "Lyngbya Meneghiniana",
        "authorship": "Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Mao-tản phụ-sinh dính ở giữa tản, thành nhóm thưa. Màu đỏ bầm hay vàng nâu-nâu; mao-tản dài đến 1mm, rộng 8µ; bao dày cỡ 1µ, trong và không màu; tế-bào rộng bằng 2,5 dài, vách ngang nhận được. Tế-bào chót không phù.",
        "status": "Phụ-sinh trên Chaetomorpha Linum, Cladophora spp.",
        "distribution": "Đại Tây Dương, duyên hải Việt Nam.",
        "literature": "Gomont 1890 : Journ. de Bot. IV : 354; Frémy 1933 : Cyanophyceae des côtes d'Europe : pl. 26, fig. 4.",
        "synonyms": [],
        "fig": "fig_1_23.png"
    },
    {
        "index": 24,
        "vn_name": "Rong Lương-ba A-gạc",
        "scientific_name": "Lyngbya Agardhii",
        "authorship": "Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Mẫu-vật trên Galaxaura elongata, làm thành bụi nhỏ, cao 300-600µ màu lục. Mao-tản cứng, dính ở giữa vào chủ, đo 8µ bề rộng; bao mỏng, trong không màu; tế-bào cao bằng 1/2 rộng hay cao bằng rộng; nội-dung có hạt rất mịn; tế-bào chót tròn không chóp. Rất gần L. Meneghiniana.",
        "status": "Phụ-sinh tìm gặp ở Hòn Thu (Poulo-Cecir de mer).",
        "distribution": "Hòn Thu (Bình Thuận); Đại Tây Dương.",
        "literature": "Gomont 1893 : Monographie Oscillat. : 124, pl. 11, figs. 18-19; Frémy 1933 : Cyanophycées côtes d'Europe : 102, pl. 26, fig. 2.",
        "synonyms": [],
        "fig": "fig_1_24.png"
    },
    {
        "index": 25,
        "vn_name": "Rong Lương-ba cửa biển",
        "scientific_name": "Lyngbya aestuarii",
        "authorship": "Liebm. ex. Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Sợi dài đến 2cm, màu nâu sậm; mao-tản rộng 10-20µ, không eo ở vách ngang; tế-bào cao bằng 1/3-1/6 bề rộng, vách ngang có hạt rõ-rệt; tế-bào ngọn tròn với một vách dày hay không. Bao lúc non không màu, lúc già màu nâu-sậm và có lớp.",
        "status": "Thông-thường ở duyên-hải, trên đá, trên rong, mắc vào rễ cây..., từ tầng trung-duyên-hải đến hạ-duyên-hải, trên bùn hay nổi thành dề.",
        "distribution": "Khắp cùng duyên-hải Việt Nam và phổ-thông khắp vùng nhiệt-đới.",
        "literature": "Gomont 1893 : Monog. Oscillar. : 127, pl. 3, figs. 1-2; W. Van Bosse 1913 : Liste Alg. Siboga : 13; Frémy 1933 : Cyanop. côtes d'Europe : 104, pl. 27; Dawson 1954 : Mar. Pl. Vicin. Nha-trang : 380, fig. 3a; Desikachary 1959 : Cyanophyta : 305, pl. 52. fig. 8.",
        "synonyms": [],
        "fig": "fig_1_25.png"
    },
    {
        "index": 26,
        "vn_name": "Rong Lương-ba nước ngọt",
        "scientific_name": "Lyngbya limnetica",
        "authorship": "Lemm.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Bụi rất nhỏ hay lông the, do mao-tản mịn, rộng 1,5-2µ; bao hồng, rất mỏng; vách ngang rất khó nhận.",
        "status": "Ở lớp đáy của Enteromorpha sp. và Chaetomorpha gracilis.",
        "distribution": "Nha Trang. Đại Tây Dương.",
        "literature": "Lemmermann 1898 : Beitr. Kenntn. Planktonalg. : 6; Geitler 1932 : Kryptogamenflora : 1046, figs. 661a, b; Frémy 1933 : Cyanoph. côtes d'Europe : 110, pl. 29, f. 3.",
        "synonyms": [],
        "fig": "fig_1_26.png"
    },
    {
        "index": 27,
        "vn_name": "Rong Lương-ba vàng",
        "scientific_name": "Lyngbya lutea",
        "authorship": "(Ag.) Gom.",
        "order": "Nostocales",
        "family": "Oscillatoriaceae",
        "genus": "Lyngbya",
        "morphology": "Tản làm thành một lớp phủ nhầy trơn-trợt trên đá, màu vàng đỏ, vàng lục hay nâu-nâu lúc khô. Mao-tản rộng 3-7µ, không eo ở vách ngang, tế-bào rộng bằng 3 lần cao, nội-dung đều; tế-bào ngọn có chóp tròn; bao trong không màu, mỏng lúc đầu, song có thể dày đến 3µ và có phiến; Cl2Zn và I2 nhuộm màu tím.",
        "status": "Tấm khảm do loài này thông-thường gặp dài theo duyên hải ở Vũng Tàu, Phan Thiết, Nha Trang...",
        "distribution": "Vũng Tàu, Phan Thiết, Nha Trang. Tứ xứ.",
        "literature": "Gomont 1893 : Monogr. Oscill. : 161, pl. 3, fig. 12; Frémy 1933 : Cyanophycées côtes d'Europe : 109, pl. 28, fig. 4.",
        "synonyms": [],
        "fig": "fig_1_27.png"
    }
]

def query_worms(name):
    # Query WoRMS
    parts = name.split()
    query_name = f"{parts[0]}+{parts[1]}" if len(parts) >= 2 else name
    url = f"https://www.marinespecies.org/rest/AphiaRecordsByMatchNames?scientificnames[]={query_name}&marine_only=false"
    req = urllib.request.Request(url, headers={"User-Agent": "CamNangCaBien/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and data[0]:
                rec = data[0][0]
                return {
                    "worms_id": rec.get("AphiaID"),
                    "worms_status": rec.get("status"),
                    "worms_accepted_name": rec.get("valid_name"),
                    "worms_url": f"https://www.marinespecies.org/aphia.php?p=taxdetails&id={rec.get('AphiaID')}"
                }
    except Exception as e:
        print(f"WoRMS query error for {name}: {e}")
    return {
        "worms_id": None,
        "worms_status": "unverified",
        "worms_accepted_name": name,
        "worms_url": ""
    }

output_rows = []
for sp in SPECIES_DATA:
    print(f"Processing #{sp['index']}: {sp['scientific_name']}...")
    worms = query_worms(sp["scientific_name"])
    time.sleep(1.5)  # Rate limit 1.5s as per skill rules

    row = {
        "id": f"thucvat-tap2-species-{sp['index']}",
        "collection_id": "thuc-vat-bien",
        "volume": 2,
        "species_index": sp["index"],
        "vn_name": sp["vn_name"],
        "scientific_name": sp["scientific_name"],
        "authorship": sp["authorship"],
        "en_common_name": "",
        "vn_alternate_names": "",
        "tax_class_vn": "Lớp Tảo Lam",
        "tax_class_latin": "Cyanophyceae",
        "tax_order_vn": "",
        "tax_order_latin": sp["order"],
        "tax_family_vn": "",
        "tax_family_latin": sp["family"],
        "tax_genus_vn": f"Chi {sp['vn_name'].split()[1] if len(sp['vn_name'].split()) > 1 else ''}",
        "tax_genus_latin": sp["genus"],
        "morphology_vn": sp["morphology"],
        "morphology_en": "",
        "photo_url": f"/images/species/thuc-vat-bien/v2/{sp['fig']}",
        "photo_caption": f"Hình tiêu bản giải phẫu {sp['scientific_name']} trong công trình Rong biển Việt Nam (GS. Phạm Hoàng Hộ, 1969)",
        "photo_author": "GS. Phạm Hoàng Hộ (1969)",
        "vn_distribution": sp["distribution"],
        "vn_specimen": "",
        "vn_status": sp["status"],
        "vn_literature": sp["literature"],
        "en_size": "",
        "en_distribution": "",
        "en_specimen": "",
        "en_status": "",
        "en_literature": "",
        "conservation_status": "common" if "thông thường" in sp["status"].lower() or "khắp" in sp["distribution"].lower() else "unknown",
        "synonyms": sp["synonyms"],
        "worms_id": worms["worms_id"],
        "worms_status": worms["worms_status"],
        "worms_accepted_name": worms["worms_accepted_name"],
        "worms_url": worms["worms_url"]
    }
    output_rows.append(row)

out_file = "data/ocr_batches/thuc-vat-bien_batch1.json"
os.makedirs("data/ocr_batches", exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(output_rows, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully generated {len(output_rows)} rows to {out_file}")
