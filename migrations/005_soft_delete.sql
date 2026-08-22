-- Migration: 005_soft_delete.sql
-- Thêm soft-delete cho bảng species
-- Chạy trong Supabase SQL Editor

-- 1. Thêm cột deleted_at (nullable timestamp)
ALTER TABLE species
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL;

-- 2. Tạo index để GET nhanh (filter WHERE deleted_at IS NULL)
CREATE INDEX IF NOT EXISTS idx_species_not_deleted
  ON species (collection_id, volume, species_index)
  WHERE deleted_at IS NULL;

-- 3. RLS policy SELECT: chỉ lấy chưa xóa (anon/authenticated)
-- CREATE POLICY không hỗ trợ IF NOT EXISTS → DROP trước, rồi CREATE
DROP POLICY IF EXISTS "species_select_not_deleted" ON species;
CREATE POLICY "species_select_not_deleted"
  ON species FOR SELECT
  USING (deleted_at IS NULL);

-- 4. Verify
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'species' AND column_name = 'deleted_at';
