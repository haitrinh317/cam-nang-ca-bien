# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-16
> **Supabase (SSOT):** 2,971 loài (8 collection) | **Production Live:** https://www.tracuusinhvatbien.app
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-16)

- [x] **Triển khai toàn diện 143 loài Thân mềm Hai mảnh vỏ Bivalvia (Đỗ Công Thung 2015) theo quy trình 7 bước `ocr-to-audit.md`**:
  - **Bước ① (OCR & Bóc tách):** Quét native Apple Vision 206 trang scan sách chuyên khảo, trích xuất cấu trúc trọn vẹn 143/143 loài Bivalvia (Họ Sò, Vẹm, Trai ngọc, Bàn mai, Hàu, Điệp, Ngao, Nghêu, Móng tay, Tu hài, Trai tai tượng...).
  - **Bước ② (WoRMS Sync):** Xác thực 100% danh pháp quốc tế WoRMS AphiaID và taxonomy Lớp/Bộ/Họ/Chi hiện hành cho 143/143 loài.
  - **Bước ③ (SeaLifeBase Sync v2.0):** Tra cứu cơ sở dữ liệu chuyên ngành SeaLifeBase v25.04 & GBIF, đồng bộ thành công dữ liệu sinh học, độ sâu phân bố, kích thước tối đa cho toàn bộ collection `than-mem` (189/217 loài).
  - **Bước ④ (iNaturalist Sync):** Thu thập ảnh Research Grade CC-BY, nén chuẩn WebP và tải lên Supabase Storage 302 ảnh cho 106 loài (đạt tỷ lệ 74.1% loài có ảnh đại diện).
  - **Bước ⑤ (Enrich Tên Gọi):** Chuẩn hóa nhị thức khoa học, làm sạch chi phụ/năm và đồng bộ tên tiếng Anh (`en_common_name`) & tên gọi khác tiếng Việt (`vn_alternate_names`) từ Wikidata.
  - **Bước ⑥ (Sách Đỏ VAST 2024):** Tích hợp hồ sơ Sách Đỏ Việt Nam VAST 2024 đạt 100% Quy chuẩn Bố cục Vàng Golden Standard cho toàn bộ 5 loài Trai tai tượng khổng lồ (*Hippopus hippopus* [CR], *Tridacna gigas* [CR], *Tridacna maxima* [EN], *Tridacna squamosa* [EN], *Tridacna crocea* [EN]).
  - **Bước ⑦ (Audit Sinh Vật):** Chạy kiểm toán chất lượng toàn diện, đạt 106/143 loài Complete (74.1%), 37/143 loài Partial (25.9%), 0% Skeleton; 100% có đầy đủ hình thái vỏ, kích thước, sinh thái học, phân bố và tài liệu dẫn; xuất báo cáo `scratch/audit_report_thanmem.md`.
  - Nâng cấp `lib/collection-registry.ts` khai báo Tập 2 Bivalvia (`volumeCount: 2`). Kiểm thử localhost HTTP 200 OK.
- [x] **Chuẩn hóa danh xưng tiếng Việt 143 loài Bivalvia Tập 2 (Đỗ Công Thung 2015)**:
  - Tách 8 loài có nhiều tên ngăn cách bằng dấu phẩy (#34-#39, #84, #86): chỉ giữ 1 tên đầu tiên làm `vn_name`, đưa các tên còn lại vào `vn_alternate_names` (kèm viết hoa chuẩn danh từ).
  - Tách 4 loài có từ nối "Hến hoặc Ngao" (#64, #66, #67, #68) theo Phương án 1: `vn_name` = "Hến", `vn_alternate_names` = "Ngao".
  - Khử triệt để dấu chấm câu thừa scan OCR cho 3 loài (#21, #54, #65) và làm sạch text rác Wikidata ở #143.
  - Cập nhật hàm `process_vietnamese_names` vào script `scripts/sync_all_bivalvia_clean_143.py`, deploy Vercel Production (`0024c86`).


---

## 🔲 Đang chờ / WIP

### Ưu tiên cao 🔥
- [ ] Mở rộng collection `than-mem` Phase 3 cho các họ tiếp theo từ Hylleberg 2003
- [ ] Chuẩn bị Hợp nhất Phase 4 cho Thân mềm độc (11 loài ốc cối, bạch tuộc)
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh

### Ưu tiên thấp
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem danh sách chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor
