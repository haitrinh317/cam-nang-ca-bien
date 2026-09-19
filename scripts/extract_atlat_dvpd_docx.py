#!/usr/bin/env python3
"""
extract_atlat_dvpd_docx.py
Bóc tách toàn diện 102 loài Giáp xác chân chèo (Copepoda) và 103 ảnh vi thể
từ file gốc Documents/dong-vat-phu-du/Atlat DVPD_2016_2019.docx
theo quy chuẩn CSDL Cẩm Nang Sinh Vật Biển Việt Nam.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import os
import json

DOCX_PATH = 'Documents/dong-vat-phu-du/Atlat DVPD_2016_2019.docx'
IMG_OUT_DIR = 'scratch/dvpd_images'
OUTPUT_JSON = 'scratch/dvpd_atlat_raw_102.json'

os.makedirs(IMG_OUT_DIR, exist_ok=True)

def extract_dvpd():
    print(f"[*] Đang đọc file DOCX: {DOCX_PATH}")
    with zipfile.ZipFile(DOCX_PATH, 'r') as z:
        # 1. Trích xuất quan hệ ảnh (Relationships)
        rels_xml = z.read('word/_rels/document.xml.rels')
        rels_tree = ET.fromstring(rels_xml)
        rel_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
        r_map = {r.attrib.get('Id'): r.attrib.get('Target') for r in rels_tree.findall('.//rel:Relationship', rel_ns)}

        # 2. Đọc nội dung document.xml
        xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        }
        body = tree.find('.//w:body', ns)

        # 3. Trích xuất toàn bộ ảnh sang scratch/dvpd_images/
        media_files = [f for f in z.namelist() if f.startswith('word/media/')]
        print(f"[*] Trích xuất {len(media_files)} ảnh vi thể sang {IMG_OUT_DIR}/...")
        for mf in media_files:
            fname = os.path.basename(mf)
            out_p = os.path.join(IMG_OUT_DIR, fname)
            with open(out_p, 'wb') as out_f:
                out_f.write(z.read(mf))

        # 4. Duyệt body paragraphs và gom cụm
        elements = []
        for elem in body:
            if elem.tag.endswith('p'):
                txt = ''.join(t.text for t in elem.findall('.//w:t', ns) if t.text).strip()
                blips = elem.findall('.//a:blip', ns)
                imgs = [r_map.get(b.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')) for b in blips]
                imgs = [os.path.basename(img) for img in imgs if img]
                elements.append((txt, imgs))

    # Nhận diện đầu mục loài
    entries = []
    curr = {'header': '', 'paragraphs': [], 'images': []}

    for txt, imgs in elements:
        words = txt.split()
        is_header = False
        if words and len(words) >= 2:
            w0 = words[0]
            w1 = words[1]
            if w0[0].isupper() and w0.isalpha() and not any(txt.startswith(p) for p in [
                'Việt Nam', 'Thế giới', 'Phân bố', 'Sinh học', 'Sinh thái', 'Ghi chú', 'Đặc điểm', 
                'Hình', 'Mẫu', 'ATLAT', 'Ba loài', 'Là loài', 'Nhóm', 'Bộ', 'Lớp', 'Họ', 'Giới', 'Ngành',
                '- Việt Nam', '- Thế giới', '–'
            ]):
                if w1[0].islower() or (w1.startswith('(') and len(words) > 2 and words[2][0].islower()):
                    is_header = True

        if is_header:
            if curr['header'] or curr['paragraphs']:
                entries.append(curr)
            curr = {'header': txt, 'paragraphs': [], 'images': list(imgs)}
        else:
            if txt:
                curr['paragraphs'].append(txt)
            if imgs:
                curr['images'].extend(imgs)

    if curr['header'] or curr['paragraphs']:
        entries.append(curr)

    print(f"[*] Tổng số mục mô tả phát hiện: {len(entries)}")

    # Gom cụm theo Tên Nhị thức Khoa học (Hợp nhất Đa Nguồn / Merge)
    species_by_canonical = {}

    for e in entries:
        h = e['header']
        # Tách tên nhị thức sạch: Chi + Loài
        # Loại bỏ subgenus dạng (Odontacartia) hoặc (Acartiura)
        clean = re.sub(r'\(.*?\)', '', h)
        clean = re.sub(r'[–-].*', '', clean)
        words = clean.strip().split()
        genus = words[0].strip() if words else "Unknown"
        species_ep = words[1].strip() if len(words) >= 2 else ""
        if species_ep:
            canonical = f"{genus} {species_ep}"
        else:
            canonical = h

        # Lấy tác giả / năm nếu có
        author_year = ""
        m_ay = re.search(r'([A-Z][a-zà-ỹ\.\&]+.*?\d{4}|\(.*?\d{4}.*?\))', h)
        if m_ay:
            author_year = m_ay.group(1).strip()

        # Parse chi tiết
        eco_parts = []
        vn_dist_parts = []
        world_dist_parts = []
        specimens = []
        captions = []
        notes = []

        for p in e['paragraphs']:
            if p.startswith('Sinh học') or p.startswith('Sinh thái') or p.startswith('Đặc điểm'):
                eco_parts.append(p)
            elif 'Việt Nam' in p or p.startswith('Việt Nam') or p.startswith('- Việt Nam'):
                vn_dist_parts.append(p)
            elif 'Thế giới' in p or p.startswith('Thế giới') or p.startswith('- Thế giới'):
                world_dist_parts.append(p)
            elif p.startswith('Ghi chú'):
                notes.append(p)
            elif p.startswith('Hình'):
                captions.append(p)
                m_spec = re.findall(r'VNMN?[_\.][A-Za-z0-9_\.\-]+', p, re.I)
                specimens.extend(m_spec)
            elif 'Mẫu' in p:
                m_spec = re.findall(r'VNMN?[_\.][A-Za-z0-9_\.\-]+', p, re.I)
                if m_spec:
                    specimens.extend(m_spec)
                else:
                    specimens.append(p)

        if canonical not in species_by_canonical:
            species_by_canonical[canonical] = {
                'canonical_name': canonical,
                'raw_headers': [h],
                'genus': genus,
                'species': species_ep,
                'author_year': author_year,
                'ecology_vn': " ".join(eco_parts),
                'vn_distribution': " ".join(vn_dist_parts),
                'en_distribution': " ".join(world_dist_parts),
                'specimens': list(set(specimens)),
                'images': list(set(e['images'])),
                'captions': captions,
                'notes': " ".join(notes)
            }
        else:
            # Merge thông tin bổ sung nếu loài xuất hiện lần 2 (vd tiêu bản đực/cái)
            sp = species_by_canonical[canonical]
            sp['raw_headers'].append(h)
            if not sp['author_year'] and author_year:
                sp['author_year'] = author_year
            if eco_parts:
                sp['ecology_vn'] = (sp['ecology_vn'] + " " + " ".join(eco_parts)).strip()
            if vn_dist_parts:
                sp['vn_distribution'] = (sp['vn_distribution'] + " " + " ".join(vn_dist_parts)).strip()
            if world_dist_parts:
                sp['en_distribution'] = (sp['en_distribution'] + " " + " ".join(world_dist_parts)).strip()
            sp['specimens'] = list(set(sp['specimens'] + specimens))
            sp['images'] = list(set(sp['images'] + e['images']))
            sp['captions'].extend(captions)
            if notes:
                sp['notes'] = (sp['notes'] + " " + " ".join(notes)).strip()

    print(f"[*] Tổng số loài độc bản sau khi Hợp nhất: {len(species_by_canonical)}")

    # Chuẩn hóa danh sách thành phẳng theo Schema Supabase
    final_list = []
    idx = 1

    for canonical, sp in sorted(species_by_canonical.items()):
        if not canonical or not canonical.strip() or sp['genus'] == 'Unknown':
            continue

        # Làm sạch chuỗi phân bố
        vn_dist = re.sub(r'^(?:Phân bố[\.\:\s]*)?(?:-\s*)?(?:Việt Nam[\.\:\s]*)?', '', sp['vn_distribution']).strip()
        world_dist = re.sub(r'^(?:Phân bố[\.\:\s]*)?(?:-\s*)?(?:Thế giới[\.\:\s]*)?', '', sp['en_distribution']).strip()
        eco = re.sub(r'^(?:Sinh học\s*[–-]\s*sinh thái|Sinh thái|Đặc điểm)[\.\:\s]*', '', sp['ecology_vn']).strip()

        # Quy ước tên tiếng Việt = Tên khoa học theo chỉ đạo của chú Chình
        item = {
            'species_index': idx,
            'id': f"dvpd-species-{idx}",
            'collection_id': 'dong-vat-phu-du',
            'scientific_name': canonical,
            'vn_name': canonical,  # Quyết định: dùng danh pháp khoa học
            'author_year': sp['author_year'],
            'raw_headers': sp['raw_headers'],
            'taxonomy_class': 'Hexanauplia',
            'taxonomy_subclass': 'Copepoda',
            'taxonomy_genus': sp['genus'],
            'ecology_vn': eco,
            'vn_distribution': vn_dist,
            'en_distribution': world_dist,
            'specimens': sp['specimens'],
            'notes': sp['notes'],
            'captions': sp['captions'],
            'images': sp['images'],
            'image_count': len(sp['images']),
            'vn_literature': "Atlat Động vật phù du (2016–2019) — TS. Trương Sĩ Hải Trình & CS (Viện Hải dương học, Viện Hàn lâm KHCN Việt Nam / Bảo tàng Thiên nhiên Việt Nam VNMN)."
        }
        final_list.append(item)
        idx += 1

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as out_f:
        json.dump(final_list, out_f, ensure_ascii=False, indent=2)

    print(f"[✓] Đã xuất thành công {len(final_list)} loài vào {OUTPUT_JSON}")
    return final_list

if __name__ == '__main__':
    extract_dvpd()
