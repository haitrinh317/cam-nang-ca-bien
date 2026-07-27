# TODO — Dự án OCR Cá biển Việt Nam

> Cập nhật: 2026-07-24 16:33
> Next Session Starting Point: Kiểm tra mobile UI trên browser → enrichment pipeline Tập 2

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

## 🔲 Chưa làm

### OCR còn thiếu
- [ ] Tập IV loài 101-316: cần OCR + chuẩn hóa thủ công
- [ ] Tập V: dữ liệu thô chưa được chuẩn hóa (tên VN bị lỗi, taxonomy trống)
- [ ] Tập I & II: chưa có dữ liệu OCR parsed JSON (chỉ có PSV cũ cho 50 loài Tập I)

### Chất lượng dữ liệu
- [ ] Trường `alternateNames` (tên gọi khác) — nhiều loài còn trống, cần bổ sung
- [ ] `commonName` (EN) — enrichment pipeline mới test 10/266 loài Tập 2
- [ ] WoRMS sync cho loài mới (Tập III chưa sync)
- [ ] Google Search fallback cho loài không tìm được trên Wikidata/Wikipedia
- [ ] Loài 78 Tập IV bị thiếu data trong OCR gốc
