-- Migration 010: Upgrade Marine Reptiles Collection
-- Unifies ran-bien into bo-sat-bien (33 species total: 27 Sea Snakes + 5 Sea Turtles + 1 Saltwater Crocodile)

-- 1. Insert new collection bo-sat-bien
INSERT INTO collections (id, slug, name_vn, name_en, icon, accent_color, volume_count, status, sort_order)
VALUES (
  'bo-sat-bien',
  'bo-sat-bien',
  'Bò sát biển',
  'Marine Reptiles of Vietnam',
  '🐢',
  '#f59e0b',
  3,
  'active',
  4
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

-- 2. Migrate existing 27 species from ran-bien to bo-sat-bien
UPDATE species
SET collection_id = 'bo-sat-bien'
WHERE collection_id = 'ran-bien';

-- 3. Mark old ran-bien collection as archived
UPDATE collections
SET status = 'archived'
WHERE id = 'ran-bien';
