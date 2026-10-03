-- Migration 014: RPC tìm kiếm có bộ lọc nâng cao (IUCN, độ sâu, kích thước)
-- Run on Supabase SQL Editor SAU migration 012 + 013. Date: 2026-10-03
--
-- Thay thế search_species / search_species_counts (012) bằng bản có thêm tham số lọc.
-- DROP bản cũ trước: giữ cả hai chữ ký sẽ làm PostgREST không chọn được hàm khi gọi theo tên tham số.
-- Không đổi dữ liệu. Từ khóa có thể rỗng (chỉ lọc, không tìm chữ).
--
-- Ngữ nghĩa lọc (loài thiếu dữ liệu bị LOẠI khi bộ lọc đó đang bật — UI ghi chú rõ):
--   p_iucn            mảng mã, vd {CR,EN,VU}
--   p_depth_min/max   khoảng người dùng chọn (m); loài khớp nếu khoảng sâu của loài GIAO với khoảng này.
--                     depth_min NULL ("đến 30 m") coi như 0. depth_max NULL -> loại.
--   p_len_min/max     max_length_cm nằm trong [min, max]; NULL -> loại.

DROP FUNCTION IF EXISTS public.search_species(text, text, int, int);
DROP FUNCTION IF EXISTS public.search_species_counts(text);

-- Một chỗ duy nhất định nghĩa "loài này qua bộ lọc không" — dùng cho cả 3 hàm bên dưới.
CREATE OR REPLACE FUNCTION public.species_pass_filters(
  iucn text, dmin numeric, dmax numeric, len numeric,
  f_iucn text[], f_dmin numeric, f_dmax numeric, f_lmin numeric, f_lmax numeric
) RETURNS boolean
LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$
  SELECT (f_iucn IS NULL OR cardinality(f_iucn) = 0 OR iucn = ANY (f_iucn))
     AND (f_dmin IS NULL AND f_dmax IS NULL
          OR (dmax IS NOT NULL
              AND dmax >= coalesce(f_dmin, 0)
              AND coalesce(dmin, 0) <= coalesce(f_dmax, 'Infinity'::numeric)))
     AND (f_lmin IS NULL AND f_lmax IS NULL
          OR (len IS NOT NULL
              AND len >= coalesce(f_lmin, 0)
              AND len <= coalesce(f_lmax, 'Infinity'::numeric)))
$$;

CREATE OR REPLACE FUNCTION public.search_species(
  p_query      text    DEFAULT NULL,
  p_collection text    DEFAULT NULL,
  p_iucn       text[]  DEFAULT NULL,
  p_depth_min  numeric DEFAULT NULL,
  p_depth_max  numeric DEFAULT NULL,
  p_len_min    numeric DEFAULT NULL,
  p_len_max    numeric DEFAULT NULL,
  p_limit      int     DEFAULT 12,
  p_offset     int     DEFAULT 0
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
      AND public.species_pass_filters(s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm,
                                      p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max)
  ),
  hit AS (
    SELECT b.*, q2.phrase, q2.pats,
           '|' || regexp_replace(trim(b.n_alt), '\s*[,;]\s*', '|', 'g') || '|' AS alt_items
    FROM base b, q2
    -- LIKE ALL trên mảng rỗng = TRUE -> từ khóa rỗng nghĩa là "không lọc chữ"
    WHERE (b.n_vn || ' ' || b.n_alt || ' ' || b.n_en || ' ' || b.n_sci) LIKE ALL (q2.pats)
  )
  SELECT h.id, h.volume, h.vn_name, h.scientific_name, h.authorship, h.collection_id,
         h.vn_alternate_names, h.en_common_name,
         CASE
           WHEN cardinality(h.pats) = 0     THEN 'none'
           WHEN h.n_vn  LIKE ALL (h.pats) THEN 'vn'
           WHEN h.n_alt LIKE ALL (h.pats) THEN 'alt'
           WHEN h.n_en  LIKE ALL (h.pats) THEN 'en'
           WHEN h.n_sci LIKE ALL (h.pats) THEN 'sci'
           ELSE 'mix'
         END AS matched,
         CASE
           WHEN cardinality(h.pats) = 0                    THEN 0
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

-- Đếm theo phân hệ: áp mọi bộ lọc TRỪ phân hệ (để chip phân hệ luôn hiện số khả dĩ)
CREATE OR REPLACE FUNCTION public.search_species_counts(
  p_query     text    DEFAULT NULL,
  p_iucn      text[]  DEFAULT NULL,
  p_depth_min numeric DEFAULT NULL,
  p_depth_max numeric DEFAULT NULL,
  p_len_min   numeric DEFAULT NULL,
  p_len_max   numeric DEFAULT NULL
)
RETURNS TABLE (collection_id text, total bigint)
LANGUAGE sql STABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  WITH q AS (
    SELECT array(SELECT '%' || t || '%' FROM unnest(public.search_tokens(p_query)) AS t) AS pats
  )
  SELECT s.collection_id, count(*)
  FROM public.species s, q
  WHERE s.deleted_at IS NULL
    AND (public.vn_fold(s.vn_name) || ' ' || public.vn_fold(s.vn_alternate_names) || ' ' ||
         public.vn_fold(s.en_common_name) || ' ' || public.vn_fold(s.scientific_name)) LIKE ALL (q.pats)
    AND public.species_pass_filters(s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm,
                                    p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max)
  GROUP BY s.collection_id
$$;

-- Đếm theo mã IUCN: áp mọi bộ lọc TRỪ IUCN, có phân hệ. Dòng iucn_code NULL = chưa có dữ liệu.
CREATE OR REPLACE FUNCTION public.search_species_iucn_counts(
  p_query      text    DEFAULT NULL,
  p_collection text    DEFAULT NULL,
  p_depth_min  numeric DEFAULT NULL,
  p_depth_max  numeric DEFAULT NULL,
  p_len_min    numeric DEFAULT NULL,
  p_len_max    numeric DEFAULT NULL
)
RETURNS TABLE (iucn_code text, total bigint)
LANGUAGE sql STABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  WITH q AS (
    SELECT array(SELECT '%' || t || '%' FROM unnest(public.search_tokens(p_query)) AS t) AS pats
  )
  SELECT s.iucn_code, count(*)
  FROM public.species s, q
  WHERE s.deleted_at IS NULL
    AND (p_collection IS NULL OR s.collection_id = p_collection)
    AND (public.vn_fold(s.vn_name) || ' ' || public.vn_fold(s.vn_alternate_names) || ' ' ||
         public.vn_fold(s.en_common_name) || ' ' || public.vn_fold(s.scientific_name)) LIKE ALL (q.pats)
    AND public.species_pass_filters(s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm,
                                    NULL, p_depth_min, p_depth_max, p_len_min, p_len_max)
  GROUP BY s.iucn_code
$$;

GRANT EXECUTE ON FUNCTION public.species_pass_filters(text, numeric, numeric, numeric, text[], numeric, numeric, numeric, numeric) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species(text, text, text[], numeric, numeric, numeric, numeric, int, int)               TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species_counts(text, text[], numeric, numeric, numeric, numeric)                       TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species_iucn_counts(text, text, numeric, numeric, numeric, numeric)                    TO anon, authenticated, service_role;

-- Kiểm tra sau khi chạy:
--   SELECT vn_name, iucn_code FROM search_species(NULL, NULL, '{CR,EN}') ;           -- chỉ lọc
--   SELECT * FROM search_species_iucn_counts('ca map');
