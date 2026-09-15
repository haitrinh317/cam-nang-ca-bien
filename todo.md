# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-15
> **Supabase (SSOT):** 2,828 loài (8 collection) | **Production Live:** https://www.tracuusinhvatbien.app
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-15)

- [x] **Commit & Deploy Vercel Production fix lặp rank prefix** (`fix(taxonomy): strip duplicated rank prefixes`): Sửa triệt để lỗi hiển thị lặp từ cấp bậc (`Lớp - Lớp`, `Bộ - Bộ`, `Họ - Họ`...) trên cả cây phân loại bậc thang lẫn card đối chiếu song song WoRMS / Sách gốc; hệ thống live tại `https://cam-nang-ca-bien.vercel.app` & `https://www.tracuusinhvatbien.app`.

## ✅ Hoàn thành (2026-09-14)

- [x] **Thu thập & tải 31 bài báo/sách chuyên khảo Động vật phù du** (TS. Trương Sĩ Hải Trình & CN. Nguyễn Cho) toàn văn PDF vào `Documents/dong-vat-phu-du/` (~55.6 MB).
- [x] **Sửa lỗi trắng Tab "Phân loại" trên trang chi tiết loài**: Chuyển trạng thái bento card sang `opacity: 1`, gỡ bỏ `useScrollReveal` trên dynamic tab panels (tuân thủ quy tắc AGENTS.md: chỉ dùng scroll reveal cho static DOM).
- [x] **Khôi phục toàn diện & sửa lỗi chính tả 100% Tập IV Cá Biển Việt Nam** (341/341 loài): Thay thế 10 loài Cá Mú (#51–#60) bằng Cá Bàng Chài gốc; phục hồi 3 loài khuyết (#78, #102, #124); chuẩn hóa Họ Cá Đối Đục (*Opistognathidae*); sửa lỗi chính tả 27 loài ("Cá đối chứ không phải cá đồi"); đồng bộ WoRMS cho 19 loài.
- [x] **Rà soát & chuẩn hóa toàn diện Cây phân loại Cá biển (1,767 loài)**: Bóc tách 31 trang Mục lục sách gốc Tập 3, phục hồi 508 loài Tập 3 bị khuyết trắng taxonomy; chuẩn hóa 100% prefix `"Họ "` và `"Bộ "`; xóa sạch chữ Latin rò rỉ; triệt tiêu hoàn toàn mục "Unknown" (0 loài thiếu Lớp/Bộ/Họ/Giống).
- [x] **Nâng cấp phân trang fetch Supabase 3,000 loài** cho trang Cây phân loại (`/[collection]/taxonomy` & `TaxonomyTree.tsx`), loại bỏ giới hạn trần PostgREST 1000/2000 dòng.
- [x] **Thiết kế & Triển khai Kiến trúc Cây Phân Loại Kép (Dual Taxonomy Architecture)**: Đồng bộ 100% WoRMS Taxonomy (56 bộ phân tử hiện đại) cho 1,767 loài cá biển; tích hợp bộ chuyển đổi Toggle Switch tức thì giữa **🧬 WoRMS Hiện Đại (2026)** và **🏛️ Sách Gốc (Viện Hải dương học)** trên cây phân loại và bảng đối chiếu song song trên trang chi tiết loài.
- [x] **Sửa lỗi lặp tiền tố cấp bậc taxonomy** (`Lớp - Lớp`, `Bộ - Bộ`, `Họ - Họ`...): Nâng cấp `cleanTaxonHierarchy` + `stripRankPrefix`, cập nhật `PhanloaiTab.tsx` (stepped tree + comparison card) và `TaxonomyTree.tsx`. Build pass 100%.
- [x] **Kiểm tra phân loại Cá Mó (Scaridae → Labridae)**: Xác nhận 31 loài cá mó trong dự án đều đã đúng `family = "Labridae"` theo WoRMS 2026 / Near et al. 2025. Sách gốc vẫn giữ `Scaridae` đúng học thuật.

## ✅ Hoàn thành (2026-09-13 — phiên đêm)

- [x] Tái cấu trúc Admin Shell sang Fixed Two-Panel Grid (100dvh, isolated scroll) chuẩn Vibe Design Harness: sửa dứt điểm lỗi gãy sticky & trôi tụt sidebar
- [x] Nâng cấp Nhật ký kiểm toán Admin (`/admin/audit-log`): phân trang server-side + lọc theo ngày/phân hệ
- [x] Tạo trang quản trị tài liệu nguồn chuyên khảo (`/admin/literature`)
- [x] Khắc phục lỗi đếm 967 loài Cá biển trên Sidebar (PostgREST limit 1000 rows) → đếm song song bằng `head: true` trả về đúng 1.764 loài
- [x] Khởi tạo & Triển khai toàn diện Collection Thú biển Việt Nam (`thu-bien` — 34 loài: 1 Bò biển Dugong + 33 Cá voi/heo) theo workflow 7 bước `ocr-to-audit.md`
- [x] Nâng cấp AI Skill `sealifebase-sync` v2.0 hỗ trợ 5 nhóm sinh vật ngoài cá kèm Deep Merge bảo toàn Sách Đỏ VAST
- [x] Tạo AI Skill `vnredlist-sync` v1.0 (Sách Đỏ VAST → Golden Standard) & chuẩn hóa 79/79 loài đạt 100%

---

## 🔲 Đang chờ / WIP

### Ưu tiên cao 🔥
- [ ] Mở rộng collection `than-mem` Phase 2 cho các họ tiếp theo từ Hylleberg 2003
- [ ] Chuẩn bị Hợp nhất Phase 3 cho Thân mềm độc (11 loài ốc cối, bạch tuộc)

### Ưu tiên trung bình
- [ ] Bổ sung scan trang 102 chuyên khảo San hô (loài 30 & đuôi loài 29)
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh

### Ưu tiên thấp
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem danh sách chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor
