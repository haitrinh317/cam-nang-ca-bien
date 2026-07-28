# Memory — OCR Cá biển Việt Nam

> Cập nhật lần cuối: 2026-07-27 16:21
> Production URL: https://cam-nang-ca-bien.vercel.app

## Kiến trúc Web App (v2 — hiện tại)

### 4 file HTML + shared assets
| File | Data source | Chức năng |
|---|---|---|
| `index.html` | `data/species.json` | Trang chủ + tìm kiếm Fuse.js + Hero Stats |
| `tap.html` | `data/species.json` | Duyệt loài theo Tập (filter `volume`) |
| `browse.html` | `data/taxonomy_tree.json` | Cây phân loại: Lớp > Bộ > Họ > Giống > Loài |
| `species.html` | `data/species.json` + `data/fishbase_sync.json` | Chi tiết loài |
| `assets/shared.css` | — | CSS toàn cục + back-to-top styles |
| `assets/shared.js` | — | Back-to-top button injection |

### Volume Color System
| Tập | Hex | CSS var |
|-----|-----|---------|
| 1 | #818cf8 (indigo) | `--vol-color` via `.vol-1` |
| 2 | #34d399 (emerald) | `.vol-2` |
| 3 | #f87171 (rose) | `.vol-3` |
| 4 | #fbbf24 (amber) | `.vol-4` |
| 5 | #60a5fa (blue) | `.vol-5` |

### Schema chuẩn `species.json`
```json
{
  "id": "tap4-species-82",
  "volume": 4,
  "speciesIndex": 82,
  "vnName": "Cá Mó đen",
  "scientificName": "Scarus niger",
  "authorship": "Forskal, 1775",
  "status": "common",
  "taxonomy": {
    "order":  { "vn": "Cá Vược", "latin": "PERCIFORMES" },
    "family": { "vn": "Họ Cá Mó", "latin": "SCARIDAE" },
    "genus":  { "vn": "Giống Cá Mó Scarus Forskal, 1775", "latin": "Scarus" }
  },
  "specs": {
    "vn": {
      "alternateNames": "",
      "size": "Kích thước: ...",
      "distribution": "Phân bố: ...",
      "specimen": "Nơi lưu trữ mẫu: ...",
      "status": "Tình trạng: ...",
      "literature": "Tài liệu dẫn: ..."
    },
    "en": {
      "commonName": "Black parrotfish",
      "size": "Size: ...",
      "distribution": "Distribution: ...",
      "specimen": "Conservation: ...",
      "status": "Status: ...",
      "literature": "Literature: ..."
    }
  },
  "synonyms": ["Scarus niger Forskal, ..."]
}
```

### Build pipeline
```
scratch/tap3_parsed_details.json  ─┐
scratch/tap4_parsed_details.json  ─┼─> scripts/build_database.py ─> data/species.json
scratch/tap5_parsed_details.json  ─┘                              ─> data/taxonomy_tree.json
```

### Enrichment pipeline
```
data/species.json → scripts/enrich_names.py --volume X → Wikidata (commonName EN + alternateNames VN)
                  → scripts/audit_species.py --volume X --fix → OCR batch restore + mirror VN→EN
```
Skills: `enrich-cabien` (tên gọi) + `audit-cabien` (data quality)

## Dữ liệu nguồn

| Tập | File nguồn | Số loài | Trạng thái |
|---|---|---|---|
| I | `data/species.json` (volume=1) | 101 | ✅ Hoàn chỉnh nhất |
| II | `data/species.json` (volume=2) | 266 | ✅ Enriched: EN 232/266, VN 240/266 |
| III | `data/species.json` (volume=3) | 518 | ⚠️ EN 100%, VN 47%, 60 skeleton cần FishBase |
| IV | `scratch/tap4_parsed_details.json` (list) | 316 | ⚠️ Loài 1-100 chuẩn, 101-316 còn thô |
| V | `scratch/tap5_parsed_details.json` (list) | 199 | ⚠️ OCR thô, tên VN lỗi |

## Taxonomy Tree
- **3 lớp**: Cá Sụn (93 loài, 6 bộ) · Cá Lưỡng Tiêm (1) · Cá Xương (1.107, 21 bộ)
- Mapping order → class: hardcoded trong `scripts/build_taxonomy_tree.py` (line 60-74)
- **Quan trọng**: Phải rebuild tree sau mỗi lần thêm/sửa loài: `python scripts/build_taxonomy_tree.py`

