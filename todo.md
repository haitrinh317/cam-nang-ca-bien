# TODO — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-15
> **Supabase (SSOT):** 2,828 loài (8 collection) | **Production Live:** https://www.tracuusinhvatbien.app
> **Lịch sử hoàn thành đầy đủ:** xem `todo-archive.md`

---

## ✅ Hoàn thành gần nhất (2026-09-15)

- [x] **Khắc phục dứt điểm lỗi vỡ CSS ô tìm kiếm trên toàn hệ thống (`GlobalSearch.tsx` & `GlobalSearch.css`)**:
  - Tách CSS tìm kiếm thành stylesheet độc lập tự chứa `components/search/GlobalSearch.css`, loại bỏ phụ thuộc vào `hero.css` của Trang chủ.
  - Sửa lỗi vỡ giao diện dropdown khi tìm kiếm trên tất cả các trang danh mục (`/giap-xac`, `/ca-bien`, `/thuc-vat-bien`...): định dạng flexbox cho hàng kết quả, khoảng cách padding chuẩn, gạch phân cách và hiệu ứng hover mượt mà.
  - Thiết kế bảng huy hiệu phân loại (badge pills) sắc nét cho từng nhóm sinh vật (Giáp xác, Thực vật biển, San hô, Thân mềm, Da gai, Bò sát, Độc biển, Cá biển) và hỗ trợ hoàn hảo chế độ tối Dark Mode.
- [x] **Audit & Nâng Cấp Toàn Diện Nhóm Giáp Xác Biển (136 loài: 132 `giap-xac` + 4 `sinh-vat-doc`)**:
  - **Audit 7 bước chuẩn `ocr-to-audit.md`:** Khảo sát và đánh giá toàn diện cấu trúc OCR, WoRMS (100% có AphiaID), SeaLifeBase (99.3% có biology), iNaturalist và Sách Đỏ VAST 2024 (6 loài Tôm hùm đạt 100% Golden Standard).
  - **Chuẩn hóa danh pháp WoRMS:** Bổ sung `worms_accepted_name` cho 5 loài Tôm tít đồng danh (`Lysiosquilla maculata`, `Bigelowina phalangium`, `Carinosquilla lirata`, `Miyakella nepa`, `Quollastria gonypetes`), đạt 100% độ phủ danh pháp hiện hành.
  - **Dịch thuật song ngữ 100%:** Dùng Gemini AI Carcinology dịch và cập nhật 132/132 loài có `en_size` và `en_distribution` học thuật trên Supabase (nâng tỷ lệ song ngữ từ 2.9% lên 100.0%).
  - **Bổ sung ảnh iNaturalist bằng WoRMS Fallback:** Thu thập và tải lên 25 ảnh WebP chất lượng cao CC-BY vào bucket `species-photos`, bổ sung 9 loài có ảnh mới, nâng tổng số ảnh giáp xác lên 178 ảnh và tỷ lệ loài Complete lên 48.5% (66/136 loài).
- [x] **Đột phá Phủ Ảnh Minh Họa Cá Biển Hoàn Tất (1,553 / 1,767 loài — 87.9%)**:
  - **Backfill giải cứu 841 loài cá biển:** Phát hiện & giải cứu 841 loài đã có ảnh chất lượng cao trên Supabase Storage nhưng bị bỏ trống cột `photo_url` trên bảng `species`. Chạy thành công `backfill_cabien_photo_urls.py`, nâng độ phủ từ 32% lên 79.68%.
  - **Chạy hoàn tất 100% `inaturalist-sync` cho 359 loài còn thiếu:** Bổ sung thêm **145 loài** cá biển có ảnh research-grade CC-BY từ iNaturalist, nén và tải lên **422 ảnh WebP mới** vào bucket `species-photos` (nâng tổng số ảnh hệ thống lên **5,331 ảnh**).
  - **Kết quả tổng kết:** Tỷ lệ cá biển hiển thị ảnh đại diện đạt **87.89% (1,553 / 1,767 loài)**. 214 loài còn lại chủ yếu là cá tầng đáy sâu/hiếm gặp không có quan sát CC-licensed trên iNaturalist. Toàn hệ thống sinh vật biển đạt **2,470 / 2,830 loài có ảnh (87.28%)**.
- [x] **Đồng bộ toàn diện FishBase v25.04 & SeaLifeBase v25.04 (99.8% FishBase coverage)**:
  - Sửa dứt điểm lỗi chính tả & danh pháp tam thức cho 6 loài cá biển (`Parexocoetus brachypterus`, `Parexocoetus mento`, `Ostracion meleagris`, `Cá ngựa vằn`, `Cá Đường`, `Cá Ngừ mắt to`) trên Supabase.
  - Xây dựng `sync_fishbase_ca_bien.py` với cơ chế đối chiếu 3 tầng (*Tên gốc OCR ➔ WoRMS Accepted Name ➔ Bảng đồng danh FishBase `synonyms.parquet`*): đồng bộ thành công **544 / 547 loài** cá biển còn thiếu; nâng tỷ lệ phủ FishBase toàn bộ 1,767 loài cá lên **99.83% (1,764/1,767 loài)**; bổ sung 1,482 loài có dải độ sâu và 1,176 loài có mô tả sinh học dịch tiếng Việt bằng Gemini AI.
  - Chạy `sync_sealifebase.py` hoàn tất: Bổ sung 20 loài San hô (`san-ho`), 11 loài Bò sát biển (`bo-sat-bien` đạt 100% 33/33 loài), và 31 loài Sinh vật độc (`sinh-vat-doc`).
- [x] **Chuẩn hóa nhãn cấp bậc "Giống" (Động vật) vs "Chi" (Thực vật) & Tinh gọn UI tab Phân loại**:
  - Chuẩn hóa hiển thị cấp Genus trong tab Phân loại (`PhanloaiTab.tsx`) và Cây phân loại (`TaxonomyTree.tsx`): tự động hiển thị **Chi** cho `thuc-vat-bien` và **Giống** cho tất cả các collection động vật (`ca-bien`, `bo-sat-bien`, `giap-xac`, `than-mem`, `san-ho`, `thu-bien`, `sinh-vat-doc`) ở cả 2 chế độ WoRMS Hiện Đại và Sách Chuyên Khảo.
  - Loại bỏ khối 2 card so sánh tĩnh ("Chuẩn Hiện Đại" và "Sách Gốc") trong `PhanloaiTab.tsx` do đã có toggle switch 2 chế độ trên cây phân loại trực quan; giúp giao diện liền mạch, tinh gọn. Build pass 100%.
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

- [x] **Hoàn tất xử lý khuyết trang 102 Chuyên khảo San hô (`san-ho`)**: Bóc tách trang 102 từ `IMG_1300.HEIC`, cập nhật hoàn chỉnh loài 29 (*Sclerophytum minimum*) và loài 30 (*Sclerophytum notandum*) lên Supabase, đạt 100% WoRMS và 100% chuyên khảo cho toàn bộ 42 loài san hô.
- [ ] **Triển khai bóc tách 100+ loài Thân mềm Hai mảnh vỏ (Bivalvia) kinh tế biển Việt Nam** (PGS.TS. Đỗ Công Thung 2015, 206 trang scan Chương 3).
- [ ] Admin Phase 2: CSV Import + Inline Edit nhanh

### Ưu tiên thấp
- [ ] Bổ sung tên VN rong biển (~17 loài chưa tra sách — xem danh sách chi tiết ở `todo-archive.md`)
- [ ] Admin Phase 3: Multi-user, phân quyền editor
