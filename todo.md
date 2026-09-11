# TODO — Dự án Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> Cập nhật: 2026-09-11 (Hoàn thành Phase 0 & Phase 1 Pilot Họ Ốc sứ Cypraeidae 74 loài collection than-mem — 100% WoRMS + SeaLifeBase + Ảnh iNat)
> **Next Session Starting Point**: Tiếp tục mở rộng collection `than-mem` Phase 2 cho các họ tiếp theo từ Hylleberg 2003, hoặc triển khai di chuyển các loài thân mềm độc theo ADR-001.
> **Supabase (SSOT):** 2,745 loài (1,764 cá biển + 672 thực vật biển + 132 giáp xác + 27 rắn biển + 76 động vật độc biển + 74 thân mềm biển). 100% WoRMS cho toàn bộ 2,745 loài.

## ✅ Hoàn thành mới nhất (2026-09-11)
- [x] **Khởi tạo collection `than-mem` và Hoàn thành Pilot test Họ Ốc sứ Cypraeidae (74 loài)**:
  - **Quyết định kiến trúc ADR-001 (Taxonomy-First)**: Thống nhất lấy phân loại học làm trục chính (Mollusca), chuyển `sinh-vat-doc` thành Thematic Special Group lọc đa ngành (`biology->toxicology IS NOT NULL`).
  - **Phase 0 (Hạ tầng)**: Tạo collection `than-mem` trong CSDL Supabase, cập nhật `lib/collections.ts`, `lib/books-data.ts` (cuốn Hylleberg & Kilburn 2003), khởi tạo từ điển họ tiếng Việt `scripts/data/mollusc_family_vi.json`.
  - **Bước ① (OCR Vision)**: Bóc tách 74 loài từ 7 trang scan (PDF 47–53, sách 49–55) bằng Gemini 3.6 Flash; tự động ghép nối văn bản continuation ngắt qua ranh giới trang (như *Cypraea arabica*).
  - **Bước ② (WoRMS Validation)**: 100% (74/74) loài được xác thực AphiaID và danh pháp hợp lệ mới nhất (1 accepted *Cypraea tigris*, 73 loài đã chuyển sang các chi hiện đại *Monetaria*, *Mauritia*, *Lyncina*, *Erronea*, *Naria*, *Palmadusta*, *Talparia*...).
  - **Bước ③ (SeaLifeBase Sync)**: 85.1% (63/74 loài) được làm giàu kích thước vỏ tối đa, độ sâu phân bố, sinh cảnh rạn san hô và tập tính qua DuckDB offline cache.
  - **Bước ④ (iNaturalist Photos)**: 97.3% (72/74 loài) được gán ảnh thực địa nghiên cứu (research-grade) kèm bản quyền tác giả.
  - **Bước ⑤ (Tên tiếng Việt đối chiếu)**: 79.7% (59/74 loài) được gán tên tiếng Việt thông dụng chuẩn (*Ốc sứ hổ, Ốc sứ nhẫn, Ốc tiền, Ốc sứ đầu rắn, Ốc sứ A-rập, Ốc sứ chuột chũi, Ốc sứ đồi mồi...*); các loài còn lại chuẩn hóa theo Tầng 3.
  - **Bước ⑥ (Supabase Upsert)**: Nạp thành công 74/74 records vào Supabase (`thanmem-species-1` đến `thanmem-species-74`).
  - **Kiểm định Build**: Kích hoạt `than-mem` trên `BottomNav.tsx` và chạy `npm run build` Next.js 16 thành công 100%, 0 lỗi TypeScript.

## ✅ Hoàn thành trước đó (2026-09-09)
- [x] **Nâng Cấp Bộ Soạn Thảo Phân Bố Loài & Chuẩn Hóa Schema Zod Frontend - Backend (`SpeciesForm.tsx`, `DistributionEditor.tsx`, `SpecimenVisualWidgets.tsx`, `lib/distribution.ts`)**:
  - Khắc phục lỗi logic bóc tách ở `SpecimenVisualWidgets.tsx`: ngăn chặn việc tự ý cắt văn bản tiếng Việt của các loài chỉ phân bố ở Việt Nam (như Sao biển Gai) rồi đẩy nhầm sang mục THẾ GIỚI.
  - Xây dựng module tiện ích `lib/distribution.ts` với `splitDistribution`, `formatDistribution`, `parseDistribution` dùng chung.
  - Xây dựng component `components/admin/DistributionEditor.tsx`: chia 2 ô nhập liệu độc lập (Phân bố tại Việt Nam & Phân bố trên Thế giới), kèm gợi ý vùng biển nhanh, bộ đếm ký tự `.../2000`, nút bật tắt văn bản gộp thô và **Live Preview** hiển thị thẻ trực tiếp theo thời gian thực.
  - Tích hợp vào `components/admin/SpeciesForm.tsx` và bổ sung lớp phòng thủ Zod validation client-side (`validator.safeParse(payload)`), bảo toàn 100% Data Contract và cờ `.strict()` của backend.
  - Build Next.js Production pass 100%, 0 lỗi TypeScript (`npx tsc --noEmit`).
- [x] **Thiết kế & Tích hợp Logo Mới Phương Án 1 (Modern Ocean Wave & Whale Tail)**:
  - Thay thế toàn diện logo Viện Hải dương học cũ bằng logo biểu trưng sóng biển và vây cá voi tuần hoàn hiện đại.
  - Tách nền trong suốt (RGBA), khử viền răng cưa, căn giữa quang học 534×534 px.
  - Xuất khẩu trọn bộ nhận diện: `public/logo.png` (512×512), `public/icons/icon-512x512.png`, `public/icons/icon-192x192.png`, `public/favicon.ico`.
  - Sao lưu toàn bộ assets cũ vào `.backups/`.
  - Đồng bộ hiển thị trên Header Navbar (`/logo.png` + cyan glow drop-shadow) và Footer.
- [x] **Khắc phục lỗi 'Dữ liệu không hợp lệ' khi lưu chỉnh sửa loài ở Admin (`SpeciesForm.tsx`, `route.ts`, `schemas.ts`)**:
  - Đảo ngược logic sai ở `SpeciesForm.tsx` (`if (id) delete payload.id`), không gửi thừa `id` trong body khi gọi `PATCH /api/species`.
  - Bổ sung `deleted_at: z.string().nullable().optional()` vào `lib/schemas.ts`, hỗ trợ khôi phục loài từ thùng rác.
  - Cho phép trường `id` tùy chọn trong `speciesUpdateSchema` và loại bỏ `body.id` tại route `PATCH` trước khi ghi DB (phòng thủ đa tầng).
- [x] **Khắc phục lỗi ngắt dòng sớm & từ mồ côi (Orphan / Widow) ở Thẻ đầu sách gốc các trang con**:
  - Gỡ bỏ giới hạn `p { max-width: 68ch }` trên `.book-card p` trong cả `styles/book-browser.css` và `styles/globals.css`.
  - Bổ sung `max-width: none; text-wrap: pretty; line-height: 1.55;` cho `.bc-desc`, triệt tiêu hoàn toàn hiện tượng rớt chữ mồ côi ở dòng cuối (như chữ 'ban đầu.' ở cuốn Động vật độc biển VN).
  - Bổ sung `text-wrap: balance` cho `.bc-title` và `text-wrap: pretty` cho `.bc-author`.
  - Build test Next.js Production thành công không có lỗi.
