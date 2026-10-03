-- Migration 015: Bộ lọc nâng cao đợt 2+3 — môi trường sống + vùng biển
-- Run on Supabase SQL Editor SAU 012, 013, 014. Date: 2026-10-03
--
-- 1. Thêm 2 cột mảng nhãn (cho phép NULL/rỗng), điền bởi `node scripts/derive_filter_cols.mjs --apply --tags`
--      habitat_tags : ran-san-ho | day-cat-bun | day-da | tham-co-bien | ngap-man-cua-song | bien-khoi | bien-sau
--      region_tags  : bac-bo | trung-bo | nam-bo | hoang-sa | truong-sa
--    Cột thường (không generated) — cùng lý do với 013. Chạy lại script sau mỗi đợt OCR/enrich.
-- 2. Thay RPC của 014 bằng bản có p_habitat, p_region (khớp nếu loài có BẤT KỲ nhãn nào được chọn: toán tử &&)
--    và thêm search_species_facets: đếm cho cả 3 nhóm lọc trong MỘT lần gọi (thay search_species_iucn_counts).
--    Mỗi nhóm đếm với mọi bộ lọc KHÁC áp dụng, trừ chính nó (để biết "chọn thêm giá trị này sẽ ra bao nhiêu").
-- Loài chưa có dữ liệu bị loại khi bộ lọc tương ứng bật (UI ghi chú rõ).

ALTER TABLE public.species
  ADD COLUMN IF NOT EXISTS habitat_tags text[],
  ADD COLUMN IF NOT EXISTS region_tags  text[];

COMMENT ON COLUMN public.species.habitat_tags IS 'Nhãn môi trường sống chuẩn hóa từ biology.habitat/habitatVn (derive_filter_cols.mjs)';
COMMENT ON COLUMN public.species.region_tags  IS 'Nhãn vùng biển chuẩn hóa từ vn_distribution (derive_filter_cols.mjs); KHÔNG dùng vn_specimen (nơi lưu mẫu)';

DROP FUNCTION IF EXISTS public.search_species(text, text, text[], numeric, numeric, numeric, numeric, int, int);
DROP FUNCTION IF EXISTS public.search_species_counts(text, text[], numeric, numeric, numeric, numeric);
DROP FUNCTION IF EXISTS public.search_species_iucn_counts(text, text, numeric, numeric, numeric, numeric);
DROP FUNCTION IF EXISTS public.species_pass_filters(text, numeric, numeric, numeric, text[], numeric, numeric, numeric, numeric);

