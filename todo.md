# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-10-03 (Commit: `ae09914`)
> **Supabase (SSOT):** 3,072 loài (9 collection) | **Production Live:** https://www.tracuusinhvatbien.app
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-10-03)

- [x] **Tìm kiếm nâng cấp:** RPC không dấu + xếp hạng (migration 012), Enter mở `/tim-kiem`, điều hướng bàn phím/ARIA combobox, gợi ý khớp tên gọi khác/tên Anh/tên khoa học.
- [x] **Bộ lọc nâng cao (migration 013-015):** IUCN, độ sâu, kích thước, môi trường sống (7 nhãn), vùng biển (5 vùng); badge IUCN + dòng thông tin theo bộ lọc trên mỗi kết quả; link từ trang phân hệ.

- [x] **Hoàn thiện tìm kiếm (9b4e78f, e094842, ae09914):** loài "Khắp ven biển" gán Bắc/Trung/Nam Bộ (vùng 2261/2770); dòng kết quả luôn hiện Vùng + Môi trường; thanh tìm kiếm canh lề trái; bỏ dòng "Một dự án bởi haitrinh" lặp (header nhóm, footer); badge Hoàng Sa - Trường Sa xuống dòng trên mobile.

- [x] **Audit toàn diện dự án, nâng cấp Next.js 16.3.8 & ESLint 9, tối ưu bảo mật Vercel (Deploy 7dbebee / jzbt673ha)**:
  - **Dọn dẹp code & CSS:** Khử dead code, gọt -1,291 dòng CSS chết (9 file), dọn 54 scripts one-shot vào `scripts/archive/` (giữ 12 scripts hoạt động).
  - **Bảo mật & Linting:** Nâng cấp Next.js 16.3.8 (0 lỗ hổng), cài đặt ESLint 9 (`eslint.config.mjs`) đạt chuẩn 0 lỗi / 0 cảnh báo.
  - **Bảo mật biến môi trường:** Cấu hình đầy đủ env Production & Preview trên Vercel, chặn triệt để upload `.env` bằng `.vercelignore`.
  - **Kiến trúc Next 16:** Thay `middleware.ts` bằng `proxy.ts`, bỏ header cache vô hiệu, render trang loài trực tiếp theo request (cập nhật tức thì khi admin chỉnh sửa).
  - **Dọn manifest:** Di chuyển `site (1).webmanifest` cũ vào `.backups/`.

---

## 🔲 Đang chờ / WIP

### Ưu tiên cao 🔥
- [ ] Đổi Supabase Service Role Key (tăng cường bảo mật sau khi chặn upload `.env`)
- [ ] Mở rộng collection `than-mem` Phase 3 cho các họ tiếp theo từ Hylleberg 2003
- [ ] Chuẩn bị Hợp nhất Phase 4 cho Thân mềm độc (11 loài ốc cối, bạch tuộc)

- [ ] **Audit UX/hiệu năng/a11y** — kế hoạch lưu ở `.agents/plans/backlog--ux--audit-hieu-nang-a11y-2026-10-03.md` (Gói A: nhẹ trang `/ca-bien`, `/ca-bien/taxonomy`, CLS, số liệu cứng; Gói B: tương phản/skip-link/chữ nhỏ)

### Ưu tiên thấp
- [ ] Tìm kiếm — phần C: bổ sung tên gọi thường dùng (nguồn dữ liệu chưa chọn; tên gọi khác phủ 70%, giáp xác/phù du 0%, san hô 5%)
- [ ] **Lỗi nháy:** `/tim-kiem?c=san-ho` cả trang nháy như tải lại nhiều lần (chưa tái hiện; cần mở browser xem Network/console, nghi layout/theme dùng chung)
- [ ] Sau mỗi batch OCR/enrich: chạy `node --env-file=.env.local scripts/derive_filter_cols.mjs --apply --tags`
- [ ] Trùng loài giữa phân hệ (vd *Arothron mappa* ở `ca-bien` và `sinh-vat-doc`) hiện 2 dòng khi tìm
- [ ] Đọc số loài từ DB thay vì hardcode 1767/3072 (DB thực: ca-bien 1766, tổng 3073)
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor

