import Link from 'next/link'
import { IUCN_LABEL, IUCN_ORDER, HABITAT_LABEL, REGION_LABEL, resultsHref, hasFilters, type SearchFilters, type Facets } from '@/lib/search'

interface Props {
  q: string
  collection: string | null
  filters: SearchFilters
  /** Đếm theo từng nhóm lọc (đã áp các bộ lọc KHÁC, trừ chính nhóm đó). */
  facets: Facets
}

/** Nhóm checkbox: chỉ hiện giá trị có kết quả (count > 0) hoặc đang được chọn. */
function CheckGroup({ legend, name, labels, order, counts, selected, note }: {
  legend: string; name: string; labels: Record<string, string>; order: readonly string[]
  counts: Map<string, number>; selected: string[]; note?: string
}) {
  const keys = order.filter(k => (counts.get(k) ?? 0) > 0 || selected.includes(k))
  if (!keys.length) return null
  return (
    <fieldset className="sr-fs">
      <legend>{legend}</legend>
      {keys.map(k => (
        <label key={k} className="sr-check">
          <input type="checkbox" name={name} value={k} defaultChecked={selected.includes(k)} />
          <span>{labels[k]}</span>
          <em>{counts.get(k) ?? 0}</em>
        </label>
      ))}
      {note && <p className="sr-fs-note">{note}</p>}
    </fieldset>
  )
}

/**
 * Bộ lọc nâng cao — form GET thuần (server component, không JS): trạng thái nằm hết trên URL,
 * chia sẻ được, nút Back hoạt động. Dùng chung cho /tim-kiem (và trang phân hệ qua link ?c=).
 */
export default function FilterPanel({ q, collection, filters, facets }: Props) {

  return (
    <form className="sr-filters" action="/tim-kiem" method="get" aria-label="Bộ lọc nâng cao">
      {q && <input type="hidden" name="q" value={q} />}
      {collection && <input type="hidden" name="c" value={collection} />}

      <CheckGroup
        legend="Mức IUCN" name="iucn" labels={IUCN_LABEL} order={IUCN_ORDER} counts={facets.iucn} selected={filters.iucn}
        note={facets.iucnMissing > 0 ? `${facets.iucnMissing} loài chưa có dữ liệu IUCN (bị ẩn khi chọn mức).` : undefined}
      />
      <CheckGroup
        legend="Vùng biển" name="region" labels={REGION_LABEL} order={Object.keys(REGION_LABEL)} counts={facets.region} selected={filters.region}
        note="Theo địa danh ghi trong sách; loài chỉ ghi chung 'Biển Đông' hoặc không nêu địa danh sẽ không có nhãn vùng."
      />
      <CheckGroup
        legend="Môi trường sống" name="habitat" labels={HABITAT_LABEL} order={Object.keys(HABITAT_LABEL)} counts={facets.habitat} selected={filters.habitat}
        note="Loài chưa có dữ liệu môi trường sống bị ẩn khi chọn."
      />

      <fieldset className="sr-fs">
        <legend>Độ sâu (m)</legend>
        <div className="sr-range">
          <input type="number" name="dmin" min="0" inputMode="decimal" placeholder="Từ" defaultValue={filters.dmin} aria-label="Độ sâu từ (m)" />
          <span aria-hidden="true">–</span>
          <input type="number" name="dmax" min="0" inputMode="decimal" placeholder="Đến" defaultValue={filters.dmax} aria-label="Độ sâu đến (m)" />
        </div>
      </fieldset>

      <fieldset className="sr-fs">
        <legend>Kích thước tối đa (cm)</legend>
        <div className="sr-range">
          <input type="number" name="lmin" min="0" inputMode="decimal" placeholder="Từ" defaultValue={filters.lmin} aria-label="Kích thước từ (cm)" />
          <span aria-hidden="true">–</span>
          <input type="number" name="lmax" min="0" inputMode="decimal" placeholder="Đến" defaultValue={filters.lmax} aria-label="Kích thước đến (cm)" />
        </div>
        <p className="sr-fs-note">Loài chưa có dữ liệu độ sâu/kích thước sẽ bị ẩn khi dùng bộ lọc tương ứng.</p>
      </fieldset>

      <div className="sr-filter-actions">
        <button type="submit" className="sr-btn">Áp dụng</button>
        {(hasFilters(filters)) && <Link href={resultsHref(q, collection)} className="sr-clear">Xóa bộ lọc</Link>}
      </div>
    </form>
  )
}
