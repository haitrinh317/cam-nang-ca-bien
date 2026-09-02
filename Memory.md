# Memory — Cẩm Nang Sinh Vật Biển Việt Nam

> **Cập nhật lần cuối:** 2026-08-24 21:20 (session-end phiên tối)
> **Giai đoạn hiện tại:** Tập VI online ✅ — Chuẩn bị Phase 3 (Admin CRUD + Register + CSV Import).
> **Single Source of Truth:** ⚡ **Supabase PostgreSQL** — species.json là backup local, KHÔNG phải nguồn chính.
> **Production URL:** https://cam-nang-ca-bien.vercel.app/
> **Dev**: `npm run dev` từ root → localhost:3000
> **Vercel Dashboard:** https://vercel.com/haitrinh082-6335s-projects/cam-nang-ca-bien

---

## ⚡ Source of Truth

> **Supabase** là nguồn dữ liệu DUY NHẤT cho toàn bộ dự án.
>
> - Frontend (Next.js) fetch trực tiếp từ Supabase
> - Admin Panel CRUD ghi/đọc Supabase
> - OCR pipeline upsert thẳng vào Supabase
> - `species.json` (local) là file backup cũ — KHÔNG đồng bộ realtime, KHÔNG dùng để build
> - `fishbase_sync.json` — deprecated, WoRMS data nằm trong bảng `species` (cột worms_*)

---

## 📊 Kiểm Kê Dữ Liệu (từ Supabase — 2026-09-02)

### Collection: Cá biển (`ca-bien`) — 1,765 loài

| Tập      | Số loài | Trạng thái                                                                                            |
| -------- | --------- | ------------------------------------------------------------------------------------------------------- |
| I        | 100       | ✅ Hoàn chỉnh                                                                                         |
| II       | 266       | ✅ Hoàn chỉnh                                                                                         |
| III      | 518       | ✅ Hoàn chỉnh                                                                                         |
| IV       | 339       | ⚠️ Có loài 78 đang giữ chỗ `[THIẾU DATA — cần OCR lại]`                                                |
| V        | 279       | ✅ Hoàn chỉnh                                                                                         |
| **VI (Atlas)** | **263** | ✅ **Hoàn chỉnh** (Atlas cá rạn san hô Việt Nam — 2026-08-24)                              |

### Collection: Thực vật biển (`thuc-vat-bien`) — 201 loài

| Tập | Số loài | Trạng thái    |
| ---- | --------- | --------------- |
| 1    | 201       | ✅ Hoàn chỉnh |

### Tổng: **1,966 loài** trong Supabase (đã dọn sạch orphan volume=0)
- **Độ phủ tên tiếng Anh (`en_common_name`)**: 1,764 / 1,765 loài (99.9% — 100% loài hợp lệ)
- **Độ phủ tên gọi khác tiếng Việt (`vn_alternate_names`)**: 1,764 / 1,765 loài (99.9% — 100% loài hợp lệ)
- **Toàn bộ 6 Tập Cá biển (I, II, III, IV, V, VI)**: Đạt **100.0%** trọn vẹn ở cả hai trường `vn_alternate_names` và `en_common_name` (1,764/1,765 loài hợp lệ, loài 78 Tập IV chờ OCR trang sách gốc).

---

## 🏗️ Kiến Trúc Web App (Next.js 16 App Router)

### Tech Stack

```
Next.js 16 (App Router) + React 19 + TypeScript
Supabase (PostgreSQL + Auth + Storage)
Vanilla CSS (tokens.css + globals.css)
Deploy: Vercel CLI + GitHub (branch: master)
```

### Routes