- [x] **Tạo & Thiết lập Ảnh OpenGraph Sharing Link Mới (Option 2 — Photorealistic Ocean Hero)**:
  - Thay thế ảnh cũ có logo Viện Hải dương học (1922) bằng ảnh mới mang định vị thương hiệu cá nhân `haitrinh`.
  - Thiết kế mỹ thuật đại dương chiều sâu với cá mập voi, rùa biển bơi lội dưới luồng ánh sáng mặt trời (*God rays*) qua rạn san hô lân quang.
  - Khối card kính mờ (Frosted Glass) tôn vinh con số thực tế **`2.671+ LOÀI SINH VẬT BIỂN`** và 5 nhóm loài (`Cá biển`, `Thực vật`, `Giáp xác`, `Rắn biển`, `Độc biển`).
  - Đồng bộ cập nhật metadata `2.671+` trong `app/layout.tsx`, `app/(public)/page.tsx` và `lib/species-photos.ts`.
- [x] **Triển khai Production Vercel (`/deploy-cabien`) — Commit `1d6288e`**:
  - Xác thực tài khoản chuẩn `haitrinh082@gmail.com` (`haitrinh082-6335s-projects`), link project và deploy thành công qua Vercel CLI (`vercel --prod --yes`).
  - URLs chính thức: `https://www.tracuusinhvatbien.app` và `https://cam-nang-ca-bien.vercel.app` (HTTP 200 OK).
  - Đã kiểm tra trực tiếp qua curl trên Production: Render chính xác `Chiến binh Bồ Đào Nha, Sứa lửa, Sứa bọng`, không còn lỗi JSON/Unicode.
- [x] **Khắc phục lỗi giao diện & chuẩn hóa hiển thị tiếng Việt theo phản hồi của chú Chình**:
  - **Bỏ trùng lặp Hồ sơ Độc học**: Gỡ bỏ `<ToxicologyWidget>` khỏi Tab 2 (Sinh học), chỉ giữ lại ở Tab 1 (Thông số).
  - **Rút gọn thông tin chủ biên**: Giữ `Chủ biên chuyên khảo: PGS.TS. Đào Việt Hà`, bỏ phần chức danh Viện trưởng.
  - **Sửa đếm tài liệu dẫn**: Logic `parseLiterature` chỉ bẻ dòng sau năm 4 chữ số khi có từ 2 mốc năm trở lên; badge hiển thị chuẩn xác `1 tài liệu dẫn`.
  - **Triệt tiêu từ mồ côi & Tự động giãn cột**: Grid thẻ mẫu vật tự động chuyển sang 1 cột full-width khi không có nơi lưu trữ mẫu vật, bổ sung `text-wrap: pretty; word-break: normal;` cho văn bản.
  - **Sửa lỗi tiếng Việt "Tên gọi khác" (`vn_alternate_names`)**: Chuẩn hóa toàn diện 76/76 loài trong Supabase từ JSON array Unicode escaped sang chuỗi tiếng Việt phân cách bằng dấu phẩy; bổ sung hàm phòng thủ `formatAlternateNames()` trên React UI.
- [x] **Khởi tạo & Hoàn thành 100% Pipeline Bộ Sưu Tập Động Vật Độc Biển Việt Nam (`sinh-vat-doc`) — 76 loài**:
  - **Kiến trúc & Cấu trúc Dữ liệu**: Thực hiện Phương án 3 (Hybrid Architecture) được chú Chình phê duyệt. Thêm collection `sinh-vat-doc` và chuyên khảo *Động vật độc biển Việt Nam* (PGS.TS. Đào Việt Hà) vào CSDL Supabase.
  - **Bóc tách 76 loài/taxa**: Trích xuất 100% đặc điểm hình thái, kích thước, phân bố, cơ chế độc tính, triệu chứng lâm sàng và phác đồ sơ cứu từ chuyên khảo.
  - **Số hóa & Tải lên Kho Ảnh Thực địa**: Chuyển đổi 80 ảnh từ thư mục ảnh gốc độ phân giải cao sang WebP chuẩn và tải lên Supabase Storage bucket `species-photos/sinh-vat-doc/`. Đạt 100% loài có ảnh đại diện và bản quyền tác giả nhiếp ảnh (Trương Sĩ Hải Trình, Thái Minh Quang, Bùi Quang Nghị, Cao Văn Nguyện...).
  - **WoRMS Sync 100%**: Đồng bộ danh pháp và AphiaID quốc tế cho 76/76 loài vào Supabase.
  - **Frontend UI & Bento Widget Độc Học (`ToxicologyWidget`)**: Xây dựng widget chuyên biệt cảnh báo nguy cơ tử vong, nhận diện độc tố (TTX, STX, Conotoxins, Ciguatoxin...), cơ chế dược lý, triệu chứng và phác đồ sơ cứu khẩn cấp (Do's & Don'ts). Tích hợp vào `SpecimenCard`, Thống số, Sinh học tab.
  - **Tích hợp Trang chủ & Điều hướng**: Bổ sung chuyên đề Động vật độc trên Trang chủ (`SpecialGroupsSection`), Top Nav, Bottom Mobile Sheet Drawer và Cổng Quản trị Admin.
  - **Kiểm định chất lượng**: 0 lỗi TypeScript (`npx tsc --noEmit` PASS 100%).

## ✅ Hoàn thành trước đó (2026-09-08)
- [x] **Fix ISR cache — Admin chỉnh sách phản ánh ngay trang chủ (Commit 08e9746)**:
  - Phát hiện: `app/(admin)/admin/literature/page.tsx` là `'use client'`, không thể gọi `revalidatePath` — dù toggle `is_visible` xong, trang chủ vẫn giữ bản cache ISR cũ đến 1 tiếng.
  - Tạo mới `app/api/revalidate-home/route.ts` (Server Route): xác thực admin, gọi `revalidatePath('/')` để flush cache ngay lập tức.
  - Gắn `flushHomeCache()` fire-and-forget vào 3 handler Admin: `handleSave`, `handleDelete`, `toggleVisible`.
  - Build + Deploy Production Vercel thành công (Commit `08e9746`).
- [x] **Fix `parseLiterature` ngắt dòng mồ côi trong Tài liệu dẫn (rắn biển)**:
  - Làm sạch 14 loài rắn biển trong Supabase: gộp ký tự `\n` scan trong `vn_literature` thành khoảng trắng đơn.
  - Nâng cấp `parseLiterature` trong `SpecimenCard.tsx`: tách theo `;` ưu tiên, không bị lừa bởi `\n` vật lý.
  - Chuẩn hóa format ghi vào `patterns.md` và `ocr-sinhvat-bien/SKILL.md` (mục 4.9) để các phiên OCR sau tuân thủ.
