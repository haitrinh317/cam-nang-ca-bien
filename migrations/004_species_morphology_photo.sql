-- Migration 004: Add morphology + photo data columns
-- Shared across ALL collections (ca-bien, thuc-vat-bien, future...)
-- Date: 2026-08-20
--
-- Rationale:
--   morphology_vn/en: Hình thái học — cá biển lấy từ FishBase, rong biển từ sách OCR
--   photo_place/depth/date: Metadata ảnh thu mẫu thực địa — dùng chung

ALTER TABLE species ADD COLUMN IF NOT EXISTS morphology_vn TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS morphology_en TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS photo_place TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS photo_depth TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS photo_date TEXT DEFAULT '';

-- Thêm collection "Thực vật biển" nếu chưa có
INSERT INTO collections (id, slug, name_vn, name_en, icon, accent_color, volume_count, status, sort_order)
VALUES ('thuc-vat-bien', 'thuc-vat-bien', 'Thực vật biển Việt Nam', 'Vietnamese Marine Plants', '🌿', '#a7f3d0', 1, 'draft', 2)
ON CONFLICT (id) DO UPDATE SET
  name_vn = EXCLUDED.name_vn,
  name_en = EXCLUDED.name_en;
