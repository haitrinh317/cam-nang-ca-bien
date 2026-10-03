-- Migration 011: Create Collection dong-vat-phu-du (Động vật phù du Việt Nam)
-- Date: 2026-09-19

INSERT INTO collections (id, slug, name_vn, name_en, icon, accent_color, volume_count, status, sort_order)
VALUES (
  'dong-vat-phu-du',
  'dong-vat-phu-du',
  'Động vật phù du',
  'Marine Zooplankton of Vietnam',
  '🔬',
  '#38bdf8',
  1,
  'active',
  9
)
ON CONFLICT (id) DO UPDATE SET
  name_vn = EXCLUDED.name_vn,
  name_en = EXCLUDED.name_en,
  slug = EXCLUDED.slug,
  icon = EXCLUDED.icon,
  accent_color = EXCLUDED.accent_color,
  volume_count = EXCLUDED.volume_count,
  status = EXCLUDED.status,
  sort_order = EXCLUDED.sort_order;
