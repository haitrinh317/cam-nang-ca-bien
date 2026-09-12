import os
import sys
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    for f in ['.env.local', '.env']:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_fish_overlap import matches, unmatched

BOOK_TITLES_VI = {
    1: "GS. Nguyễn Khắc Hường, 1992. Danh mục Cá biển Việt Nam — Tập I: Cá Nhám, Cá Đuối, Cá Trích, Cá Chình. NXB Nông nghiệp.",
    2: "GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi, 1994. Danh mục Cá biển Việt Nam — Tập II. NXB Nông nghiệp.",
    3: "GS. Nguyễn Khắc Hường, 2000. Danh mục Cá biển Việt Nam — Tập III: Cá Hồng, Cá Mú, Cá Đù, Cá Mối. NXB Nông nghiệp.",
    4: "TS. Nguyễn Nhật Thi, 2004. Danh mục Cá biển Việt Nam — Tập IV: Cá Bướm, Cá Thiên nga, Cá Tai tượng. NXB Nông nghiệp.",
    5: "TS. Nguyễn Nhật Thi, 2007. Danh mục Cá biển Việt Nam — Tập V: Cá Bống, Cá Bơn, Cá Nóc, Cá Cóc biển. NXB Nông nghiệp.",
    6: "TS. Đỗ Thị Cát Tường, 2020. Atlas Cá rạn san hô Việt Nam (Tập VI). NXB Khoa học Tự nhiên và Công nghệ."
}

BOOK_SINHVATDOC_VI = "PGS.TS. Đào Việt Hà (Chủ biên), 2021. Động vật độc biển Việt Nam. NXB Khoa học Tự nhiên và Công nghệ."

print("=== DANH SÁCH 17 LOÀI CÁ BIỂN ĐỘC TRÙNG KHỚP 1-1 ===")
for idx, (sf, cb_list, m_type) in enumerate(matches, 1):
    cb_books = []
    cb_ids = []
    for c in cb_list:
        vol = c.get('volume')
        book_title = BOOK_TITLES_VI.get(vol, f"Danh mục Cá biển Việt Nam Tập {vol}")
        cb_books.append(book_title)
        cb_ids.append(f"{c['id']} (Vol {vol})")
    
    unique_books = list(dict.fromkeys(cb_books))
    all_books = unique_books + [BOOK_SINHVATDOC_VI]
    
    print(f"\n#{idx:2d}. SVD #{sf['species_index']:2d}: {sf['scientific_name']} ({sf['vn_name']})")
    print(f"    • Bản ghi ca-bien: {', '.join(cb_ids)}")
    print(f"    • Các đầu sách sẽ hợp nhất ({len(all_books)} sách):")
    for b_idx, b in enumerate(all_books, 1):
        print(f"       [{b_idx}] {b}")
