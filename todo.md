# TODO — Dự án OCR Cá biển Việt Nam

> Cập nhật: 2026-07-30 16:08
> Next Session Starting Point: Vá RLS species table → setup Supabase Auth → Admin UI

## ✅ Hoàn thành

### Kiến trúc Web App
- [x] Thiết kế lại kiến trúc: 4 file HTML duy nhất (`index.html`, `tap.html`, `browse.html`, `species.html`)
- [x] Tất cả dữ liệu tập trung vào `data/species.json` + `data/taxonomy_tree.json`
- [x] Xóa hoàn toàn các file static `tap-1.html` ... `tap-5.html` (legacy)
- [x] Schema thống nhất cho `species.json`: `specs.vn`, `specs.en`, `synonyms[]`
- [x] Viết lại `scripts/build_database.py` — đọc trực tiếp từ OCR parsed JSON

### OCR & Chuẩn hóa dữ liệu
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
- [ ] Tập V: dữ liệu thô chưa được chuẩn hóa (tên VN bị lỗi, taxonomy trống)
- [ ] Tập I & II: chưa có dữ liệu OCR parsed JSON (chỉ có PSV cũ cho 50 loài Tập I)

### Chất lượng dữ liệu
- [x] `commonName` (EN) — Tập II: 232/266, Tập III: 518/518 ✅
- [x] `alternateNames` (VN) — Tập II: 240/266, Tập III: 246/518 (đúng bản chất)
- [ ] 50 loài skeleton Tập III — cần re-OCR targeted pages từ PDF gốc (Hướng 1)
- [ ] Deploy bản restore mới nhất lên Vercel
- [ ] WoRMS sync cho loài mới (Tập III chưa sync)
- [ ] Loài 78 Tập IV bị thiếu data trong OCR gốc

### Admin Panel (Hướng 1: Supabase Auth + Dashboard)

#### Phase 1 — Vá RLS (ưu tiên cao)
- [ ] Sửa RLS policy: xóa "Service write access" mở toang
- [ ] Tạo policy mới: chỉ `service_role` hoặc authenticated user có role admin mới write được
- [ ] Test: confirm anon key chỉ SELECT, không INSERT/UPDATE/DELETE

#### Phase 2 — Auth + Admin UI
- [ ] Enable Supabase Auth (email/password hoặc Google OAuth)
- [ ] Tạo bảng `profiles` (id, email, role: admin/editor/viewer, created_at)
- [ ] Viết migration `002_create_profiles_and_fix_rls.sql`
- [ ] Xây `/admin.html` — danh sách loài + tìm kiếm/lọc
- [ ] Form thêm/sửa/xóa loài (CRUD đầy đủ)
- [ ] Bulk import từ CSV/JSON
- [ ] Audit log (ai sửa gì, lúc nào)

#### Phase 3 — Multi-user (tương lai)
- [ ] Phân quyền editor: chỉ sửa loài mình phụ trách
- [ ] Admin toàn quyền
- [ ] Invite system cho collaborators
