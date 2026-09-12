# Memory — Tra Cứu Thông Tin Sinh Vật Biển Việt Nam

> **Cập nhật:** 2026-09-13 | **Production:** https://www.tracuusinhvatbien.app
> **SSOT:** Supabase PostgreSQL — file local chỉ là cache/backup cũ.

---

## 🎯 Tầm nhìn dài hạn

**Một cơ sở dữ liệu sinh vật biển Việt Nam thống nhất** — không phải nhiều bộ sưu tập rời rạc, mà là 1 DB tập trung nơi mỗi loài chỉ có **1 hồ sơ duy nhất** được làm giàu từ nhiều nguồn tài liệu.

### Nguyên tắc kiến trúc cốt lõi

1. **Taxonomy-First / Merge Đa Nguồn**: Khi một loài xuất hiện trong nhiều đầu sách (VD: cá nóc vừa có trong *Danh mục Cá biển VN* vừa có trong *Sinh vật độc biển VN*), thông tin được **merge** vào 1 bản ghi duy nhất neo bằng AphiaID (WoRMS). Trường `vn_literature` ghi nhận tất cả nguồn bằng dấu `;`. Không tạo bản ghi trùng lặp.

2. **Frontend-Backend Parity**: Mọi trường dữ liệu hiển thị trên trang chi tiết loài (frontend) **PHẢI** có mặt trong biểu mẫu chỉnh sửa loài ở Admin (backend). Đảm bảo khi export database, dữ liệu xuất ra khớp 100% với giao diện hiển thị — không có trường "ẩn" chỉ hiện trên UI mà Admin không sửa được, và ngược lại.

3. **Phân bố theo Vùng biển**: Chuẩn hóa dữ liệu phân bố loài theo vùng biển Việt Nam (bảng `marine_regions` + `species_regions`), hướng tới **bản đồ tương tác đa dạng sinh học** — đặc biệt khu vực **Hoàng Sa - Trường Sa**. Xem plan chi tiết: `.agents/plans/backlog--ban-do--da-dang-sinh-hoc.md`

4. **Deep Module & Unified Registry**: Mọi thông tin định danh collection, sách OCR gốc (`books`) và nhóm chuyên đề (`specialGroups`) được tập trung duy nhất tại `lib/collection-registry.ts` (client) và `lib/collection-registry-server.ts` (server). Tránh phân mảnh dữ liệu cấu hình ra nhiều file nông.

---

## 📊 Kiểm Kê Dữ Liệu — 2,787 loài

| Collection | Loài | WoRMS | Trạng thái |
|---|:---:|:---:|---|
| `ca-bien` (Tập I-VI) | 1,764 | 100% | ✅ Hoàn chỉnh + Hợp nhất 21 loài cá độc |
| `thuc-vat-bien` (Tập 1-2) | 672 | 100% | ✅ Hoàn chỉnh (201 + 471 ảnh tiêu bản) |
| `giap-xac` | 132 | 100% | ✅ 99.2% SeaLifeBase + 40% ảnh iNat |
| `ran-bien` | 27 | 100% | ✅ Hợp nhất Đa Nguồn + 100% Độc học PIB |
| `sinh-vat-doc` | 76 | 100% | ✅ 100% Toxicology + 80 ảnh thực địa |
| `than-mem` (Pilot Ốc sứ) | 74 | 100% | ✅ 85% SeaLifeBase + 210 ảnh iNat |
| `san-ho` | 42 | 97.6% | ✅ Khuyết trang 102 (loài 30) |

---

## 🏗️ Tech Stack & Routes

```
Next.js 16 (App Router) + React 19 + TypeScript
Supabase (PostgreSQL + RLS + Auth + Storage)
CSS: Vanilla CSS (tokens.css + globals.css + admin.css)
Deploy: git push origin master + vercel --prod --yes
```