- [x] **Chuẩn hóa hiển thị Thẻ Mẫu vật (`SpecimenCard`), Sửa lỗi ngắt dòng mồ côi & Tách rõ 2 dòng Tình trạng thực địa / Bảo tồn**:
  - `components/species/SpecimenCard.tsx`: Tinh chỉnh `parseLocations` không split theo dấu phẩy ngữ pháp, giữ nguyên vẹn câu văn mô tả địa danh/năm thu mẫu, xóa bỏ hiện tượng rớt dòng mồ côi và chấm tròn vô nghĩa.
  - Bổ sung `parseStatus` tự động nhận diện và bóc tách thành 2 mục rõ ràng: **Tình trạng thực địa** và **Hiện trạng bảo tồn** kèm styling riêng biệt (`.specimen-vault-status-*`).
  - Thống nhất quy chuẩn và ghi nhận vào `.agents/memory/patterns.md` và skill `ocr-sinhvat-bien` v3.0 để tất cả các phiên làm việc và OCR sau này tuân thủ 100%.
  - Deploy thành công lên Vercel Production (`7128351`) tại `https://www.tracuusinhvatbien.app` và `https://cam-nang-ca-bien.vercel.app`.
- [x] **Khắc phục lỗi thiết kế rò rỉ Mobile Drawer dưới Footer Desktop & Chuẩn hóa SEO Login/Admin (`haitrinh`)**:
  - Sửa `styles/mobile.css`: Ẩn triệt để `.bottom-sheet-backdrop` và `.bottom-sheet-container` ở tầng desktop (`display: none`), chấm dứt rò rỉ mã HTML thô dưới chân trang footer.
  - Chuẩn hóa SEO Metadata cho phân hệ Login & Admin: Gỡ bỏ toạ độ GPS của Viện Hải dương học Nha Trang, cập nhật CSDL 2.595 loài sinh vật biển do `haitrinh` phát triển.
  - Cập nhật `app/robots.ts` bổ sung `/login` vào danh sách `disallow`.
  - Bổ sung dynamic metadata cho các trang con admin (`/[collection]`, `/literature`).
  - Deploy thành công lên Vercel Production (`https://www.tracuusinhvatbien.app`).
- [x] **Cập nhật SEO, Schema Graph & Chuyển đổi định vị thương hiệu cá nhân (`haitrinh`)**:
  - Tên dự án: `Tra cứu thông tin Sinh Vật Biển Việt Nam`.
  - Dòng định danh: `Một dự án được phát triển bởi haitrinh`.
  - Định hướng: `Số hóa tri thức di sản phân loại học & bảo tồn đại dương`.
  - Gỡ bỏ 100% liên kết và từ khóa liên quan đến *Viện Hải dương học*, *Bảo tàng Hải dương học*, *Viện Hàn lâm Khoa học và Công nghệ Việt Nam* ở Header, Footer, Hero, About, FAQ, Admin, Login.
  - Chuyển đổi thực thể trong Schema Graph (`websiteSchema` trong `app/layout.tsx`) từ Organization sang `Person` (`haitrinh`, nhà phát triển độc lập), tối ưu hóa SEO và Rich Snippets trên Google.
  - Đồng bộ thẻ OpenGraph, Twitter Cards, PWA Manifest (`public/site.webmanifest`), `CatalogHeader.tsx` và `locales/vi.json`, `locales/en.json`.
- [x] **Tích hợp Nhóm Rắn Biển & Đồng bộ Toàn diện Khu vực Quản trị (`/admin`)**:
  - `AdminSidebar.tsx`: Bổ sung nhóm `🐍 Rắn biển Việt Nam` (27 loài); cập nhật badge `Thực vật biển` thành `672`.
  - `app/(admin)/admin/page.tsx`: Mở rộng Dashboard KPI đếm đủ cả 4 collection (`ca-bien`, `thuc-vat-bien`, `giap-xac`, `ran-bien`), hiển thị chính xác tổng số **2.595 loài** và 2 thẻ KPI mới (Giáp xác 132, Rắn biển 27).
  - `SpeciesTable.tsx`: Tự động nhận diện số tập, ẩn dropdown lọc tập thừa cho các collection 1 tập (`ran-bien`, `giap-xac`).
- [x] **Sửa Top Navbar Desktop, Ô Search Placeholder & Triệt tiêu lỗi Line xanh Border**:
  - Rút gọn nhãn các tabs trên desktop thành `Cá biển` | `Rong biển` | `Giáp xác` | `Rắn biển`, căn chỉnh flexbox gọn gàng, loại bỏ hoàn toàn hiện tượng tràn viền hay đè lên cụm controls ngôn ngữ / dark mode.
  - Sửa placeholder ô tìm kiếm thích ứng theo từng nhóm loài (132+ Giáp xác, 27+ Rắn biển, 672+ Thực vật, 1,764+ Cá biển).
  - Gỡ bỏ pseudo-element `::before` dải màu cyan trong `CatalogHeader.css`, khôi phục viền bo tròn sắc nét cho card danh mục.
- [x] **Tái thiết kế Floating Bottom Navbar trên Mobile (Phương án 1 — Bottom Sheet Drawer)**:
  - Bố cục thanh dock 4 tabs chuẩn công thái học (`Trang chủ`, `Cá biển`, `Rong biển`, `Nhóm loài`).
  - Tab 4 tự động đổi icon theo ngữ cảnh (`<Shrimp />` khi ở Giáp xác, `🐍` khi ở Rắn biển) kèm badge chấm cam phát sáng.
  - Khi bấm tab 4, trượt lên Modal Drawer cao cấp (`backdrop-filter: blur(32px)`) với Grid 2 cột mở ra tất cả các nhóm sinh vật và lối tắt tới Cây phân loại.
- [x] **Deploy Production Vercel Lần 2 (Commit `6eac29a`)**:
  - Push GitHub `master` và deploy thành công lên Vercel Production (`vercel --prod --yes`).
  - URLs: `https://www.tracuusinhvatbien.app` và `https://cam-nang-ca-bien.vercel.app`.
- [x] **Khởi tạo & Hoàn thành 100% Pipeline Nhóm Rắn Biển Việt Nam (`ran-bien`) — 27 loài**:

  - Bóc tách kỹ thuật số 100% từ tài liệu chuyên khảo *"Rắn biển Việt Nam"* (Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng, Phan Kim Hồng, Võ Văn Quang, John C. Murphy — Viện Hải dương học Nha Trang, WAR, IOC VN, 2016).
  - Trích xuất 27 loài với 15 trường dữ liệu chuyên sâu (đặc điểm nhận dạng vảy thân/cổ/bụng, răng hàm, màu sắc, phân bố VN & thế giới, mẫu vật bảo tàng, độc tố học, tình trạng bảo tồn CITES/NĐ160/IUCN/Sách đỏ VN).
  - Nạp thành công 27/27 loài (100.0%) vào CSDL Supabase theo flat schema trực tiếp.
  - **WoRMS Sync (Bước ②)**: Chuẩn hóa danh pháp và liên kết mã AphiaID quốc tế cho 100% 27 loài (25 accepted, 2 unaccepted đã liên kết accepted name).
  - **SeaLifeBase Sync (Bước ③)**: Đồng bộ 100% 27 loài dữ liệu sinh học, độ sâu phân bố, tập tính thức ăn, độc tính và dịch thuật học thuật chuyên ngành Bò sát - Rắn biển sang tiếng Việt bằng Gemini AI.
  - **Trích xuất ảnh gốc từ sách & iNaturalist Sync (Bước ④)**: Ứng dụng thuật toán Smart Crop render DPI 250, autocrop viền trắng, nén WebP 960px và tải lên Supabase Storage bucket `species-photos/ran-bien/{species_id}/01.webp` cho 22 loài có hình trong sách; kéo thêm ảnh Research Grade từ iNaturalist cho 3 loài hiếm (Loài 2, 22, 26). Đạt **25/27 loài (92.6%)** có ảnh minh họa.
  - **Tài liệu gốc & Audit (Bước ⑤ & ⑥)**: Thêm bản ghi tài liệu chuyên khảo *Rắn biển Việt Nam* vào bảng `literature_sources` trong Supabase; audit dữ liệu 100% trường tiếng Việt và sinh học đạt chuẩn.
  - **Tích hợp Frontend Next.js 16 (Bước ⑦)**: Đăng ký collection `ran-bien` vào `STATIC_COLLECTIONS`, bổ sung metadata sách trong `lib/books-data.ts`, thêm tab Rắn biển kèm biểu tượng 🐍 trong `BottomNav.tsx`. TypeScript và Next.js build passing 100%.

