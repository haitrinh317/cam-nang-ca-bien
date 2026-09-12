# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-12
> **Supabase (SSOT):** 2,787 loài (7 collection)
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-13)

- [x] Tái cấu trúc kiến trúc toàn diện (5/5 Ứng viên hoàn thành):
  - [x] Ứng viên #1: Đào sâu SpecimenCard (tách orchestrator 170 dòng + 3 tabs + 6 pure parsers)
  - [x] Ứng viên #2: Frontend-Backend Parity (Tab Đồng bộ trong Admin, sửa WoRMS/Synonyms/IUCN/Size)
  - [x] Ứng viên #3: Hợp nhất Collection Registry (gộp 4 file thành 1 deep module `collection-registry.ts`)
  - [x] Ứng viên #4: Đóng gói seam render sinh học (`BiologyDashboard.tsx` helper `getCollectionMeta`)
  - [x] Ứng viên #5: Chuẩn hóa hằng số SELECT query (`SPECIES_LIST_COLS`, `SPECIES_DETAIL_COLS`)

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
