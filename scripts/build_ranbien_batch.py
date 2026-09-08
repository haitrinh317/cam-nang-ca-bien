#!/usr/bin/env python3
"""
build_ranbien_batch.py
----------------------
Bóc tách toàn diện 27 loài Rắn biển Việt Nam từ tài liệu:
"Rắn biển Việt Nam / Sea Snakes in Vietnam"
(Viện Hải dương học Nha Trang, WAR, IOC VN, 2016)
Output: data/ocr_batches/ranbien_batch1.json theo đúng flat Supabase schema.
"""

import os
import sys
import re
import json
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE, 'Documents', 'ran-bien', 'Rắn biển Việt Nam.pdf')
OUT_PATH = os.path.join(BASE, 'data', 'ocr_batches', 'ranbien_batch1.json')

# Metadata cố định và chuẩn hóa tên họ/chi
TAXONOMY_MAP = {
    'Aipysurus': {
        'genus_vn': 'Chi Đẻn biển Aipysurus Lacépède, 1804',
        'genus_latin': 'Aipysurus Lacépède, 1804',
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    },
    'Emydocephalus': {
        'genus_vn': 'Chi Rắn đầu rùa Emydocephalus Krefft, 1869',
        'genus_latin': 'Emydocephalus Krefft, 1869',
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    },
    'Hydrophis': {
        'genus_vn': 'Chi Đẻn Hydrophis Latreille, 1801',
        'genus_latin': 'Hydrophis Latreille, 1801',
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    },
    'Laticauda': {
        'genus_vn': 'Chi Đẻn cạp nong Laticauda Laurenti, 1768',
        'genus_latin': 'Laticauda Laurenti, 1768',
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    },
    'Microcephalophis': {
        'genus_vn': 'Chi Đẻn đầu nhỏ Microcephalophis Lesson, 1832',
        'genus_latin': 'Microcephalophis Lesson, 1832',
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    },
    'Acrochordus': {
        'genus_vn': 'Chi Rắn rầm ri Acrochordus Hornstedt, 1787',
        'genus_latin': 'Acrochordus Hornstedt, 1787',
        'family_vn': 'Rắn Rầm Ri',
        'family_latin': 'Acrochordidae',
    }
}