## Quy trình OCR thủ công (Tập IV)
1. Script `scripts/ocr_tap4_species_61_100.py` chạy EasyOCR → `tap4_parsed_details.json` (thô)
2. Tạo patch script `scratch/patch_parsed_XX_YY.py` sửa tên VN, taxonomy, synonyms
3. Chạy patch → cập nhật `tap4_parsed_details.json`
4. Chạy `scripts/build_database.py` → cập nhật `data/species.json`
5. Chạy `scripts/build_taxonomy_tree.py` → cập nhật `data/taxonomy_tree.json`
6. Copy files sang `public/` → deploy

## Quy tắc quan trọng
- **Tên gọi khác (alternateNames)** là trường BẮT BUỘC — UI luôn hiển thị hàng này (dùng '—' nếu trống)
- **Common Name (EN)** — tương tự, luôn hiển thị
- **Encoding**: luôn dùng `sys.stdout.reconfigure(encoding='utf-8')` trong mọi script Python trên Windows
- **Không dùng Gemini API** cho OCR, chỉ EasyOCR offline + sửa thủ công
- **Template species.html**: luôn hiển thị 12 trường (6 VN + 6 EN), dùng '—' cho null
- **Không dùng PSV** nữa — toàn bộ tập trung vào parsed JSON
- **Không dùng tap-N.html** nữa — web app chỉ có 4 file HTML + shared assets
- **Sync public/**: Sau mỗi thay đổi HTML/CSS/JS, phải copy sang `public/` trước khi deploy

## Deploy
- Platform: Vercel CLI (`vercel --prod --yes` từ root dự án)
- GitHub: `https://github.com/haitrinh317/cam-nang-ca-bien` (branch: master)
- Workflow: git push (version history) + vercel --prod (CDN) — cả 2 mỗi lần
- Production URL: https://cam-nang-ca-bien.vercel.app
- **CSS versioning**: Dùng `?v=N` trong link CSS để bust CDN cache khi CSS thay đổi (hiện tại: `?v=2`)
- **Lưu ý**: Vercel CDN cache static assets aggressive — sau deploy phải fetch trực tiếp URL để verify nội dung mới đã lên
- **PowerShell encoding**: PHẢI dùng `[System.IO.File]::ReadAllText/WriteAllText` với `UTF8` — KHÔNG dùng `Get-Content | Set-Content` (mangle UTF-8)

## Decisions
- 2026-07-24: Volume color system (5 màu cố định) — dùng CSS custom properties
- 2026-07-24: `shared.js` inject back-to-top — không copy-paste HTML
- 2026-07-24: `build_taxonomy_tree.py` dùng `.get()` cho optional fields
- 2026-07-24: Tập I hoàn chỉnh nhất, II-V badge "Đang cập nhật"
- 2026-07-24: Chuyển hoàn toàn sang kiến trúc 4-HTML + species.json. Bỏ legacy tap-N.html và PSV.
- 2026-07-23: Quy trình OCR: EasyOCR → patch thủ công → build_database.py
- 2026-07-23: alternateNames là trường bắt buộc
- 2026-07-24 chiều: Mobile logo dùng 2 span `.logo-full`/`.logo-short` toggle CSS (không dùng `::after` trick — conflict webkit-text-fill-color)
- 2026-07-24 chiều: Vercel CLI deploy (không có GitHub auto-trigger) — phải chạy cả `git push` + `vercel --prod`
- 2026-07-24 chiều: Skill `deploy-cabien` tự động hóa toàn bộ quy trình deploy
- 2026-07-24 tối: Vercel CDN cache static assets — dùng `?v=N` query string để bust cache sau mỗi lần thay CSS/JS
- 2026-07-24 tối: PowerShell encoding — PHẢI dùng `[System.IO.File]::ReadAllText/WriteAllText` với UTF8 explicit
- 2026-07-27: Tách enrichment thành skill riêng `enrich-cabien` — dễ gọi lại bất kỳ lúc nào
- 2026-07-27: Tạo skill `audit-cabien` — kiểm tra data quality + auto-fix từ OCR batch + mirror VN→EN
- 2026-07-27: Template species.html luôn hiển thị 12 trường — không ẩn khi null
- 2026-07-27: Wikidata không phải nguồn tốt cho alternateNames cá biển VN (47% có = đúng bản chất sách)
