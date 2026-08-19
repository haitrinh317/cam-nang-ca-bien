# Memory — OCR Cá biển Việt Nam

> Cập nhật lần cuối: 2026-08-19 21:33 — Phase 3 Hallmark Redesign + nav fix + Lora font + xóa public/*.html cũ
> Production URL: https://cam-nang-ca-bien.vercel.app
> Vercel Dashboard: https://vercel.com/haitrinh082-6335s-projects/cam-nang-ca-bien

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
| `assets/logo.png` | — | Logo website |

### Volume Color System
| Tập | Hex | CSS var |
|-----|-----|---------|
| 1 | #818cf8 (indigo) | `--vol-color` via `.vol-1` |
| 2 | #34d399 (emerald) | `.vol-2` |
| 3 | #f87171 (rose) | `.vol-3` |
| 4 | #fbbf24 (amber) | `.vol-4` |
| 5 | #60a5fa (blue) | `.vol-5` |

### Schema chuẩn `species.json` (Gold Standard: `tap1-species-1`)
```json
{
  "id": "tap1-species-1",
  "volume": 1,
  "speciesIndex": 1,
  "vnName": "Cá lưỡng tiêm",
  "scientificName": "Branchiostoma belcheri",
  "authorship": "(Gray, 1847)",
  "status": "common",
  "taxonomy": {
    "order":  { "vn": "Cá Lưỡng Tiêm", "latin": "Amphioxiformes" },
    "family": { "vn": "Cá Lưỡng Tiêm", "latin": "Branchiostomidae" },
    "genus":  { "vn": "Cá lưỡng tiêm Branchiostoma Costa, 1834", "latin": "Branchiostoma Costa, 1834" }
  },
  "specs": {
    "vn": {
      "alternateNames": "Cá lưỡng tiêm",
      "size": "Thường gặp 42 - 47mm, lớn nhất 57mm.",
      "distribution": "Đông Phi, Ấn Độ, Indonesia, ..., Việt Nam. Vịnh Bắc Bộ, Trung Bộ.",
      "specimen": "Viện Hải Dương học (Nha Trang).",
      "status": "Thường gặp, nhưng số lượng ít.",
      "literature": "Chu Nguyên Đinh, 1963. Nguyễn Khắc Hường, 1992."
    },
    "en": {
      "commonName": "Lancelet",
      "size": "Ordinary 42 - 47mm, maximum 57mm.",
      "distribution": "East Africa, India, ..., Vietnam. Gulf of Tonkin, Coast of Central Vietnam.",
      "specimen": "Institute of Oceanography (Nha Trang).",
      "status": "Common, seldom abundant.",
      "literature": "Chu, 1963. Nguyen Khac Huong, 1992."
    }
  },
  "synonyms": ["Branchiostoma Costa, Cenni Zool. Napol., p. 49, 1834. ..."]
}
```

**Lưu ý schema:**
- taxonomy chỉ có 3 cấp: `order`, `family`, `genus` (KHÔNG có class/subclass/suborder)
- taxonomy.*.vn: KHÔNG có prefix "Bộ"/"Họ"/"Giống"
- taxonomy.*.latin: Title Case (KHÔNG ALL CAPS)
- specs values: KHÔNG có prefix label ("Kích thước:", "Size:")
- status chỉ nhận: `common`, `uncommon`, `rare`, `unknown`

## Cấu trúc thư mục

```
OCR Document/
├── index.html, browse.html, species.html, tap.html  ← source HTML (sửa ở đây)
├── assets/
│   ├── shared.css, shared.js                        ← source CSS/JS
│   └── logo.png
├── data/
│   ├── species.json          (2.8MB — CSDL chính)
│   ├── taxonomy_tree.json    (341KB — cây phân loại)
│   ├── fishbase_sync.json    (569KB — WoRMS validation)
│   ├── stats.json            (thống kê)
│   ├── parsed/               ← nguồn build database
│   │   ├── tap3_parsed_details.json
│   │   ├── tap4_parsed_details.json
│   │   └── tap5_parsed_details.json
│   └── raw/                  ← PDF nguồn gốc (tap1-5)
├── scripts/                  ← 6 pipeline scripts chính
│   ├── build_database.py     (build species.json)
│   ├── build_taxonomy_tree.py
│   ├── enrich_names.py       (enrichment pipeline)
│   ├── audit_species.py      (data quality)
│   ├── sync_fishbase.py      (WoRMS sync)
│   └── update_indexes.py
├── public/                   ← Vercel serve từ đây
│   ├── *.html, assets/, data/
├── Documents/                ← PDF sách gốc
├── .agents/                  ← AI skills
├── v1_backup/                ← scripts cũ, scratch, legacy HTML
├── Memory.md, todo.md
├── vercel.json, .gitignore, .vercelignore
```

### Build pipeline
```
data/parsed/tap3_parsed_details.json  ─┐
data/parsed/tap4_parsed_details.json  ─┼─> scripts/build_database.py ─> data/species.json
data/parsed/tap5_parsed_details.json  ─┘                              ─> data/taxonomy_tree.json
```

### Enrichment pipeline
```
data/species.json → scripts/enrich_names.py --volume X → Wikidata (commonName EN + alternateNames VN)
                  → scripts/audit_species.py --volume X --fix → OCR batch restore + mirror VN→EN
```
Skills: `enrich-cabien` (tên gọi) + `audit-cabien` (data quality)

### OCR pipeline
```
PDF → scripts/pdf_to_images.py → PNG → view_file (AI Vision built-in) → JSON
→ Chuẩn hóa → WoRMS verify → Merge 3 file CSDL
```
Skill: `ocr-pdf-cabien` (v1.3.0 — dùng AI Vision built-in, KHÔNG gọi API Gemini)

## Dữ liệu nguồn

| Tập | Số loài | Trạng thái |
|---|---|---|
| I | 101 | ✅ Hoàn chỉnh nhất |
| II | 266 | ✅ OCR thủ công + chuẩn hóa + upload Supabase hoàn tất (266/266) |
| III | 518 | ⚠️ EN 100%, VN 47%, 60 skeleton cần FishBase |
| IV | 316 | ⚠️ Loài 1-100 chuẩn, 101-316 còn thô |
| V | 279 | ✅ OCR thủ công + chuẩn hóa + upload Supabase hoàn tất (279/279) |

## Taxonomy Tree
- **3 lớp**: Cá Sụn (93 loài, 6 bộ) · Cá Lưỡng Tiêm (1) · Cá Xương (1.107, 21 bộ)
- Mapping order → class: hardcoded trong `scripts/build_taxonomy_tree.py`
- **Quan trọng**: Phải rebuild tree sau mỗi lần thêm/sửa loài

## Quy tắc quan trọng
- **alternateNames** là trường BẮT BUỘC — UI luôn hiển thị (dùng '—' nếu trống)
- **commonName (EN)** — tương tự, luôn hiển thị
- **Encoding**: luôn dùng `sys.stdout.reconfigure(encoding='utf-8')` trong Python trên Windows
- **Template species.html**: luôn hiển thị 12 trường (6 VN + 6 EN), dùng '—' cho null
- **Sync public/**: Sau mỗi thay đổi HTML/CSS/JS, phải copy sang `public/` trước khi deploy

## Deploy
- Platform: Vercel CLI (`vercel --prod --yes` từ root)
- GitHub: `https://github.com/haitrinh317/cam-nang-ca-bien` (branch: master)
- Workflow: git push (version history) + vercel --prod (CDN)
- **CSS versioning**: Dùng `?v=N` trong link CSS để bust CDN cache
- **PowerShell encoding**: PHẢI dùng `[System.IO.File]::ReadAllText/WriteAllText` với `UTF8`
- **Lưu ý Rollback**: Nếu đã dùng Instant Rollback trên Vercel, bản deploy mới sẽ bị ghim — phải vào dashboard Promote to Production thủ công

### ⚠️ Vercel Account (BẮT BUỘC — đã gây lỗi deploy nhầm 2026-08-13)
| Mục | Giá trị |
|---|---|
| **Account đúng** | `haitrinh082@gmail.com` |
| **Scope/Team** | `haitrinh082-6335s-projects` |
| **Project ID** | `prj_UAcAXHMGSOq5iOLChKBHOPoam596` |
| **Org/Team ID** | `team_38z7f9cGS9vAyalMqjKVPJZJ` |
| **Production URL** | `https://cam-nang-ca-bien.vercel.app` |
| **Dashboard** | `https://vercel.com/haitrinh082-6335s-projects/cam-nang-ca-bien` |
| **Account SAI** | `haitrinhnt@gmail.com` (haitrinhnt-6798s-projects) — KHÔNG DÙNG |

**Trước khi deploy, PHẢI chạy:** `vercel whoami` → xác nhận scope = `haitrinh082-6335s-projects`.
Nếu sai → `vercel logout` rồi `vercel login` lại.

### PWA
- `manifest.json`, `sw.js`, `pwa.js` đã deploy production (2026-08-13)
- SW strategy: App Shell (cache-first) + Data (stale-while-revalidate)
- Installable trên Chrome mobile/desktop

## Supabase Database (v2 — hiện tại)

### Bảng `species`
- 21+ trường: identity, taxonomy (4 cấp), specs VN/EN, WoRMS, metadata
- RLS enabled, FTS index (simple tokenizer)
- View `taxonomy_tree` thay thế taxonomy_tree.json
- Scripts: `import_to_supabase.py`, `upsert_species.py`, `build_database.py`
- Migration: `scripts/migrations/001_create_species_table.sql`

### ⚠️ Lỗ hổng RLS hiện tại
- Policy "Service write access" đang `USING (true)` — anon key ghi được
- anon key đã public trên frontend → ai cũng INSERT/UPDATE/DELETE được
- **Cần vá ngay**: lock write cho `service_role` only

### Admin Panel — Hướng 1: Supabase Auth + Admin Dashboard
**Quyết định 2026-07-30**: Đi theo Hướng 1 (Supabase Auth + Custom Admin UI), chia 3 phase:

| Phase | Nội dung | Trạng thái |
|---|---|---|
| **Phase 1** | Vá RLS — lock write cho `service_role` only | 🔲 Chưa làm |
| **Phase 2** | Supabase Auth + bảng `profiles` + `/admin.html` (CRUD, bulk import, audit log) | 🔲 Chưa làm |
| **Phase 3** | Phân quyền multi-user (editor chỉ sửa loài mình, admin toàn quyền) | 🔲 Tương lai |

## Decisions
- 2026-07-24: Volume color system (5 màu cố định) — CSS custom properties
- 2026-07-24: `shared.js` inject back-to-top — không copy-paste HTML
- 2026-07-24: Tập I hoàn chỉnh nhất, II-V badge "Đang cập nhật"
- 2026-07-24: Kiến trúc 4-HTML + species.json. Bỏ legacy tap-N.html và PSV
- 2026-07-24: Mobile logo dùng 2 span `.logo-full`/`.logo-short` toggle CSS
- 2026-07-24: Vercel CLI deploy — phải chạy cả `git push` + `vercel --prod`
- 2026-07-24: Vercel CDN cache — dùng `?v=N` query string bust cache
- 2026-07-24: PowerShell encoding — `[System.IO.File]::ReadAllText/WriteAllText` UTF8
- 2026-07-27: Skill `enrich-cabien` — enrichment tên gọi
- 2026-07-27: Skill `audit-cabien` — data quality + auto-fix
- 2026-07-27: Wikidata không phải nguồn tốt cho alternateNames cá biển VN
- 2026-07-30: Dọn dẹp project — chuyển ~400 files (52 scripts cũ + 328 scratch + data trung gian) vào v1_backup/
- 2026-07-30: Parsed details chuyển từ scratch/ sang data/parsed/ (nguồn build database)
- 2026-07-30: Skill ocr-pdf-cabien v1.3.0 — bỏ Gemini Vision API, dùng AI Vision built-in (view_file)
- 2026-07-30: Vercel Rollback ghim production — cần Promote to Production thủ công sau deploy mới
- 2026-07-30: Admin Panel → Hướng 1 (Supabase Auth + Admin Dashboard), 3 phase: vá RLS → Auth+CRUD → multi-user
- 2026-08-13: Vercel account chính xác = haitrinh082@gmail.com (scope haitrinh082-6335s-projects). Account haitrinhnt@gmail.com là SAI.
- 2026-08-13: PWA (manifest + SW + pwa.js) deploy thành công lên production
- 2026-08-13: WoRMS sync cho Tập IV loài 11-50 hoàn tất (40 loài)
- 2026-08-14: Bổ sung 1251 loài có thông tin Sinh học - Sinh thái (Habitat, IUCN, Morphological Description, Diet, Depth) từ FishBase và GBIF vào Supabase (`biology` column).
- 2026-08-19: Phase 3 Hallmark Redesign — full UI rewrite, Lora font (Vietnamese), tokens.css v3.0, shared.css audit-clean
- 2026-08-19: Root-cause fix Vite: public/*.html cũ override root files → xóa 4 HTML khỏi public/
- 2026-08-19: Nav layout 1/3–2/3 (flex:1/flex:2), đồng bộ 3 links trên 4 trang

## Upgrade Plan v3.0 — Roadmap

> Chi tiết: `implementation_plan.md` (artifact session 02b1c773)

| Phase | Mục tiêu | Trạng thái |
|-------|----------|-----------|
| **Phase 1** | Redesign UI + Song ngữ VN/EN + Light/Dark mode | 🔶 Đang làm — CSS xong, còn i18n + toggle |
| **Phase 2** | Admin Panel CRUD hoàn chỉnh (Form + Import CSV + Audit Log) | ⬜ Chưa bắt đầu |
| **Phase 3** | Supabase Auth + Phân quyền 3 role (admin/editor/viewer) | ⬜ Chưa bắt đầu |
| **Phase 4** | Polish + Mobile test + Deploy production | ⬜ Chưa bắt đầu |

### Phase 1 còn lại
- `src/lib/i18n.js` — module song ngữ nhẹ, không cần thư viện ngoài
- `locales/vi.json` + `locales/en.json` — toàn bộ label UI tĩnh
- Toggle VN/EN + light/dark trên header (lưu `localStorage`)
- Deploy Phase 1 lên Vercel sau khi i18n xong

### Ràng buộc kỹ thuật (KHÔNG thay đổi)
- Static HTML + Vanilla JS (không React/Vue)
- Vite build + Supabase backend
- Font: Be Vietnam Pro (body) + Lora (display/heading)
- Deploy: GitHub + Vercel workflow
