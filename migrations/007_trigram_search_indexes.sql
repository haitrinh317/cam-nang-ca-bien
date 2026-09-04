-- Migration 007: Add trigram indexes for text search performance
-- Run on Supabase SQL Editor
-- Date: 2026-09-04
--
-- Vấn đề: GlobalSearch dùng `ilike %keyword%` — pattern này KHÔNG dùng được B-tree index.
-- Với 2,436 rows hiện tại thì chưa chậm lắm, nhưng trigram index sẽ:
--   1. Tăng tốc search 5-10x ngay lập tức
--   2. Sẵn sàng cho scale lên 5,000+ loài
--
-- Lưu ý: pg_trgm là extension có sẵn trên Supabase, chỉ cần enable.

-- Bước 1: Enable extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Bước 2: Trigram index cho tên Việt Nam (dùng trong GlobalSearch + API search)
CREATE INDEX IF NOT EXISTS idx_species_vn_name_trgm
  ON species USING gin (vn_name gin_trgm_ops);

-- Bước 3: Trigram index cho tên khoa học
CREATE INDEX IF NOT EXISTS idx_species_sci_name_trgm
  ON species USING gin (scientific_name gin_trgm_ops);

-- Bước 4: Trigram index cho tên tiếng Anh (dùng trong GlobalSearch)
CREATE INDEX IF NOT EXISTS idx_species_en_name_trgm
  ON species USING gin (en_common_name gin_trgm_ops);

-- Bước 5: Trigram index cho tên gọi khác (dùng trong GlobalSearch)
CREATE INDEX IF NOT EXISTS idx_species_alt_names_trgm
  ON species USING gin (vn_alternate_names gin_trgm_ops);

-- Kiểm tra sau khi chạy:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'species' ORDER BY indexname;
