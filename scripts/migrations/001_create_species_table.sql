-- Migration: create_species_table
-- Bảng chính cho Danh Mục Cá Biển Việt Nam

CREATE TABLE IF NOT EXISTS species (
    -- === Identity ===
    id              TEXT PRIMARY KEY,
    volume          SMALLINT NOT NULL,
    species_index   SMALLINT NOT NULL,

    -- === Tên ===
    vn_name             TEXT NOT NULL DEFAULT '',
    scientific_name     TEXT NOT NULL DEFAULT '',
    authorship          TEXT DEFAULT '',
    en_common_name      TEXT DEFAULT '',
    vn_alternate_names  TEXT DEFAULT '',

    -- === Taxonomy (4 cấp: class > order > family > genus) ===
    tax_class_vn    TEXT DEFAULT '',
    tax_class_latin TEXT DEFAULT '',
    tax_order_vn    TEXT DEFAULT '',
    tax_order_latin TEXT DEFAULT '',
    tax_family_vn   TEXT DEFAULT '',
    tax_family_latin TEXT DEFAULT '',
    tax_genus_vn    TEXT DEFAULT '',
    tax_genus_latin TEXT DEFAULT '',

    -- === Specs Tiếng Việt ===
    vn_size         TEXT DEFAULT '',
    vn_distribution TEXT DEFAULT '',
    vn_specimen     TEXT DEFAULT '',
    vn_status       TEXT DEFAULT '',
    vn_literature   TEXT DEFAULT '',

    -- === Specs Tiếng Anh ===
    en_size         TEXT DEFAULT '',
    en_distribution TEXT DEFAULT '',
    en_specimen     TEXT DEFAULT '',
    en_status       TEXT DEFAULT '',
    en_literature   TEXT DEFAULT '',

    -- === Phân loại & Bảo tồn ===
    conservation_status TEXT DEFAULT 'unknown'
        CHECK (conservation_status IN ('common','uncommon','rare','unknown')),

    -- === Synonyms (mảng chuỗi) ===
    synonyms        JSONB DEFAULT '[]'::jsonb,

    -- === WoRMS Validation ===
    worms_status        TEXT DEFAULT '',
    worms_accepted_name TEXT DEFAULT '',
    worms_id            INTEGER,
    worms_synced_at     TIMESTAMPTZ,

    -- === Metadata ===
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- === Indexes ===
CREATE INDEX IF NOT EXISTS idx_species_volume ON species(volume);
CREATE INDEX IF NOT EXISTS idx_species_vn_name ON species(vn_name);
CREATE INDEX IF NOT EXISTS idx_species_sci_name ON species(scientific_name);
CREATE INDEX IF NOT EXISTS idx_species_tax_order ON species(tax_order_latin);
CREATE INDEX IF NOT EXISTS idx_species_tax_family ON species(tax_family_latin);

-- Full-text search (simple tokenizer — tốt cho tiếng Việt không dấu + Latin)
CREATE INDEX IF NOT EXISTS idx_species_fts ON species USING gin(
    to_tsvector('simple',
        coalesce(vn_name,'') || ' ' ||
        coalesce(scientific_name,'') || ' ' ||
        coalesce(en_common_name,'') || ' ' ||
        coalesce(vn_alternate_names,'')
    )
);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_species_modtime
    BEFORE UPDATE ON species
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- === Row Level Security ===
ALTER TABLE species ENABLE ROW LEVEL SECURITY;

-- Public read access (cho website)
CREATE POLICY "Public read access"
    ON species FOR SELECT
    USING (true);

-- Service role write access (cho import/OCR scripts)
CREATE POLICY "Service write access"
    ON species FOR ALL
    USING (true)
    WITH CHECK (true);

-- === View: Taxonomy Tree (thay thế taxonomy_tree.json) ===
CREATE OR REPLACE VIEW taxonomy_tree AS
SELECT DISTINCT
    tax_class_vn,
    tax_class_latin,
    tax_order_vn,
    tax_order_latin,
    tax_family_vn,
    tax_family_latin,
    tax_genus_vn,
    tax_genus_latin,
    COUNT(*) as species_count
FROM species
GROUP BY
    tax_class_vn, tax_class_latin,
    tax_order_vn, tax_order_latin,
    tax_family_vn, tax_family_latin,
    tax_genus_vn, tax_genus_latin
ORDER BY tax_class_latin, tax_order_latin, tax_family_latin, tax_genus_latin;
