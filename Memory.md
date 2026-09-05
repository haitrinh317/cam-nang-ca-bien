# Memory — Cẩm Nang Sinh Vật Biển Việt Nam

> **Cập nhật lần cuối:** 2026-09-06 00:06 (Tinh chỉnh Font Danh pháp đồng nghĩa & Đồng bộ Type Scale Design System)
> **Production URL:** https://cam-nang-ca-bien.vercel.app
> **Dev:** `npm run dev` → localhost:3000
> **Single Source of Truth:** ⚡ **Supabase PostgreSQL** — species.json là backup local cũ, KHÔNG phải nguồn chính.

---

## 📊 Kiểm Kê Dữ Liệu (Supabase — 2026-09-04)

### Tổng: 2,436 loài (1,764 cá biển + 672 thực vật biển)

| Collection | Tập | Loài | WoRMS | Biology | Trạng thái |
|---|:---:|:---:|:---:|:---:|---|
| `ca-bien` | I | 100 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | II | 266 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | III | 518 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | IV | 338 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | V | 279 | 100% | 100% | ✅ Hoàn chỉnh |
| `ca-bien` | VI (Atlas) | 263 | 100% | 100% | ✅ 98.5% ảnh iNaturalist |
| `thuc-vat-bien` | 1 (Tsutsui) | 201 | 100% | 100% | ✅ Hoàn chỉnh |
| `thuc-vat-bien` | 2 (PHH 1969) | 471 | 100% | 100% | ✅ 471 ảnh tiêu bản 300 DPI |

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

### Supabase DB Tables

| Table | Mô tả |
|---|---|
| `species` | 2,436 loài, `collection_id` FK, flat schema |
| `species_photos` | Ảnh loài (Supabase Storage bucket `species-photos`) |
| `collections` | Registry: `ca-bien`, `thuc-vat-bien` |
| `literature_sources` | Sách tham khảo hiển thị trên homepage (CRUD từ admin) |
| `user_roles` | admin/editor/viewer — `haitrinh082@gmail.com` = admin |
| `audit_log` | Nhật ký thay đổi (jsonb old/new) |

### Migrations đã chạy

001 (collections) → 002 (collection_id) → 003 (user_roles) → 004 (profiles) → 005 (search indexes) → 006 (species_photos) → 007 (trigram) → 008 (literature_sources) → 008b (fix RLS recursion)

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
- API routes: POST/PATCH/DELETE verify `user_roles.role = 'admin'`
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

---

## 🛣️ Ràng buộc kỹ thuật

- Next.js 16 App Router + React 19 + TypeScript
- Supabase (Backend & Auth & Storage)
- Tailwind **KHÔNG DÙNG** (Vanilla CSS only)
- Deploy: `git push` + `vercel --prod --yes`
- Scripts Python: credentials từ `.env` / `os.environ`
