-- Migration 002: add biology JSONB column
-- Lưu dữ liệu sinh học-sinh thái từ FishBase + GBIF

ALTER TABLE species
  ADD COLUMN IF NOT EXISTS biology JSONB DEFAULT NULL;

-- Index GIN để query các trường trong biology (optional nhưng hữu ích)
CREATE INDEX IF NOT EXISTS idx_species_biology ON species USING gin(biology)
  WHERE biology IS NOT NULL;

-- Ghi chú các trường trong biology:
-- {
--   "fbSpecCode":      int,      -- FishBase SpecCode
--   "fbName":          text,     -- Tên tiếng Anh FishBase
--   "source":          text,     -- "FishBase v25.04"
--   "maxLength":       text,     -- "120 cm TL"
--   "maxWeight":       text,     -- "15,000 g"
--   "longevity":       text,     -- "22 năm"
--   "depth":           text,     -- "1 - 100 m"
--   "habitat":         text,     -- "Neritic, Coral reefs, Mangroves"
--   "feedingType":     text,     -- "hunting macrofauna (predator)"
--   "trophicLevel":    float,    -- 4.0
--   "reproduction":    text,     -- "protogyny, external fertilization"
--   "spawning":        text,     -- "one clear seasonal peak per year"
--   "spawnAggregation": bool,    -- true/false
--   "parentalCare":    text,     -- "none" / "maternal"
--   "vulnerability":   float,    -- 57.51 (FishBase vulnerability index)
--   "importance":      text,     -- "commercial"
--   "priceCategory":   text,     -- "high"
--   "aquaculture":     text,     -- "commercial"
--   "dangerous":       text,     -- "harmless" / "traumatogenic" / "venomous"
--   "biologySummary":  text,     -- mô tả sinh học tổng hợp (EN, từ FishBase)
--   "ecologyNotes":    text,     -- ghi chú sinh thái (EN, từ FishBase)
--   "reproductionNotes": text,   -- ghi chú sinh sản (EN)
--   "gbifKey":         int,      -- GBIF usage key
--   "iucnStatus":      text,     -- "LC" / "NT" / "VU" / "EN" / "CR" / "EX"
--   "morphDescription": text     -- mô tả hình thái (EN, từ GBIF)
-- }
