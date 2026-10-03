-- Migration 001: Create collections table
-- Run on Supabase SQL Editor
-- Date: 2026-08-19

CREATE TABLE IF NOT EXISTS collections (
  id           TEXT PRIMARY KEY,         -- 'ca-bien', 'thuc-vat-bien'
  name_vn      TEXT NOT NULL,            -- 'Cá biển Việt Nam'
  name_en      TEXT NOT NULL,            -- 'Vietnamese Marine Fish'
  slug         TEXT UNIQUE NOT NULL,     -- 'ca-bien' (URL segment)
  icon         TEXT,                     -- emoji or SVG path
  accent_color TEXT DEFAULT '#6fffe8',   -- collection accent
  volume_count INT  DEFAULT 0,
  status       TEXT DEFAULT 'active'     -- active | draft | archived
    CHECK (status IN ('active', 'draft', 'archived')),
  sort_order   INT  DEFAULT 0,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- Seed: Cá biển (existing data)
INSERT INTO collections (id, name_vn, name_en, slug, icon, accent_color, volume_count, status, sort_order)
VALUES ('ca-bien', 'Cá biển Việt Nam', 'Vietnamese Marine Fish', 'ca-bien', '🐟', '#6fffe8', 5, 'active', 1)
ON CONFLICT (id) DO NOTHING;

-- Seed: Thực vật biển (next collection — draft)
INSERT INTO collections (id, name_vn, name_en, slug, icon, accent_color, volume_count, status, sort_order)
VALUES ('thuc-vat-bien', 'Thực vật biển Việt Nam', 'Vietnamese Marine Plants', 'thuc-vat-bien', '🌿', '#a7f3d0', 0, 'draft', 2)
ON CONFLICT (id) DO NOTHING;

-- RLS: public can read active collections
ALTER TABLE collections ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read active collections" ON collections
  FOR SELECT USING (status = 'active');
-- Admin can see all (add admin policy when auth is set up in M4)