- [x] **Đồng bộ Dữ liệu Sinh học SeaLifeBase v25.04 cho Nhóm Giáp Xác Biển (`giap-xac`) — 131/132 loài (99.2%)**:
  - Nghiên cứu và kết nối hệ thống dữ liệu SeaLifeBase v25.04 Parquet (102,822 loài, 68,830 sinh thái, 66,392 sinh sản, 143,101 tên đồng danh).
  - Xây dựng thuật toán đối chiếu 4 tầng (Override $\rightarrow$ Tên gốc lọc phân giống $\rightarrow$ WoRMS valid $\rightarrow$ Bảng đồng danh SeaLifeBase).
  - Tích hợp Gemini AI dịch thuật học thuật Giáp xác học (Carcinology) sang tiếng Việt hàn lâm cho 3 khối mô tả: sinh học, sinh thái, sinh sản.
  - Cập nhật trực tiếp Supabase PostgreSQL (SSOT): **131 / 132 loài (99.2%)** đã có đầy đủ trường `biology` (kích thước TL/CL, dải độ sâu, sinh cảnh, bậc dinh dưỡng, kiểu ăn, độ tổn thương sinh thái, độc tính, tên tiếng Anh).
  - Nâng cấp giao diện `BiologyDashboard.tsx`: Hỗ trợ hiển thị nhãn `SeaLifeBase`, icon vector `<Shrimp size={20} />` màu hồng san hô cho nhóm Giáp xác.
  - Đóng gói hoàn chỉnh AI Skill `.agents/skills/sealifebase-sync/` và cập nhật Bước ③ trong workflow pipeline `.agents/workflows/ocr-to-audit.md`.
- [x] **Khởi tạo & Hoàn thành 100% Pipeline Nhóm Giáp Xác Biển (`giap-xac`) — 132 loài**:
  - Bóc tách toàn diện từ sách scan *"Động vật chí Việt Nam - Tập 1: Tôm biển"* (GS. Nguyễn Văn Chung, Đặng Ngọc Thanh, Phạm Thị Dự - 2000).
  - Hoàn thành đầy đủ 87 loài thuộc Bộ Mười Chân (*Decapoda*: Tôm biển, Tôm hùm gai, Tôm mũ ni) và 45 loài thuộc Bộ Chân Miệng (*Stomatopoda*: Tôm tít).
  - Đối soát chuẩn danh pháp quốc tế WoRMS cho 100% 132 loài (96 accepted, 24 superseded combination, 7 unaccepted, 5 junior subjective synonym; 0 not_found).
  - Đã nạp thành công 132/132 loài (100.0%) vào CSDL Supabase theo flat schema trực tiếp.
  - Tích hợp giao diện Frontend: Đăng ký collection, cấu hình đầu sách, cập nhật thanh điều hướng Top Nav, Bottom Nav mobile và Next.js 16 build passing 100%.
  - **iNaturalist Sync (Bước ④)**: Nạp thành công 148 ảnh minh họa WebP 640px cho 53 loài (40.2%) lên Supabase Storage `species-photos/giap-xac/...`.
  - **Enrich Tên Gọi (Bước ⑤)**: 132/132 loài (100.0%) đã có tên tiếng Anh chuẩn.
  - **Audit Sinh Vật (Bước ⑥)**: 100% loài có đầy đủ hình thái, kích thước, phân bố, mẫu vật, sinh thái học, giá trị kinh tế, tài liệu dẫn và đồng danh.
- [x] **Tối ưu Thanh Menu Mobile (BottomNav Dock) & Đồng bộ Vector SVG (`lucide-react`)**:
  - Thay thế hoàn toàn emoji `🦐` bằng icon vector chuẩn `<Shrimp size={20} />` đồng bộ phong cách với `<Home>`, `<Fish>`, `<Leaf>`.
  - Đồng bộ icon `Shrimp` trên cả 3 vị trí điều hướng: BottomNav mobile, Top Nav desktop và AdminSidebar.
  - Tối ưu dock 400px x 62px, chống ngắt chữ (`white-space: nowrap`), căn chỉnh active dot 3.5px và bổ sung cơ chế tự hiện lại khi cuộn chạm đáy trang (`isNearBottom`).
- [x] **Deploy Production Vercel**:
  - Đã commit (`4b39cbe`), push GitHub master và deploy production thành công lên `https://www.tracuusinhvatbien.app` / `https://cam-nang-ca-bien.vercel.app`.
- [x] **Enrich 100% dữ liệu sinh học FishBase cho Danh mục Cá biển Tập 1 (Lớp Cá sụn Chondrichthyes)**: Khắc phục triệt để lỗi lệch danh pháp nhờ thuật toán đối chiếu 3 tầng (Tên thủ công $\rightarrow$ Tên gốc $\rightarrow$ Danh pháp hợp lệ WoRMS). Khớp thành công 47 loài cá mập, cá nhám, cá đuối, cá đao; dịch thuật học thuật 100% các đoạn mô tả sinh học sang tiếng Việt hàn lâm bằng Gemini AI (`gemini-3.6-flash`); cập nhật trực tiếp lên Supabase (SSOT) và đồng bộ file backup `data/species.json`.
- [x] **Đóng gói AI Skill chuyên biệt `/fishbase-sync`**: Tạo mới `.agents/skills/fishbase-sync/SKILL.md`, chuẩn hóa toàn bộ quy trình tra cứu FishBase v25.04 Parquet, dịch thuật ngữ loại học và cập nhật Supabase.
- [x] **Chuẩn hóa SEO sharing metadata**: Cập nhật toàn diện title và OpenGraph/Twitter Cards sang "Tra cứu sinh vật biển Việt Nam" trên toàn bộ trang.

