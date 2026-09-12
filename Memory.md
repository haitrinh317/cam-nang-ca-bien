# Memory — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> **Cập nhật lần cuối:** 2026-09-12 10:25 (Hoàn thành Phase 1 Rắn biển 27 loài & Phase 2 Cá biển độc 25 taxa — Hợp nhất Tri thức Đa Nguồn & Tích hợp Độc học Tetrodotoxin/Ciguatera)
> **Production URL:** https://www.tracuusinhvatbien.app / https://cam-nang-ca-bien.vercel.app
> **Dev:** `npm run dev` → localhost:3000
> **Single Source of Truth:** ⚡ **Supabase PostgreSQL** — species.json là backup local cũ, KHÔNG phải nguồn chính.

---

## 📊 Kiểm Kê Dữ Liệu (Supabase — 2026-09-12)

### Tổng: 2,787 loài (1,764 cá biển + 672 thực vật biển + 132 giáp xác + 27 rắn biển + 76 động vật độc biển + 74 thân mềm + 42 san hô)

| Collection | Tập | Loài | WoRMS | Biology / Morphology | Trạng thái |
|---|:---:|:---:|:---:|:---:|---|
| `ca-bien` | I | 100 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | II | 266 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | III | 518 | 100% | 100% | ✅ Hoàn chỉnh + Hợp nhất Ciguatera (*Lutjanus bohar*) |
| `ca-bien` | IV | 338 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | V | 279 | 100% | 100% | ✅ Hoàn chỉnh + Hợp nhất 16 loài Cá nóc độc (Tập V) |
| `ca-bien` | VI (Atlas) | 263 | 100% | 100% | ✅ 98.5% ảnh iNat + Hợp nhất 5 loài Cá nóc độc (Tập VI) |
| `thuc-vat-bien` | 1 (Tsutsui) | 201 | 100% | 100% | ✅ Hoàn chỉnh |
| `thuc-vat-bien` | 2 (PHH 1969) | 471 | 100% | 100% | ✅ 471 ảnh tiêu bản 300 DPI |
| `giap-xac` | 1 (ĐVC: Tôm biển) | 132 | 100% | 99.2% | ✅ 100% OCR + WoRMS + 99.2% SeaLifeBase + 40.2% ảnh iNat |
| `ran-bien` | 1 (Rắn biển VN) | 27 | 100% | 100% | ✅ 100% Hợp nhất Tri thức Đa Nguồn (23 loài SVD) + 100% Độc học lâm sàng PIB + 52 ảnh |
| `sinh-vat-doc` | Chuyên khảo (2021) | 76 | 100% | 100% | ✅ 100% OCR + WoRMS + 100% Toxicology + 100% Ảnh thực địa sách + 100% FishBase/SeaLifeBase + 100% Song ngữ EN |
| `than-mem` | 1 (Hylleberg 2003) | 74 | 100% | 100% | ✅ Pilot Họ Ốc sứ: 100% WoRMS + 100% SeaLifeBase + 210 ảnh WebP Storage + 79.7% tên VN |
| `san-ho` | Chuyên khảo (TS. Bền) | 42 | 97.6% (41/42) | 97.6% (41/42) | ✅ 100% OCR + 100% WoRMS (loài 30 khuyết trang 102) + 16 SeaLifeBase + 24 ảnh WebP Storage |

---

## 🏗️ Tech Stack & Kiến Trúc

```
Next.js 16 (App Router) + React 19 + TypeScript
Supabase (PostgreSQL + RLS + Auth + Storage)
CSS: Vanilla CSS (styles/tokens.css + styles/globals.css + styles/admin.css)
Deploy: git push origin master + vercel --prod --yes
```

### Routes chính

| Route | Chức năng |
|---|---|
| `/` | Landing + GlobalSearch + Literature cards |
| `/:collection` | Duyệt theo đầu sách, Compact List View |
| `/:collection/taxonomy` | Cây phân loại |
| `/:collection/:speciesId` | Chi tiết loài (ISR 24h) |
| `/admin` | Dashboard stats |
| `/admin/:collection` | CRUD loài |
| `/admin/literature` | CRUD tài liệu gốc |
| `/login` | Supabase Auth |
| `/api/species` | REST API (role-check) |
| `/api/revalidate-home` | Flush ISR cache trang chủ khi Admin chỉnh `literature_sources` |

### Supabase DB Tables

| Table | Mô tả |
|---|---|
| `species` | 2,787 loài, `collection_id` FK, flat schema |
| `species_photos` | Ảnh loài (Supabase Storage bucket `species-photos`) |
| `collections` | Registry: `ca-bien`, `thuc-vat-bien`, `giap-xac`, `ran-bien`, `sinh-vat-doc`, `than-mem`, `san-ho` |
| `literature_sources` | Sách tham khảo hiển thị trên homepage (CRUD từ admin) |
| `user_roles` | admin/editor/viewer — `haitrinh082@gmail.com` = admin |
| `audit_log` | Nhật ký thay đổi (jsonb old/new) |

