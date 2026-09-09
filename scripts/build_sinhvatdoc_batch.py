#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_sinhvatdoc_batch.py — Bóc tách dữ liệu Sách chuyên khảo "Động vật độc biển Việt Nam"
(PGS.TS. Đào Việt Hà chủ biên — Viện Hải dương học) thành flat Supabase rows.
"""

import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
import unicodedata

DOCX_PATH = 'Documents/sinh-vat-doc/sach-sinh-vat-bien-doc/Sách Cô Hà/Sách chuyên khảo _ĐV độc biển VN_-Trinh_format_text  .docx'
IMG_DIR = 'Documents/sinh-vat-doc/sach-sinh-vat-bien-doc/Sách Cô Hà/List hình/List hình'
OUTPUT_JSON = 'scratch/sinhvatdoc_parsed.json'

def get_docx_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = []
        for p in tree.iterfind('.//w:p', namespaces):
            texts = [node.text for node in p.iterfind('.//w:t', namespaces) if node.text]
            if texts:
                paragraphs.append(unicodedata.normalize('NFC', ''.join(texts).strip()))
    return paragraphs

def get_image_files(img_dir):
    files = os.listdir(img_dir)
    fig_map = {}
    for f in files:
        norm_f = unicodedata.normalize('NFC', f)
        m = re.search(r'Hình\s*(\d+)', norm_f, re.IGNORECASE)
        if m:
            fig_num = int(m.group(1))
            fig_map.setdefault(fig_num, []).append(f)
    return fig_map

def main():
    os.makedirs('scratch', exist_ok=True)
    paragraphs = get_docx_paragraphs(DOCX_PATH)
    img_files = get_image_files(IMG_DIR)
    
    # Define species specs catalog
    species_defs = [
        # --- CHƯƠNG II: TIẾP XÚC ---
        # Ngành Thân lỗ
        {
            "index": 1, "fig_nums": [1],
            "vn_name": "Hải miên Lửa", "scientific_name": "Tedania sp.", "authorship": "",
            "tax_class_vn": "Lớp Hải miên có gai", "tax_class_latin": "Demospongiae",
            "tax_order_vn": "Bộ Poecilosclerida", "tax_order_latin": "Poecilosclerida",
            "tax_family_vn": "Họ Tedaniidae", "tax_family_latin": "Tedaniidae",
            "tax_genus_vn": "Chi Hải miên", "tax_genus_latin": "Tedania",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "moderate", "danger_level_vn": "Gây bỏng rát, viêm da tiếp xúc dữ dội",
            "toxin_names": ["Tedaniatoxin", "Histamine", "Spongin"],
            "photographer": "Thái Minh Quang",
            "size": "Kích thước đa dạng (khối 5 - 20 cm)",
            "distribution": "Vùng rạn san hô ven bờ biển Việt Nam",
            "morphology": "Cơ thể Hải miên ở dạng khối đặc với hình thù rất đa dạng (hình cầu, hình ống, hình chén hoặc dạng vỏ bọc bề mặt), màu sắc sặc sỡ từ đỏ cam, vàng cam đến nâu đỏ. Bộ xương cấu tạo từ các sợi spongin và các gai nhỏ sillic sắc nhọn.",
            "mechanism": "Khi đụng chạm cơ học, các gai nhỏ (spicules) sillic cắm vào da nạn nhân đồng thời tiết độc tố và histamine gây kích ứng dữ dội.",
            "symptoms": "Sau khi tiếp xúc vài phút đến vài giờ, xuất hiện cảm giác đau nhức buốt, ngứa rát dữ dội, vùng da nổi mẩn đỏ phù nề, xuất hiện mụn nước li ti giống như viêm da tiếp xúc nặng.",
            "first_aid": "Nhanh chóng rửa sạch vùng da tiếp xúc bằng xà phòng và nước biển/nước sạch. Dùng gạc mềm hoặc băng dính y tế dán nhẹ rồi kéo ra để loại bỏ triệt để các gai sillic cắm vào da. Thoa kem làm dịu da hoặc kem chứa kháng histamine, corticosteroid để giảm viêm ngứa."
        },
        # Ngành Ruột khoang
        {
            "index": 2, "fig_nums": [2],
            "vn_name": "San hô Lửa", "scientific_name": "Millepora sp.", "authorship": "",
            "tax_class_vn": "Lớp Thủy tức", "tax_class_latin": "Hydrozoa",
            "tax_order_vn": "Bộ Anthoathecata", "tax_order_latin": "Anthoathecata",
            "tax_family_vn": "Họ Milleporidae", "tax_family_latin": "Milleporidae",
            "tax_genus_vn": "Chi San hô lửa", "tax_genus_latin": "Millepora",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Hoại tử da, bỏng rát kéo dài)",
            "toxin_names": ["Cytolysins", "Pore-forming proteins"],
            "photographer": "Hoàng Xuân Bền",
            "size": "Tập đoàn nhánh cao 10 - 50 cm",
            "distribution": "Tất cả các rạn san hô vùng biển Việt Nam (Nha Trang, Côn Đảo, Phú Quốc, Trường Sa)",
            "morphology": "Có hình dáng giống san hô cứng thật với dạng nhánh, dạng phiến hình lưỡi dao hoặc phủ trên đá. Màu sắc tiêu biểu là nâu vàng hoặc xanh nâu với các đỉnh ngọn màu trắng sáng. Bề mặt có vô số lỗ nhỏ li ti chứa thích ty bào.",
            "mechanism": "Các thích ty bào phóng kim độc cắm vào da trong 3 phần nghìn giây, tiết protein cytolysin làm thủng màng tế bào, gây hoại huyết và hoại tử cục bộ.",
            "symptoms": "Khoảng 5 - 30 phút sau khi chạm vào, cảm giác đau rát dữ dội như bị bỏng lửa, có thể kéo dài hàng tuần. Vết thương đỏ rực, sưng phồng, phỏng nước và bong tróc hoại tử biểu bì.",
            "first_aid": "Khéo léo gắp bỏ các mảnh vỡ kim độc. Tuyệt đối không rửa bằng nước ngọt hay chà xát. Dùng giấm ăn (acid acetic 5%) thấm đẫm vết thương trong 15-30 phút để vô hiệu hóa thích ty bào, sau đó rửa sạch bằng nước muối hoặc nước biển."
        },
        {
            "index": 3, "fig_nums": [3],
            "vn_name": "Thủy tức Lông chim", "scientific_name": "Lytocarpus sp.", "authorship": "",
            "tax_class_vn": "Lớp Thủy tức", "tax_class_latin": "Hydrozoa",
            "tax_order_vn": "Bộ Leptothecata", "tax_order_latin": "Leptothecata",
            "tax_family_vn": "Họ Aglaopheniidae", "tax_family_latin": "Aglaopheniidae",
            "tax_genus_vn": "Chi Lytocarpus", "tax_genus_latin": "Lytocarpus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "moderate", "danger_level_vn": "Gây bỏng rát, mẩn đỏ dạng cành lông chim",
            "toxin_names": ["Cytolysins", "Neurotoxic peptides"],
            "photographer": "Hoàng Xuân Bền",
            "size": "Cành tập đoàn dài 10 - 25 cm",
            "distribution": "Bám trên vách đá rạn san hô, hang hốc ngầm",
            "morphology": "Tập đoàn thủy tức có hình dạng giống như chiếc lông chim hoặc cành cây nhỏ màu nâu đen, xám hoặc trắng đục. Các nhánh bên mang nhiều polyp nhỏ li ti chứa tuyến thích ty bào.",
            "mechanism": "Thích ty bào phóng gai độc khi người lặn va quẹt vào cành tập đoàn.",
            "symptoms": "Vết thương có hình vệt dài dạng cành lông chim, đau rát tức thì, sưng đỏ, nổi mề đay, mụn nước li ti.",
            "first_aid": "Rửa sạch bằng nước biển hoặc giấm ăn. Không cọ xát. Thoa kem corticoid hoặc uống thuốc kháng histamine giảm ngứa."
        },
        {
            "index": 4, "fig_nums": [4],
            "vn_name": "Hải quỳ Sáp", "scientific_name": "Actinodendron plumosum", "authorship": "Haddon, 1898",
            "tax_class_vn": "Lớp San hô", "tax_class_latin": "Anthozoa",
            "tax_order_vn": "Bộ Hải quỳ", "tax_order_latin": "Actiniaria",
            "tax_family_vn": "Họ Actinodendridae", "tax_family_latin": "Actinodendridae",
            "tax_genus_vn": "Chi Actinodendron", "tax_genus_latin": "Actinodendron",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Gây lở loét hoại tử sâu, sốt cao)",
            "toxin_names": ["Actinoporins", "Polypeptide neurotoxins"],
            "photographer": "Kha Mai",
            "size": "Đường kính xòe 15 - 30 cm",
            "distribution": "Nền cát pha bùn đáy rạn san hô ven bờ miền Trung",
            "morphology": "Thân dạng cột bám đáy cát, phần trên xòe ra nhiều nhánh xúc tu phân nhánh phức tạp trông giống như một bụi cây súp lơ hoặc bụi cây sáp mềm màu xám nâu, vàng rêu.",
            "mechanism": "Tiết actinoporin và các peptide độc phá hủy màng tế bào, mở kênh natri và canxi gây co cơ liên tục và hoại tử biểu bì.",
            "symptoms": "Đau buốt nhức nhối ngay lập tức, vết loét sâu phồng rộp, phù nề nặng, vùng da hoại tử đen, có thể kèm theo sốt, ớn lạnh, nôn mửa và tụt huyết áp.",
            "first_aid": "Rửa bằng giấm ăn hoặc nước biển ấm (40-45°C). Không rửa bằng nước ngọt. Giữ bất động vùng chi bị thương, đưa nạn nhân đến cơ sở y tế để sát trùng và điều trị chống hoại tử."
        },
        {
            "index": 5, "fig_nums": [5],
            "vn_name": "Sứa Lửa (Chiến binh Bồ Đào Nha)", "scientific_name": "Physalia sp.", "authorship": "",
            "tax_class_vn": "Lớp Thủy tức", "tax_class_latin": "Hydrozoa",
            "tax_order_vn": "Bộ Siphonophorae", "tax_order_latin": "Siphonophorae",
            "tax_family_vn": "Họ Physaliidae", "tax_family_latin": "Physaliidae",
            "tax_genus_vn": "Chi Sứa lửa", "tax_genus_latin": "Physalia",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc (Nguy cơ tử vong do suy hô hấp, ngừng tim)",
            "toxin_names": ["Physaliatoxin", "Hypnotoxin", "Hemolysins"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Phao nổi 10 - 30 cm, xúc tu dài tới 10 - 30 m",
            "distribution": "Trôi nổi trên mặt nước biển khơi và ven bờ khắp các đại dương",
            "morphology": "Cơ thể có một phao khí nổi trên mặt nước màu xanh lam, ánh tím hoặc hồng sặc sỡ như một cánh buồm nhỏ. Phía dưới phao là chùm xúc tu dài ngoằng từ vài mét đến hàng chục mét chứa hàng triệu thích ty bào cực độc.",
            "mechanism": "Thích ty bào trên xúc tu phóng kim tiêm physaliatoxin vào máu gây tán huyết mạnh, liệt thần kinh vận động và ức chế trung khu hô hấp tuần hoàn.",
            "symptoms": "Đau rát dữ dội như bị roi nung đỏ quất vào da. Vết thương nổi hằn đỏ tía thành chuỗi hạt phồng rộp. Nạn nhân bị sốc phản vệ, khó thở, co thắt ngực, mạch đập nhanh, ngất xỉu, đuối nước do hoảng loạn.",
            "first_aid": "Cứu hộ nạn nhân lên bờ ngay. Gắp bỏ nhẹ nhàng xúc tu bằng nhíp hoặc găng tay (tuyệt đối không chạm tay trần). Rửa vết thương bằng nước biển. Đối với sứa Lửa Physalia, KHÔNG dùng giấm ăn (vì có thể kích hoạt tế bào độc phóng thêm); nên ngâm nước nóng (45°C) hoặc chườm đá lạnh để giảm đau. Hô hấp nhân tạo nếu nạn nhân ngưng thở."
        },
        {
            "index": 6, "fig_nums": [6],
            "vn_name": "Sứa Bắp cày (Sứa Hộp)", "scientific_name": "Chironex fleckeri", "authorship": "Southcott, 1956",
            "tax_class_vn": "Lớp Sứa hộp", "tax_class_latin": "Cubozoa",
            "tax_order_vn": "Bộ Chirodropida", "tax_order_latin": "Chirodropida",
            "tax_family_vn": "Họ Chirodropidae", "tax_family_latin": "Chirodropidae",
            "tax_genus_vn": "Chi Chironex", "tax_genus_latin": "Chironex",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Động vật biển nguy hiểm nhất hành tinh",
            "toxin_names": ["Cardiotoxins", "Neurotoxins", "Dermatonecrotic toxins"],
            "photographer": "Robert Harwick",
            "size": "Chuông đường kính 15 - 30 cm, xúc tu dài đến 3 m",
            "distribution": "Ven bờ biển Việt Nam, Úc, Philippines (thường xuất hiện gần bờ mùa nước ấm)",
            "morphology": "Thân chuông hình hộp vuông trong suốt hơi ánh xanh lam, nhìn từ trên xuống giống sọ người. Có 24 mắt phân bố trong 4 hốc mắt. Mỗi góc chuông có chùm xúc tu (lên đến 15 xúc tu mỗi góc) chứa vô số giác bám thích ty bào độc.",
            "mechanism": "Độc tố là hỗn hợp hơn 250 protein tấn công tim mạch, hệ thần kinh và làm tan tế bào. Có thể gây tử vong chỉ trong vòng 2 - 5 phút do ngừng tim.",
            "symptoms": "Đau rát kinh hoàng tức thì, vùng da bị quất chuyển màu tím bầm hoại tử. Nạn nhân suy tim cấp tính, phù phổi, co giật, mất ý thức và tử vong rất nhanh trong nước.",
            "first_aid": "Đưa nạn nhân lên bờ, gọi cấp cứu 115 ngay lập tức. Dội đẫm giấm ăn (acid acetic 5%) liên tục lên vết thương ít nhất 30 giây để ức chế thích ty bào chưa vỡ. Không dùng nước ngọt hay cồn. Tiến hành ép tim ngoài lồng ngực và hô hấp nhân tạo (CPR) liên tục nếu tim ngừng đập."
        },
        {
            "index": 7, "fig_nums": [7, 8, 9],
            "vn_name": "Sứa Vòng (Ấu trùng ngứa thợ lặn)", "scientific_name": "Linuche unguiculata", "authorship": "(Swartz, 1788)",
            "tax_class_vn": "Lớp Sứa thật", "tax_class_latin": "Scyphozoa",
            "tax_order_vn": "Bộ Coronatae", "tax_order_latin": "Coronatae",
            "tax_family_vn": "Họ Linuchidae", "tax_family_latin": "Linuchidae",
            "tax_genus_vn": "Chi Linuche", "tax_genus_latin": "Linuche",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "moderate", "danger_level_vn": "Gây phát ban ngứa dữ dội kéo dài hàng tuần",
            "toxin_names": ["Antigenic peptides", "Hydrolases"],
            "photographer": "Trương Sĩ Hải Trình, Hoàng Xuân Bền, Thái Minh Quang",
            "size": "Cá thể trưởng thành 16 - 20 mm; ấu trùng 0.5 mm",
            "distribution": "Khắp các vùng biển ấm nhiệt đới; bùng phát mật độ lớn tại Vịnh Nha Trang từ tháng 3 - 8",
            "morphology": "Sứa trưởng thành hình chuông nhỏ màu nâu cam do tảo cộng sinh, có 16 rãnh dọc. Ấu trùng siêu nhỏ (0.5 mm), trong suốt, lọt qua khe vải đồ bơi và dính bám vào da.",
            "mechanism": "Khi người bơi lên bờ cởi đồ hoặc tắm nước ngọt, áp suất thẩm thấu làm ấu trùng vỡ ra và phóng thích ồ ạt thích ty bào vào da.",
            "symptoms": "Phát ban mụn mủ đỏ li ti, ngứa dữ dội như châm chích tại các vùng da bị đồ bơi che phủ (ngực, lưng, bẹn, nách). Cơn ngứa kéo dài 1 - 2 tuần, có thể gây sốt nhẹ ở trẻ em.",
            "first_aid": "Khi nghi ngờ tiếp xúc, lên bờ cởi bỏ đồ bơi ngay và rửa bằng nước biển (tuyệt đối không tắm nước ngọt khi chưa cởi đồ bơi). Thoa kem calamine, uống thuốc kháng histamine hoặc corticoid bôi da để giảm ngứa."
        },
        {
            "index": 8, "fig_nums": [10],
            "vn_name": "Sứa Tầm ma", "scientific_name": "Chrysaora chinensis", "authorship": "Vanhöffen, 1888",
            "tax_class_vn": "Lớp Sứa thật", "tax_class_latin": "Scyphozoa",
            "tax_order_vn": "Bộ Semaeostomeae", "tax_order_latin": "Semaeostomeae",
            "tax_family_vn": "Họ Pelagiidae", "tax_family_latin": "Pelagiidae",
            "tax_genus_vn": "Chi Chrysaora", "tax_genus_latin": "Chrysaora",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Đau đớn dữ dội, nổi lằn đỏ sưng phồng)",
            "toxin_names": ["Hemolytic proteins", "Proteases", "Hyaluronidase"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Đường kính dù 15 - 30 cm, xúc tu dài 1 - 2 m",
            "distribution": "Vùng biển ven bờ vịnh Bắc Bộ và miền Trung Việt Nam",
            "morphology": "Dù hình đĩa dẹp, màu trắng đục có các dải vân màu nâu đỏ tỏa ra từ tâm như nan hoa bánh xe. Viền dù có 24 xúc tu mảnh dài và các thùy miệng lớn gợn sóng buông rủ bên dưới.",
            "mechanism": "Enzyme hyaluronidase làm tăng tính thấm mô liên kết, giúp protein độc khuếch tán nhanh gây tán huyết và viêm sưng dây thần kinh cục bộ.",
            "symptoms": "Đau rát nhức nhối ngay tức khắc, vệt hằn đỏ sưng tấy theo hình xúc tu quệt qua da, có thể xuất hiện bóng nước, buồn nôn, vã mồ hôi và đau cơ.",
            "first_aid": "Rửa bằng giấm ăn hoặc nước biển. Không dùng cồn, nước ngọt hay chà xát cát. Thoa kem lidocaine giảm đau tại chỗ."
        },
        {
            "index": 9, "fig_nums": [11],
            "vn_name": "Sứa Sư tử", "scientific_name": "Cyanea sp.", "authorship": "",
            "tax_class_vn": "Lớp Sứa thật", "tax_class_latin": "Scyphozoa",
            "tax_order_vn": "Bộ Semaeostomeae", "tax_order_latin": "Semaeostomeae",
            "tax_family_vn": "Họ Cyaneidae", "tax_family_latin": "Cyaneidae",
            "tax_genus_vn": "Chi Cyanea", "tax_genus_latin": "Cyanea",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Nguy hiểm cho người mẫn cảm và trẻ nhỏ)",
            "toxin_names": ["Cyaneatoxin", "Hemolysins"],
            "photographer": "Thái Minh Quang",
            "size": "Đường kính dù 20 - 50 cm, xúc tu dài hàng mét",
            "distribution": "Vùng biển khơi và ven bờ nước ấm",
            "morphology": "Dù có màu đỏ sẫm, nâu tía hoặc vàng cam, mép dù xẻ thùy sâu. Phía dưới mang hàng trăm sợi xúc tu dài dày đặc như bờm sư tử.",
            "mechanism": "Thích ty bào tiết độc tố phá vỡ hồng cầu và ức chế dẫn truyền cơ thần kinh.",
            "symptoms": "Bỏng rát dữ dội, nổi ban phồng rộp, đau cơ bắp, tức ngực, khó thở nhẹ.",
            "first_aid": "Rửa vết thương bằng giấm ăn hoặc nước muối sinh lý, loại bỏ nhẹ nhàng xúc tu còn sót, chườm lạnh hoặc thoa kem giảm ngứa."
        },
        {
            "index": 10, "fig_nums": [12],
            "vn_name": "Sứa Xanh", "scientific_name": "Catostylus sp.", "authorship": "",
            "tax_class_vn": "Lớp Sứa thật", "tax_class_latin": "Scyphozoa",
            "tax_order_vn": "Bộ Rhizostomeae", "tax_order_latin": "Rhizostomeae",
            "tax_family_vn": "Họ Catostylidae", "tax_family_latin": "Catostylidae",
            "tax_genus_vn": "Chi Catostylus", "tax_genus_latin": "Catostylus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "moderate", "danger_level_vn": "Gây viêm rát da tiếp xúc",
            "toxin_names": ["Rhizostome toxins", "Proteins"],
            "photographer": "Hoàng Xuân Bền",
            "size": "Đường kính dù 10 - 25 cm",
            "distribution": "Vùng cửa sông, đầm phá và vịnh ven bờ",
            "morphology": "Dù dày hình vòm tròn, màu trắng xanh đục hoặc nâu nhạt, không có xúc tu viền dù mà có 8 cánh tay miệng dày hình trụ phân nhánh.",
            "mechanism": "Tuyến thích ty bào trên cánh miệng phóng chất gây viêm da tiếp xúc.",
            "symptoms": "Cảm giác ngứa ngáy, râm ran, nổi mẩn đỏ tại vùng da chạm phải.",
            "first_aid": "Rửa bằng nước biển sạch, thoa kem dịu da. Thuốc kháng histamin ít có tác dụng đối với nhóm này."
        },
        # Ốc Cối (7 loài)
        {
            "index": 11, "fig_nums": [13],
            "vn_name": "Ốc cối Địa lý", "scientific_name": "Conus geographus", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Loài ốc độc nhất hành tinh, tử vong cao",
            "toxin_names": ["Conotoxins (alpha, omega, mu, delta)", "Conopressins"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 10 - 15 cm",
            "distribution": "Rạn san hô vùng biển miền Trung và các hải đảo Việt Nam",
            "morphology": "Vỏ hình nón rộng, mỏng và nhẹ hơn các ốc cối khác; miệng vỏ rất rộng. Vỏ có màu nâu hồng hoặc nâu tím loang lổ với các đốm trắng bất định.",
            "mechanism": "Ốc phóng lưỡi sừng mang kim nọc tiêm hàng trăm loại conotoxin khoá kênh natri và canxi ở ngã ba thần kinh - cơ, làm tê liệt toàn bộ hệ cơ vận động và hô hấp.",
            "symptoms": "Vết chích nhỏ như ong đốt nhưng tê cứng tức thì, sau đó lan ra toàn thân. Mắt nhìn mờ, sụp mí, mất phối hợp cơ, líu lưỡi, liệt cơ hoành dẫn đến ngưng thở và tử vong sau 40 phút đến 5 giờ.",
            "first_aid": "Không có kháng huyết thanh đặc hiệu. Hô hấp nhân tạo và đặt nội khí quản hỗ trợ thở ngay lập tức (quyết định mạng sống). Tuyệt đối không rạch vết thương hay garô thắt chặt. Chườm nước ấm (40-45°C) để giảm đau và đưa ngay vào bệnh viện có máy thở."
        },
        {
            "index": 12, "fig_nums": [14],
            "vn_name": "Ốc cối Hoa lưới", "scientific_name": "Conus textile", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Nguy cơ tử vong cao do liệt cơ hô hấp",
            "toxin_names": ["Conotoxins", "Neurotoxic peptides"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 7 - 12 cm",
            "distribution": "Rạn san hô, nền sỏi cát ven biển miền Trung",
            "morphology": "Vỏ hình thoi nón dày dặn, láng bóng, có hoa văn dạng lưới tam giác màu vàng nâu óng ánh xen kẽ các ô trắng trông như mắt lưới dệt tinh xảo.",
            "mechanism": "Phóng kim độc tiêm hỗn hợp peptide conotoxin phong bế dẫn truyền xung thần kinh vận động.",
            "symptoms": "Tê bì quanh vết chích, yếu liệt cơ bắp, nói ngọng, khó nuốt, khó thở, hôn mê.",
            "first_aid": "Thực hiện cấp cứu hỗ trợ hô hấp liên tục, đưa đến trung tâm y tế gần nhất."
        },
        {
            "index": 13, "fig_nums": [15],
            "vn_name": "Ốc cối Hoa", "scientific_name": "Conus marmoreus", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Gây tê liệt cơ, nguy hiểm tính mạng)",
            "toxin_names": ["Conotoxins", "Alpha-conotoxin"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 6 - 10 cm",
            "distribution": "Vùng dưới triều rạn san hô",
            "morphology": "Vỏ nặng, hình nón cân đối, nền vỏ màu đen tuyền hoặc nâu đen nổi bật với vô số đốm hình tam giác màu trắng như đá hoa cẩm thạch.",
            "mechanism": "Tiêm nọc độc peptide làm liệt con mồi và gây độc thần kinh cơ ở người.",
            "symptoms": "Đau nhức dữ dội tại chỗ, tê bì tay chân, yếu cơ toàn thân.",
            "first_aid": "Bất động chi, chườm ấm, theo dõi nhịp thở và đưa đến bệnh viện."
        },
        {
            "index": 14, "fig_nums": [16],
            "vn_name": "Ốc cối Vằn", "scientific_name": "Conus striatus", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Chuyên săn cá, nọc độc tác động cực nhanh)",
            "toxin_names": ["Striatoxin", "Conotoxins"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 8 - 12 cm",
            "distribution": "Đáy cát ven rạn san hô",
            "morphology": "Vỏ dài hình trụ nón, màu trắng hồng có nhiều đường sọc gợn sóng ngang màu nâu đen hoặc tím than chạy song song.",
            "mechanism": "Striatoxin làm mở kênh natri liên tục gây co cứng cơ rồi liệt mềm.",
            "symptoms": "Tê liệt cơ nhanh chóng, hoa mắt, rối loạn nhịp tim.",
            "first_aid": "Cố định chi bị chích, duy trì thông khí nhân tạo nếu khó thở."
        },
        {
            "index": 15, "fig_nums": [17],
            "vn_name": "Ốc cối Chấm đầu tím", "scientific_name": "Conus litteratus", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "moderate", "danger_level_vn": "Gây đau nhức, tê bì kéo dài",
            "toxin_names": ["Conotoxins"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 6 - 13 cm",
            "distribution": "Đáy cát ven rạn san hô",
            "morphology": "Vỏ dày và nặng, hình nón cụt đầu phẳng, nền vỏ màu trắng ngà phủ đầy các chấm vuông nhỏ màu nâu đen xếp thành hàng vòng quanh vỏ, chóp đuôi phớt tím.",
            "mechanism": "Peptide độc gây liệt cơ con mồi giun nhiều tơ.",
            "symptoms": "Sưng đỏ, đau buốt như ong chích, tê rần cục bộ.",
            "first_aid": "Rửa sạch vết thương, ngâm nước ấm giảm đau, không nặn ép."
        },
        {
            "index": 16, "fig_nums": [18],
            "vn_name": "Ốc cối Hoa đuôi ngắn", "scientific_name": "Conus omaria", "authorship": "Hwass in Bruguière, 1792",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Gây liệt cơ vận động)",
            "toxin_names": ["Conotoxins"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 5 - 8 cm",
            "distribution": "Rạn san hô nước cạn",
            "morphology": "Vỏ hình nón thuôn dài, vai vỏ tròn, hoa văn đốm trắng hình tam giác trên nền màu hạt dẻ hoặc nâu đỏ.",
            "mechanism": "Conotoxin ức chế dẫn truyền thần kinh cơ vân.",
            "symptoms": "Đau rát, tê cứng ngón tay chân, choáng váng.",
            "first_aid": "Nẹp cố định chi, theo dõi hô hấp và chuyển viện cấp cứu."
        },
        {
            "index": 17, "fig_nums": [19],
            "vn_name": "Ốc cối Da đốm vàng", "scientific_name": "Conus magus", "authorship": "Linnaeus, 1758",
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": "Họ Ốc cối", "tax_family_latin": "Conidae",
            "tax_genus_vn": "Chi Ốc cối", "tax_genus_latin": "Conus",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Nguồn chiết xuất thuốc giảm đau Ziconotide)",
            "toxin_names": ["Omega-conotoxin MVIIA", "Conotoxins"],
            "photographer": "Tư liệu khoa học",
            "size": "Chiều dài vỏ 4 - 7 cm",
            "distribution": "Vùng cát cạn ven rạn san hô",
            "morphology": "Vỏ nhỏ hình nón nhọn, hoa văn biến đổi nhiều với các vệt đốm màu nâu vàng, xám xanh trên nền trắng.",
            "mechanism": "Omega-conotoxin phong bế chọn lọc kênh canxi type N của tế bào thần kinh (mạnh gấp 1.000 lần morphine).",
            "symptoms": "Mất cảm giác đau nhưng gây yếu liệt cơ, hạ huyết áp, buồn ngủ sâu.",
            "first_aid": "Hỗ trợ tuần hoàn hô hấp và đưa nạn nhân đến bệnh viện."
        },
        # Mực tuộc Đốm xanh
        {
            "index": 18, "fig_nums": [20, 50],
            "vn_name": "Mực tuộc Đốm xanh lớn", "scientific_name": "Hapalochlaena lunulata", "authorship": "(Quoy & Gaimard, 1832)",
            "tax_class_vn": "Lớp Chân đầu", "tax_class_latin": "Cephalopoda",
            "tax_order_vn": "Bộ Bạch tuộc", "tax_order_latin": "Octopoda",
            "tax_family_vn": "Họ Octopodidae", "tax_family_latin": "Octopodidae",
            "tax_genus_vn": "Chi Bạch tuộc đốm xanh", "tax_genus_latin": "Hapalochlaena",
            "poison_type": "both", "poison_type_vn": "CỰC KỲ NGUY HIỂM: Gây độc cả khi CẮN và khi ĂN PHẢI",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Chứa độc tố Tetrodotoxin (TTX) gây tử vong nhanh",
            "toxin_names": ["Tetrodotoxin (TTX)", "Maculotoxin", "Hapalo-toxin"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Chiều dài thân 5 - 12 cm, nặng 10 - 50 g",
            "distribution": "Vùng triều rạn san hô, vũng nước cạn ven biển miền Trung (vụ ngộ độc 85 người tại Bình Thuận 2004)",
            "morphology": "Kích thước nhỏ chỉ bằng nắm tay hoặc bao diêm. Khi bình thường có màu vàng nâu ngụy trang; khi bị kích động hay đe dọa, trên khắp thân và xúc tu sẽ phát sáng rực rỡ các vòng tròn màu xanh lam huỳnh quang tuyệt đẹp.",
            "mechanism": "Tuyến nước bọt và các mô cơ thể chứa lượng lớn Tetrodotoxin (TTX). Một cá thể nhỏ có đủ nọc độc giết chết 20-25 người trưởng thành trong vài phút.",
            "symptoms": "Nếu bị cắn hoặc ăn phải: Sau vài phút xuất hiện tê môi, lưỡi, đầu chi; tiếp theo nôn mửa, khó nuốt, khó thở, liệt toàn thân trong khi nạn nhân vẫn hoàn toàn tỉnh táo nhưng không cử động được; tử vong do suy hô hấp.",
            "first_aid": "Băng ép cố định chi (Pressure Immobilization) nếu bị cắn (tuyệt đối không garô máu). Hô hấp nhân tạo ngay lập tức. Nếu ăn phải, tìm cách gây nôn trong 30 phút đầu nếu nạn nhân còn tỉnh, uống than hoạt tính và đưa cấp cứu hồi sức hô hấp khẩn cấp."
        },
        # Da gai
        {
            "index": 19, "fig_nums": [21],
            "vn_name": "Sao biển Gai (Sao biển Vương miện)", "scientific_name": "Acanthaster planci", "authorship": "(Linnaeus, 1758)",
            "tax_class_vn": "Lớp Sao biển", "tax_class_latin": "Asteroidea",
            "tax_order_vn": "Bộ Valvatida", "tax_order_latin": "Valvatida",
            "tax_family_vn": "Họ Acanthasteridae", "tax_family_latin": "Acanthasteridae",
            "tax_genus_vn": "Chi Acanthaster", "tax_genus_latin": "Acanthaster",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Gai đâm gây viêm loét mưng mủ, sốt cao)",
            "toxin_names": ["Plancitoxin", "Saponins (Asterosaponins)", "Pore-forming proteins"],
            "photographer": "Hoàng Xuân Bền",
            "size": "Đường kính 25 - 40 cm (có thể đạt 60 cm)",
            "distribution": "Các rạn san hô khắp vùng biển Việt Nam (loài ăn san hô tàn phá rạn)",
            "morphology": "Cơ thể có từ 14 đến 21 cánh tay, toàn bộ mặt lưng tua tủa các gai nhọn dài 3 - 5 cm rất sắc, màu sắc biến đổi từ xám xanh, đỏ cam đến tím than.",
            "mechanism": "Lớp biểu bì phủ gai chứa plancitoxin (tương đồng deoxyribonuclease) và saponin gây độc tế bào gan, gây tan máu và kích ứng mô nghiêm trọng.",
            "symptoms": "Đau nhức buốt dữ dội kéo dài nhiều giờ, sưng tấy phù nề, chảy máu nhiều, vết đâm đổi màu xanh đen. Sau vài ngày vết thương mưng mủ, có thể kèm theo sốt cao, nôn mửa và nổi hạch.",
            "first_aid": "Ngâm ngay vùng bị đâm vào nước nóng (45 - 50°C) trong 30 - 90 phút (nhiệt độ làm biến tính độc tố protein). Cẩn thận rút các mảnh gai gãy cắm trong da bằng nhíp sạch. Sát trùng và uống kháng sinh/kháng viêm theo chỉ định bác sĩ."
        },
        {
            "index": 20, "fig_nums": [22],
            "vn_name": "Cầu gai Hoa (Nhum hoa)", "scientific_name": "Toxopneustes pileolus", "authorship": "(Lamarck, 1816)",
            "tax_class_vn": "Lớp Cầu gai", "tax_class_latin": "Echinoidea",
            "tax_order_vn": "Bộ Camarodonta", "tax_order_latin": "Camarodonta",
            "tax_family_vn": "Họ Toxopneustidae", "tax_family_latin": "Toxopneustidae",
            "tax_genus_vn": "Chi Toxopneustes", "tax_genus_latin": "Toxopneustes",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Loài cầu gai nguy hiểm nhất thế giới",
            "toxin_names": ["Contractin A", "Pedicellarial toxin", "Hemolysins"],
            "photographer": "Hoàng Xuân Bền",
            "size": "Đường kính vỏ 10 - 15 cm",
            "distribution": "Thảm cỏ biển và vùng rạn san hô cạn",
            "morphology": "Vỏ tròn dẹp, gai ngắn bị che phủ bởi vô số chân kìm (pedicellariae) dạng cánh hoa xòe ra màu hồng, xanh hoặc vàng nhạt, trông giống như một đóa hoa nở rộ dưới đáy biển.",
            "mechanism": "Khi chạm vào, hàng trăm chân kìm hình hoa sẽ kẹp chặt vào da và tiêm nọc độc contractin A gây co cứng cơ trơn, tan máu và ức chế thần kinh cơ.",
            "symptoms": "Đau đớn dữ dội tức thì, tê liệt cơ, khó thở, cứng hàm, hạ huyết áp và ngất xỉu. Người lặn có thể bị đuối nước do choáng ngất.",
            "first_aid": "Loại bỏ ngay các chân kìm bám trên da. Ngâm vùng tổn thương trong nước nóng (45°C) để phá hủy nọc độc. Đưa ngay nạn nhân vào bệnh viện cấp cứu nếu có dấu hiệu khó thở."
        },
        # Động vật có xương sống (Cá độc)
        {
            "index": 21, "fig_nums": [23],
            "vn_name": "Cá đuối Gai độc", "scientific_name": "Dasyatis sp.", "authorship": "",
            "tax_class_vn": "Lớp Cá sụn", "tax_class_latin": "Chondrichthyes",
            "tax_order_vn": "Bộ Cá đuối gai độc", "tax_order_latin": "Myliobatiformes",
            "tax_family_vn": "Họ Cá đuối gai độc", "tax_family_latin": "Dasyatidae",
            "tax_genus_vn": "Chi Dasyatis", "tax_genus_latin": "Dasyatis",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Vết rách cơ sâu, nhiễm nọc độc protein)",
            "toxin_names": ["Stingray venom protein", "Serotonin", "5-nucleotidase"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Đường kính đĩa 30 - 100 cm, đuôi dài",
            "distribution": "Đáy cát, bùn cát ven bờ và vũng vịnh",
            "morphology": "Thân dẹp hình đĩa tròn hoặc thoi, mắt ở mặt lưng, miệng và khe mang ở mặt bụng. Đuôi dài thanh mảnh, trên cuống đuôi có 1 đến 3 gai răng cưa cứng nhọn hoắt có rãnh tiết nọc.",
            "mechanism": "Khi bị giẫm phải, cá quất đuôi cắm gai độc vào chân, gai răng cưa xé rách mô sâu đồng thời màng bao gai vỡ ra phóng nọc độc vào vết thương.",
            "symptoms": "Đau nhức buốt thấu xương, vết rách sâu chảy máu đầm đìa, phù nề bầm tím, co thắt cơ, có thể ngất xỉu do quá đau đớn.",
            "first_aid": "Rửa sạch dưới vòi nước để trôi chất bẩn. Ngâm ngay vết thương vào nước nóng (45°C) trong 30-60 phút để làm bất hoạt nọc protein. Không tự ý rút gai nếu gai cắm sâu vào ngực/bụng. Cần đến bệnh viện để tiêm phòng uốn ván và phẫu thuật lấy mảnh gai gãy."
        },
        {
            "index": 22, "fig_nums": [24],
            "vn_name": "Cá Mao tiên (Cá Sư tử)", "scientific_name": "Pterois sp.", "authorship": "",
            "tax_class_vn": "Lớp Cá xương", "tax_class_latin": "Actinopterygii",
            "tax_order_vn": "Bộ Cá mù làn", "tax_order_latin": "Scorpaeniformes",
            "tax_family_vn": "Họ Cá mù làn", "tax_family_latin": "Scorpaenidae",
            "tax_genus_vn": "Chi Cá mao tiên", "tax_genus_latin": "Pterois",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Tia vây nọc độc gây đau đớn dữ dội)",
            "toxin_names": ["Pterois toxin", "Acetylcholine", "Proteins"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Chiều dài thân 15 - 35 cm",
            "distribution": "Các rạn san hô ven biển và hải đảo",
            "morphology": "Màu sắc tuyệt đẹp với các sọc đỏ, nâu, trắng xen kẽ. Các tia vây lưng, vây ngực và vây hậu môn vươn dài tự do như cánh quạt lông vũ xòe rộng. Mỗi tia vây lưng là một kim tiêm nọc độc sắc nhọn.",
            "mechanism": "Gai vây đâm vào thịt ép bao nọc phóng protein độc gây giải phóng acetylcholine, ức chế tim mạch và gây phù nề cơ dữ dội.",
            "symptoms": "Đau nhức kinh khủng ngay khi bị đâm, lan rộng khắp chi, sưng phù, khó thở, buồn nôn, vã mồ hôi, co giật cơ.",
            "first_aid": "Ngâm ngay vết đâm vào nước nóng (45°C) trong 30-90 phút để phân hủy protein độc. Rửa sạch sát trùng và đến bệnh viện kiểm tra."
        },
        {
            "index": 23, "fig_nums": [25],
            "vn_name": "Cá Bống biển (Cá Mù làn)", "scientific_name": "Scorpaena sp.", "authorship": "",
            "tax_class_vn": "Lớp Cá xương", "tax_class_latin": "Actinopterygii",
            "tax_order_vn": "Bộ Cá mù làn", "tax_order_latin": "Scorpaeniformes",
            "tax_family_vn": "Họ Cá mù làn", "tax_family_latin": "Scorpaenidae",
            "tax_genus_vn": "Chi Scorpaena", "tax_genus_latin": "Scorpaena",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "severe", "danger_level_vn": "Độc mạnh (Ngụy trang hoàn hảo, gai vây cực độc)",
            "toxin_names": ["Scorpaenatoxin", "Enzymes"],
            "photographer": "Tư liệu chuyên khảo",
            "size": "Chiều dài thân 15 - 30 cm",
            "distribution": "Nằm ngụy trang trên đáy đá, san hô",
            "morphology": "Đầu to gồ ghề có nhiều gai và mấu thịt, da xù xì màu nâu đỏ loang lổ giống hệt tảng đá bám rêu. Các tia vây lưng to khỏe có rãnh tiết nọc độc.",
            "mechanism": "Gai vây lưng đâm sâu khi người bơi hoặc ngư dân vô tình đạp phải.",
            "symptoms": "Đau buốt nhức nhối, sưng phù đỏ bầm, hoại tử nhẹ quanh vết đâm.",
            "first_aid": "Ngâm nước nóng (45°C), giảm đau và sát trùng y tế."
        },
        {
            "index": 24, "fig_nums": [26],
            "vn_name": "Cá Đá (Cá Mặt quỷ)", "scientific_name": "Synanceja sp.", "authorship": "",
            "tax_class_vn": "Lớp Cá xương", "tax_class_latin": "Actinopterygii",
            "tax_order_vn": "Bộ Cá mù làn", "tax_order_latin": "Scorpaeniformes",
            "tax_family_vn": "Họ Cá mặt quỷ", "tax_family_latin": "Synanceiidae",
            "tax_genus_vn": "Chi Synanceja", "tax_genus_latin": "Synanceja",
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Loài cá độc nhất thế giới, nguy cơ tử vong cao",
            "toxin_names": ["Stonustoxin (SNTX)", "Verrucotoxin (VTX)", "Cardiolethal toxins"],
            "photographer": "Trương Sĩ Hải Trình",
            "size": "Chiều dài thân 20 - 40 cm, nặng tới 2 kg",
            "distribution": "Ngụy trang vùi mình dưới cát, rạn đá vùng triều",
            "morphology": "Hình dạng xấu xí thô ráp kỳ dị, đầu gồ ghề hốc hác, miệng hướng lên trên, da xù xì nhớp nháp bọc rêu tảo trông như hòn đá chết. Có 13 tia gai vây lưng cực cứng có thể đâm xuyên qua cả đế giày cao su.",
            "mechanism": "Mỗi gai vây lưng có 2 túi nọc lớn chứa Stonustoxin. Khi bị giẫm lên, toàn bộ lượng nọc được tống thẳng vào thịt như 13 ống tiêm nén áp lực.",
            "symptoms": "Đau đớn dữ dội tột cùng làm nạn nhân co giật ngất xỉu ngay tức khắc. Chân sưng phồng gấp đôi, tím đen hoại tử nhanh chóng. Độc tố phá hủy tim mạch, gây phù phổi cấp, suy tuần hoàn và tử vong trong vài giờ.",
            "first_aid": "Ngâm ngay vào nước nóng hết mức chịu đựng được (45 - 50°C) liên tục để phá hủy độc tố. Đưa đi cấp cứu khẩn cấp để tiêm kháng huyết thanh (nếu có), giảm đau mạnh và phẫu thuật rạch giải áp mô hoại tử."
        }
    ]
    
    # Rắn biển (23 loài: Index 25 đến 47)
    sea_snakes_meta = [
        (25, 27, "Đẻn Đuôi gai", "Aipysurus eydouxii", "Gray, 1849", "Lưng hơi nâu hoặc xanh ô-liu, có các khoanh nâu đậm.", "Aipysurus"),
        (26, 28, "Đẻn Vảy đầu phân", "Hydrophis annandalei", "(Laidlaw, 1901)", "Đầu lớn, thân chắc khỏe, lưng màu xám tro với các khoanh đen.", "Hydrophis"),
        (27, 29, "Đẻn Đầu đen", "Hydrophis atriceps", "Günther, 1864", "Đầu nhỏ màu đen sẫm, phần trước thân mảnh màu đen nhạt.", "Hydrophis"),
        (28, 30, "Đẻn Khoanh mờ", "Hydrophis belcheri", "(Gray, 1849)", "Đầu đen sẫm có vệt đốm xanh ô-liu, thân có các khoanh mờ.", "Hydrophis"),
        (29, 31, "Đẻn Brooke", "Hydrophis brookii", "Günther, 1872", "Đầu nhỏ hơi đen có vệt móng ngựa vàng hai bên.", "Hydrophis"),
        (30, 32, "Đẻn Nhiều răng", "Hydrophis caerulescens", "(Shaw, 1802)", "Lưng màu xám xanh, thân có 40-60 khoanh đen xám.", "Hydrophis"),
        (31, 33, "Đẻn Cơm", "Hydrophis curtus", "(Shaw, 1802)", "Thân ngắn to dày, đuôi dẹp như mái chèo.", "Hydrophis"),
        (32, 34, "Sông chằn", "Hydrophis cyanocinctus", "Daudin, 1803", "Thân dài lớn, màu vàng nhạt có các khoanh đen xanh rõ nét.", "Hydrophis"),
        (33, 35, "Đẻn Mõm nhọn", "Hydrophis jerdonii", "(Gray, 1849)", "Mõm nhọn dài, vảy thân có gờ nhọn.", "Hydrophis"),
        (34, 36, "Đẻn Lambetti", "Hydrophis lamberti", "Smith, 1917", "Lưng hơi trắng hoặc xám nhạt, có các khoanh tròn lớn.", "Hydrophis"),
        (35, 37, "Đẻn Khoang cổ mảnh", "Hydrophis melanocephalus", "Gray, 1849", "Đầu nhỏ, cổ rất mảnh, phần sau thân to phình.", "Hydrophis"),
        (36, 38, "Đẻn Bông", "Hydrophis ornatus", "(Gray, 1842)", "Thân chắc nịch, có các đốm khoanh rộng màu xám đen.", "Hydrophis"),
        (37, 39, "Đẻn Đầu rộng", "Hydrophis pachycercos", "Fischer, 1855", "Đầu đen ở phần trên, trắng ở phần dưới, mắt có vòng tròn trắng.", "Hydrophis"),
        (38, 40, "Đẻn Đầu ngắn", "Hydrophis parviceps", "Smith, 1935", "Đầu rất nhỏ ngắn, cổ mảnh, loài hiếm gặp.", "Hydrophis"),
        (39, 41, "Đẻn Đầu gai", "Hydrophis peronii", "(Duméril, 1853)", "Trên đỉnh đầu có các gai nhỏ gồ lên ráp ráp.", "Hydrophis"),
        (40, 42, "Đẻn Đuôi vàng", "Hydrophis platura", "(Linnaeus, 1766)", "Nửa lưng đen tuyền phẳng tắp, nửa bụng vàng óng, đuôi có đốm hoa.", "Hydrophis"),
        (41, 43, "Đẻn Mỏ", "Hydrophis schistosus", "Daudin, 1803", "Mỏ quặp như mỏ chim, độc tính cực mạnh, chịu trách nhiệm cho đa số ca tử vong do rắn biển.", "Hydrophis"),
        (42, 44, "Đẻn Bụng vàng", "Hydrophis spiralis", "(Shaw, 1802)", "Loài rắn biển dài nhất (có thể đạt 2.5 - 3 m), thân màu vàng có khoanh đen hẹp xoắn ốc.", "Hydrophis"),
        (43, 45, "Đẻn Stoke", "Hydrophis stokesii", "(Gray, 1846)", "Thân cực kỳ to dày nặng nề, vảy nhô gờ sắc.", "Hydrophis"),
        (44, 46, "Đẻn Đầu xám", "Hydrophis torquatus diadema", "(Günther, 1864)", "Đầu màu xám chì, thân có các khoanh xám đen vòng quanh.", "Hydrophis"),
        (45, 47, "Rắn Lục biển", "Hydrophis viperinus", "(Schmidt, 1852)", "Đầu hình tam giác hơi giống rắn lục đất liền.", "Hydrophis"),
        (46, 48, "Đẻn Cạp nong môi vàng", "Laticauda colubrina", "(Schneider, 1799)", "Lên bờ đẻ trứng, thân có khoanh đen trắng bạc, môi và mũi vàng tươi.", "Laticauda"),
        (47, 49, "Đẻn Đầu nhỏ", "Hydrophis gracilis", "(Shaw, 1802)", "Đầu và cổ cực nhỏ như que tăm, phần sau thân phình to gấp 4-5 lần.", "Hydrophis")
    ]
    
    for s_idx, fig_n, vn, sci, auth, morph, genus in sea_snakes_meta:
        species_defs.append({
            "index": s_idx, "fig_nums": [fig_n],
            "vn_name": vn, "scientific_name": sci, "authorship": auth,
            "tax_class_vn": "Lớp Bò sát", "tax_class_latin": "Reptilia",
            "tax_order_vn": "Bộ Có vảy", "tax_order_latin": "Squamata",
            "tax_family_vn": "Họ Rắn hổ", "tax_family_latin": "Elapidae",
            "tax_genus_vn": f"Chi {genus}", "tax_genus_latin": genus,
            "poison_type": "contact", "poison_type_vn": "Gây nhiễm độc qua tiếp xúc (Nọc độc)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Nọc độc thần kinh và hủy hoại cơ vân",
            "toxin_names": ["Postsynaptic neurotoxins", "Myotoxins (Phospholipase A2)"],
            "photographer": "Cao Văn Nguyện",
            "size": "Chiều dài thân 60 - 150 cm",
            "distribution": "Vùng biển ven bờ, vịnh cạn và hải đảo Việt Nam",
            "morphology": f"{morph} Thân dẹp bên về phía sau, đuôi biến dạng thành mái chèo dẹp thích nghi bơi lặn.",
            "mechanism": "Răng nọc nhỏ ở hàm trên tiêm myotoxin và neurotoxin phá hủy cơ vân, giải phóng myoglobin làm tắc nghẽn ống thận và liệt cơ hô hấp.",
            "symptoms": "Vết cắn thường không đau và không sưng đỏ (dễ bị bỏ qua). Sau 30 phút - 2 giờ: sụp mí mắt, cứng hàm, đau nhức cơ bắp toàn thân, nước tiểu màu đỏ nâu (tiểu ra myoglobin), suy thận cấp và ngừng thở.",
            "first_aid": "Băng ép bất động (Pressure Immobilization Bandage) ngay lập tức từ ngón lên gốc chi. Cố định nẹp chi. Tuyệt đối không rạch vết cắn, không hút nọc, không garô chặt làm hoại tử. Chuyển gấp đến bệnh viện có máy thở và lọc máu."
        })
    
    # Ốc biển ngộ độc thực phẩm (Index 48 - 51)
    gastropods_meta = [
        (48, "a", "Ốc bùn răng cưa", "Nassarius papillosus", "(Linnaeus, 1758)", "Vỏ hình trứng dài, mặt ngoài có nhiều u gai nhọn xếp thành hàng như răng cưa, màu vàng cam nhạt.", "Nassarius"),
        (49, "b", "Ốc mặt trăng", "Natica fasciata", "(Röding, 1798)", "Vỏ tròn bóng láng như mắt ngọc, có các dải vân màu nâu nhạt quấn quanh trục vỏ.", "Natica"),
        (50, "c", "Ốc bùn trơn", "Nassarius glans", "(Linnaeus, 1758)", "Vỏ trơn láng, hình nón nhọn, có các đốm nâu đỏ đều đặn trên nền vỏ trắng bóng.", "Nassarius"),
        (51, "d", "Ốc bùn kẻ", "Nassarius comptus", "(A. Adams, 1852)", "Vỏ nhỏ hình thoi, mặt ngoài có các đường kẻ gờ dọc thanh mảnh màu nâu sẫm.", "Nassarius")
    ]
    for s_idx, sub_fig, vn, sci, auth, morph, genus in gastropods_meta:
        species_defs.append({
            "index": s_idx, "fig_nums": [51],
            "vn_name": vn, "scientific_name": sci, "authorship": auth,
            "tax_class_vn": "Lớp Chân bụng", "tax_class_latin": "Gastropoda",
            "tax_order_vn": "Bộ Neogastropoda", "tax_order_latin": "Neogastropoda",
            "tax_family_vn": f"Họ {genus}idae", "tax_family_latin": f"{genus}idae",
            "tax_genus_vn": f"Chi {genus}", "tax_genus_latin": genus,
            "poison_type": "food", "poison_type_vn": "Gây ngộ độc thực phẩm (Ăn phải)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Độc tố Tetrodotoxin (TTX) & Saxitoxin (STX)",
            "toxin_names": ["Tetrodotoxin (TTX)", "Saxitoxin (STX)"],
            "photographer": "Bùi Quang Nghị",
            "size": "Chiều dài vỏ 2 - 5 cm",
            "distribution": "Đáy bùn cát vùng triều và ven bờ các tỉnh Quảng Ngãi, Bình Định, Phú Yên, Khánh Hòa",
            "morphology": f"{morph} Thường bị người dân nhầm lẫn với các loài ốc hương, ốc bùn ăn được.",
            "mechanism": "Tích lũy độc tố TTX và STX từ vi sinh vật hoặc tảo đáy qua chuỗi thức ăn. Độc tố bền nhiệt, nấu chín không bị phân hủy.",
            "symptoms": "Sau khi ăn 20 - 30 phút: tê môi, tê lưỡi, nôn mửa, đau bụng, mất thăng bằng, liệt cơ hô hấp dẫn đến tử vong nhanh chóng.",
            "first_aid": "Kích thích gây nôn ngay lập tức khi còn tỉnh táo. Cho uống than hoạt tính (1g/kg thể trọng) để hấp phụ bớt độc tố trong dạ dày. Đưa ngay đi cấp cứu hồi sức hô hấp nhân tạo."
        })
    
    # So biển (Index 52)
    species_defs.append({
        "index": 52, "fig_nums": [52, 53],
        "vn_name": "So biển (Cua Móng ngựa độc)", "scientific_name": "Carcinoscorpius rotundicauda", "authorship": "(Latreille, 1802)",
        "tax_class_vn": "Lớp Giáp cổ (Sam)", "tax_class_latin": "Merostomata",
        "tax_order_vn": "Bộ Xiphosura", "tax_order_latin": "Xiphosura",
        "tax_family_vn": "Họ Limulidae", "tax_family_latin": "Limulidae",
        "tax_genus_vn": "Chi Carcinoscorpius", "tax_genus_latin": "Carcinoscorpius",
        "poison_type": "food", "poison_type_vn": "Gây ngộ độc thực phẩm (Ăn phải)",
        "danger_level": "lethal", "danger_level_vn": "Cực độc — Hay nhầm với Sam ăn được, tỷ lệ tử vong rất cao",
        "toxin_names": ["Tetrodotoxin (TTX)"],
        "photographer": "Đào Việt Hà",
        "size": "Chiều dài cơ thể 20 - 35 cm (nhỏ hơn Sam)",
        "distribution": "Vùng bãi bùn lầy rừng ngập mặn, cửa sông ven biển miền Trung và miền Nam",
        "morphology": "Toàn thân bọc giáp hình móng ngựa màu xanh nâu. Phân biệt với Sam biển: So đi đơn lẻ (không đi cặp), đuôi tròn tiết diện hình tam giác không có gai gờ nhọn ở sống đuôi, kích thước nhỏ hơn Sam.",
        "mechanism": "Trứng và các mô thịt của So chứa hàm lượng cực cao chất độc Tetrodotoxin (TTX), đặc biệt vào mùa sinh sản (tháng 2 đến tháng 8). Độc tố không bị phá hủy bởi nhiệt độ sôi hay gia vị nướng rán.",
        "symptoms": "Ăn phải trứng hoặc thịt So gây tê môi, lưỡi, liệt cơ bắp, khó thở, hôn mê và ngừng tim chỉ sau 30 phút - vài giờ.",
        "first_aid": "Gây nôn khẩn cấp, uống than hoạt tính và chuyển viện cấp cứu ngay lập tức."
    })
    
    # Cua quạt cực độc (Index 53 - 55)
    crabs_meta = [
        (53, 54, "Cua Mặt quỷ", "Zosimus aeneus", "(Linnaeus, 1758)", "Vỏ đầu ngực láng có nhiều u lồi sần sùi, màu nâu đỏ hoặc xanh xám lốm đốm, các đầu ngón càng màu đen tuyền.", "Zosimus"),
        (54, 55, "Cua Hạt", "Platypodia granulosa", "(Rüppell, 1830)", "Vỏ đầu ngực hình nửa vòng tròn, mép sắc có khía răng, toàn bộ mai phủ kín các u sần dạng quả lê nhỏ, màu nâu cam.", "Platypodia"),
        (55, 56, "Cua Florida", "Atergatis floridus", "(Linnaeus, 1767)", "Vỏ hình elip láng bóng, bề ngang rộng gấp 1.4 lần chiều dài, mặt mai có các đốm hoa văn loang lổ như da báo, ngón càng đen.", "Atergatis")
    ]
    for s_idx, fig_n, vn, sci, auth, morph, genus in crabs_meta:
        species_defs.append({
            "index": s_idx, "fig_nums": [fig_n],
            "vn_name": vn, "scientific_name": sci, "authorship": auth,
            "tax_class_vn": "Lớp Giáp xác", "tax_class_latin": "Malacostraca",
            "tax_order_vn": "Bộ Mười chân", "tax_order_latin": "Decapoda",
            "tax_family_vn": "Họ Cua quạt", "tax_family_latin": "Xanthidae",
            "tax_genus_vn": f"Chi {genus}", "tax_genus_latin": genus,
            "poison_type": "food", "poison_type_vn": "Gây ngộ độc thực phẩm (Ăn phải)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Độc tố Saxitoxin & TTX cực mạnh trong thịt cua",
            "toxin_names": ["Saxitoxin (STX)", "Tetrodotoxin (TTX)", "Gonyautoxins"],
            "photographer": "Nguyễn Thị Dự",
            "size": "Mai rộng 4 - 9 cm",
            "distribution": "Các rạn san hô, hốc đá ngầm ven biển và các đảo rạn",
            "morphology": f"{morph} Thường có màu sắc sặc sỡ, đầu ngón càng luôn có màu đen đặc trưng.",
            "mechanism": "Thịt và gạch cua tích lũy độc tố thần kinh saxitoxin cực độc. Ăn nửa con cua mặt quỷ có thể làm tử vong một người trưởng thành khỏe mạnh.",
            "symptoms": "Bỏng rát râm ran ở đầu lưỡi, tê cóng môi và ngón tay, nôn mửa dữ dội, mạch đập yếu, trụy tim mạch và liệt cơ hoành dẫn đến tử vong.",
            "first_aid": "Gây nôn tức khắc, uống than hoạt tính, hô hấp nhân tạo và cấp cứu tại bệnh viện."
        })
        
    # 20 loài Cá nóc (Index 56 - 75)
    puffers_meta = [
        (56, 57, "Cá nóc Chuột vằn mang", "Arothron immaculatus", "(Bloch & Schneider, 1801)", "8 - 18 cm (max 30 cm)", "Da xám đen trừ bụng trắng, rìa vây đuôi đen tuyền, quanh lỗ mang có viền xám đen rõ rệt.", "Arothron"),
        (57, 58, "Cá nóc Chuột chấm son", "Arothron nigropunctatus", "(Bloch & Schneider, 1801)", "9 - 15 cm (max 33 cm)", "Thân màu xám tro, nâu vàng hoặc xanh xám, rải rác có các chấm đen tròn như chấm son trên thân.", "Arothron"),
        (58, 59, "Cá nóc Chuột chấm sao", "Arothron stellatus", "(Bloch & Schneider, 1801)", "12 - 41 cm (max 120 cm - loài cá nóc lớn nhất)", "Toàn thân phủ đầy vô số chấm đen nhỏ li ti như bầu trời sao, bụng có các chấm nhỏ.", "Arothron"),
        (59, 60, "Cá nóc Chuột vân bụng", "Arothron hispidus", "(Linnaeus, 1758)", "10 - 26 cm (max 50 cm)", "Thân to tròn nhiều gai nhỏ, lưng xám xanh có đốm trắng, bụng có các đường vân sọc đen uốn lượn rõ rệt.", "Arothron"),
        (60, 61, "Cá nóc Chuột mappa", "Arothron mappa", "(Lesson, 1831)", "35 cm (max 65 cm)", "Thân to có hoa văn phức tạp đan xen ngoằn ngoèo trông như bản đồ địa lý (mappa).", "Arothron"),
        (61, 62, "Cá nóc Chấm cam", "Torquigener gloerfelti", "Hardy, 1984", "11 - 19 cm (max 20 cm)", "Lưng có nhiều đốm tròn màu cam sáng hoặc vàng nâu, mặt bên có hàng đốm đậm.", "Torquigener"),
        (62, 63, "Cá nóc Vằn mặt", "Torquigener brevipinnis", "(Regan, 1903)", "7 - 8 cm", "Kích thước nhỏ, vùng đầu và má có các vệt vằn sọc nâu uốn lượn.", "Torquigener"),
        (63, 64, "Cá nóc Gai mềm", "Amblyrhynchotes honckenii", "(Bloch, 1785)", "8 - 10 cm (max 30 cm)", "Thân hình trứng dài phủ nhiều gai nhỏ mềm, lưng màu nâu đen với các đốm trắng mờ.", "Amblyrhynchotes"),
        (64, 65, "Cá nóc Vằn", "Takifugu oblongus", "(Bloch, 1786)", "7 - 24 cm (max 40 cm)", "Đầu to, trên lưng có các dải vằn sọc ngang màu nâu đậm, hai bên thân có đốm tròn trắng.", "Takifugu"),
        (65, 66, "Cá nóc Sao", "Takifugu niphobles", "(Jordan & Snyder, 1901)", "10 - 12 cm (max 15 cm)", "Lưng màu xanh đen phủ nhiều đốm trắng nhỏ như hạt tuyết, có một đốm đen lớn sau vây ngực.", "Takifugu"),
        (66, 67, "Cá nóc Vây vàng", "Takifugu xanthopterus", "(Temminck & Schlegel, 1847)", "max 50 cm", "Lưng xanh xám có các sọc nhạt, các vây có màu vàng tươi đặc trưng.", "Takifugu"),
        (67, 68, "Cá nóc Hoa trắng", "Takifugu alboplumbeus", "(Richardson, 1844)", "15 - 25 cm", "Lưng nâu đen có vô số đốm hoa tròn màu trắng bạc phủ đều.", "Takifugu"),
        (68, 69, "Cá nóc Vân hai chấm", "Takifugu bimaculatus", "(Richardson, 1845)", "12 - 25 cm", "Mỗi bên thân phía sau vây ngực có một đốm tròn đen lớn viền trắng rất rõ nét.", "Takifugu"),
        (69, 70, "Cá nóc Sọc bên", "Takifugu ocellatus", "(Linnaeus, 1758)", "10 - 15 cm", "Lưng có hai vệt vằn sáng hình yên ngựa, bên thân có đốm tròn mắt (ocellus) viền sáng.", "Takifugu"),
        (70, 71, "Cá nóc Răng rùa", "Chelonodon patoca", "(Hamilton, 1822)", "7 - 15 cm (max 38 cm)", "Mặt lưng có đám gai nhọn hình khiên, có các đốm tròn trắng trứng rải rác trên nền nâu xám.", "Chelonodon"),
        (71, 72, "Cá nóc Mỏ chim", "Lagocephalus inermis", "(Temminck & Schlegel, 1850)", "8 - 14 cm (max 90 cm)", "Mõm dài nhọn hướng xuống như mỏ chim, cơ thể hoàn toàn trơn láng không gai.", "Lagocephalus"),
        (72, 73, "Cá nóc Đầu thỏ chấm tròn", "Lagocephalus sceleratus", "(Gmelin, 1789)", "20 - 40 cm (max 80 cm)", "Lưng xám xanh có nhiều chấm đen tròn đều đặn, bên hông có một dải ánh bạc sáng lóa, độc tính cực cao.", "Lagocephalus"),
        (73, 74, "Cá nóc Tro", "Lagocephalus lunaris", "(Bloch & Schneider, 1801)", "14 - 34 cm (max 45 cm)", "Lưng màu xám chì hoặc xám xanh như màu tro, vây đuôi có rìa sau hình lưỡi liềm mép trắng.", "Lagocephalus"),
        (74, 75, "Cá nóc Vằn vện", "Lagocephalus suezensis", "Clark & Gohar, 1953", "12 - 18 cm", "Lưng có các vết vằn vện ngoằn ngoèo màu xám nâu.", "Lagocephalus"),
        (75, 76, "Cá nóc Xanh", "Lagocephalus gloveri", "Abe & Tabeta, 1983", "15 - 28 cm (max 35 cm)", "Lưng có màu xanh đậm ánh lục, gờ bên ánh bạc, vây đuôi trắng đục.", "Lagocephalus")
    ]
    for s_idx, fig_n, vn, sci, auth, sz, morph, genus in puffers_meta:
        species_defs.append({
            "index": s_idx, "fig_nums": [fig_n],
            "vn_name": vn, "scientific_name": sci, "authorship": auth,
            "tax_class_vn": "Lớp Cá xương", "tax_class_latin": "Actinopterygii",
            "tax_order_vn": "Bộ Cá nóc", "tax_order_latin": "Tetraodontiformes",
            "tax_family_vn": "Họ Cá nóc", "tax_family_latin": "Tetraodontidae",
            "tax_genus_vn": f"Chi {genus}", "tax_genus_latin": genus,
            "poison_type": "food", "poison_type_vn": "Gây ngộ độc thực phẩm (Ăn phải)",
            "danger_level": "lethal", "danger_level_vn": "Cực độc — Độc tố thần kinh Tetrodotoxin (TTX) gây chết người",
            "toxin_names": ["Tetrodotoxin (TTX)"],
            "photographer": "Trần Thị Hồng Hoa",
            "size": sz,
            "distribution": "Vùng biển ven bờ khắp ba miền Bắc - Trung - Nam, tập trung cao tại miền Trung",
            "morphology": f"{morph} Miệng nhỏ hình mỏ vẹt, xương hàm trên dưới dính liền tạo thành răng chắc khỏe. Bụng có khả năng hút nước hoặc khí phồng to như quả bóng khi bị đe dọa.",
            "mechanism": "Tetrodotoxin (TTX) tập trung cao nhất ở buồng trứng, gan, mật, ruột và da cá. Độc tố khoá kênh natri chọn lọc, ngăn dẫn truyền xung thần kinh.",
            "symptoms": "Sau khi ăn 10 - 45 phút: Tê rần môi lưỡi, đầu ngón tay chân, nôn mửa, khó thở, huyết áp tụt, liệt toàn thân và tử vong do liệt cơ hô hấp sau 4 - 6 giờ.",
            "first_aid": "Kích thích gây nôn ngay trong vòng 30 phút đầu. Uống than hoạt tính để trung hòa độc tố. Hô hấp nhân tạo liên tục và chuyển cấp cứu hồi sức ngay lập tức."
        })
        
    # Cá Hồng Đốm Bạc (Index 76)
    species_defs.append({
        "index": 76, "fig_nums": [77],
        "vn_name": "Cá hồng Đốm bạc", "scientific_name": "Lutjanus bohar", "authorship": "(Forsskål, 1775)",
        "tax_class_vn": "Lớp Cá xương", "tax_class_latin": "Actinopterygii",
        "tax_order_vn": "Bộ Cá vược", "tax_order_latin": "Perciformes",
        "tax_family_vn": "Họ Cá hồng", "tax_family_latin": "Lutjanidae",
        "tax_genus_vn": "Chi Cá hồng", "tax_genus_latin": "Lutjanus",
        "poison_type": "food", "poison_type_vn": "Gây ngộ độc thực phẩm (Ăn phải)",
        "danger_level": "severe", "danger_level_vn": "Độc mạnh — Ngộ độc độc tố Ciguatera (CFP) do vi tảo đáy",
        "toxin_names": ["Ciguatoxins (CTXs)", "Maitotoxin (MTX)"],
        "photographer": "Lê Thị Thu Thảo",
        "size": "Chiều dài thân 70 cm (lớn nhất 90 cm)",
        "distribution": "Các rạn san hô sâu và rạn ngầm ngoài khơi (Hoàng Sa, Trường Sa, Côn Đảo)",
        "morphology": "Thân hình thoi dẹp bên, màu đỏ sẫm hoặc nâu đỏ; cá non có 2 đốm tròn màu trắng bạc nổi bật ở lưng; vây ngực và vây bụng màu hồng nhạt.",
        "mechanism": "Tích lũy sinh học độc tố ciguatoxin (CTX) từ việc ăn các loài cá ăn vi tảo đơn bào sống đáy Gambierdiscus toxicus. Cá càng lớn độc tính tích lũy càng cao.",
        "symptoms": "Sau khi ăn vài giờ: Rối loạn tiêu hóa (nôn, tiêu chảy), sau đó rối loạn thần kinh đặc trưng là cảm giác đảo ngược nóng - lạnh (chạm vào nước lạnh thấy bỏng rát như chạm lửa), tê ngứa da, rụng tóc và yếu cơ kéo dài nhiều tháng.",
        "first_aid": "Điều trị hỗ trợ triệu chứng và bù dịch điện giải. Truyền tĩnh mạch Mannitol 20% trong giai đoạn sớm để giảm triệu chứng thần kinh. Không có kháng độc đặc hiệu."
    })
    
    print(f"Constructed {len(species_defs)} species entries.")
    
    # Assemble full flat Supabase rows
    flat_rows = []
    for s in species_defs:
        idx = s["index"]
        species_id = f"sinhvatdoc-species-{idx}"
        
        # Associated images
        associated_files = []
        for fn in s["fig_nums"]:
            if fn in img_files:
                associated_files.extend(img_files[fn])
                
        row = {
            "id": species_id,
            "collection_id": "sinh-vat-doc",
            "volume": 1,
            "species_index": idx,
            "vn_name": s["vn_name"],
            "scientific_name": s["scientific_name"],
            "authorship": s["authorship"],
            "tax_class_vn": s["tax_class_vn"],
            "tax_class_latin": s["tax_class_latin"],
            "tax_order_vn": s["tax_order_vn"],
            "tax_order_latin": s["tax_order_latin"],
            "tax_family_vn": s["tax_family_vn"],
            "tax_family_latin": s["tax_family_latin"],
            "tax_genus_vn": s["tax_genus_vn"],
            "tax_genus_latin": s["tax_genus_latin"],
            "vn_size": s.get("size", "—"),
            "vn_distribution": s.get("distribution", "—"),
            "morphology_vn": s.get("morphology", ""),
            "vn_status": f"Mức độ nguy hiểm: {s['danger_level_vn']}. {s['poison_type_vn']}.",
            "vn_literature": "PGS.TS. Đào Việt Hà (Chủ biên), 2021. Động vật độc biển Việt Nam. NXB Khoa học Tự nhiên và Công nghệ.",
            "biology": {
                "toxicology": {
                    "poison_type": s["poison_type"],
                    "poison_type_vn": s["poison_type_vn"],
                    "danger_level": s["danger_level"],
                    "danger_level_vn": s["danger_level_vn"],
                    "toxin_names": s["toxin_names"],
                    "mechanism": s.get("mechanism", ""),
                    "symptoms": s.get("symptoms", ""),
                    "first_aid": s.get("first_aid", "")
                },
                "photographer": s.get("photographer", "Viện Hải dương học"),
                "figure_nums": s["fig_nums"],
                "image_files": associated_files
            }
        }
        flat_rows.append(row)
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(flat_rows, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(flat_rows)} species records to {OUTPUT_JSON}.")

if __name__ == '__main__':
    main()
