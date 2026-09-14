#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/standardize_tap4_orthography.py
Chuẩn hóa toàn bộ chính tả, danh pháp, và phục hồi dữ liệu Cá biển Tập IV (collection_id = 'ca-bien', volume = 4).
100% đối chiếu theo sách gốc "Danh mục Cá biển Việt Nam — Tập IV" (Viện Hải dương học Nha Trang, NXB KHKT 1997).
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env.local")
    sys.exit(1)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}

# 1. Định nghĩa 32 Họ chuẩn của Tập IV theo dải index loài
FAMILY_RANGES = [
    (1, 68, "Họ Cá Bàng Chài", "Labridae", "Bộ Cá Vược", "Perciformes"),
    (69, 104, "Họ Cá Mó", "Scaridae", "Bộ Cá Vược", "Perciformes"),
    (105, 108, "Họ Cá Đối Đục", "Opistognathidae", "Bộ Cá Vược", "Perciformes"),
    (109, 116, "Họ Cá Lú", "Pinguipedidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Mugiloididae (Parapercidae)
    (117, 117, "Họ Cá Chai Giả", "Percophidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Percophididae (Bembropidae)
    (118, 118, "Họ Cá Lưng Sợi", "Trichonotidae", "Bộ Cá Vược", "Perciformes"),
    (119, 126, "Họ Cá Sao", "Uranoscopidae", "Bộ Cá Vược", "Perciformes"),
    (127, 127, "Họ Cá Mắt Lồi", "Champsodontidae", "Bộ Cá Vược", "Perciformes"),
    (128, 149, "Họ Cá Mào Gà", "Blenniidae", "Bộ Cá Vược", "Perciformes"),
    (150, 150, "Họ Cá Đai Chình", "Congrogadidae", "Bộ Cá Vược", "Perciformes"),
    (151, 151, "Họ Cá Ba Vây", "Tripterygiidae", "Bộ Cá Vược", "Perciformes"),
    (152, 152, "Họ Cá Kim", "Schindleriidae", "Bộ Cá Vược", "Perciformes"),
    (153, 153, "Họ Cá Cát", "Ammodytidae", "Bộ Cá Vược", "Perciformes"),
    (154, 169, "Họ Cá Đàn Lia", "Callionymidae", "Bộ Cá Vược", "Perciformes"),
    (170, 170, "Họ Cá Bóp", "Butidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Bostrychidae
    (171, 185, "Họ Cá Bống Đen", "Eleotridae", "Bộ Cá Vược", "Perciformes"),
    (186, 246, "Họ Cá Bống Trắng", "Gobiidae", "Bộ Cá Vược", "Perciformes"),
    (247, 252, "Họ Cá Thòi Lòi", "Oxudercidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Periophthalmidae
    (253, 258, "Họ Cá Nhàm", "Gobiidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Taenioididae
    (259, 263, "Họ Cá Rễ Cau", "Gobiidae", "Bộ Cá Vược", "Perciformes"), # Sách gốc: Trypauchenidae
    (264, 265, "Họ Cá Bống Bay", "Ptereleotridae", "Bộ Cá Vược", "Perciformes"),
    (266, 287, "Họ Cá Đuôi Gai", "Acanthuridae", "Bộ Cá Vược", "Perciformes"),
    (288, 288, "Họ Cá Thù Lù", "Zanclidae", "Bộ Cá Vược", "Perciformes"),
    (289, 302, "Họ Cá Dìa", "Siganidae", "Bộ Cá Vược", "Perciformes"),
    (303, 306, "Họ Cá Thu Rắn", "Gempylidae", "Bộ Cá Vược", "Perciformes"),
    (307, 310, "Họ Cá Hố", "Trichiuridae", "Bộ Cá Vược", "Perciformes"),
    (311, 331, "Họ Cá Thu Ngừ", "Scombridae", "Bộ Cá Vược", "Perciformes"),
    (332, 334, "Họ Cá Buồm", "Istiophoridae", "Bộ Cá Vược", "Perciformes"),
    (335, 335, "Họ Cá Kiếm", "Xiphiidae", "Bộ Cá Vược", "Perciformes"),
    (336, 336, "Họ Cá Gai", "Centrolophidae", "Bộ Cá Vược", "Perciformes"),
    (337, 338, "Họ Cá Liệt Sứa", "Nomeidae", "Bộ Cá Vược", "Perciformes"),
    (339, 341, "Họ Cá Chim Trắng", "Stromateidae", "Bộ Cá Vược", "Perciformes"),
]

def get_family_info(idx):
    for start, end, fam_vn, fam_latin, ord_vn, ord_latin in FAMILY_RANGES:
        if start <= idx <= end:
            return fam_vn, fam_latin, ord_vn, ord_latin
    return "Họ Cá Biển", "Perciformes", "Bộ Cá Vược", "Perciformes"

# 2. Dữ liệu chuẩn cho 11 loài Cá Bàng Chài (#51 – #61)
SPECIES_51_61 = {
    51: {
        "species_index": 51,
        "vn_name": "Cá Bàng Chài sọc to",
        "scientific_name": "Bodianus macrurus",
        "authorship": "(Günther, 1862)",
        "en_common_name": "Macrura hogfish",
        "tax_genus_vn": "Cá Bàng Chài sọc to",
        "tax_genus_latin": "Bodianus",
        "vn_size": "125 mm. Lớn nhất 900 mm.",
        "en_size": "125 mm. Maximum 900 mm.",
        "vn_distribution": "Đông và Nam Phi, Australia, Indonesia, Philippin, Nhật Bản, Melanesia, Việt Nam: Trung Bộ.",
        "en_distribution": "Eastern and Southern Africa, Australia, Indonesia, Philippines, Japan, Melanesia, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Rất hiếm.",
        "en_status": "Very rare.",
        "vn_literature": "Herre, 1953. Orsi, 1974. Carcasson, 1977. Thẩm Thế Kiệt, 1984.",
        "en_literature": "Herre, 1953. Orsi, 1974. Carcasson, 1977. Shen, 1984.",
    },
    52: {
        "species_index": 52,
        "vn_name": "Cá Bàng Chài axin",
        "scientific_name": "Bodianus axillaris",
        "authorship": "(Bennett, 1831)",
        "en_common_name": "Axilspot hogfish",
        "tax_genus_vn": "Cá Bàng Chài axin",
        "tax_genus_latin": "Bodianus",
        "vn_size": "57 - 140 mm. Lớn nhất 200 mm.",
        "en_size": "57 - 140 mm. Maximum 200 mm.",
        "vn_distribution": "Đông và Nam Phi, Hồng Hải, Xây xen, Ấn Độ, Indonesia, Đài Loan, Nhật Bản, Micronesia, Macsan, Việt Nam: Trung Bộ.",
        "en_distribution": "Eastern and Southern Africa, Red Sea, Seychelles, India, Indonesia, Taiwan, Japan, Micronesia, Marshall, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "Durand, 1940. Carcasson, 1977. Thẩm Thế Kiệt, 1984. Myers, 1991.",
        "en_literature": "Durand, 1940. Carcasson, 1977. Shen, 1984. Myers, 1991.",
    },
    53: {
        "species_index": 53,
        "vn_name": "Cá Bàng Chài lếch",
        "scientific_name": "Cymolutes lecluse",
        "authorship": "(Quoy and Gaimard, 1824)",
        "en_common_name": "Brown-lined wrasse",
        "tax_genus_vn": "Cá Bàng Chài ximô",
        "tax_genus_latin": "Cymolutes",
        "vn_size": "97 - 200 mm.",
        "en_size": "97 - 200 mm.",
        "vn_distribution": "Natan, Đông Phi, Srilanca, Indonesia, Philippin, Nhật Bản, Fiji, Hawai, Việt Nam: Trường Sa.",
        "en_distribution": "Natal, Eastern Africa, Sri Lanka, Indonesia, Philippines, Japan, Fiji, Hawaii, Vietnam: Spratly Islands.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Rất hiếm.",
        "en_status": "Very rare.",
        "vn_literature": "de Beaufort, 1940. Carcasson, 1977. Nguyễn Hữu Phụng, 1991. Myers, 1991.",
        "en_literature": "de Beaufort, 1940. Carcasson, 1977. Nguyen Huu Phung, 1991. Myers, 1991.",
    },
    54: {
        "species_index": 54,
        "vn_name": "Cá Bàng Chài vằn đuôi",
        "scientific_name": "Pseudolabrus gracilis",
        "authorship": "(Steindachner, 1887)",
        "en_common_name": "Long parrot fish",
        "tax_genus_vn": "Cá Bàng Chài lăng",
        "tax_genus_latin": "Pseudolabrus",
        "vn_size": "85 - 109 mm.",
        "en_size": "85 - 109 mm.",
        "vn_distribution": "Trung Quốc, Triều Tiên, Nhật Bản, Việt Nam: Vịnh Bắc Bộ.",
        "en_distribution": "China, Korea, Japan, Vietnam: Gulf of Tonkin.",
        "vn_specimen": "Phân viện Hải Dương Học Hải Phòng.",
        "en_specimen": "Haiphong Branch of Institute of Oceanography.",
        "vn_status": "Thường gặp.",
        "en_status": "Common.",
        "vn_literature": "Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977.",
        "en_literature": "Zheng, 1962. Orsi, 1974. Carcasson, 1977.",
    },
    55: {
        "species_index": 55,
        "vn_name": "Cá Bàng Chài gờ nổi",
        "scientific_name": "Stethojulis interrupta",
        "authorship": "(Bleeker, 1851)",
        "en_common_name": "Cutribbon wrasse",
        "tax_genus_vn": "Cá Bàng Chài gờ",
        "tax_genus_latin": "Stethojulis",
        "vn_size": "79 - 97 mm. Lớn nhất 130 mm.",
        "en_size": "79 - 97 mm. Maximum 130 mm.",
        "vn_distribution": "Đông Phi, Hồng Hải, Indonesia, Philippin, Trung Quốc, Việt Nam: Vịnh Bắc Bộ, Trung Bộ.",
        "en_distribution": "Eastern Africa, Red Sea, Indonesia, Philippines, China, Vietnam: Gulf of Tonkin, Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang). Phân viện Hải Dương Học Hải Phòng.",
        "en_specimen": "Institute of Oceanography (Nhatrang). Haiphong Branch of Institute of Oceanography.",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977.",
        "en_literature": "Zheng, 1962. Orsi, 1974. Carcasson, 1977.",
    },
    56: {
        "species_index": 56,
        "vn_name": "Cá Bàng Chài chồn",
        "scientific_name": "Stethojulis renardi",
        "authorship": "(Bleeker, 1851)",
        "en_common_name": "Three ribbon wrasse",
        "tax_genus_vn": "Cá Bàng Chài gờ",
        "tax_genus_latin": "Stethojulis",
        "vn_size": "120 - 126 mm.",
        "en_size": "120 - 126 mm.",
        "vn_distribution": "Mozambic, Zanziba, Indonesia, Malaysia, Australia, Philippin, Nhật Bản, Mariana, Việt Nam: Trung Bộ.",
        "en_distribution": "Mozambique, Zanzibar, Indonesia, Malaysia, Australia, Philippines, Japan, Mariana, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Thường gặp.",
        "en_status": "Common.",
        "vn_literature": "de Beaufort, 1940. Orsi, 1974. Carcasson, 1977. Nguyễn Hữu Phụng, 1991.",
        "en_literature": "de Beaufort, 1940. Orsi, 1974. Carcasson, 1977. Nguyen Huu Phung, 1991.",
    },
    57: {
        "species_index": 57,
        "vn_name": "Cá Bàng Chài đĩa",
        "scientific_name": "Stethojulis kalosoma",
        "authorship": "(Bleeker, 1852)",
        "en_common_name": "Lugday wrasse",
        "tax_genus_vn": "Cá Bàng Chài gờ",
        "tax_genus_latin": "Stethojulis",
        "vn_size": "68 - 83 mm. Lớn nhất 126 mm.",
        "en_size": "68 - 83 mm. Maximum 126 mm.",
        "vn_distribution": "Đông Phi, Hồng Hải, Indonesia, Australia, Philippin, Trung Quốc, Triều Tiên, Nhật Bản, Việt Nam: Vịnh Bắc Bộ, Trung Bộ.",
        "en_distribution": "Eastern Africa, Red Sea, Indonesia, Australia, Philippines, China, Korea, Japan, Vietnam: Gulf of Tonkin, Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang). Phân viện Hải Dương Học Hải Phòng.",
        "en_specimen": "Institute of Oceanography (Nhatrang). Haiphong Branch of Institute of Oceanography.",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "de Beaufort, 1940. Trịnh Bảo San, 1962. Orsi, 1974.",
        "en_literature": "de Beaufort, 1940. Zheng, 1962. Orsi, 1974.",
    },
    58: {
        "species_index": 58,
        "vn_name": "Cá Bàng Chài chấm đỏ",
        "scientific_name": "Stethojulis axillaris",
        "authorship": "(Quoy and Gaimard, 1824)",
        "en_common_name": "Red spot wrasse, Red shoulder wrasse",
        "tax_genus_vn": "Cá Bàng Chài gờ",
        "tax_genus_latin": "Stethojulis",
        "vn_size": "Lớn nhất 13 cm.",
        "en_size": "Maximum 130 mm.",
        "vn_distribution": "Hawai, Micronesia, Indonesia, Malaysia, Australia, Madagasca, Hồng Hải, Nhật Bản, Trung Quốc, Philippin, Việt Nam: Trung Bộ, Nam Bộ.",
        "en_distribution": "Hawaii, Micronesia, Indonesia, Malaysia, Australia, Madagascar, Red Sea, Japan, China, Philippines, Vietnam: Central and Southern Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Thường gặp.",
        "en_status": "Common.",
        "vn_literature": "de Beaufort, 1940. Herre, 1953. Orsi, 1974.",
        "en_literature": "de Beaufort, 1940. Herre, 1953. Orsi, 1974.",
    },
    59: {
        "species_index": 59,
        "vn_name": "Cá Bàng Chài đầu đen",
        "scientific_name": "Thalassoma lunare",
        "authorship": "(Linnaeus, 1758)",
        "en_common_name": "Moon wrasse, Crescent wrasse",
        "tax_genus_vn": "Cá Bàng Chài đầu đen",
        "tax_genus_latin": "Thalassoma",
        "vn_size": "87 - 150 mm. Lớn nhất 300 mm.",
        "en_size": "87 - 150 mm. Maximum 300 mm.",
        "vn_distribution": "Đông Phi, Hồng Hải, Srilanca, Thái Lan, Indonesia, Australia, Philippin, Trung Quốc, Nhật Bản, Micronesia, Polynesia, Việt Nam: Vịnh Bắc Bộ, Trung Bộ.",
        "en_distribution": "Eastern Africa, Red Sea, Sri Lanka, Thailand, Indonesia, Australia, Philippines, China, Japan, Micronesia, Polynesia, Vietnam: Gulf of Tonkin, Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang). Phân viện Hải Dương Học Hải Phòng.",
        "en_specimen": "Institute of Oceanography (Nhatrang). Haiphong Branch of Institute of Oceanography.",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977. Myers, 1991.",
        "en_literature": "Zheng, 1962. Orsi, 1974. Carcasson, 1977. Myers, 1991.",
    },
    60: {
        "species_index": 60,
        "vn_name": "Cá Bàng Chài sáu vạch",
        "scientific_name": "Thalassoma hardwickii",
        "authorship": "(Bennett, 1830)",
        "en_common_name": "Sixbar wrasse",
        "tax_genus_vn": "Cá Bàng Chài đầu đen",
        "tax_genus_latin": "Thalassoma",
        "vn_size": "67 - 170 mm. Lớn nhất 450 mm.",
        "en_size": "67 - 170 mm. Maximum 450 mm.",
        "vn_distribution": "Đông Phi, Srilanca, Indonesia, Australia, Philippin, Trung Quốc, Nhật Bản, Melanesia, Polynesia, Việt Nam: Trung Bộ, Hoàng Sa, Trường Sa.",
        "en_distribution": "Eastern Africa, Sri Lanka, Indonesia, Australia, Philippines, China, Japan, Melanesia, Polynesia, Vietnam: Central Vietnam, Paracel and Spratly Islands.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Hiếm.",
        "en_status": "Rare.",
        "vn_literature": "Trịnh Bảo San, 1962. Orsi, 1974. Carcasson, 1977. Nguyễn Hữu Phụng, 1991. Myers, 1991.",
        "en_literature": "Zheng, 1962. Orsi, 1974. Carcasson, 1977. Nguyen Huu Phung, 1991. Myers, 1991.",
    },
    61: {
        "species_index": 61,
        "vn_name": "Cá Bàng Chài đuôi dài",
        "scientific_name": "Thalassoma amblycephalum",
        "authorship": "(Bleeker, 1856)",
        "en_common_name": "Twotone wrasse",
        "tax_genus_vn": "Cá Bàng Chài đầu đen",
        "tax_genus_latin": "Thalassoma",
        "vn_size": "160 mm.",
        "en_size": "160 mm.",
        "vn_distribution": "Indonesia, Philippin, Trung Quốc, Melanesia, Micronesia, Polynesia, bờ tây Mexico, Việt Nam: Trung Bộ.",
        "en_distribution": "Indonesia, Philippines, China, Melanesia, Micronesia, Polynesia, Western Mexico, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Rất ít gặp.",
        "en_status": "Very uncommon.",
        "vn_literature": "Durand, 1940. Orsi, 1974. de Beaufort, 1940. Herre, 1953. Carcasson, 1977.",
        "en_literature": "Durand, 1940. Orsi, 1974. de Beaufort, 1940. Herre, 1953. Carcasson, 1977.",
    }
}

# 3. Dữ liệu chuẩn cho 3 loài khuyết/hỏng (#78, #102, #124)
SPECIES_RECOVER = {
    78: {
        "species_index": 78,
        "vn_name": "Cá Mó xanh đen",
        "scientific_name": "Scarus oedema",
        "authorship": "(Snyder, 1909)",
        "en_common_name": "Oedema parrotfish",
        "tax_genus_vn": "Cá Mó",
        "tax_genus_latin": "Scarus",
        "vn_size": "430 mm.",
        "en_size": "430 mm.",
        "vn_distribution": "Philippin, Nhật Bản, Việt Nam: Trung Bộ.",
        "en_distribution": "Philippines, Japan, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "Herre, 1953. Orsi, 1974. Carcasson, 1977.",
        "en_literature": "Herre, 1953. Orsi, 1974. Carcasson, 1977.",
    },
    102: {
        "species_index": 102,
        "vn_name": "Cá Mó Giava",
        "scientific_name": "Scarus bataviensis",
        "authorship": "Bleeker, 1857",
        "en_common_name": "Batavia parrotfish",
        "tax_genus_vn": "Cá Mó",
        "tax_genus_latin": "Scarus",
        "vn_size": "360 mm. Lớn nhất 600 mm.",
        "en_size": "360 mm. Maximum 600 mm.",
        "vn_distribution": "Madagasca, Zanziba, Ấn Độ, Indonesia, Philippin, Nhật Bản, Samoa, Carolin, Hawai, Macsan, Việt Nam: Trung Bộ.",
        "en_distribution": "Madagascar, Zanzibar, India, Indonesia, Philippines, Japan, Samoa, Caroline, Hawaii, Marshall, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Ít gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "de Beaufort, 1940. Herre, 1953. Carcasson, 1977.",
        "en_literature": "de Beaufort, 1940. Herre, 1953. Carcasson, 1977.",
    },
    124: {
        "species_index": 124,
        "vn_name": "Cá Sao thanh",
        "scientific_name": "Gnathagnus elongatus",
        "authorship": "(Temminck and Schlegel, 1846)",
        "en_common_name": "Blue spotted stargazer",
        "tax_genus_vn": "Cá Sao thanh",
        "tax_genus_latin": "Gnathagnus",
        "vn_size": "52 - 94 mm.",
        "en_size": "52 - 94 mm.",
        "vn_distribution": "Trung Quốc, Đài Loan, Nhật Bản, Việt Nam: Vịnh Bắc Bộ.",
        "en_distribution": "China, Taiwan, Japan, Vietnam: Gulf of Tonkin.",
        "vn_specimen": "Bảo tàng Động vật Quảng Châu (Trung Quốc).",
        "en_specimen": "Zoological Museum of Guangzhou (China).",
        "vn_status": "Không thường gặp.",
        "en_status": "Uncommon.",
        "vn_literature": "Thành Khánh Thái, 1962. Thẩm Thế Kiệt, 1984.",
        "en_literature": "Cheng, 1962. Shen, 1984.",
    }
}

# 4. Dữ liệu chuẩn cho 4 loài Họ Cá Đối Đục (#105 – #108)
SPECIES_OPISTOGNATHIDAE = {
    105: {
        "species_index": 105,
        "vn_name": "Cá Đối Đục hàm dài",
        "scientific_name": "Gnathypops evermanni",
        "authorship": "Jordan and Snyder, 1902",
        "en_common_name": "Long jawfish",
        "tax_genus_vn": "Cá Đối Đục hàm dài",
        "tax_genus_latin": "Gnathypops",
        "vn_size": "52 - 80 mm.",
        "en_size": "52 - 80 mm.",
        "vn_distribution": "Trung Quốc, Nhật Bản, Việt Nam: Trung Bộ.",
        "en_distribution": "China, Japan, Vietnam: Central Vietnam.",
        "vn_specimen": "Bảo tàng Quảng Châu (Trung Quốc).",
        "en_specimen": "Museum of Guangzhou (China).",
        "vn_status": "Rất ít gặp, hiếm.",
        "en_status": "Very uncommon, rare.",
        "vn_literature": "Thành Khánh Thái, 1962. Orsi, 1974.",
        "en_literature": "Cheng, 1962. Orsi, 1974.",
    },
    106: {
        "species_index": 106,
        "vn_name": "Cá Đối Đục rôsen",
        "scientific_name": "Gnathypops rosenbergi",
        "authorship": "(Bleeker, 1856)",
        "en_common_name": "Rosenberg jawfish",
        "tax_genus_vn": "Cá Đối Đục",
        "tax_genus_latin": "Gnathypops",
        "vn_size": "120 mm.",
        "en_size": "120 mm.",
        "vn_distribution": "Ấn Độ, Indonesia, Malaysia, Việt Nam: Trung Bộ.",
        "en_distribution": "India, Indonesia, Malaysia, Vietnam: Central Vietnam.",
        "vn_specimen": "Bảo tàng Động vật Pari (Pháp).",
        "en_specimen": "Zoological Museum of Paris (France).",
        "vn_status": "Hiếm.",
        "en_status": "Rare.",
        "vn_literature": "de Beaufort, 1951. Orsi, 1974.",
        "en_literature": "de Beaufort, 1951. Orsi, 1974.",
    },
    107: {
        "species_index": 107,
        "vn_name": "Cá Đối Đục caten",
        "scientific_name": "Opisthognathus castelnaui",
        "authorship": "Bleeker, 1860",
        "en_common_name": "Brown jawfish",
        "tax_genus_vn": "Cá Đối Đục",
        "tax_genus_latin": "Opisthognathus",
        "vn_size": "150 mm. Lớn nhất 200 mm.",
        "en_size": "150 mm. Maximum 200 mm.",
        "vn_distribution": "Indonesia, Philippin, Malaysia, Việt Nam: Trung Bộ.",
        "en_distribution": "Indonesia, Philippines, Malaysia, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Rất ít gặp.",
        "en_status": "Very uncommon.",
        "vn_literature": "de Beaufort, 1951. Heere, 1953. Fourmanoir, 1965.",
        "en_literature": "de Beaufort, 1951. Heere, 1953. Fourmanoir, 1965.",
    },
    108: {
        "species_index": 108,
        "vn_name": "Cá Đối Đục ria nhỏ",
        "scientific_name": "Opisthognathus nigromarginatus",
        "authorship": "Rüppell, 1828",
        "en_common_name": "Dark jawfish",
        "tax_genus_vn": "Cá Đối Đục",
        "tax_genus_latin": "Opisthognathus",
        "vn_size": "200 mm.",
        "en_size": "200 mm.",
        "vn_distribution": "Vùng nhiệt đới Ấn Độ Dương, Việt Nam: Trung Bộ.",
        "en_distribution": "Tropical Indian Ocean, Vietnam: Central Vietnam.",
        "vn_specimen": "Viện Hải Dương Học (Nha Trang).",
        "en_specimen": "Institute of Oceanography (Nhatrang).",
        "vn_status": "Rất ít gặp.",
        "en_status": "Very uncommon.",
        "vn_literature": "Orsi, 1974. Carcasson, 1977.",
        "en_literature": "Orsi, 1974. Carcasson, 1977.",
    }
}

# 5. Bản đồ sửa lỗi chính tả cho các loài khác trong Tập IV
ORTHOGRAPHY_FIXES = {
    19: {"vn_name": "Cá Bàng Chài mắt võng"},
    31: {"vn_name": "Cá Bàng Chài hai sọc đen"},
    38: {"scientific_name": "Anampses geographicus"},
    63: {"vn_name": "Cá Bàng Chài năm vết", "scientific_name": "Thalassoma quinquevittatum"},
    64: {"vn_name": "Cá Bàng Chài dansen", "scientific_name": "Thalassoma jansenii"},
    65: {"vn_name": "Cá Bàng Chài vằn mõm"},
    66: {"vn_name": "Cá Bàng Chài đai đuôi"},
    77: {"vn_name": "Cá Mó vệt trắng"},
    86: {"scientific_name": "Scarus janthochir"},
    89: {"vn_name": "Cá Mó lừa"},
    96: {"vn_name": "Cá Mó đỏ vằn"},
    101: {"vn_name": "Cá Mó u đầu", "scientific_name": "Scarus muricatus"},
    103: {"vn_name": "Cá Mó gai"},
    104: {"vn_name": "Cá Mó tiêm"},
    120: {"vn_name": "Cá Sao sừng"},
    122: {"vn_name": "Cá Sao Nhật"},
    147: {"vn_name": "Cá Mào Gà tiên êlêgan"},
    171: {"vn_name": "Cá Bống cầu"},
    173: {"vn_name": "Cá Bống cửa"},
    203: {"vn_name": "Cá Bống vằn mắt"},
    226: {"vn_name": "Cá Bống trọ"},
    233: {"vn_name": "Cá Bống hương"},
    242: {"vn_name": "Cá Bống răng xẻ"},
    246: {"vn_name": "Cá Bống nước"},
    258: {"vn_name": "Cá Nhàm nhẵn"},
    272: {"vn_name": "Cá Bắp Nẻ bleeke"},
    337: {"vn_name": "Cá Liệt sứa nhẵn"}
}

def fetch_existing_tap4():
    url = f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.ca-bien&volume=eq.4&select=id,species_index,vn_name,scientific_name"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error fetching existing tap 4: {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.json()

def update_or_insert_species(payload, sp_id=None):
    if sp_id:
        url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        resp = requests.patch(url, headers=HEADERS, json=payload)
    else:
        url = f"{SUPABASE_URL}/rest/v1/species"
        resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code not in [200, 201, 204]:
        print(f"Failed to upsert species #{payload.get('species_index')}: {resp.status_code} {resp.text}")
        return False
    return True

def main():
    print("=== BẮT ĐẦU CHUẨN HÓA TẬP IV CÁ BIỂN VIỆT NAM ===")
    existing = fetch_existing_tap4()
    existing_by_idx = {sp['species_index']: sp for sp in existing}
    print(f"Hiện có trong DB: {len(existing)} loài")

    updated_count = 0
    inserted_count = 0

    # 1. Cập nhật 11 loài Cá Bàng Chài (#51 – #61)
    print("\n--- 1. Cập nhật 11 loài Cá Bàng Chài (#51 – #61) ---")
    for idx in range(51, 62):
        sp_data = SPECIES_51_61[idx].copy()
        fam_vn, fam_latin, ord_vn, ord_latin = get_family_info(idx)
        sp_data.update({
            "collection_id": "ca-bien",
            "volume": 4,
            "tax_class_vn": "Lớp Cá Xương",
            "tax_class_latin": "Osteichthyes",
            "tax_order_vn": ord_vn,
            "tax_order_latin": ord_latin,
            "tax_family_vn": fam_vn,
            "tax_family_latin": fam_latin,
        })
        existing_sp = existing_by_idx.get(idx)
        if existing_sp:
            sp_id = existing_sp['id']
            print(f"Thay thế #{idx}: '{existing_sp.get('vn_name')}' -> '{sp_data['vn_name']}'")
            if update_or_insert_species(sp_data, sp_id):
                updated_count += 1
        else:
            print(f"Thêm mới #{idx}: '{sp_data['vn_name']}'")
            if update_or_insert_species(sp_data):
                inserted_count += 1

    # 2. Khôi phục 3 loài khuyết/hỏng (#78, #102, #124)
    print("\n--- 2. Khôi phục 3 loài khuyết/hỏng (#78, #102, #124) ---")
    for idx, sp_data in SPECIES_RECOVER.items():
        fam_vn, fam_latin, ord_vn, ord_latin = get_family_info(idx)
        payload = sp_data.copy()
        payload.update({
            "collection_id": "ca-bien",
            "volume": 4,
            "tax_class_vn": "Lớp Cá Xương",
            "tax_class_latin": "Osteichthyes",
            "tax_order_vn": ord_vn,
            "tax_order_latin": ord_latin,
            "tax_family_vn": fam_vn,
            "tax_family_latin": fam_latin,
        })
        existing_sp = existing_by_idx.get(idx)
        if existing_sp:
            sp_id = existing_sp['id']
            print(f"Khôi phục dữ liệu #{idx}: '{existing_sp.get('vn_name')}' -> '{payload['vn_name']}'")
            if update_or_insert_species(payload, sp_id):
                updated_count += 1
        else:
            print(f"Thêm mới loài bị khuyết #{idx}: '{payload['vn_name']}'")
            if update_or_insert_species(payload):
                inserted_count += 1

    # 3. Chuẩn hóa 4 loài Họ Cá Đối Đục (#105 – #108)
    print("\n--- 3. Chuẩn hóa 4 loài Họ Cá Đối Đục (#105 – #108) ---")
    for idx, sp_data in SPECIES_OPISTOGNATHIDAE.items():
        fam_vn, fam_latin, ord_vn, ord_latin = get_family_info(idx)
        payload = sp_data.copy()
        payload.update({
            "collection_id": "ca-bien",
            "volume": 4,
            "tax_class_vn": "Lớp Cá Xương",
            "tax_class_latin": "Osteichthyes",
            "tax_order_vn": ord_vn,
            "tax_order_latin": ord_latin,
            "tax_family_vn": fam_vn,
            "tax_family_latin": fam_latin,
        })
        existing_sp = existing_by_idx.get(idx)
        if existing_sp:
            sp_id = existing_sp['id']
            print(f"Cập nhật chuẩn hóa #{idx}: '{existing_sp.get('vn_name')}' -> '{payload['vn_name']}' (Họ: {fam_vn})")
            if update_or_insert_species(payload, sp_id):
                updated_count += 1
        else:
            print(f"Thêm mới #{idx}: '{payload['vn_name']}'")
            if update_or_insert_species(payload):
                inserted_count += 1

    # 4. Sửa lỗi chính tả tên VN và tên KH cho các loài khác
    print("\n--- 4. Sửa lỗi chính tả OCR cho các loài khác ---")
    for idx, fixes in ORTHOGRAPHY_FIXES.items():
        existing_sp = existing_by_idx.get(idx)
        if existing_sp:
            sp_id = existing_sp['id']
            payload = fixes.copy()
            # Đảm bảo Họ chuẩn
            fam_vn, fam_latin, ord_vn, ord_latin = get_family_info(idx)
            payload["tax_family_vn"] = fam_vn
            payload["tax_family_latin"] = fam_latin
            print(f"Sửa lỗi chính tả #{idx}: DB='{existing_sp.get('vn_name')}' -> Sửa={payload}")
            if update_or_insert_species(payload, sp_id):
                updated_count += 1

    # 5. Rà soát và cập nhật Họ (tax_family_vn, tax_family_latin) cho toàn bộ 341 loài
    print("\n--- 5. Chuẩn hóa Họ (tax_family_vn, tax_family_latin) cho tất cả loài còn lại ---")
    for idx in range(1, 342):
        if idx in range(51, 62) or idx in SPECIES_RECOVER or idx in SPECIES_OPISTOGNATHIDAE:
            continue
        existing_sp = existing_by_idx.get(idx)
        if existing_sp:
            fam_vn, fam_latin, ord_vn, ord_latin = get_family_info(idx)
            sp_id = existing_sp['id']
            payload = {
                "tax_family_vn": fam_vn,
                "tax_family_latin": fam_latin,
                "tax_order_vn": ord_vn,
                "tax_order_latin": ord_latin,
            }
            update_or_insert_species(payload, sp_id)

    print("\n=== HOÀN THÀNH CHUẨN HÓA ===")
    print(f"Tổng số bản ghi đã cập nhật: {updated_count}")
    print(f"Tổng số bản ghi đã thêm mới: {inserted_count}")

    # Kiểm tra lại tổng số loài sau khi update
    final_list = fetch_existing_tap4()
    print(f"Tổng số loài Tập IV trong DB hiện tại: {len(final_list)} / 341")

if __name__ == '__main__':
    main()