### Migrations đã chạy

001 (collections) → 002 (collection_id) → 003 (user_roles) → 004 (profiles) → 005 (search indexes) → 006 (species_photos) → 007 (trigram) → 008 (literature_sources) → 008b (fix RLS recursion) → 009 (fix security: is_admin() DEFINER + audit_log RLS)

---

## 📂 Cấu trúc thư mục

```
OCR Document/                         ← Next.js project root
├── app/
│   ├── (public)/                     ← Trang công khai
│   │   ├── page.tsx                  ← Landing + Search + Literature
│   │   └── [collection]/             ← Grid + Taxonomy + Detail
│   ├── (admin)/admin/                ← Dashboard + CRUD + Literature
│   ├── (auth)/login/                 ← Supabase Auth
│   ├── api/species/                  ← REST API + Import + Photo
│   └── sitemap.ts, robots.ts        ← SEO
├── components/
│   ├── admin/    (SpeciesTable, SpeciesForm, ImportModal, AuditLog, PhotoManager)
│   ├── browse/   (SpeciesGrid, TaxonomyTree)
│   ├── home/     (LiteratureSection)
│   ├── layout/   (Nav, Footer, AdminSidebar, AuthStatus)
│   ├── search/   (GlobalSearch)
│   └── species/  (SpecimenCard, PhotoGallery)
├── lib/          (supabase-browser/server, collections, i18n, theme)
├── styles/
│   ├── tokens.css                    ← Design tokens (OKLCH)
│   ├── globals.css                   ← Public CSS (~3,800 dòng)
│   └── admin.css                     ← Admin CSS (~900 dòng, lazy loaded)
├── locales/vi.json, en.json
├── middleware.ts                     ← Auth guard /admin/*
├── scripts/                          ← OCR + enrichment (active)
│   └── archive/                      ← Scripts one-shot đã dùng xong
├── migrations/                       ← SQL 001-008b
├── data/                             ← Backup local (KHÔNG phải SSOT)
└── .agents/                          ← AI skills + memory
```

---

## 🔧 Pipelines

### OCR → Supabase
```
PDF → scripts/pdf_to_images.py → PNG → AI Vision → JSON → upsert Supabase
```
Skill hiện tại: `ocr-sinhvat-bien` v3.0 (thay thế `ocr-pdf-cabien` deprecated)

### Deploy
```
git add -A && git commit -m "..." && git push origin master
vercel --prod --yes
```
Skill: `deploy-cabien` — xác nhận account trước khi deploy.

---

## 🔐 Bảo mật

- RLS: write locked cho `service_role` + authenticated admin
- `is_admin()`: SECURITY DEFINER function — bypass RLS trên `user_roles`, dùng trong mọi policy cần check admin
- `audit_log`: RLS bật, chỉ `service_role` INSERT, chỉ admin SELECT (qua `/api/audit-log`)
- API routes: POST/PATCH/DELETE verify `user_roles.role = 'admin'` (qua `service_role` client)
- Middleware: `/admin/*` → redirect `/login`
- `.env` + `.env.local`: credentials (gitignored)

---

## ⚠️ Vercel Account (BẮT BUỘC KIỂM TRA)

| Mục | Giá trị |
|---|---|
| **Account ĐÚNG** | `haitrinh082@gmail.com` |
| **Scope/Team** | `haitrinh082-6335s-projects` |
| **Production URL** | `https://cam-nang-ca-bien.vercel.app` |
| **Account SAI** | `haitrinhnt@gmail.com` — KHÔNG DÙNG |

⚠️ GitHub push chỉ tạo **preview** deployment. Phải chạy `vercel --prod --yes` để lên production.

---

## 📝 Quy tắc quan trọng

- **SSOT**: Supabase. `species.json` là backup cũ.
- **Deploy**: Luôn `vercel --prod` sau `git push` (GitHub chỉ tạo preview)
- **alternateNames** + **commonName (EN)**: BẮT BUỘC hiển thị (dùng '—' nếu trống)
- **Thực vật biển**: dùng "Chi" thay cho "Giống" (taxonomy)
- **OCR**: KHÔNG báo tiến độ ảo — chỉ báo khi đã upsert thành công
- **RLS gotcha**: KHÔNG reference bảng có RLS trong policy (gây infinite recursion)

---

## 📜 Decisions quan trọng còn hiệu lực

