# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-13 (phiên đêm)
> **Supabase (SSOT):** 2,828 loài (8 collection)
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-13 — phiên đêm)

- [x] Tái cấu trúc Admin Shell sang Fixed Two-Panel Grid (100dvh, isolated scroll) chuẩn Vibe Design Harness: sửa dứt điểm lỗi gãy sticky & trôi tụt sidebar
- [x] Nâng cấp Nhật ký kiểm toán Admin (`/admin/audit-log`): phân trang server-side + lọc theo ngày/phân hệ
- [x] Tạo trang quản trị tài liệu nguồn chuyên khảo (`/admin/literature`)
- [x] Khắc phục lỗi đếm 967 loài Cá biển trên Sidebar (PostgREST limit 1000 rows) → đếm song song bằng `head: true` trả về đúng 1.764 loài
- [x] Hệ thống hóa toàn bộ thư mục công trình khoa học & bài báo Động vật phù du (TS. Trương Sĩ Hải Trình & Nguyễn Cho) vào `docs/thu-muc-dong-vat-phu-du.md`
- [x] UI Audit vibe-design-harness: Purge 100% emoji → Lucide SVG (Nav, BottomNav, SpecimenCard, SpeciesGrid, SpeciesForm) + xây dựng `hooks/useScrollReveal.ts`
- [x] Scroll entrance animation: book-card stagger (browse) + heroReveal/panelReveal/bentoReveal (chi tiết loài) + fix bug invisible rows async data
- [x] Codify UI rules vào AGENTS.md (Section 6) + 2 patterns mới vào patterns.md + refactor animation tokens
- [x] SpeciesForm.tsx refactor sidebar 2-column workspace layout (chú tự thực hiện)
- [x] Khởi tạo & Triển khai toàn diện Collection Thú biển Việt Nam (`thu-bien` — 34 loài: 1 Bò biển Dugong + 33 Cá voi/heo gồm Cá nhà táng) theo workflow 7 bước `ocr-to-audit.md`
- [x] Đăng ký Collection & Đầu sách đại diện: *Danh lục Thú biển Việt Nam & Mẫu vật Lăng Ông* (Smith et al. 1995; McGowen, Vũ Long et al. 2021; Viện Hải dương học), NXB Khoa học và Kỹ thuật vào Supabase và `lib/collection-registry.ts`
- [x] Sửa dứt điểm lỗi trùng ảnh Vích & Quản đồng (*Caretta caretta*) — nạp 3 ảnh iNat chuẩn hình thái đầu to, chuẩn hóa `taxon_id` search
- [x] Nâng cấp AI Skill `sealifebase-sync` v2.0 hỗ trợ toàn bộ 5 nhóm sinh vật biển ngoài cá (Bò sát biển, Thân mềm, San hô, Giáp xác, Động vật độc) kèm 5 System Prompts dịch thuật học thuật, Deep Merge bảo toàn Sách Đỏ VAST, và đồng bộ 100% cho `bo-sat-bien`
- [x] Tối ưu hóa ngắt đoạn tự động (smart paragraph splitting) trong Bento cards (Hình thái, Sinh thái, Giá trị kinh tế), dọn dẹp nhãn mồ côi "Tại" trong phân bố và chuẩn hóa Trend Pill Sách Đỏ
- [x] Tạo AI Skill `vnredlist-sync` v1.0 (Sách Đỏ VAST → Golden Standard) & chuẩn hóa 79/79 loài đạt 100%
- [x] Bổ sung bước ⑥ `vnredlist-sync` vào workflow `ocr-to-audit.md` (pipeline 7 bước)
- [x] Nâng cấp & Hợp nhất Collection Bò sát biển Việt Nam (`bo-sat-bien` — 33 loài: 27 Rắn biển + 5 Rùa biển + 1 Cá sấu hoa cà) kèm 18 ảnh iNaturalist CC-BY & 301 redirects
- [x] Bổ sung hồ sơ Sách Đỏ VAST 2024 (`http://vnredlist.vast.vn/`) & hoàn thành Audit 100% Complete cho 6 loài bò sát biển mới
- [x] Tích hợp Danh Lục Đỏ Việt Nam (VAST 2024-1) & Hệ thống Dual-Conservation Badges (74 loài)
- [x] Tái cấu trúc kiến trúc toàn diện (5/5 Ứng viên hoàn thành: SpecimenCard, Parity, Registry, Biology seam, Query cols)
- [x] Sửa ảnh cá mặt trăng *Mola mola* (Research-grade) & thắt chặt bộ lọc `find_taxon_id`
- [x] Hiển thị in nghiêng HTML (`<i>`, `<em>`) & ngắt đoạn thông minh ghi chú sinh học dài, quét sạch CJK
- [x] Thiết kế lại mục "Tư Liệu Khoa Học & Ghi Chú Chuyên Sâu" chuẩn Bento Card Hallmark
- [x] Chuẩn hóa cấu trúc & ngắt đoạn thông minh Hồ Sơ Bảo Tồn Sách Đỏ Việt Nam (tách Biện pháp hiện hành, Đề xuất cấp thiết, Pill xu hướng)
- [x] Rà soát & Việt hóa 100% tiếng Việt khoa học cho tab Sinh học (môi trường sống, sinh sản, dinh dưỡng)

## ✅ Hoàn thành (2026-09-12)

- [x] Thu hẹp khoảng cách Frontend-Backend (Parity Gap) — Phương án B: Tab Đồng bộ trong Admin (Sửa WoRMS, Synonyms, IUCN, Kích thước; Xem toàn bộ Biology JSONB)
- [x] Khôi phục Logo Cá nhân (Sóng biển & Vây cá tuần hoàn)
- [x] Tích hợp sách Thân mềm + San hô vào `literature_sources`
- [x] Hoàn thành Phase 2 Hợp nhất Cá biển độc (25 taxa)
- [x] Hoàn thành Phase 1 Hợp nhất Rắn biển (27 loài) — độc tố học lâm sàng + 22 ảnh

## ✅ Hoàn thành (2026-09-11)

- [x] Pipeline San hô Việt Nam (`san-ho`) — 42 loài: OCR + WoRMS 100% + 24 ảnh WebP
- [x] Pilot Thân mềm (`than-mem`) — 74 loài Ốc sứ: OCR + WoRMS 100% + 210 ảnh iNat

---

## 🔲 Đang chờ / WIP

### Ưu tiên cao
- [ ] Mở rộng collection `than-mem` Phase 2 cho các họ tiếp theo từ Hylleberg 2003
- [ ] Chuẩn bị Hợp nhất Phase 3 cho Thân mềm độc (11 loài ốc cối, bạch tuộc)

### Ưu tiên trung bình
- [ ] Bổ sung scan trang 102 chuyên khảo San hô (loài 30 & đuôi loài 29)
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh

### Ưu tiên thấp
- [ ] Tập I Cá biển: chưa có dữ liệu OCR (chỉ có PSV cũ cho 50 loài)
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem danh sách chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor
