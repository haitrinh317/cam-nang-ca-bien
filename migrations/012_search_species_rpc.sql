-- Migration 012: Tìm kiếm KHÔNG DẤU + xếp hạng theo độ khớp
-- Run on Supabase SQL Editor (một lần, an toàn chạy lại: CREATE OR REPLACE)
-- Date: 2026-10-03
--
-- Vấn đề: GlobalSearch dùng `ilike %từ khóa%` ở trình duyệt nên:
--   1. Gõ "ca map" không ra "Cá mập" (ilike không bỏ dấu)
--   2. Kết quả xếp theo tập sách, không theo độ khớp; chỉ lấy 12 dòng
--   3. Không có tổng số kết quả để dựng trang kết quả /tim-kiem
--
-- Giải pháp: 3 hàm SQL, KHÔNG đổi cấu trúc bảng species
--   vn_fold(text)                       bỏ dấu + chữ thường (đ -> d)
--   search_tokens(text)                 tách từ khóa (tối đa 6 từ, chỉ a-z0-9)
--   search_species(q, collection, limit, offset)   danh sách đã xếp hạng + tổng
--   search_species_counts(q)            số kết quả theo từng phân hệ (chip lọc)
--
-- ponytail: quét tuần tự ~3k dòng (vài chục ms), chưa cần chỉ mục.
--   Trần: > 50k loài -> thêm cột search_text sinh sẵn + chỉ mục GIN trigram.
--   Không dùng generated column vì script OCR/enrich đọc `*` rồi upsert lại
--   sẽ lỗi "cannot insert into generated column".

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA extensions;

-- Bỏ dấu tiếng Việt, chữ thường. IMMUTABLE để sau này có thể đánh chỉ mục biểu thức.
CREATE OR REPLACE FUNCTION public.vn_fold(p text)
RETURNS text
LANGUAGE sql IMMUTABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$ SELECT lower(unaccent(coalesce(p, ''))) $$;

-- "Cá  mập-trắng!" -> {ca,map,trang}
CREATE OR REPLACE FUNCTION public.search_tokens(p text)
RETURNS text[]
LANGUAGE sql IMMUTABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  SELECT coalesce((
    array_remove(
      string_to_array(
        trim(regexp_replace(public.vn_fold(left(coalesce(p, ''), 100)), '[^a-z0-9]+', ' ', 'g')),
        ' '),
      '')
  )[1:6], '{}'::text[])
$$;

-- Danh sách kết quả đã xếp hạng. total = tổng số dòng khớp (trước LIMIT) để phân trang.
-- matched: vn | alt | en | sci | mix  (trường nào chứa từ khóa — để hiện "khớp tên gọi khác")
-- Điểm: tên VN khớp đúng 100 > tên khoa học khớp đúng 95 > tên VN bắt đầu bằng 90
--       > tên gọi khác khớp đúng 85 > ... > chỉ khớp rải rác nhiều trường 40
CREATE OR REPLACE FUNCTION public.search_species(
  p_query      text,
  p_collection text DEFAULT NULL,
  p_limit      int  DEFAULT 12,
  p_offset     int  DEFAULT 0
)
RETURNS TABLE (
  id                 text,
  volume             int,
  vn_name            text,
  scientific_name    text,
  authorship         text,
  collection_id      text,
  vn_alternate_names text,
  en_common_name     text,
  matched            text,
  score              int,
  total              bigint
)
LANGUAGE sql STABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  WITH q AS (
    SELECT public.search_tokens(p_query) AS toks,
           array_to_string(public.search_tokens(p_query), ' ') AS phrase
  ),
  q2 AS (
    SELECT toks, phrase,
           array(SELECT '%' || t || '%' FROM unnest(toks) AS t) AS pats
    FROM q
  ),
  base AS (
    SELECT s.id, s.volume::int AS volume, s.species_index,
           s.vn_name, s.scientific_name, s.authorship, s.collection_id,
           s.vn_alternate_names, s.en_common_name,
           public.vn_fold(s.vn_name)            AS n_vn,
           public.vn_fold(s.vn_alternate_names) AS n_alt,
           public.vn_fold(s.en_common_name)     AS n_en,
           public.vn_fold(s.scientific_name)    AS n_sci
    FROM public.species s
    WHERE s.deleted_at IS NULL
      AND (p_collection IS NULL OR s.collection_id = p_collection)
  ),
  hit AS (
    SELECT b.*, q2.phrase, q2.pats,
           -- các tên gọi khác tách bằng , hoặc ; -> "|a|b|c|" để so khớp theo từng tên
           '|' || regexp_replace(trim(b.n_alt), '\s*[,;]\s*', '|', 'g') || '|' AS alt_items
    FROM base b, q2
    WHERE cardinality(q2.toks) > 0
      AND (b.n_vn || ' ' || b.n_alt || ' ' || b.n_en || ' ' || b.n_sci) LIKE ALL (q2.pats)
  )
  SELECT h.id, h.volume, h.vn_name, h.scientific_name, h.authorship, h.collection_id,
         h.vn_alternate_names, h.en_common_name,
         CASE
           WHEN h.n_vn  LIKE ALL (h.pats) THEN 'vn'
           WHEN h.n_alt LIKE ALL (h.pats) THEN 'alt'
           WHEN h.n_en  LIKE ALL (h.pats) THEN 'en'
           WHEN h.n_sci LIKE ALL (h.pats) THEN 'sci'
           ELSE 'mix'
         END AS matched,
         CASE
           WHEN h.n_vn = h.phrase                          THEN 100
           WHEN h.n_sci = h.phrase                         THEN 95
           WHEN h.n_vn LIKE h.phrase || '%'                THEN 90
           WHEN h.alt_items LIKE '%|' || h.phrase || '|%'  THEN 85
           WHEN h.n_sci LIKE h.phrase || '%'               THEN 85
           WHEN h.n_vn LIKE '% ' || h.phrase || '%'        THEN 80
           WHEN h.alt_items LIKE '%|' || h.phrase || '%'   THEN 75
           WHEN h.n_vn LIKE '%' || h.phrase || '%'         THEN 70
           WHEN h.n_alt LIKE '%' || h.phrase || '%'        THEN 60
           WHEN h.n_sci LIKE '%' || h.phrase || '%'        THEN 60
           WHEN h.n_en = h.phrase                          THEN 55
           WHEN h.n_en LIKE '%' || h.phrase || '%'         THEN 50
           ELSE 40
         END AS score,
         count(*) OVER () AS total
  FROM hit h
  ORDER BY score DESC, length(h.vn_name), h.volume, h.species_index, h.id
  LIMIT least(greatest(p_limit, 1), 50)
  OFFSET greatest(p_offset, 0)
$$;

-- Số kết quả theo từng phân hệ (cho chip lọc trên trang kết quả)
CREATE OR REPLACE FUNCTION public.search_species_counts(p_query text)
RETURNS TABLE (collection_id text, total bigint)
LANGUAGE sql STABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  WITH q AS (
    SELECT public.search_tokens(p_query) AS toks,
           array(SELECT '%' || t || '%' FROM unnest(public.search_tokens(p_query)) AS t) AS pats
  )
  SELECT s.collection_id, count(*)
  FROM public.species s, q
  WHERE s.deleted_at IS NULL
    AND cardinality(q.toks) > 0
    AND (public.vn_fold(s.vn_name) || ' ' || public.vn_fold(s.vn_alternate_names) || ' ' ||
         public.vn_fold(s.en_common_name) || ' ' || public.vn_fold(s.scientific_name)) LIKE ALL (q.pats)
  GROUP BY s.collection_id
$$;

GRANT EXECUTE ON FUNCTION public.vn_fold(text)                              TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_tokens(text)                        TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species(text, text, int, int)       TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species_counts(text)                TO anon, authenticated, service_role;

-- Kiểm tra sau khi chạy:
--   SELECT vn_name, matched, score, total FROM search_species('ca map');
--   SELECT * FROM search_species_counts('ca map');
