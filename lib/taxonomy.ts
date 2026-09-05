/**
 * Shared taxonomy utilities.
 * Previously duplicated between:
 *   - app/(public)/[collection]/taxonomy/page.tsx  (Server Component)
 *   - components/browse/TaxonomyTree.tsx            (Client Component)
 */

export const TAXONOMY_COLS =
  'id, vn_name, scientific_name, tax_class_vn, tax_class_latin, tax_order_vn, tax_order_latin, tax_family_vn, tax_family_latin, tax_genus_vn, tax_genus_latin, species_index'

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
}

type GenusNode  = { vn: string; species: SpeciesRow[] }
type FamilyNode = { vn: string; genera: Record<string, GenusNode> }
type OrderNode  = { vn: string; families: Record<string, FamilyNode> }
type ClassNode  = { vn: string; orders: Record<string, OrderNode> }
export type TaxonomyTree = Record<string, ClassNode>

/** Sort flat rows: Class → Order → Family → species_index */
export function sortTaxonomyRows(rows: SpeciesRow[]): SpeciesRow[] {
  return [...rows].sort((a, b) => {
    const cl = (a.tax_class_latin || '').localeCompare(b.tax_class_latin || '')
    if (cl !== 0) return cl
    const or = (a.tax_order_latin || '').localeCompare(b.tax_order_latin || '')
    if (or !== 0) return or
    const fa = (a.tax_family_latin || '').localeCompare(b.tax_family_latin || '')
    if (fa !== 0) return fa
    return (a.species_index || 0) - (b.species_index || 0)
  })
}

/** Assemble a nested taxonomy tree from flat (pre-sorted) rows */
export function buildTaxonomyTree(rows: SpeciesRow[]): TaxonomyTree {
  const tree: TaxonomyTree = {}
  for (const sp of rows) {
    const cl  = sp.tax_class_latin  || 'Unknown'
    const clv = sp.tax_class_vn     || cl
    const or  = sp.tax_order_latin  || 'Unknown'
    const orv = sp.tax_order_vn     || or
    const fa  = sp.tax_family_latin || 'Unknown'
    const fav = sp.tax_family_vn    || fa
    const ge  = sp.tax_genus_latin  || 'Unknown'
    const gev = sp.tax_genus_vn     || ge

    if (!tree[cl]) tree[cl] = { vn: clv, orders: {} }
    if (!tree[cl].orders[or]) tree[cl].orders[or] = { vn: orv, families: {} }
    if (!tree[cl].orders[or].families[fa]) tree[cl].orders[or].families[fa] = { vn: fav, genera: {} }
    if (!tree[cl].orders[or].families[fa].genera[ge])
      tree[cl].orders[or].families[fa].genera[ge] = { vn: gev, species: [] }
    tree[cl].orders[or].families[fa].genera[ge].species.push(sp)
  }
  return tree
}