| Route                    | Component                                          | Chức năng                                |
| ------------------------ | -------------------------------------------------- | ------------------------------------------ |
| `/`                    | `app/(public)/page.tsx`                          | Landing + GlobalSearch + Collection cards  |
| `/ca-bien`             | `app/(public)/[collection]/page.tsx`             | Duyệt theo Tập                           |
| `/ca-bien/taxonomy`    | `app/(public)/[collection]/taxonomy/page.tsx`    | Cây phân loại                           |
| `/ca-bien/[speciesId]` | `app/(public)/[collection]/[speciesId]/page.tsx` | Chi tiết loài                            |
| `/admin`               | `app/(admin)/admin/page.tsx`                     | Dashboard stats + audit log                |
| `/admin/ca-bien`       | `app/(admin)/admin/[collection]/page.tsx`        | CRUD loài                                 |
| `/login`               | `app/(auth)/login/page.tsx`                      | Supabase Auth                              |
| `/api/species`         | `app/api/species/route.ts`                       | GET/POST/PATCH/DELETE + role check + audit |
| `/api/species/import`  | `app/api/species/import/route.ts`                | POST bulk upsert JSON                      |
| `/sitemap.xml`         | `app/sitemap.ts`                                 | Dynamic sitemap                            |

### Middleware: bảo vệ `/admin/*` → redirect `/login?next=`

### Supabase DB Tables

| Table           | Mô tả                                                            |
| --------------- | ------------------------------------------------------------------ |
| `species`     | ~1,719 loài (cá biển + thực vật biển),`collection_id` FK   |
| `collections` | registry:`ca-bien`, `thuc-vat-bien` (active)                   |
| `user_roles`  | admin/editor/viewer —`haitrinh082@gmail.com` = admin            |
| `audit_log`   | Nhật ký thay đổi: ai sửa gì, lúc nào, old/new data (jsonb) |

### Admin Panel Components

| Component        | File                                  | Chức năng                                |
| ---------------- | ------------------------------------- | ------------------------------------------ |
| `SpeciesTable` | `components/admin/SpeciesTable.tsx` | Bảng CRUD + tìm kiếm + phân trang      |
| `SpeciesForm`  | `components/admin/SpeciesForm.tsx`  | Modal 4 tab: Cơ bản, Phân loại, VN, EN |
| `ImportModal`  | `components/admin/ImportModal.tsx`  | Upload JSON → preview → bulk upsert      |
| `AuditLog`     | `components/admin/AuditLog.tsx`     | Bảng nhật ký thay đổi                 |
| `PhotoManager` | `components/admin/PhotoManager.tsx` | Upload/xóa/preview ảnh loài             |

### Admin Panel Progress

- ✅ Phase 1: Vá RLS — chỉ service_role/admin write
- ✅ Phase 2: Dashboard (thống kê tổng/cá/thực vật, breakdown tập)
- ✅ Phase 3: Import JSON hàng loạt
- ✅ Phase 4: Quản lý ảnh loài (Supabase Storage bucket `species-photos`)
- ✅ Phase 5: Audit Log (bảng DB + component + API ghi log)
- ✅ Phase 6: API route role-check (POST/PATCH/DELETE verify admin role)
- ⚠️ Chưa: soft-delete, inline edit, CSV import

---

## 📂 Cấu trúc thư mục

