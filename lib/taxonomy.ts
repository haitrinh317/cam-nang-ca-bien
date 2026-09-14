/**
 * Shared taxonomy utilities for Dual Taxonomy Architecture:
 * - 'modern': WoRMS Molecular Phylogenetics (Nelson et al. 2016)
 * - 'classic': Original Monograph Structure (Oceanographic Institute)
 */

export const TAXONOMY_COLS =
  'id, vn_name, scientific_name, tax_class_vn, tax_class_latin, tax_order_vn, tax_order_latin, tax_family_vn, tax_family_latin, tax_genus_vn, tax_genus_latin, species_index, biology'

export interface WormsTaxonomyNode {
  class?: string | null
  classVn?: string | null
  order?: string | null
  orderVn?: string | null
  family?: string | null
  familyVn?: string | null
  genus?: string | null
  genusVn?: string | null
  aphiaId?: number | null
  status?: string | null
  validName?: string | null
}

export interface SpeciesRow {
  id: string
  vn_name: string
  scientific_name: string
  tax_class_vn: string | null
  tax_class_latin: string | null
  tax_order_vn: string | null
  tax_order_latin: string | null
  tax_family_vn: string | null
  tax_family_latin: string | null
  tax_genus_vn: string | null
  tax_genus_latin: string | null
  species_index: number | null
  biology?: {
    wormsTaxonomy?: WormsTaxonomyNode | null
    [key: string]: unknown
  } | null
}

export type TaxonomyMode = 'modern' | 'classic'

export type GenusNode  = { vn: string; species: SpeciesRow[] }
export type FamilyNode = { vn: string; genera: Record<string, GenusNode> }
export type OrderNode  = { vn: string; families: Record<string, FamilyNode> }
export type ClassNode  = { vn: string; orders: Record<string, OrderNode> }
export type TaxonomyTree = Record<string, ClassNode>

/** Helper: Extract taxonomic ranks according to selected mode */
export function getSpeciesTaxonomy(sp: SpeciesRow, mode: TaxonomyMode = 'modern') {
  const wt = sp.biology?.wormsTaxonomy

  if (mode === 'modern' && wt && wt.order && wt.family) {
    return {
      classLatin: wt.class || sp.tax_class_latin || 'Unknown',
      classVn: wt.classVn || sp.tax_class_vn || wt.class || 'Lớp chưa xác định',
      orderLatin: wt.order || sp.tax_order_latin || 'Unknown',
      orderVn: wt.orderVn || sp.tax_order_vn || wt.order || 'Bộ chưa xác định',
      familyLatin: wt.family || sp.tax_family_latin || 'Unknown',
      familyVn: wt.familyVn || sp.tax_family_vn || wt.family || 'Họ chưa xác định',
      genusLatin: wt.genus || sp.tax_genus_latin || 'Unknown',
      genusVn: wt.genusVn || sp.tax_genus_vn || wt.genus || 'Chi chưa xác định',
    }
  }

  // Classic mode fallback
  return {
    classLatin: sp.tax_class_latin || 'Unknown',
    classVn: sp.tax_class_vn || sp.tax_class_latin || 'Lớp chưa xác định',
    orderLatin: sp.tax_order_latin || 'Unknown',
    orderVn: sp.tax_order_vn || sp.tax_order_latin || 'Bộ chưa xác định',
    familyLatin: sp.tax_family_latin || 'Unknown',
    familyVn: sp.tax_family_vn || sp.tax_family_latin || 'Họ chưa xác định',
    genusLatin: sp.tax_genus_latin || 'Unknown',
    genusVn: sp.tax_genus_vn || sp.tax_genus_latin || 'Giống chưa xác định',
  }
}

/** Sort flat rows: Class → Order → Family → species_index */
export function sortTaxonomyRows(rows: SpeciesRow[], mode: TaxonomyMode = 'modern'): SpeciesRow[] {
  return [...rows].sort((a, b) => {
    const taxA = getSpeciesTaxonomy(a, mode)
    const taxB = getSpeciesTaxonomy(b, mode)

    const cl = taxA.classLatin.localeCompare(taxB.classLatin)
    if (cl !== 0) return cl
    const or = taxA.orderLatin.localeCompare(taxB.orderLatin)
    if (or !== 0) return or
    const fa = taxA.familyLatin.localeCompare(taxB.familyLatin)
    if (fa !== 0) return fa
    return (a.species_index || 0) - (b.species_index || 0)
  })
}

/** Assemble a nested taxonomy tree from flat rows according to mode */
export function buildTaxonomyTree(rows: SpeciesRow[], mode: TaxonomyMode = 'modern'): TaxonomyTree {
  const tree: TaxonomyTree = {}
  for (const sp of rows) {
    const tax = getSpeciesTaxonomy(sp, mode)

    const cl  = tax.classLatin
    const clv = tax.classVn
    const or  = tax.orderLatin
    const orv = tax.orderVn
    const fa  = tax.familyLatin
    const fav = tax.familyVn
    const ge  = tax.genusLatin
    const gev = tax.genusVn

    if (!tree[cl]) tree[cl] = { vn: clv, orders: {} }
    if (!tree[cl].orders[or]) tree[cl].orders[or] = { vn: orv, families: {} }
    if (!tree[cl].orders[or].families[fa]) tree[cl].orders[or].families[fa] = { vn: fav, genera: {} }
    if (!tree[cl].orders[or].families[fa].genera[ge])
      tree[cl].orders[or].families[fa].genera[ge] = { vn: gev, species: [] }
    tree[cl].orders[or].families[fa].genera[ge].species.push(sp)
  }
  return tree
}

/** Calculate summary counts for a built tree */
export function getTaxonomyStats(tree: TaxonomyTree) {
  let orderCount = 0
  let familyCount = 0
  let genusCount = 0
  let speciesCount = 0

  const classCount = Object.keys(tree).length
  for (const cl of Object.values(tree)) {
    orderCount += Object.keys(cl.orders).length
    for (const ord of Object.values(cl.orders)) {
      familyCount += Object.keys(ord.families).length
      for (const fam of Object.values(ord.families)) {
        genusCount += Object.keys(fam.genera).length
        for (const gen of Object.values(fam.genera)) {
          speciesCount += gen.species.length
        }
      }
    }
  }

  return { classCount, orderCount, familyCount, genusCount, speciesCount }
}