## ✅ Hoàn thành (2026-09-07)
- [x] **Vá 2 lỗ hổng bảo mật nghiêm trọng (Migration 009)**: Khắc phục đệ quy vô hạn trên bảng `user_roles` bằng hàm `is_admin()` `SECURITY DEFINER`; kích hoạt RLS toàn diện trên bảng `audit_log`, chuyển `AuditLog.tsx` sang API route server-side an toàn (`/api/audit-log`).
- [x] **Hardening bảo mật hạ tầng**: Bổ sung `Strict-Transport-Security` (HSTS 1 năm, preload) và `Permissions-Policy` vào `next.config.ts`; chuẩn hóa domain canonical trong `app/robots.ts` và `app/sitemap.ts` sang `www.tracuusinhvatbien.app`.
- [x] **Xác thực dữ liệu đầu vào bằng Zod (`lib/schemas.ts`)**: Áp dụng Zod schema validation chặt chẽ cho toàn bộ API routes (`POST /api/species`, `PATCH /api/species`, `POST /api/species/import`), loại bỏ hoàn toàn nguy cơ chèn trường độc hại (mass assignment).
- [x] **Tái thiết kế trang đăng nhập Admin (`/login`) chuẩn `/hallmark` & `/ui-ux-pro-max`**: Triển khai Phương án 2 (Centered Vault Card) với nền biển sâu Oxford Navy, font Lora upright + Be Vietnam Pro, toggle ẩn/hiện mật khẩu SVG, loading spinner và thông báo lỗi rõ ràng; tạo file CSS độc lập `styles/auth.css` khắc phục dứt điểm lỗi mất style trang login.
- [x] **Tái thiết kế toàn bộ phân hệ Admin (`/admin`) chuẩn `/hallmark` & `/ui-ux-pro-max`**:
  - Dọn sạch 100% trùng lặp CSS giữa `admin.css` và `admin-dashboard.css`, gỡ bỏ class login cũ, đồng bộ sang tokens OKLCH.
  - Nâng cấp `AdminSidebar`: thương hiệu uy nghiêm, nút "← Ra trang tra cứu", badge đếm số lượng thời gian thực.
  - Nâng cấp `AuthStatus`: user card sang trọng với avatar chữ cái, role badge `QUẢN TRỊ VIÊN`, nút đăng xuất tinh tế.
  - Nâng cấp `AdminDashboard`: Bento KPI grid 4 thẻ, Volume bar chart đa sắc theo chuẩn tập sách (`--color-vol-1` đến `--color-vol-5`), bảng Audit Log format chi tiết thông minh thay cho chuỗi JSON thô.
  - Nâng cấp `SpeciesTable`: Toolbar phân tách mạch lạc, ô tìm kiếm có nút xóa nhanh, phân trang đầy đủ.
- [x] **Cải tiến thao tác sửa loài trong `SpeciesTable`**: Click trực tiếp vào Tên tiếng Việt hoặc Tên khoa học sẽ mở ngay Form/Modal chỉnh sửa toàn diện của loài (kèm hiệu ứng hover bút chì cyan và trạng thái tải dữ liệu chi tiết).
- [x] **Deploy Production Vercel**: Đã commit (`b197d3d`) và deploy production thành công lên `https://www.tracuusinhvatbien.app` (`cam-nang-ca-bien.vercel.app`). Chuẩn hóa toàn bộ SEO sharing title sang "Tra cứu sinh vật biển Việt Nam".

## ✅ Hoàn thành (2026-09-06)
- [x] **Khắc phục lệch text & tràn viền Hero Stats trên Mobile theo /hallmark**: Chuyển đổi `.hero__stats` sang CSS Grid 3 cột đối xứng 100% (`minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr)`), căn giữa hoàn hảo cột Họ (`168 Họ`) tại trung tâm card, co giãn Type Scale clamp cho số liệu và nhãn chữ `Tài liệu gốc`, triệt tiêu dứt điểm lỗi tràn viền và lệch trục trên mọi kích thước màn hình điện thoại (320px - 414px).
- [x] **Responsive Mobile Thẻ Định Danh Tên Gọi (.specimen-identity-card)**: Chuyển sang bố cục dọc 2 hàng độc lập trên mobile (<= 640px) kèm đường kẻ chấm hairline tinh tế chuẩn `/hallmark`, khắc phục triệt để lỗi rớt từng chữ xuống dòng và tràn mép màn hình.
- [x] **Khóa thẳng hàng đường chân chữ (Baseline) Thẻ Định Danh Tên Gọi**: Đổi `.specimen-identity-label` thành `display: inline-block`, icon SVG dùng `vertical-align: -1.5px`, `.specimen-identity-col` dùng `align-items: baseline; gap: 6px;` giúp nhãn in hoa và giá trị chữ thường bám phẳng tắp trên cùng một đường chân chữ.
- [x] **Tách `globals.css` (124KB) thành 11 CSS modules**: Tách CSS monolith thành 11 modules (`hero.css`, `browse.css`, `catalogue.css`, `specimen.css`, `responsive.css`, `about.css`, `buttons.css`, `mobile.css`, `faq.css`, `book-browser.css`, `dark-mode.css`) tối ưu hóa dung lượng tải theo từng trang.
- [x] **Khắc phục lỗi 404 trang chi tiết loài**: Revert query Supabase về `SELECT *` sau khi danh sách explicit column gây lỗi cột không tồn tại.
- [x] **Khắc phục cảnh báo React 19 Script**: Inline script chống giật sáng trực tiếp trong `<head>` layout.
- [x] **Khôi phục layout 3 block ngang hàng WoRMS Dossier**: Bỏ class `worms-tile--full`, cấu hình lưới Grid 3 cột song song (`repeat(3, minmax(0, 1fr))`) trên desktop giúp 3 block (Trạng thái danh pháp, Mã AphiaID, Danh pháp hiện hành) đứng thẳng hàng cân đối chuẩn `/hallmark`.
- [x] **Khắc phục lỗi unclosed brace trong globals.css**: Đóng đúng dấu `}` cho selector `.specimen__photo-dots`, cân bằng hoàn hảo 100% toàn bộ 5,190 dòng CSS, khôi phục toàn diện giao diện desktop trên Vercel Production.
- [x] **Cập nhật thương hiệu Top Nav**: Đổi nhãn logo từ "Bảo tàng Hải dương học" thành "Tra cứu sinh vật biển" (`components/layout/Nav.tsx`).
- [x] **Cân đối Type Scale danh sách loài trang con**: Hạ font size & weight của tên loài tiếng Việt (`0.88rem`, weight 600) và tên Latinh (`0.84rem`, italic, weight 500) trong bảng danh mục loài (`SpeciesGrid`), Cây phân loại (`TaxonomyTree`) và Tìm kiếm (`GlobalSearch`), giảm đệm hàng còn `7px` giúp bảng thanh thoát, gọn gàng chuẩn monograph `/hallmark`.
- [x] **Tinh gọn khoảng cách dọc Mobile Tab Phân loại**: Loại bỏ nút mở CSDL WoRMS trùng lặp ở header Card, gỡ bỏ padding inline cứng trên các ô WoRMS, co gọn khoảng cách node cây phân loại và đệm card giúp chiều cao cuộn trên mobile giảm gần 40%.
- [x] **Chuẩn hóa Bento Tab Thông số**: Bố cục 2 cột song song (Phương án A), chuẩn hóa typography `Lora` + `Be Vietnam Pro` + `JetBrains Mono` theo `tokens.css`.
- [x] **Bảo tồn dữ liệu thực địa sách gốc OCR**: Ràng buộc trích xuất 100% từ dữ liệu gốc Viện Hải dương học Nha Trang, loại bỏ triệt để tiếng Anh và dữ liệu dịch thuật của FishBase/GBIF khỏi tab Thông số.
- [x] **Khắc phục lỗi ngắt dòng sớm / từ mồ côi**: Triệt tiêu `--measure: 68ch` trên `<p>`, áp dụng `max-width: none` và `text-wrap: pretty` chuẩn `/hallmark`.
- [x] **Chuẩn hóa danh pháp sinh học quốc tế (ICZN/ICN)**: Bắt buộc Tên Chi + Loài in nghiêng (*Italics*), Tên tác giả + Năm công bố đứng thẳng (*Roman/Upright*).
- [x] **Tái thiết kế Khối WoRMS (.worms-pill)**: Chuyển đổi khối alert banner cồng kềnh thành Huy hiệu vi kiểm định dạng viên thuốc (Pill) thanh mảnh 24px đặt cùng hàng với tên khoa học (`.specimen__sci-row`), chống lỗi dính icon và bảo vệ màu sắc kép (inline + `globals.css`).

