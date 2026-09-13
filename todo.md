# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-13
> **Supabase (SSOT):** 2,793 loài (7 collection)
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-13)

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
