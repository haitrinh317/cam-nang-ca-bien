# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-19
> **Supabase (SSOT):** 3,072 loài (9 collection) | **Production Live:** https://www.tracuusinhvatbien.app
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-19)

- [x] **Triển khai toàn diện 101 loài Động vật phù du Copepoda (Atlat ĐVPD 2016–2019, TS. Trương Sĩ Hải Trình & CS) theo quy trình 7 bước `ocr-to-audit.md` (Deploy 6ad781f)**:
  - **Bước ① (Bóc tách):** Trích xuất cấu trúc 101 loài độc bản từ Word DOCX, hợp nhất tiêu bản đực/cái, xuất 103 ảnh vi thể chất lượng cao sang WebP.
  - **Bước ② (WoRMS Sync):** Xác thực 100/101 loài (99.0%) với WoRMS AphiaID và taxonomy chuẩn quốc tế (81 Accepted, 19 Synonyms/Alternative representation).
  - **Bước ③ (Banyuls Copepoda Sync):** Khai thác CSDL chuyên ngành Banyuls (`copepodes.obs-banyuls.fr`), làm giàu dải kích thước F/M (mm), tầng sinh thái nước và công trình dẫn liệu quốc tế đạt 99.0% loài có kích thước.
  - **Bước ④ (Kho ảnh Storage):** Tải 103 ảnh vi thể lên Supabase Storage bucket `species-photos`, nạp bảng `species_photos` đạt 98.0% độ phủ ảnh.
  - **Bước ⑤ (Nạp DB):** Khởi tạo collection `dong-vat-phu-du` và nạp thành công 101/101 loài vào bảng `species`.
  - **Bước ⑥ (Nâng cấp 9 Phân hệ):** Cập nhật Nav, BottomNav, AdminSidebar, `collection-registry.ts` và KPI Admin Dashboard từ 8 lên 9 phân hệ sinh thái.
  - **Bước ⑦ (Audit & Giao diện):** Nâng cấp `BiologyDashboard.tsx` hiển thị thẻ kích thước vi thể mm, liên kết CSDL Banyuls và mã số tiêu bản Bảo tàng Thiên nhiên Việt Nam (VNMN). Kiểm toán đạt 98.0% Complete, 0% Skeleton. Deploy Production thành công.
- [x] **Chuẩn hóa danh xưng tiếng Việt 143 loài Bivalvia Tập 2 (Đỗ Công Thung 2015)**:
  - Tách 8 loài có nhiều tên ngăn cách bằng dấu phẩy (#34-#39, #84, #86): chỉ giữ 1 tên đầu tiên làm `vn_name`, đưa các tên còn lại vào `vn_alternate_names`.
  - Tách 4 loài có từ nối "Hến hoặc Ngao" (#64, #66, #67, #68) theo Phương án 1: `vn_name` = "Hến", `vn_alternate_names` = "Ngao".
  - Khử triệt để dấu chấm câu thừa scan OCR cho 3 loài (#21, #54, #65) và làm sạch text rác Wikidata ở #143 (Deploy 0024c86).

---

## 🔲 Đang chờ / WIP

### Ưu tiên cao 🔥
- [ ] Mở rộng collection `than-mem` Phase 3 cho các họ tiếp theo từ Hylleberg 2003
- [ ] Chuẩn bị Hợp nhất Phase 4 cho Thân mềm độc (11 loài ốc cối, bạch tuộc)
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh

### Ưu tiên thấp
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem danh sách chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor
