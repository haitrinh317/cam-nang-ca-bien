-- Migration 013: Cột đã chuẩn hóa cho bộ lọc nâng cao (đợt 1: IUCN, độ sâu, kích thước)
-- Run on Supabase SQL Editor (một lần, an toàn chạy lại: IF NOT EXISTS)
-- Date: 2026-10-03
--
-- Chỉ THÊM cột (cho phép NULL) — không đổi/xóa dữ liệu gốc.
-- Các cột được điền bởi `node scripts/derive_filter_cols.mjs --apply` từ biology.* gốc.
-- Cột thường, KHÔNG dùng generated column: script OCR/enrich đọc `*` rồi upsert lại
-- sẽ lỗi "cannot insert into generated column". Sau mỗi đợt OCR/enrich cần chạy lại script.
--
--   iucn_code       LC/NT/VU/EN/CR/EW/EX/DD/NE  (từ biology.iucnStatus; KHÔNG phải conservation_status
--                   — cột đó chỉ là độ phổ biến common/uncommon/rare/unknown)
--   depth_min/max   mét; NULL = không có dữ liệu. "đến 30 m" -> min NULL (coi như 0 khi lọc)
--   max_length_cm   cm (đã đổi từ mm); NULL = không có dữ liệu hoặc không rõ đơn vị

ALTER TABLE public.species
  ADD COLUMN IF NOT EXISTS iucn_code text,
  ADD COLUMN IF NOT EXISTS depth_min numeric,
  ADD COLUMN IF NOT EXISTS depth_max numeric,
  ADD COLUMN IF NOT EXISTS max_length_cm numeric;

COMMENT ON COLUMN public.species.iucn_code IS 'IUCN code chuẩn hóa từ biology.iucnStatus (derive_filter_cols.mjs)';
COMMENT ON COLUMN public.species.depth_min IS 'Độ sâu tối thiểu (m), NULL = không có/không rõ';
COMMENT ON COLUMN public.species.depth_max IS 'Độ sâu tối đa (m), NULL = không có';
COMMENT ON COLUMN public.species.max_length_cm IS 'Kích thước tối đa (cm), NULL = không có/không rõ đơn vị';