```
OCR Document/                         ← Next.js project root
├── app/                              ← Next.js App Router
│   ├── (public)/                     ← Public pages
│   │   ├── page.tsx                  ← Landing + Search
│   │   └── [collection]/             ← Grid + Taxonomy + Detail
│   ├── (admin)/admin/                ← Admin dashboard + CRUD
│   ├── (auth)/login/                 ← Supabase Auth
│   ├── api/species/                  ← REST API + Import
│   ├── sitemap.ts, robots.ts        ← SEO
│   └── not-found.tsx
├── components/                       ← React components
│   ├── admin/    (SpeciesTable, SpeciesForm, ImportModal, AuditLog, PhotoManager)
│   ├── browse/   (SpeciesGrid, TaxonomyTree)
│   ├── layout/   (Nav, Footer, AuthStatus, HeaderControls, ThemeScript)
│   ├── search/   (GlobalSearch)
│   └── species/  (SpecimenCard)
├── lib/                              ← Utilities
│   ├── supabase-browser.ts, supabase-server.ts
│   ├── i18n.ts, theme.ts, collections.ts
├── styles/
│   ├── tokens.css                    ← Design tokens
│   └── globals.css                   ← Full CSS
├── locales/vi.json, en.json          ← i18n
├── middleware.ts                     ← Auth guard /admin/*
├── next.config.ts, tsconfig.json     ← Next.js config
├── data/                             ← Local data (backup, not source of truth)
│   ├── species.json      (backup — stale, chỉ 1279 loài)
│   ├── taxonomy_tree.json
│   ├── fishbase_sync.json (deprecated)
│   ├── parsed/            ← OCR parsed sources
│   └── raw/               ← PDF nguồn gốc (gitignored)
├── scripts/               ← Pipeline scripts
├── migrations/            ← SQL migrations (001-004)
├── .agents/               ← AI skills
├── Memory.md, todo.md
```

---

## 🔧 Pipelines

### OCR pipeline

```
PDF → scripts/pdf_to_images.py → PNG → view_file (AI Vision) → JSON
→ Chuẩn hóa → WoRMS verify → scripts/upsert_species.py → Supabase
```

Skill: `ocr-pdf-cabien` v2.0

### Enrichment pipeline

```
Supabase → scripts/enrich_names.py → Wikidata (commonName EN + alternateNames VN)
         → scripts/audit_species.py → data quality fix
         → scripts/sync_fishbase_biology.py → FishBase/GBIF biology
         → scripts/sync_taxonomy_worms.py → WoRMS taxonomy
```

### Deploy pipeline

```
git push (GitHub) + vercel --prod (CDN)
```

---

## 📋 Schema chuẩn Supabase (flat)

| Column                                              | Type     | Ghi chú                                               |
| --------------------------------------------------- | -------- | ------------------------------------------------------ |
| `id`                                              | text PK  | `tap{vol}-species-{N}` hoặc `thucvat-species-{N}` |
| `collection_id`                                   | text FK  | `ca-bien` / `thuc-vat-bien`                        |
| `volume`                                          | int      | Tập (1-5 cho cá, 1 cho thực vật)                   |
| `species_index`                                   | int      | STT trong tập                                         |
| `vn_name`                                         | text     | Tên Việt Nam                                         |
| `scientific_name`                                 | text     | Tên khoa học                                         |
| `authorship`                                      | text     | Tác giả + năm                                       |
| `en_common_name`                                  | text     | Tên tiếng Anh                                        |
| `vn_alternate_names`                              | text     | Tên gọi khác                                        |
| `tax_class_vn/latin`                              | text     | Lớp                                                   |
| `tax_order_vn/latin`                              | text     | Bộ                                                    |
| `tax_family_vn/latin`                             | text     | Họ                                                    |
| `tax_genus_vn/latin`                              | text     | Chi/Giống                                             |
| `vn_size/distribution/specimen/status/literature` | text     | Specs VN                                               |
| `en_size/distribution/specimen/status/literature` | text     | Specs EN                                               |
| `conservation_status`                             | text     | common/uncommon/rare/unknown                           |
| `synonyms`                                        | jsonb    | Array of synonym strings                               |
| `morphology_vn/en`                                | text     | Mô tả hình thái                                    |
| `photo_place/depth/date`                          | text     | Thông tin ảnh                                        |
| `biology`                                         | jsonb    | FishBase/GBIF enrichment data                          |
| `worms_status/accepted_name/id`                   | text/int | WoRMS validation                                       |

---

## 🔐 Bảo mật

- RLS: write locked cho `service_role` + authenticated admin only
- API routes: POST/PATCH/DELETE verify `user_roles.role = 'admin'`
- Middleware: `/admin/*` redirect → `/login`
- Scripts Python: credentials từ `.env` (SUPABASE_SERVICE_ROLE_KEY), KHÔNG hardcode