MASTER_SPECIES_DICT = {
    1: {
        'scientific_name': 'Aipysurus eydouxii',
        'authorship': '(Gray, 1849)',
        'vn_name': 'Đẻn biển đuôi gai',
        'vn_alternate_names': '',
        'en_common_name': 'Spine-tailed sea snake',
    },
    2: {
        'scientific_name': 'Emydocephalus annulatus',
        'authorship': 'Krefft, 1869',
        'vn_name': 'Rắn đầu rùa',
        'vn_alternate_names': '',
        'en_common_name': 'Turtle-headed sea snake, Egg-eating sea snake',
    },
    3: {
        'scientific_name': 'Hydrophis annandalei',
        'authorship': '(Laidlaw, 1901)',
        'vn_name': 'Đẻn vảy đầu phân',
        'vn_alternate_names': 'Đẻn đầu to',
        'en_common_name': 'Bighead sea snake',
    },
    4: {
        'scientific_name': 'Hydrophis anomalus',
        'authorship': '(Schmidt, 1852)',
        'vn_name': 'Rắn biển Anomalous',
        'vn_alternate_names': '',
        'en_common_name': 'Anomalous sea snake',
    },
    5: {
        'scientific_name': 'Hydrophis atriceps',
        'authorship': 'Günther, 1864',
        'vn_name': 'Đẻn cạp nong',
        'vn_alternate_names': '',
        'en_common_name': 'Black-headed banded sea snake',
    },
    6: {
        'scientific_name': 'Hydrophis belcheri',
        'authorship': '(Gray, 1849)',
        'vn_name': 'Đẻn khoanh mờ',
        'vn_alternate_names': '',
        'en_common_name': 'Faint-banded sea snake',
    },
    7: {
        'scientific_name': 'Hydrophis brookii',
        'authorship': 'Günther, 1872',
        'vn_name': 'Đẻn Brooke',
        'vn_alternate_names': '',
        'en_common_name': "Brooke's sea snake",
    },
    8: {
        'scientific_name': 'Hydrophis caerulescens',
        'authorship': '(Shaw, 1802)',
        'vn_name': 'Đẻn nhiều răng',
        'vn_alternate_names': '',
        'en_common_name': 'Dwarf sea snake',
    },
    9: {
        'scientific_name': 'Hydrophis curtus',
        'authorship': '(Shaw, 1802)',
        'vn_name': 'Đẻn cơm',
        'vn_alternate_names': 'Đẻn cá',
        'en_common_name': "Shaw's sea snake, Short sea snake",
    },
    10: {
        'scientific_name': 'Hydrophis cyanocinctus',
        'authorship': 'Daudin, 1803',
        'vn_name': 'Sông chằn',
        'vn_alternate_names': 'Đẻn đai xanh',
        'en_common_name': 'Blue banded sea snake',
    },
    11: {
        'scientific_name': 'Hydrophis jerdonii',
        'authorship': '(Gray, 1849)',
        'vn_name': 'Đẻn mõm nhọn',
        'vn_alternate_names': '',
        'en_common_name': "Jerdon's sea snake",
    },
    12: {
        'scientific_name': 'Hydrophis klossi',
        'authorship': 'Boulenger, 1912',
        'vn_name': 'Đẻn Kloss',
        'vn_alternate_names': '',
        'en_common_name': "Kloss' sea snake",
    },
    13: {
        'scientific_name': 'Hydrophis lamberti',
        'authorship': 'Smith, 1917',
        'vn_name': 'Đẻn Lambetti',
        'vn_alternate_names': '',
        'en_common_name': "Lambert's sea snake",
    },
    14: {
        'scientific_name': 'Hydrophis melanocephalus',
        'authorship': 'Gray, 1849',
        'vn_name': 'Đẻn khoang cổ mảnh',
        'vn_alternate_names': '',
        'en_common_name': 'Slender necked sea snakes',
    },
    15: {
        'scientific_name': 'Hydrophis ornatus',
        'authorship': '(Gray, 1842)',
        'vn_name': 'Đẻn bông',
        'vn_alternate_names': 'Đẻn vết',
        'en_common_name': 'Ornate Reef sea snake',
    },
    16: {
        'scientific_name': 'Hydrophis pachycercos',
        'authorship': 'Fischer, 1855',
        'vn_name': 'Đẻn đuôi dày',
        'vn_alternate_names': 'Đẻn Fischer',
        'en_common_name': "Fischer's sea snake",
    },
    17: {
        'scientific_name': 'Hydrophis parviceps',
        'authorship': 'Smith, 1935',
        'vn_name': 'Đẻn đầu nhỏ Smith',
        'vn_alternate_names': 'Đẻn đặc hữu Việt Nam',
        'en_common_name': "Smith's small-headed sea snake",
    },
    18: {
        'scientific_name': 'Hydrophis peronii',
        'authorship': '(Duméril, 1853)',
        'vn_name': 'Đẻn đầu gai',
        'vn_alternate_names': '',
        'en_common_name': 'Spiny-headed sea snake, Horned sea snake',
    },
    19: {
        'scientific_name': 'Hydrophis platura',
        'authorship': '(Linnaeus, 1766)',
        'vn_name': 'Đẻn đuôi vàng',
        'vn_alternate_names': 'Đẻn sọc dưa',
        'en_common_name': 'Yellow belly sea snake, Pelagic sea snake',
    },
    20: {
        'scientific_name': 'Hydrophis schistosus',
        'authorship': 'Daudin, 1803',
        'vn_name': 'Đẻn mỏ',
        'vn_alternate_names': 'Đẻn mũi khoằm',
        'en_common_name': 'Beaked sea snake, Hook-nosed sea snake',
    },
    21: {
        'scientific_name': 'Hydrophis spiralis',
        'authorship': '(Shaw, 1802)',
        'vn_name': 'Đẻn bụng vàng',
        'vn_alternate_names': '',
        'en_common_name': 'Yellow sea snake',
    },
    22: {
        'scientific_name': 'Hydrophis stokesii',
        'authorship': '(Gray (in Stokes), 1846)',
        'vn_name': 'Đẻn Stokes',
        'vn_alternate_names': 'Đẻn gai lớn',
        'en_common_name': "Stokes' sea snake",
    },
    23: {
        'scientific_name': 'Hydrophis torquatus diadema',
        'authorship': 'Günther, 1864',
        'vn_name': 'Đẻn khoang cổ bờ Tây',
        'vn_alternate_names': 'Rắn biển diadema',
        'en_common_name': 'West Coast Black-headed sea snake',
    },
    24: {
        'scientific_name': 'Hydrophis viperina',
        'authorship': '(Schmidt, 1852)',
        'vn_name': 'Rắn lục biển',
        'vn_alternate_names': 'Đẻn lục',
        'en_common_name': 'Viperine sea snake',
    },
    25: {
        'scientific_name': 'Laticauda colubrina',
        'authorship': '(Schneider, 1799)',
        'vn_name': 'Đẻn cạp nong môi vàng',
        'vn_alternate_names': '',
        'en_common_name': 'Colubrine sea krait, Yellow-lipped sea krait',
    },
    26: {
        'scientific_name': 'Microcephalophis gracilis',
        'authorship': '(Shaw, 1802)',
        'vn_name': 'Đẻn đầu nhỏ',
        'vn_alternate_names': 'Đẻn giun, Đẻn kim',
        'en_common_name': 'Graceful small headed sea snake, Slender sea snake',
    },
    27: {
        'scientific_name': 'Acrochordus granulatus',
        'authorship': '(Schneider, 1799)',
        'vn_name': 'Rắn rầm ri hạt',
        'vn_alternate_names': '',
        'en_common_name': 'Little filesnake, Marine file snake, Wart snake',
    }
}