| Ngày | Quyết định |
|---|---|
| 2026-09-12 | **Hợp nhất Tri thức Đa Nguồn (Taxonomy-First / Single Source of Truth Entity)**: Thống nhất một loài chỉ có 1 hồ sơ duy nhất neo vào phân loại học; gom góp toàn bộ đầu sách ghi nhận loài vào trường `vn_literature` phân tách dấu `;` (`[1]`, `[2]`, `[3]`); tích hợp độc tố học lâm sàng (toxicology), ảnh thực địa và tên gọi khác; hoàn tất Phase 1 cho 27 loài rắn biển. |
| 2026-08-22 | **Supabase = SSOT** (species.json deprecated) |
| 2026-08-20 | Next.js 16 migration, deploy Vercel |
| 2026-08-20 | Rong biển schema khác cá: morphology, photo_place/depth/date |
| 2026-08-19 | Hallmark Redesign, Lora font (Vietnamese subset) |
| 2026-09-03 | Skill `algaebase-sync` cho thực vật biển |
| 2026-09-04 | `literature_sources` DB table — quản lý sách từ admin |
| 2026-09-04 | Deploy: `vercel --prod` bắt buộc (GitHub chỉ preview) |
| 2026-09-04 | SEO & Social Thumbnail: `favicon.ico`, `og-default.png` (1200x630), dynamic species OG photo từ Supabase Storage, Schema.org Taxon/WebSite |
| 2026-09-04 | PWA: tên app `SVBVN` (`site.webmanifest`), `PwaInstallPrompt` modal hướng dẫn cài app iOS/Android cho khách mới |
| 2026-09-04 | Typography: Self-hosted `next/font/google` (Lora, Be Vietnam Pro, JetBrains Mono), xóa @import CDN, fallback Segoe UI / Be Vietnam Pro tránh vỡ dấu tiếng Việt |
| 2026-09-05 | **4 Chuyên đề Sinh thái & Bảo tồn** (San hô, Nguy cấp IUCN, Cá sụn, Thực vật biển) kết nối dữ liệu Supabase thật; IUCN Badge SSOT (`IucnBadge.tsx`) |
| 2026-09-05 | **Infographics Sinh học Thích ứng** (`SpecimenVisualWidgets.tsx`): Thước đo chiều dài tự nhận diện mm/cm/m, thang đo co giãn 0-40cm/0-1m/0-5m+ so sánh Bàn tay |
| 2026-09-05 | **Refactor Module Sâu**: `lib/taxonomy.ts` (xóa 42 dòng trùng lặp), `lib/species-query.ts`, `lib/species-photos.ts`, gộp `collections-static.ts` |
| 2026-09-05 | **Chuẩn hóa Bento Tab Thông số & /hallmark Header**: Tên Chi + Loài bắt buộc in nghiêng (*Italics*), tác giả đứng thẳng (ICZN/ICN); WoRMS badge dạng Pill 24px thanh mảnh (`.worms-pill`); Ưu tiên 100% dữ liệu gốc OCR, loại bỏ tiếng Anh/dịch thô khỏi tab Thông số. |
| 2026-09-08 | **Nhóm Giáp xác biển (`giap-xac`) — 132 loài**: Động vật chí VN Tập 1 (GS. Nguyễn Văn Chung et al., 2000), 100% WoRMS, 99.2% SeaLifeBase sinh học song ngữ, 148 ảnh iNaturalist Research Grade. |
| 2026-09-08 | **Nhóm Rắn biển Việt Nam (`ran-bien`) — 27 loài**: Chuyên khảo Viện Hải dương học - WAR - IOC VN (2016), 100% WoRMS, 100% SeaLifeBase, 92.6% ảnh minh họa (22 ảnh mẫu vật sách gốc + iNaturalist). |
| 2026-09-08 | **Tái cấu trúc Nhận diện Thương hiệu Cá nhân (`haitrinh`)**: Tên dự án: "Tra cứu thông tin Sinh Vật Biển Việt Nam", phát triển bởi `haitrinh`. Gỡ bỏ 100% thông tin cơ quan nhà nước; Schema Graph `websiteSchema` chuyển sang thực thể `Person` (`haitrinh`). |
| 2026-09-08 | **BottomNav Mobile Drawer**: Giữ 4 tabs chuẩn công thái học, tích hợp Bottom Sheet Drawer (`backdrop-filter: blur(32px)`) cho tab thứ 4 mở rộng toàn bộ các nhóm sinh vật biển hiện có và tương lai. |
| 2026-09-08 | **Quản trị đa Collection (Admin)**: Mở rộng AdminSidebar, Dashboard KPI đếm 4 collection tổng 2.595 loài; tự động ẩn bộ lọc tập cho các nhóm chỉ có 1 tập chuyên khảo. |
| 2026-09-08 | **Fix Rò Rỉ Mobile Drawer & Chuẩn Hóa SEO Login/Admin (`haitrinh`)**: Ẩn triệt để drawer trên desktop (`display: none`); gỡ bỏ toạ độ GPS Viện Hải dương học ở login; cập nhật dynamic metadata SEO cho các trang con admin; cập nhật robots.ts disallow `/login`. |
| 2026-09-09 | **Bộ sưu tập Động vật độc biển (`sinh-vat-doc`) — 76 loài**: Chuyên khảo PGS.TS. Đào Việt Hà (2021), 100% WoRMS, 100% Ảnh thực địa sách (80 ảnh WebP), 100% Bento widget độc học y tế (`ToxicologyWidget`), 100% FishBase/SeaLifeBase song ngữ học thuật, nâng quy mô toàn hệ thống lên **2.671 loài**. |
| 2026-09-09 | **Thiết kế Ảnh OpenGraph Mới (Option 2 — Photorealistic Ocean Hero)**: Kích thước 1200x630 chuẩn 1.91:1, định vị thương hiệu cá nhân `haitrinh`, tôn vinh con số 2.671+ loài và 5 nhóm sinh vật biển, thay thế logo cũ của Viện Hải dương học. |
| 2026-09-09 | **Chuẩn hóa Hiển thị Tiếng Việt & Layout Thẻ Mẫu vật**: Loại bỏ trùng lặp widget Độc học ở tab 2; rút gọn tiêu đề chủ biên; sửa `parseLiterature` chống bẻ đôi trích dẫn đơn lẻ; kích hoạt lưới 1 cột full-width (`.specimen-vault-grid--1col`) và `text-wrap: pretty` chống từ mồ côi; chuẩn hóa 76/76 loài về chuỗi tiếng Việt phân cách dấu phẩy cho `vn_alternate_names`. |
| 2026-09-09 | **Triệt tiêu từ mồ côi & ngắt dòng sớm Thẻ đầu sách gốc**: Gỡ bỏ giới hạn `p { max-width: 68ch }` trên `.book-card p` trong `book-browser.css` và `globals.css`; bổ sung `max-width: none; text-wrap: pretty; line-height: 1.55;` cho `.bc-desc` và `text-wrap: balance` cho `.bc-title`, giúp đoạn mô tả sách giãn đều tự nhiên và không bao giờ rớt từ mồ côi. |
| 2026-09-09 | **Fix lỗi 'Dữ liệu không hợp lệ' khi lưu sửa loài Admin**: Đảo ngược logic `if (id) delete payload.id` trong `SpeciesForm.tsx`; phòng thủ xóa `body.id` trong route `PATCH`; bổ sung `deleted_at` và cho phép trường `id` tùy chọn trong `speciesUpdateSchema`. |
| 2026-09-09 | **Thiết kế & Triển khai Logo Mới Phương Án 1 (Modern Ocean Wave & Whale Tail)**: Thay thế hoàn toàn logo Viện Hải dương học cũ; tách nền trong suốt chuẩn RGBA 512×512, bộ app icon PWA (192, 512px) và Favicon đa kích cỡ; đồng bộ hiệu ứng glow cyan trên Header Navbar và Chân trang Footer. |
| 2026-09-09 | **Nâng Cấp Bộ Soạn Thảo Phân Bố Loài & Chuẩn Hóa Schema Zod Frontend - Backend**: Tách 2 ô trực quan (Việt Nam & Thế giới) trong `SpeciesForm.tsx` (`DistributionEditor.tsx`), Live Preview thời gian thực; sửa lỗi bóc tách ở `SpecimenVisualWidgets.tsx` không gán nhầm sang Thế giới; bảo toàn 100% Zod `.strict()` schema và ràng buộc `<= 2000` ký tự. |

---

## 🛣️ Ràng buộc kỹ thuật

- Next.js 16 App Router + React 19 + TypeScript
- Supabase (Backend & Auth & Storage)
- Tailwind **KHÔNG DÙNG** (Vanilla CSS only)
- Deploy: `git push` + `vercel --prod --yes`
- Scripts Python: credentials từ `.env` / `os.environ`

---

## 🗺️ Knowledge Graph (`.ua/`)

| Chỉ số | Giá trị |
|---|---|
| Nodes | 405 |
| Edges | 455 |
| Layers | 8 (DB, Lib, API, Components, Pages, Scripts, Styles, Config) |
| Tour steps | 12 bước (tiếng Việt) |
| Analyzed at | 2026-09-06 10:36 |
| Commit | `99115b9959ec8c2cd707b4be1ce75cad44359ef0` |
| Dashboard | `npm run dev --prefix .understand-anything-plugin/packages/dashboard` → port 4242 |

**Ghi chú incremental update:** Lần sau chạy `/understand` sẽ detect tự động files thay đổi kể từ commit `99115b9` và chỉ re-analyze những files đó (nhanh hơn nhiều).