| Route | Chức năng |
|---|---|
| `/` | Landing + GlobalSearch + Literature cards |
| `/:collection` | Duyệt theo đầu sách, Compact List View |
| `/:collection/taxonomy` | Cây phân loại |
| `/:collection/:speciesId` | Chi tiết loài (ISR 24h) |
| `/admin` | Dashboard stats |
| `/admin/:collection` | CRUD loài |
| `/admin/literature` | CRUD tài liệu gốc |
| `/api/species` | REST API (role-check) |
| `/api/revalidate-home` | Flush ISR cache trang chủ |

---

## 🗄️ Supabase DB

| Table | Mô tả |
|---|---|
| `species` | 2,787 loài, `collection_id` FK, flat schema |
| `species_photos` | Ảnh loài (Storage bucket `species-photos`) |
| `collections` | 7 collection: ca-bien, thuc-vat-bien, giap-xac, ran-bien, sinh-vat-doc, than-mem, san-ho |
| `literature_sources` | Sách tham khảo hiển thị trên homepage |
| `user_roles` | admin/editor/viewer — `haitrinh082@gmail.com` = admin |
| `audit_log` | Nhật ký thay đổi (jsonb old/new) |

**Migrations:** 001→009 (xem `migrations/` cho chi tiết)

---

## 🔐 Bảo mật

- `is_admin()`: SECURITY DEFINER — bypass RLS trên `user_roles`
- RLS: write locked cho `service_role` + authenticated admin
- API routes: POST/PATCH/DELETE verify admin role
- Middleware: `/admin/*` → redirect `/login`

---

## ⚠️ Vercel Account

| Mục | Giá trị |
|---|---|
| **Account ĐÚNG** | `haitrinh082@gmail.com` / `haitrinh082-6335s-projects` |
| **Account SAI** | `haitrinhnt@gmail.com` — KHÔNG DÙNG |

⚠️ GitHub push chỉ tạo preview. Phải `vercel --prod --yes` để lên production.

---

## 📝 Quy tắc quan trọng

- **SSOT**: Supabase. File local JSON chỉ là backup cũ.
- **Frontend–Backend Parity**: Dữ liệu hiển thị ở Frontend (WoRMS, Synonyms, Biology) được hỗ trợ xem và chỉnh sửa có kiểm soát trong Admin (tab Đồng bộ, merge JSONB an toàn).
- **OCR**: KHÔNG báo tiến độ ảo — chỉ báo khi đã upsert thành công
- **RLS**: KHÔNG reference bảng có RLS trong policy (gây infinite recursion)
- **Hợp nhất Đa Nguồn**: Một loài = 1 hồ sơ, neo phân loại học, gom `vn_literature` bằng dấu `;`
- **Thực vật biển**: dùng "Chi" thay cho "Giống" (taxonomy)
- **Thương hiệu**: `haitrinh` — cá nhân độc lập, không gắn cơ quan nhà nước

---

## 📂 Cấu trúc chính

```
OCR Document/                    ← Next.js project root
├── app/                         ← Routes & pages
├── components/                  ← React components
├── lib/                         ← Utilities
├── styles/                      ← CSS (tokens + globals + admin)
├── public/                      ← Static assets
├── scripts/                     ← Active scripts (13 file)
│   └── archive/                 ← Scripts one-shot đã dùng xong
├── migrations/                  ← SQL 001-009
├── _offline/                    ← Data offline (gitignored)
│   ├── data/                    ← Cache FishBase/SeaLifeBase
│   └── logs/                    ← Nhật ký phiên làm việc
├── .agents/                     ← AI skills + memory + plans
│   ├── plans/                   ← Kế hoạch triển khai (xem _index.md)
│   ├── memory/                  ← Patterns, corrections, preferences
│   ├── skills/                  ← OCR, sync, audit skills
│   └── rules/                   ← Quy tắc agent
└── Memory.md / todo.md          ← Agent context
```

> 📜 Lịch sử quyết định: `.agents/memory/decisions-archive.md`
> 📋 Kế hoạch triển khai: `.agents/plans/_index.md`