def clean_text(t: str) -> str:
    if not t:
        return ''
    t = t.replace('Kreﬀt', 'Krefft').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    lines = [l.strip() for l in t.splitlines()]
    text = ' '.join([l for l in lines if l])
    return re.sub(r'\s+', ' ', text).strip()


def parse_species_page(page_text: str, sp_index: int) -> dict:
    text = page_text.replace('Kreﬀt', 'Krefft').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    
    meta = MASTER_SPECIES_DICT[sp_index]
    sci_name = meta['scientific_name']
    authorship = meta['authorship']
    vn_name = meta['vn_name']
    vn_alt = meta['vn_alternate_names']
    en_common = meta['en_common_name']

    # 3. Synonyms
    synonyms = []
    m_syn = re.search(r'Synonyms?\s*\([^\)]+\)[\:\;]\s*(.*?)(?=Hiện trạng bảo tồn|Đặc điểm nhận dạng|(?:\n\s*\d{1,2}\.\s+[A-Z])|$)', text, re.DOTALL | re.IGNORECASE)
    if m_syn:
        raw_syn = m_syn.group(1).strip()
        if raw_syn.lower() not in ('none', 'none.'):
            for s in raw_syn.split(';'):
                s_clean = ' '.join(s.strip().split()).rstrip('.')
                if s_clean and len(s_clean) > 3 and not re.match(r'^\d{1,2}\s*$', s_clean):
                    synonyms.append(s_clean)

    # 4. Conservation status
    cs_block = ''
    m_cs = re.search(r'Hiện trạng bảo tồn[\:\;]\s*(.*?)(?=Đặc điểm nhận dạng|Màu sắc|(?:\n\s*\d{1,2}\.\s+[A-Z])|$)', text, re.DOTALL | re.IGNORECASE)
    if m_cs:
        cs_block = m_cs.group(1).strip()

    cites = ''
    nd160 = ''
    iucn = ''
    redbook = ''
    if cs_block:
        m_cites = re.search(r'CITES[^\:]*[\:]([^\n]+)', cs_block)
        if m_cites: cites = m_cites.group(1).strip().rstrip('.')
        m_nd = re.search(r'Nghị định[^\:]*[\:]([^\n]+)', cs_block)
        if m_nd: nd160 = m_nd.group(1).strip().rstrip('.')
        m_iucn = re.search(r'Danh lục đỏ IUCN[^\:]*[\:]([^\n]+)', cs_block)
        if m_iucn: iucn = m_iucn.group(1).strip().rstrip('.')
        m_rb = re.search(r'Sách đỏ Việt Nam[^\:]*[\:]([^\n]+)', cs_block)
        if m_rb: redbook = m_rb.group(1).strip().rstrip('.')

    # 5. Section extractor helper
    def extract_field(pattern_name: str, next_patterns: list) -> str:
        stop_lookahead = '|'.join([f'(?:{p})' for p in next_patterns])
        pat = rf'(?:{pattern_name})[\:\;]\s*(.*?)(?=(?:{stop_lookahead})|(?:\n\s*\d{{1,2}}\.\s+[A-Z])|$)'
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m and m.group(1):
            val = m.group(1).strip()
            val = re.sub(r'\n\d{1,2}\s*$', '', val)
            return ' '.join(val.split())
        return ''

    NEXT_KEYS = [
        'Màu sắc', 'Phân bố chung', 'Phân bố trên thế giới', 'Phân bố ở Việt Nam',
        'Phân bố ở Việt nam', 'Môi trường sống', 'Thức ăn', 'Sinh sản', 'Độc tố học',
        'Giá trị sử dụng', 'Sử dụng và thương mại', 'Tình trạng', 'Ghi chú',
        'Hiện trạng bảo tồn', 'Common name', 'Synonyms'
    ]

    ident = extract_field('Đặc điểm nhận dạng', NEXT_KEYS)
    color = extract_field('Màu sắc', NEXT_KEYS)
    dist_world = extract_field('Phân bố chung|Phân bố trên thế giới', NEXT_KEYS)
    dist_vn = extract_field('Phân bố ở Việt [Nn]am', NEXT_KEYS)
    habitat = extract_field('Môi trường sống', NEXT_KEYS)
    food = extract_field('Thức ăn', NEXT_KEYS)
    reproduction = extract_field('Sinh sản', NEXT_KEYS)
    venom = extract_field('Độc tố học', NEXT_KEYS)
    economic = extract_field('Giá trị sử dụng|Sử dụng và thương mại', NEXT_KEYS)
    status_field = extract_field('Tình trạng', NEXT_KEYS)
    notes = extract_field('Ghi chú', NEXT_KEYS)

    # 6. Synthesize composite fields
    morphology_vn = ident
    if color:
        morphology_vn += f" Màu sắc: {color}"

    ecology_parts = []
    if habitat: ecology_parts.append(f"Môi trường sống: {habitat}")
    if food: ecology_parts.append(f"Thức ăn: {food}")
    if reproduction: ecology_parts.append(f"Sinh sản: {reproduction}")
    if venom: ecology_parts.append(f"Độc tố học: {venom}")
    ecology_vn = ' '.join(ecology_parts)

    dist_parts = []
    if dist_world: dist_parts.append(f"Thế giới: {dist_world}")
    if dist_vn: dist_parts.append(f"Việt Nam: {dist_vn}")
    vn_distribution = ' '.join(dist_parts)

    status_parts = []
    if status_field: status_parts.append(f"Tình trạng thực địa: {status_field}")
    cons_details = []
    if cites and cites != 'Không': cons_details.append(f"CITES: {cites}")
    if nd160 and nd160 != 'Không': cons_details.append(f"NĐ 160: {nd160}")
    if iucn: cons_details.append(f"IUCN: {iucn}")
    if redbook and redbook != 'Không': cons_details.append(f"Sách đỏ VN: {redbook}")
    if cons_details: status_parts.append(f"Hiện trạng bảo tồn: {', '.join(cons_details)}.")
    vn_status = ' '.join(status_parts)

    cs = "common"
    if "sẽ nguy cấp" in (redbook + iucn + notes).lower() or "vu" in (redbook + iucn + notes).lower():
        cs = "rare"
    elif "ít gặp" in status_field.lower() or "hiếm" in status_field.lower():
        cs = "uncommon"
    elif "thường gặp" in status_field.lower() or "thường được tìm thấy" in status_field.lower():
        cs = "common"

    genus = sci_name.split()[0]
    tax_info = TAXONOMY_MAP.get(genus, {
        'genus_vn': f'Chi {genus}',
        'genus_latin': genus,
        'family_vn': 'Rắn Hổ',
        'family_latin': 'Elapidae',
    })

    vn_size = ''
    m_size = re.search(r'(\d+(?:\.\d+)?\s*(?:-|đến)\s*\d+(?:\.\d+)?\s*(?:cm|mm|m))', morphology_vn, re.IGNORECASE)
    if m_size:
        vn_size = m_size.group(1)

    lit_matches = re.findall(r'\(([A-ZÀ-Ỹa-zà-ỹ\s\&\,]+,\s*\d{4}[^\)]*)\)', text)
    vn_lit = '; '.join(list(dict.fromkeys(lit_matches[:5]))) if lit_matches else "Viện Hải dương học Nha Trang, 2016."

    row = {
        "id": f"ranbien-species-{sp_index}",
        "collection_id": "ran-bien",
        "volume": 1,
        "species_index": sp_index,
        "vn_name": vn_name,
        "scientific_name": sci_name,
        "authorship": authorship,
        "en_common_name": en_common,
        "vn_alternate_names": vn_alt,
        "tax_class_vn": "Lớp Bò sát",
        "tax_class_latin": "Reptilia",
        "tax_order_vn": "Bộ Có vảy",
        "tax_order_latin": "Squamata",
        "tax_family_vn": tax_info['family_vn'],
        "tax_family_latin": tax_info['family_latin'],
        "tax_genus_vn": tax_info['genus_vn'],
        "tax_genus_latin": tax_info['genus_latin'],
        "morphology_vn": morphology_vn,
        "morphology_en": "",
        "ecology_vn": ecology_vn,
        "ecology_en": "",
        "economic_value_vn": economic,
        "economic_value_en": "",
        "vn_size": vn_size,
        "en_size": "",
        "vn_distribution": vn_distribution,
        "en_distribution": "",
        "vn_specimen": notes if "Mẫu" in notes else "Viện Hải dương học Nha Trang.",
        "en_specimen": "",
        "vn_status": vn_status,
        "en_status": "",
        "vn_literature": vn_lit,
        "en_literature": "",
        "conservation_status": cs,
        "synonyms": synonyms,
    }
    return row


def main():
    print(f"Opening {PDF_PATH}...")
    doc = pymupdf.open(PDF_PATH)
    mid_x = 340.155

    half_pages = []
    for p_idx in range(2, len(doc)):
        page = doc[p_idx]
        rect = page.rect
        left_clip = pymupdf.Rect(0, 0, mid_x, rect.height)
        right_clip = pymupdf.Rect(mid_x, 0, rect.width, rect.height)
        
        left_txt = page.get_text('text', clip=left_clip).strip()
        right_txt = page.get_text('text', clip=right_clip).strip()
        
        half_pages.append((p_idx + 1, 'LEFT', left_txt))
        if right_txt and p_idx < 15:
            half_pages.append((p_idx + 1, 'RIGHT', right_txt))

    print(f"Total candidate pages: {len(half_pages)}")
    records = []
    for sp_idx, (p_num, side, txt) in enumerate(half_pages, 1):
        row = parse_species_page(txt, sp_idx)
        records.append(row)
        print(f"[{sp_idx:2d}/27] {row['id']}: {row['vn_name']} ({row['scientific_name']}) - Syns: {len(row['synonyms'])}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Successfully generated {len(records)} records to {OUT_PATH}")


if __name__ == '__main__':
    main()