-- Một chỗ duy nhất định nghĩa "loài này qua bộ lọc không"
CREATE OR REPLACE FUNCTION public.species_pass_filters(
  iucn text, dmin numeric, dmax numeric, len numeric, habitat text[], region text[],
  f_iucn text[], f_dmin numeric, f_dmax numeric, f_lmin numeric, f_lmax numeric,
  f_habitat text[], f_region text[]
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
     AND (f_habitat IS NULL OR cardinality(f_habitat) = 0 OR coalesce(habitat && f_habitat, false))
     AND (f_region  IS NULL OR cardinality(f_region)  = 0 OR coalesce(region  && f_region,  false))
$$;

CREATE OR REPLACE FUNCTION public.search_species(
  p_query      text    DEFAULT NULL,
  p_collection text    DEFAULT NULL,
  p_iucn       text[]  DEFAULT NULL,
  p_depth_min  numeric DEFAULT NULL,
  p_depth_max  numeric DEFAULT NULL,
  p_len_min    numeric DEFAULT NULL,
  p_len_max    numeric DEFAULT NULL,
  p_habitat    text[]  DEFAULT NULL,
  p_region     text[]  DEFAULT NULL,
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
      AND public.species_pass_filters(s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm, s.habitat_tags, s.region_tags,
                                      p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max, p_habitat, p_region)
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

-- Đếm theo phân hệ: áp mọi bộ lọc TRỪ phân hệ
CREATE OR REPLACE FUNCTION public.search_species_counts(
  p_query     text    DEFAULT NULL,
  p_iucn      text[]  DEFAULT NULL,
  p_depth_min numeric DEFAULT NULL,
  p_depth_max numeric DEFAULT NULL,
  p_len_min   numeric DEFAULT NULL,
  p_len_max   numeric DEFAULT NULL,
  p_habitat   text[]  DEFAULT NULL,
  p_region    text[]  DEFAULT NULL
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
    AND public.species_pass_filters(s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm, s.habitat_tags, s.region_tags,
                                    p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max, p_habitat, p_region)
  GROUP BY s.collection_id
$$;

-- Đếm cho 3 nhóm lọc trong một lần gọi: (facet, value, total). value NULL = chưa có dữ liệu (chỉ có ở 'iucn').
CREATE OR REPLACE FUNCTION public.search_species_facets(
  p_query      text    DEFAULT NULL,
  p_collection text    DEFAULT NULL,
  p_iucn       text[]  DEFAULT NULL,
  p_depth_min  numeric DEFAULT NULL,
  p_depth_max  numeric DEFAULT NULL,
  p_len_min    numeric DEFAULT NULL,
  p_len_max    numeric DEFAULT NULL,
  p_habitat    text[]  DEFAULT NULL,
  p_region     text[]  DEFAULT NULL
)
RETURNS TABLE (facet text, value text, total bigint)
LANGUAGE sql STABLE PARALLEL SAFE
SET search_path = public, extensions
AS $$
  WITH q AS (
    SELECT array(SELECT '%' || t || '%' FROM unnest(public.search_tokens(p_query)) AS t) AS pats
  ),
  t AS (  -- khớp từ khóa + phân hệ, CHƯA áp bộ lọc nâng cao
    SELECT s.iucn_code, s.depth_min, s.depth_max, s.max_length_cm, s.habitat_tags, s.region_tags
    FROM public.species s, q
    WHERE s.deleted_at IS NULL
      AND (p_collection IS NULL OR s.collection_id = p_collection)
      AND (public.vn_fold(s.vn_name) || ' ' || public.vn_fold(s.vn_alternate_names) || ' ' ||
           public.vn_fold(s.en_common_name) || ' ' || public.vn_fold(s.scientific_name)) LIKE ALL (q.pats)
  )
  SELECT 'iucn', t.iucn_code, count(*) FROM t
  WHERE public.species_pass_filters(t.iucn_code, t.depth_min, t.depth_max, t.max_length_cm, t.habitat_tags, t.region_tags,
                                    NULL, p_depth_min, p_depth_max, p_len_min, p_len_max, p_habitat, p_region)
  GROUP BY t.iucn_code
  UNION ALL
  SELECT 'habitat', tag, count(*) FROM t, unnest(t.habitat_tags) AS tag
  WHERE public.species_pass_filters(t.iucn_code, t.depth_min, t.depth_max, t.max_length_cm, t.habitat_tags, t.region_tags,
                                    p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max, NULL, p_region)
  GROUP BY tag
  UNION ALL
  SELECT 'region', tag, count(*) FROM t, unnest(t.region_tags) AS tag
  WHERE public.species_pass_filters(t.iucn_code, t.depth_min, t.depth_max, t.max_length_cm, t.habitat_tags, t.region_tags,
                                    p_iucn, p_depth_min, p_depth_max, p_len_min, p_len_max, p_habitat, NULL)
  GROUP BY tag
$$;

GRANT EXECUTE ON FUNCTION public.species_pass_filters(text, numeric, numeric, numeric, text[], text[], text[], numeric, numeric, numeric, numeric, text[], text[]) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species(text, text, text[], numeric, numeric, numeric, numeric, text[], text[], int, int)                                  TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species_counts(text, text[], numeric, numeric, numeric, numeric, text[], text[])                                          TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.search_species_facets(text, text, text[], numeric, numeric, numeric, numeric, text[], text[])                                    TO anon, authenticated, service_role;

-- Kiểm tra sau khi chạy (cần đã chạy `derive_filter_cols.mjs --apply --tags`):
--   SELECT * FROM search_species_facets('ca map');
--   SELECT vn_name FROM search_species(NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{ran-san-ho}', '{hoang-sa}');
