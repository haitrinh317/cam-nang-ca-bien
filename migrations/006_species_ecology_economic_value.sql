-- Migration 006: Add ecology + economic_value columns to species table
-- Date: 2026-08-23
--
-- Rationale:
--   Sách "Atlas cá rạn san hô thường gặp ở biển Việt Nam" (RIMF, 2017)
--   cung cấp 2 mục chưa có trong schema:
--     • Sinh thái, dinh dưỡng  → ecology_vn / ecology_en
--     • Giá trị kinh tế        → economic_value_vn / economic_value_en
--   ecology_en và economic_value_en để trống ban đầu — sẽ bổ sung sau
--   từ FishBase hoặc nguồn EN khác.
--
-- Run on Supabase SQL Editor:
--   https://supabase.com/dashboard/project/cjxqogvtzrvnlsssnfob/sql/new

-- 1. Thêm 4 cột mới
ALTER TABLE species ADD COLUMN IF NOT EXISTS ecology_vn          TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS ecology_en          TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS economic_value_vn   TEXT DEFAULT '';
ALTER TABLE species ADD COLUMN IF NOT EXISTS economic_value_en   TEXT DEFAULT '';

-- 2. Cập nhật volume_count collection ca-bien từ 5 → 6
--    (Tập 6 = Atlas cá rạn san hô Việt Nam, volume = 6, ID prefix tap6-species-N)
UPDATE collections
SET volume_count = 6
WHERE id = 'ca-bien';