## ✅ Migration Next.js — HOÀN THÀNH (2026-08-19)

- [x] **Phase M0** — Scaffold Next.js 16, TypeScript, Supabase clients, Nav/Footer/Layout
- [x] **Phase M1** — Port 4 trang: GlobalSearch, SpeciesGrid, TaxonomyTree, SpecimenCard
- [x] **Phase M2** — Multi-collection: DB collections table, collection_id FK, dynamic routing
- [x] **Phase M3** — Admin CRUD: API routes, SpeciesTable, SpeciesForm 4-tab, 26 trường
- [x] **Phase M4** — Auth: middleware /admin/*, Login page, Logout, AuthStatus, user_roles RLS
- [x] **Phase M5** — SEO: OG/Twitter, sitemap.xml, robots.txt, redirects, 404, PWA manifest
- [x] **SQL migrations**: 001 (collections) + 002 (collection_id) + 003 (user_roles) — đã chạy
- [x] **Admin role seed**: haitrinh082@gmail.com đã có role admin

> App: `next-app/` — `npm run dev` → localhost:3001



## ✅ Hoàn thành

### Kiến trúc Web App
- [x] Thiết kế lại kiến trúc: 4 file HTML duy nhất (`index.html`, `tap.html`, `browse.html`, `species.html`)
- [x] Tất cả dữ liệu tập trung vào `data/species.json` + `data/taxonomy_tree.json`
- [x] Xóa hoàn toàn các file static `tap-1.html` ... `tap-5.html` (legacy)
- [x] Schema thống nhất cho `species.json`: `specs.vn`, `specs.en`, `synonyms[]`
- [x] Viết lại `scripts/build_database.py` — đọc trực tiếp từ OCR parsed JSON

### OCR & Chuẩn hóa dữ liệu
- [x] Tập II: 266/266 loài (OCR thủ công + chuẩn hóa + upload Supabase hoàn tất)
- [x] Tập III: 518 loài (OCR + parse hoàn tất, `scratch/tap3_parsed_details.json`)
- [x] Tập IV loài 1-100: OCR + chuẩn hóa thủ công hoàn tất
- [x] Tập V: 199 loài (OCR thô, `scratch/tap5_parsed_details.json`)
- [x] Thực vật biển (Tập I — Thực Vật Biển Thường Thấy ở Phía Nam VN, Tsutsui et al.): 201 loài hoàn tất (100% AlgaeBase & Biology song ngữ).
- [x] Thực vật biển (Tập II — Rong biển Việt Nam, GS. Phạm Hoàng Hộ, 1969): 471/471 loài (100.00% HOÀN TẤT TUYỆT ĐỐI CẢ 4 PHẦN kèm 471 ảnh tiêu bản minh họa 300 DPI, 100% WoRMS AphiaID, 100% AlgaeBase ID & Sinh học song ngữ và tên tiếng Anh chuẩn).


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

### Phase 3 — Hallmark Redesign (2026-08-19)
- [x] Full redesign 4 HTML theo Hallmark macrostructures (Workbench + Catalogue + LongDocument + Marquee)
- [x] Rewrite `tokens.css` v3.0: OKLCH, Perfect-Fourth scale, 80+ tokens
- [x] Rewrite `shared.css`: 1318 lines, full audit-clean component system
- [x] Hallmark self-audit: fix 3 critical + 4 major + 4 minor anti-patterns
- [x] Font: Instrument Serif → **Lora** (full Vietnamese subset)
- [x] Nav layout: 1/3 logo | 2/3 links, same row, `flex:1`/`flex:2`
- [x] Nav đồng bộ 3 links trên tất cả 4 trang
- [x] Xóa `public/*.html` cũ (Aug 14) — root cause Vite serve wrong file

---

## 🛣️ Upgrade Plan v3.0 — 4 Phases

> Source: Implementation Plan 2026-08-19

### Phase 1 — Redesign UI + Song ngữ VN/EN
- [x] Redesign CSS: design system, tokens, Hallmark macrostructures *(done 2026-08-19)*
- [x] Font: Lora (Vietnamese subset), Be Vietnam Pro giữ nguyên *(done 2026-08-19)*
- [x] Light/dark mode toggle (`[data-theme="light"]` / `[data-theme="dark"]`) *(done 2026-08-19)*
- [x] I18n module nhẹ: `src/lib/i18n.js` + `locales/vi.json` + `locales/en.json` *(done 2026-08-19)*
- [x] Thêm toggle VN/EN trên header (lưu `localStorage`) *(done 2026-08-19)*
- [x] Dịch label UI: menu, button, placeholder, heading cho 4 trang HTML *(done 2026-08-19)*
- [x] Deploy Phase 1 lên Vercel *(done 2026-08-20 - Next.js live)*

### Phase 2 — Admin Panel CRUD hoàn chỉnh
- [x] Modal Form CRUD loài: 26+ trường, chia tab (Cơ bản / Phân loại / VN / EN / Ảnh), hỗ trợ morphology, ecology, economic_value *(done)*
- [x] Soft-delete: `deleted_at` thay vì xóa thật, hỗ trợ khôi phục tại chỗ *(done)*
- [x] JSON Import: parse → preview → confirm → batch upsert Supabase *(done)*
- [x] Audit Log: bảng audit_log + component AuditLog + server route logging *(done)*
- [x] Admin dashboard: thống kê nhanh (tổng loài, theo tập, thống kê ảnh) *(done)*
- [ ] CSV Import: bổ sung parser CSV bên cạnh JSON
- [ ] Inline edit nhanh: double-click ô bảng → sửa tại chỗ
- [x] Deploy Phase 2 lên Vercel *(live)*

### Phase 3 — Phân quyền User + Đăng ký
- [ ] Enable Supabase Auth (email/password)
- [ ] Trang `register.html` hoặc modal đăng ký (role mặc định: `viewer`)
- [x] (1) Fix Vercel cache issue + Fix OCR structure & Supabase sync
- [x] (2) Audit data + Synonyms Enrichment for Cá biển (Batch)
- [x] (3) Hoàn thiện layout trang chủ & card detail (CSS / Design System)
- [x] (4) Bổ sung 201 Loài Thực Vật Biển (OCR, WoRMS, Tách tên thường gọi)
- [ ] (5) Admin Panel Phase 2 (CRUD form, soft delete, CSV import)
- [ ] Deploy Phase 3

### Phase 4 — Polish + Deploy Production
- [ ] Test mobile: iOS Safari, Android Chrome
- [ ] Test phân quyền: viewer/editor/admin
- [ ] Test CSV import với file thực tế
- [ ] Lazy load Supabase client + Vite code splitting
- [ ] PWA cache strategy review
- [ ] Final deploy Vercel + smoke test production URL

### Mobile UI Overhaul (2026-07-24 chiều)
- [x] Audit + fix 6 lỗi mobile: header stack, logo overflow, nav wrap, card padding, panel separator, fb-link
- [x] Fix logo mobile: `.logo-full` / `.logo-short` 2 span toggle CSS
- [x] Fix taxonomy badge: word-break + flex-wrap + max-width
- [x] Tạo skill `deploy-cabien` (sync + git push + vercel CLI)
- [x] Setup git repo + .gitignore + vercel.json cho project

### Polish UI & About Page (2026-08-23)
- [x] Đồng bộ padding, typography 3 tab (Thông số, Sinh học, Phân loại) trên mobile.
- [x] Chuyển đổi giao diện desktop sang Tab UI.
- [x] Cắt giảm khoảng trắng thừa ở homepage (hero & browse section).
- [x] Cập nhật Footer (link VNIO, iNaturalist, version).
- [x] Xây dựng trang `/about` chuẩn Hallmark (Long Document), deploy Vercel.

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
- [x] Tập IV loài 101-316: OCR + chuẩn hóa thủ công hoàn tất
- [x] Tập V: dữ liệu thô chưa được chuẩn hóa (tên VN bị lỗi, taxonomy trống) -> Đã hoàn thành (279/279 loài chuẩn hóa và đưa lên Supabase)
- [x] Tập VI: OCR + đưa lên Supabase (Atlas cá rạn san hô Việt Nam, 263 loài) hoàn tất
- [ ] Tập I: chưa có dữ liệu OCR parsed JSON (chỉ có PSV cũ cho 50 loài Tập I)

### Chất lượng dữ liệu
- [x] `commonName` (EN) — Tập II: 232/266, Tập III: 518/518 ✅
- [x] `alternateNames` (VN) — Tập II: 240/266, Tập III: 246/518 (đúng bản chất)
- [x] Tập III — đã re-OCR toàn bộ 518 loài cực kỳ chuẩn xác và đưa lên Supabase (2026-08-04)
- [x] Deploy bản Next.js mới nhất lên Vercel (Hoàn tất 2026-08-20)
- [x] WoRMS sync cho Thực vật biển: Toàn bộ 201 loài đã hoàn tất.
- [x] WoRMS sync cho toàn bộ 6 tập Cá biển (Tập I-VI): Đạt 100.00% (1.764 / 1.764 loài, 2026-09-03)
- [x] Giai đoạn B (Làm giàu sinh học FishBase): Đạt 100.00% (1.764 / 1.764 loài, 2026-09-03)
- [x] Xây dựng trang FAQ (/faq) và tái thiết kế trang About (/about) chuẩn Hallmark (2026-09-03)
- [x] Tối ưu typography, hierarchy 3 tab và responsive iPad/Mobile (2026-09-03)
- [x] Dọn sạch phantom row loài 78 Tập IV (soft-delete bản ghi rỗng không có trong sách)
- [x] Xóa 17 bản sao duplicate thực vật biển (idx 202-218) — 2026-08-22
- [x] Bổ sung vn_name 26 loài rong biển từ PDF gốc — 2026-08-22

### Tên VN rong biển còn thiếu (~17 loài chưa tra sách)
- [ ] Spyridia filamentosa (idx=17) — trang sách?
- [ ] Spyridia hypnoides (idx=18) — trang sách?
- [ ] Dasyaceae sp.1/2/3 (idx=19-21) — sách ghi "chưa có tên VN"?
- [ ] Hypoglossum barbatum (idx=22)
- [ ] Acanthophora spicifera (idx=23)
- [ ] Bostrychia tenella (idx=24)
- [ ] Chondria armata (idx=25)
- [ ] Chondria ryukyuensis (idx=26)
- [ ] Amansia rhodantha (idx=35)
- [ ] Tolypiocladia glomerulata (idx=36)
- [ ] Rhodophyta sp.1/2/3 (idx=37-39) — sách ghi "chưa có tên VN"?
- [ ] Thalassia hemprichii (idx=46)
- [ ] Cheilosporum spectabile (idx=132)
- [ ] Hydrolithon samoense (idx=133)
- [ ] Mesophyllum erubescens (idx=137)
- [ ] Sporolithon sp. (idx=138)
- [ ] Tylotus sp. (idx=145)
- [ ] Chondracanthus intermedius (idx=146)
- [ ] Carpopeltis maillardii (idx=152)
- [ ] Yonagunia formosana (idx=157)
- [ ] Stenopeltis setchelliae (idx=167)
- [ ] Portieria hornemannii (idx=168)
- [ ] Portieria japonica (idx=169)

### Xác nhận sách ghi "chưa có tên VN" (GIỮU NGUYÊN)
- [x] Gracilaria textorii (idx=1) — không có trong sách
- [x] Laurencia concreta (idx=27) — sách ghi chưa có
- [x] Tricleocarpa cylindrica (idx=118) — sách ghi chưa có
- [x] Ganonema farinosa (idx=119) — sách ghi chưa có
- [x] Helminthocladia australis (idx=120) — sách ghi chưa có
- [x] Trichogloeopsis sp. (idx=125) — sách ghi chưa có
- [x] Cheilosporum acutilobum (idx=131) — sách ghi chưa có

### Admin Panel (Hướng 1: Supabase Auth + Dashboard)

#### Phase 1 — Vá RLS (ưu tiên cao)
- [x] Sửa RLS policy: xóa "Service write access" mở toang
- [x] Tạo policy mới: chỉ `service_role` hoặc authenticated user có role admin mới write được
- [x] Test: confirm anon key chỉ SELECT, không INSERT/UPDATE/DELETE

#### Phase 2 — Auth + Admin UI
- [ ] Enable Supabase Auth (email/password hoặc Google OAuth)
- [ ] Tạo bảng `profiles` (id, email, role: admin/editor/viewer, created_at)
- [x] Viết migration `004_create_profiles.sql`
- [x] Xây `/admin.html` — danh sách loài + tìm kiếm/lọc
- [ ] Form thêm/sửa/xóa loài (CRUD đầy đủ)
- [ ] Bulk import từ CSV/JSON
- [ ] Audit log (ai sửa gì, lúc nào)

#### Phase 3 — Multi-user (tương lai)
- [ ] Phân quyền editor: chỉ sửa loài mình phụ trách
- [ ] Admin toàn quyền
- [ ] Invite system cho collaborators

### Tối ưu Hiệu năng & Core Web Vitals (2026-09-03)
- [x] Audit kích thước ảnh: 100% WebP, TB 23.5 KB/ảnh, 0% > 150 KB.
- [x] Giai đoạn 1: Bật ISR 24h & React cache() dedup query cho trang Chi tiết loài.
- [x] Giai đoạn 1: Bỏ JOIN species_photos thừa trong SpeciesGrid (tiết kiệm 41.8% payload JSON).
- [x] Giai đoạn 1: Thêm decoding="async" & width/height cho ảnh thẻ loài.
- [x] Giai đoạn 2: Prefetch cây phân loại trên Server Component kết hợp ISR 24h (loại bỏ client fetch 2,000 dòng).
- [x] Giai đoạn 2: Tối ưu LCP PhotoGallery với fetchPriority="high" & decoding="async".
- [x] Giai đoạn 2: Bổ sung vn_alternate_names và lọc deleted_at trong GlobalSearch.
- [x] Giai đoạn 2: Tối ưu đếm số Họ từ taxonomy_tree trên trang chủ.
- [x] Tái thiết kế trang `/ca-bien`: Tích hợp GlobalSearch cross-tập cho 1,764 loài.
- [x] Phân nhóm theo 2 đầu sách chính quy: Danh mục Cá biển VN (5 tập) & Atlas Cá rạn san hô VN (Tập VI).
- [x] Chuyển đổi toàn bộ sang Compact List View (STT - Tên VN - Tên khoa học), giảm 99% data transfer, load <100ms.
- [x] Fix khoảng thở padding-top cho layout container tránh dính navbar cố định; đồng bộ 100% màu sắc và layout Card Hero trang cá biển.

### Session 2026-09-04
- [x] Scroll position restoration — quay lại đúng vị trí loài sau khi xem chi tiết
- [x] Ẩn section "Các tập" khi sách chỉ có 1 tập (Atlas, Rong biển Tsutsui, PHH)
- [x] Quản lý tài liệu gốc từ Admin — bảng `literature_sources` + CRUD page + smart dropdown
- [x] Fix logo bị mất production — `.gitignore` thiếu exception `!public/logo.png`
- [x] Fix RLS infinite recursion — migration `008b_fix_literature_rls.sql`
- [x] Insert 4/4 bộ sách tham khảo vào DB `literature_sources`
- [x] Triển khai SEO toàn diện, Favicon (`favicon.ico`) đa kích thước & OpenGraph Default Thumbnail (`public/og-default.png`) 1200x630
- [x] Tích hợp Dynamic OpenGraph Thumbnail cho từng loài sinh vật biển khi share link (Zalo, Facebook, Twitter, iMessage)
- [x] Tích hợp Schema.org Structured Data: WebSite & Organization (trang chủ) + Taxon (chi tiết loài)
- [x] Nâng cấp Dynamic Sitemap cho toàn bộ collections, trang tĩnh và 2.436+ loài
- [x] Cập nhật tên PWA thành SVBVN (`site.webmanifest`, `apple-mobile-web-app-title`, `application-name`)
- [x] Xây dựng Popup / Modal hướng dẫn cài đặt app lên điện thoại (`PwaInstallPrompt.tsx`) cho người dùng mới
- [x] Sửa triệt để lỗi hiển thị font Tiếng Việt: chuyển sang self-hosted `next/font/google` (Lora, Be Vietnam Pro), loại bỏ @import CDN và chuẩn hóa fallback font stack an toàn

### Session 2026-09-05 (Sáng)
- [x] Tích hợp 37 AI Skills Toàn Cục (Engineering, TDD, Productivity) từ Matt Pocock
- [x] Refactor module sâu (Deepening): `lib/taxonomy.ts` (xóa 42 dòng trùng lặp), `lib/species-query.ts`, `lib/species-photos.ts`, gộp `collections-static.ts`
- [x] Triển khai Khám phá 4 Chuyên đề Sinh thái & Bảo tồn trên trang chủ (`SpecialGroupsSection.tsx`) kết nối dữ liệu Supabase thật: Rạn san hô (195 loài), Nguy cấp IUCN (120 loài), Cá sụn (52 loài), Thực vật biển (672 loài)
- [x] Tích hợp Banner Chuyên đề (`SpecialGroupBanner`) trong `SpeciesGrid.tsx` với chế độ xem chuyên đề, ẩn bộ chọn sách và nút quay lại sách gốc
- [x] Chuẩn hóa toàn bộ IUCN Badge trên toàn hệ thống theo code phần Sinh học (`IucnBadge.tsx` SSOT): badge chữ nhật bo góc, màu chuẩn quốc tế, không icon unicode dính chữ
- [x] Sửa lỗi hiển thị nút "Quay lại theo sách gốc" trên banner chuyên đề (`SpecialGroupBanner.css` + inline fallback + icon ArrowLeft)
- [x] Nâng cấp Thước đo kích thước tương quan (`SpecimenVisualWidgets.tsx`): tự động nhận diện `mm` (tự chia 10 ra `cm`), `cm`, `m`, từ khóa "lớn nhất/tối đa" và thang đo thích ứng 0-40cm, 0-1m, 0-5m+

### Session 2026-09-05 (Tối)
- [x] Sao lưu an toàn các component loài vào thư mục `.backups/`.
- [x] Khôi phục nguyên bản `SpecimenCard.tsx`, `SpecimenVisualWidgets.tsx`, `SpecimenVisualWidgets.css` về commit `59c4dc5` (bản ổn định chuẩn đẹp).
- [x] Đánh giá toàn diện trang `SpecimenCard` theo `/hallmark` & `/ui-ux-pro-max`, đề xuất Phương án A (Lưới Bento 2 cột).
- [x] Tạo `SpecimenCard.css` chuẩn Design System Typography (`Be Vietnam Pro` body 1.6 line-height, `Lora` display heading, `JetBrains Mono` code/citations, dark mode).
- [x] Triển khai cấu trúc Bento Archive trong `SpecimenCard.tsx`: Thẻ định danh tên gọi, Lưới 2 cột Hình thái & Sinh thái, Thẻ Giá trị kinh tế, Thẻ Hồ sơ Mẫu vật & Danh mục tài liệu dẫn.
- [x] Kiểm tra biên dịch TypeScript (`npx tsc --noEmit`) đạt 100% exit code 0.



### Session 2026-09-06 (Sáng)
- [x] Build Knowledge Graph toàn bộ codebase bằng /understand — 183 files, 405 nodes, 455 edges, 8 layers, 12 tour steps (2026-09-06)
- [x] Dashboard tại http://127.0.0.1:4242 (chạy manually: cd ~/.understand-anything-plugin/packages/dashboard && npm run dev)

### Session 2026-09-11
- [x] Khởi tạo collection `than-mem` (Thân mềm / Mollusca) và OCR thí điểm 74 loài Họ Ốc sứ (Cypraeidae) từ Hylleberg 2003.
- [x] Đồng bộ và chuẩn hóa dữ liệu Sinh học SeaLifeBase v25.04 cho 74 loài Họ Ốc sứ (`scripts/sync_thanmem_sealifebase.py`).
- [x] Nâng cấp `BiologyDashboard.tsx`: Thêm nhận diện `isMollusc`, icon `Shell`, hiển thị huy hiệu SeaLifeBase và kích hoạt đầy đủ 3 khối chuyên đề.
- [x] Đồng bộ 210 ảnh nghiên cứu từ iNaturalist vào Supabase Storage (`species-photos/than-mem/`) và bảng `species_photos`.
- [x] Nâng cấp `PhotoGallery.tsx`: Hiển thị credit bản quyền iNaturalist, hỗ trợ fallbackCredit khi chỉ có ảnh đơn.