---

## ⚠️ Vercel Account (BẮT BUỘC)

| Mục                     | Giá trị                                |
| ------------------------ | ---------------------------------------- |
| **Account đúng** | `haitrinh082@gmail.com`                |
| **Scope/Team**     | `haitrinh082-6335s-projects`           |
| **Project ID**     | `prj_UAcAXHMGSOq5iOLChKBHOPoam596`     |
| **Production URL** | `https://cam-nang-ca-bien.vercel.app`  |
| **Account SAI**    | `haitrinhnt@gmail.com` — KHÔNG DÙNG |

Trước khi deploy: `vercel whoami` → xác nhận scope đúng.

---

## 📝 Quy tắc quan trọng

- **Source of Truth**: Supabase. species.json là backup.
- **alternateNames** BẮT BUỘC — UI hiển thị (dùng '—' nếu trống)
- **commonName (EN)** — tương tự
- **Encoding Python**: `sys.stdout.reconfigure(encoding='utf-8')` trên Windows
- **File Python đọc từ PowerShell**: `encoding='utf-8-sig'` để strip BOM
- **OCR thật**: KHÔNG báo cáo tiến độ ảo
- **Thực vật biển**: dùng "Chi" thay cho "Giống" (taxonomy level)
- **Rong biển schema** khác cá: có morphology_vn/en, photo_place/depth/date

---

## 📜 Decisions

| Ngày      | Quyết định                                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| 2026-07-24 | Kiến trúc 4-HTML + species.json (v1)                                                                           |
| 2026-07-24 | Volume color system (5 màu cố định)                                                                          |
| 2026-07-27 | Wikidata không phải nguồn tốt cho alternateNames cá biển VN                                                |
| 2026-07-30 | Admin Panel → Hướng 1 (Supabase Auth + Dashboard)                                                             |
| 2026-07-30 | OCR skill v1.3.0 — dùng AI Vision built-in (view_file)                                                         |
| 2026-08-13 | PWA deploy production                                                                                            |
| 2026-08-14 | Bổ sung 1,251 loài biology (FishBase + GBIF)                                                                   |
| 2026-08-19 | Phase 3 Hallmark Redesign — full UI rewrite, Lora font                                                          |
| 2026-08-20 | Next.js 16 migration hoàn tất, deploy Vercel thành công                                                      |
| 2026-08-20 | Rong biển schema khác cá 6 điểm → mở rộng schema chung                                                   |
| 2026-08-20 | morphology + photo data = trường CHUNG cho mọi collection                                                     |
| 2026-08-22 | **Supabase = Single Source of Truth** (species.json deprecated)                                            |
| 2026-08-22 | API route: thêm role-check cho POST/PATCH/DELETE                                                                |
| 2026-08-22 | Scripts Python: chuyển key sang .env, bỏ hardcode                                                              |
| 2026-08-22 | Xóa 17 bản sao duplicate thực vật biển (idx 202-218)                                                        |
| 2026-08-22 | Bổ sung vn_name 26 loài rong biển từ PDF gốc (quy trình: chú chụp trang sách → em extract → patch DB) |
| 2026-08-22 | Các loài sách ghi "chưa có tên VN" → giữ nguyên trong DB, không bịa tên                              |
| 2026-08-23 | WoRMS link giữ nguyên mở new tab, không dùng iframe do policy `frame-ancestors` chặn                   |
| 2026-08-23 | Tạo trang `/about` dùng macrostructure Long Document của Hallmark                                      |

---

## 🛣️ Ràng buộc kỹ thuật

- Next.js 16 App Router + React 19 + TypeScript
- Supabase (Backend & Auth)
- Tailwind KHÔNG DÙNG (Vanilla CSS)
- Deploy: GitHub + Vercel (Framework Preset: Next.js)
- Scripts Python: credentials từ `.env` hoặc `os.environ`
