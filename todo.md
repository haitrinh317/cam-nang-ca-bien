# TODO — Dự án OCR Cá biển Việt Nam

> Cập nhật: 2026-08-19 23:43
> **Next Session Starting Point**: Next.js app đang chạy tại `localhost:3001`. Migrations 001+002+003 đã chạy xong. Admin role đã seed. Tiếp theo: OCR Tập IV (101-316), WoRMS sync Tập III.

## ✅ Migration Next.js — HOÀN THÀNH (2026-08-19)

- [x] **Phase M0** — Scaffold Next.js 16, TypeScript, Supabase clients, Nav/Footer/Layout
- [x] **Phase M1** — Port 4 trang: GlobalSearch, SpeciesGrid, TaxonomyTree, SpecimenCard
- [x] **Phase M2** — Multi-collection: DB collections table, collection_id FK, dynamic routing
- [x] **Phase M3** — Admin CRUD: API routes, SpeciesTable, SpeciesForm 4-tab, 26 trường
- [x] **Phase M4** — Auth: middleware /admin/*, Login page, Logout, AuthStatus, user_roles RLS
- [x] **Phase M5** — SEO: OG/Twitter, sitemap.xml, robots.txt, redirects, 404, PWA manifest
- [x] **SQL migrations**: 001 (collections) + 002 (collection_id) + 003 (user_roles) — đã chạy
- [x] **Admin role seed**: haitrinh082@gmail.com đã có role admin

> App: `next-app/` — `npm run dev` → localhost:3001



## ✅ Hoàn thành

### Kiến trúc Web App
- [x] Thiết kế lại kiến trúc: 4 file HTML duy nhất (`index.html`, `tap.html`, `browse.html`, `species.html`)
- [x] Tất cả dữ liệu tập trung vào `data/species.json` + `data/taxonomy_tree.json`
- [x] Xóa hoàn toàn các file static `tap-1.html` ... `tap-5.html` (legacy)
- [x] Schema thống nhất cho `species.json`: `specs.vn`, `specs.en`, `synonyms[]`
- [x] Viết lại `scripts/build_database.py` — đọc trực tiếp từ OCR parsed JSON

### OCR & Chuẩn hóa dữ liệu
- [x] Tập II: 266/266 loài (OCR thủ công + chuẩn hóa + upload Supabase hoàn tất)
- [x] Tập III: 518 loài (OCR + parse hoàn tất, `scratch/tap3_parsed_details.json`)
- [x] Tập IV loài 1-100: OCR + chuẩn hóa thủ công hoàn tất
- [x] Tập V: 199 loài (OCR thô, `scratch/tap5_parsed_details.json`)

### Tính năng Web App
- [x] Tìm kiếm Fuse.js trên trang chủ (đọc từ `species.json`)
- [x] Trang duyệt theo Tập (`tap.html`) — lọc theo `volume`
- [x] Trang cây phân loại (`browse.html`) — đọc `taxonomy_tree.json`
- [x] Trang chi tiết loài (`species.html`) — hiện thông số VN/EN + WoRMS badge

### UI/UX Redesign (2026-07-24)
- [x] PDCA GĐ4: Logo cá SVG, Hero Stats (count-up), Volume accent bars
- [x] Back-to-top button cho tất cả 4 trang (`shared.js`)
- [x] Đồng bộ UI tap.html + browse.html (fish logo, vol colors, mini card accents)
- [x] Fix browse.html thiếu Lớp Cá Sụn — rebuild `taxonomy_tree.json` (3 lớp)
- [x] Badge "Đang cập nhật" cho Tập II-V trên trang chủ
- [x] Deploy Vercel production — live tại cam-nang-ca-bien.vercel.app

### Phase 3 — Hallmark Redesign (2026-08-19)
- [x] Full redesign 4 HTML theo Hallmark macrostructures (Workbench + Catalogue + LongDocument + Marquee)
- [x] Rewrite `tokens.css` v3.0: OKLCH, Perfect-Fourth scale, 80+ tokens
- [x] Rewrite `shared.css`: 1318 lines, full audit-clean component system
- [x] Hallmark self-audit: fix 3 critical + 4 major + 4 minor anti-patterns
- [x] Font: Instrument Serif → **Lora** (full Vietnamese subset)
- [x] Nav layout: 1/3 logo | 2/3 links, same row, `flex:1`/`flex:2`
- [x] Nav đồng bộ 3 links trên tất cả 4 trang
- [x] Xóa `public/*.html` cũ (Aug 14) — root cause Vite serve wrong file

---

## 🛣️ Upgrade Plan v3.0 — 4 Phases

> Source: Implementation Plan 2026-08-19

### Phase 1 — Redesign UI + Song ngữ VN/EN
- [x] Redesign CSS: design system, tokens, Hallmark macrostructures *(done 2026-08-19)*
- [x] Font: Lora (Vietnamese subset), Be Vietnam Pro giữ nguyên *(done 2026-08-19)*
- [x] Light/dark mode toggle (`[data-theme="light"]` / `[data-theme="dark"]`) *(done 2026-08-19)*
- [x] I18n module nhẹ: `src/lib/i18n.js` + `locales/vi.json` + `locales/en.json` *(done 2026-08-19)*
- [x] Thêm toggle VN/EN trên header (lưu `localStorage`) *(done 2026-08-19)*
- [x] Dịch label UI: menu, button, placeholder, heading cho 4 trang HTML *(done 2026-08-19)*
- [x] Deploy Phase 1 lên Vercel *(done 2026-08-20 - Next.js live)*

### Phase 2 — Admin Panel CRUD hoàn chỉnh
- [ ] Modal Form CRUD loài: 21+ trường, chia tab (Chung / VN / EN / Taxonomy / Biology)
- [ ] Soft-delete: `deleted_at` thay vì xóa thật
- [ ] CSV/JSON Import: parse → preview → confirm → batch upsert Supabase
- [ ] Inline edit nhanh: double-click ô bảng → sửa tại chỗ
- [ ] Audit Log: migration `005_audit_log.sql` + trigger tự động
- [ ] Admin dashboard: thống kê nhanh (tổng loài, theo tập, loài thiếu data)
- [ ] Deploy Phase 2 lên Vercel

### Phase 3 — Phân quyền User + Đăng ký
- [ ] Enable Supabase Auth (email/password)
- [ ] Trang `register.html` hoặc modal đăng ký (role mặc định: `viewer`)
- [ ] Trigger auto-assign role `viewer` khi user mới đăng ký
- [ ] Header auth state: đã login hiện tên + "Đăng xuất" / chưa login hiện "Login"
- [ ] Admin: nâng cấp role viewer → editor từ admin panel
- [ ] RLS 3 role: admin (toàn quyền), editor (sửa loài), viewer (chỉ xem)
- [ ] Deploy Phase 3

### Phase 4 — Polish + Deploy Production
- [ ] Test mobile: iOS Safari, Android Chrome
- [ ] Test phân quyền: viewer/editor/admin
- [ ] Test CSV import với file thực tế
- [ ] Lazy load Supabase client + Vite code splitting
- [ ] PWA cache strategy review
- [ ] Final deploy Vercel + smoke test production URL

### Mobile UI Overhaul (2026-07-24 chiều)
- [x] Audit + fix 6 lỗi mobile: header stack, logo overflow, nav wrap, card padding, panel separator, fb-link
- [x] Fix logo mobile: `.logo-full` / `.logo-short` 2 span toggle CSS
- [x] Fix taxonomy badge: word-break + flex-wrap + max-width
- [x] Tạo skill `deploy-cabien` (sync + git push + vercel CLI)
- [x] Setup git repo + .gitignore + vercel.json cho project

### Enrichment & Data Quality (2026-07-27)
- [x] Tạo skill `enrich-cabien` — tách từ ocr-pdf-cabien, script `enrich_names.py`
- [x] Tạo skill `audit-cabien` — kiểm tra + auto-fix data quality, script `audit_species.py`
- [x] Fix 12 loài đầu Tập III (Cá Chẽm) — patch từ OCR batch sạch
- [x] Enrichment commonName EN Tập III: 518/518 (100%)
- [x] Enrichment alternateNames VN Tập III: 246/518 (47% — đúng bản chất sách)
- [x] Sửa template species.html: luôn hiển thị 12 trường (dùng '—' cho null)
- [x] Audit + fix Tập III: OCR batch restore (97 fields) + mirror VN→EN (609 fields)
- [x] Restore skeleton bằng scientificName match: 72 loài, 255 fields + 588 mirror
- [x] Deploy Vercel: commit 4fd23ff

## 🔲 Chưa làm

### OCR còn thiếu
- [ ] Tập IV loài 101-316: cần OCR + chuẩn hóa thủ công
- [x] Tập V: dữ liệu thô chưa được chuẩn hóa (tên VN bị lỗi, taxonomy trống) -> Đã hoàn thành (279/279 loài chuẩn hóa và đưa lên Supabase)
- [ ] Tập I: chưa có dữ liệu OCR parsed JSON (chỉ có PSV cũ cho 50 loài Tập I)

### Chất lượng dữ liệu
- [x] `commonName` (EN) — Tập II: 232/266, Tập III: 518/518 ✅
- [x] `alternateNames` (VN) — Tập II: 240/266, Tập III: 246/518 (đúng bản chất)
- [x] Tập III — đã re-OCR toàn bộ 518 loài cực kỳ chuẩn xác và đưa lên Supabase (2026-08-04)
- [x] Deploy bản Next.js mới nhất lên Vercel (Hoàn tất 2026-08-20)
- [ ] WoRMS sync cho loài mới (Tập III chưa sync)
- [ ] Loài 78 Tập IV bị thiếu data trong OCR gốc

### Admin Panel (Hướng 1: Supabase Auth + Dashboard)

#### Phase 1 — Vá RLS (ưu tiên cao)
- [x] Sửa RLS policy: xóa "Service write access" mở toang
- [x] Tạo policy mới: chỉ `service_role` hoặc authenticated user có role admin mới write được
- [x] Test: confirm anon key chỉ SELECT, không INSERT/UPDATE/DELETE

#### Phase 2 — Auth + Admin UI
- [ ] Enable Supabase Auth (email/password hoặc Google OAuth)
- [ ] Tạo bảng `profiles` (id, email, role: admin/editor/viewer, created_at)
- [x] Viết migration `004_create_profiles.sql`
- [x] Xây `/admin.html` — danh sách loài + tìm kiếm/lọc
- [ ] Form thêm/sửa/xóa loài (CRUD đầy đủ)
- [ ] Bulk import từ CSV/JSON
- [ ] Audit log (ai sửa gì, lúc nào)

#### Phase 3 — Multi-user (tương lai)
- [ ] Phân quyền editor: chỉ sửa loài mình phụ trách
- [ ] Admin toàn quyền
- [ ] Invite system cho collaborators
