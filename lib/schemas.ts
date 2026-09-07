/**
 * Zod schemas for species API input validation.
 * Shared between /api/species (CRUD) and /api/species/import (bulk upsert).
 */
import { z } from 'zod'

// ponytail: only validate what matters — string fields are nullable text in DB,
// so we accept string().optional() for most. Required fields match DB NOT NULL.

/** Single species — used for POST (create) */
export const speciesCreateSchema = z.object({
  id: z.string().min(1).max(200),
  collection_id: z.string().min(1).max(50),
  volume: z.coerce.number().int().min(1).max(99),
  species_index: z.coerce.number().int().nullable().optional(),
  vn_name: z.string().min(1, 'Tên tiếng Việt bắt buộc').max(500),
  scientific_name: z.string().min(1, 'Tên khoa học bắt buộc').max(500),
  authorship: z.string().max(500).nullable().optional(),
  // Taxonomy
  tax_class_vn: z.string().max(200).nullable().optional(),
  tax_class_latin: z.string().max(200).nullable().optional(),
  tax_order_vn: z.string().max(200).nullable().optional(),
  tax_order_latin: z.string().max(200).nullable().optional(),
  tax_family_vn: z.string().max(200).nullable().optional(),
  tax_family_latin: z.string().max(200).nullable().optional(),
  tax_genus_vn: z.string().max(200).nullable().optional(),
  tax_genus_latin: z.string().max(200).nullable().optional(),
  // Vietnamese specs
  vn_alternate_names: z.string().max(1000).nullable().optional(),
  vn_size: z.string().max(500).nullable().optional(),
  vn_distribution: z.string().max(2000).nullable().optional(),
  vn_specimen: z.string().max(2000).nullable().optional(),
  vn_status: z.string().max(500).nullable().optional(),
  vn_literature: z.string().max(2000).nullable().optional(),
  // English specs
  en_common_name: z.string().max(500).nullable().optional(),
  en_size: z.string().max(500).nullable().optional(),
  en_distribution: z.string().max(2000).nullable().optional(),
  en_specimen: z.string().max(2000).nullable().optional(),
  en_status: z.string().max(500).nullable().optional(),
  en_literature: z.string().max(2000).nullable().optional(),
  // Extended fields
  morphology_vn: z.string().max(5000).nullable().optional(),
  morphology_en: z.string().max(5000).nullable().optional(),
  ecology_vn: z.string().max(5000).nullable().optional(),
  ecology_en: z.string().max(5000).nullable().optional(),
  economic_value_vn: z.string().max(5000).nullable().optional(),
  economic_value_en: z.string().max(5000).nullable().optional(),
  photo_url: z.string().max(1000).nullable().optional(),
  photo_place: z.string().max(500).nullable().optional(),
  photo_depth: z.string().max(200).nullable().optional(),
  photo_date: z.string().max(200).nullable().optional(),
}).strict() // reject unknown keys

/** Partial species — used for PATCH (update) */
export const speciesUpdateSchema = speciesCreateSchema
  .partial()                    // all fields optional
  .omit({ id: true })          // can't change id via PATCH

/** Bulk import payload */
export const importSchema = z.object({
  collection_id: z.string().min(1).max(50),
  species: z
    .array(speciesCreateSchema.partial().required({ id: true, vn_name: true, scientific_name: true }))
    .min(1, 'Cần ít nhất 1 loài')
    .max(200, 'Tối đa 200 loài mỗi lần import'),
})
