-- Migration 002: Add collection_id to species table
-- Run AFTER 001_create_collections.sql
-- Date: 2026-08-19

-- Add column with default — all existing rows get 'ca-bien' automatically.
-- Zero data migration needed.
ALTER TABLE species
  ADD COLUMN IF NOT EXISTS collection_id TEXT
    REFERENCES collections(id)
    DEFAULT 'ca-bien';

-- Backfill existing rows (in case DEFAULT doesn't apply retroactively)
UPDATE species SET collection_id = 'ca-bien' WHERE collection_id IS NULL;

-- Index for collection-scoped queries
CREATE INDEX IF NOT EXISTS idx_species_collection ON species(collection_id);

-- Composite index: collection + volume (common query pattern)
CREATE INDEX IF NOT EXISTS idx_species_collection_volume ON species(collection_id, volume);
