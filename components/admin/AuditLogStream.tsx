'use client'

import { useState, useCallback, useTransition } from 'react'
import Link from 'next/link'
import { 
  ArrowRight, RotateCw, PlusCircle, Edit2, Trash2, 
  Layers, RefreshCw, Database, ShieldCheck, Clock, 
  Calendar, ChevronLeft, ChevronRight, Filter, Eye
} from 'lucide-react'

export interface LogEntry {
  id: number
  created_at: string
  user_email: string | null
  action: string
  collection_id?: string | null
  species_id?: string | null
  details: unknown
}

interface Props {
  initialLogs: LogEntry[]
  initialTotal?: number
}

const ACTION_MAP: Record<string, { label: string; cls: string; icon: React.ComponentType<{ size?: number; className?: string }> }> = {
  create:              { label: 'Thêm mới',           cls: 'audit-badge-pro--create', icon: PlusCircle },
  update:              { label: 'Cập nhật',           cls: 'audit-badge-pro--update', icon: Edit2 },
  delete:              { label: 'Xóa dữ liệu',        cls: 'audit-badge-pro--delete', icon: Trash2 },
  bulk_delete:         { label: 'Xóa hàng loạt',      cls: 'audit-badge-pro--delete', icon: Trash2 },
  merge_species:       { label: 'Hợp nhất tri thức',  cls: 'audit-badge-pro--merge',  icon: Layers },
  merge_species_fish:  { label: 'Hợp nhất cá biển',   cls: 'audit-badge-pro--merge',  icon: Layers },
  sync_worms:          { label: 'Đồng bộ WoRMS',      cls: 'audit-badge-pro--sync',   icon: RefreshCw },
  bulk_import:         { label: 'Import dữ liệu',     cls: 'audit-badge-pro--bulk',   icon: Database },
}

const COLLECTIONS = [
  { slug: 'all', label: 'Tất cả phân hệ sinh thái' },
  { slug: 'ca-bien', label: 'Cá biển (Tập I-VI)' },
  { slug: 'thuc-vat-bien', label: 'Thực vật biển (Rong)' },
  { slug: 'giap-xac', label: 'Giáp xác (Tôm, Cua)' },
  { slug: 'bo-sat-bien', label: 'Bò sát biển (Rùa, Rắn)' },
  { slug: 'sinh-vat-doc', label: 'Sinh vật độc' },
  { slug: 'than-mem', label: 'Thân mềm (Ốc, Mực)' },
  { slug: 'san-ho', label: 'San hô' },
  { slug: 'thu-bien', label: 'Thú biển (Cá voi, Dugong)' },
]

function formatRelativeTime(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 1) return 'Vừa xong'
    if (diffMins < 60) return `${diffMins} phút trước`
    if (diffHours < 24) return `${diffHours} giờ trước`
    if (diffDays === 1) return 'Hôm qua'
    if (diffDays < 7) return `${diffDays} ngày trước`
    return d.toLocaleDateString('vi-VN')
  } catch {
    return dateStr
  }
}

function parseFormattedDetails(details: unknown): React.ReactNode {
  if (!details) return <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>Không có chi tiết</span>

  let text = ''
  if (typeof details === 'string') {
    try {
      const parsed = JSON.parse(details)
      if (typeof parsed === 'object' && parsed !== null) {
        const parts: string[] = []
        if (parsed.vn_name) parts.push(`"${parsed.vn_name}"`)
        if (parsed.scientific_name) parts.push(`(${parsed.scientific_name})`)
        if (parsed.volume) parts.push(`Tập ${parsed.volume}`)
        if (parsed.count) parts.push(`${parsed.count} loài`)
        text = parts.length > 0 ? parts.join(' ') : JSON.stringify(parsed).replace(/["{}]/g, '')
      } else {
        text = details
      }
    } catch {
      text = details
    }
  } else if (typeof details === 'object' && details !== null) {
    const parsed = details as Record<string, unknown>
    const parts: string[] = []
    if (parsed.vn_name) parts.push(`"${parsed.vn_name}"`)
    if (parsed.scientific_name) parts.push(`(${parsed.scientific_name})`)
    if (parsed.volume) parts.push(`Tập ${parsed.volume}`)
    if (parsed.count) parts.push(`${parsed.count} loài`)
    text = parts.length > 0 ? parts.join(' ') : JSON.stringify(parsed).replace(/["{}]/g, '')
  } else {
    text = String(details)
  }

  // Check if text has Latin name in parentheses like (Lepidochelys olivacea)
  const match = text.match(/^(.*?)(\([^)]+\))(.*)$/)
  if (match) {
    const [, before, latin, after] = match
    return (
      <span className="audit-details-cell">
        <span className="audit-details-entity">{before}</span>
        <span className="audit-details-latin">{latin}</span>
        <span>{after}</span>
      </span>
    )
  }

  return <span className="audit-details-cell">{text}</span>
}

type FilterAction = 'all' | 'update' | 'merge' | 'create' | 'delete'
type DatePreset = 'all' | 'today' | '7days' | '30days' | 'custom'

export default function AuditLogStream({ initialLogs, initialTotal }: Props) {
  const [logs, setLogs] = useState<LogEntry[]>(initialLogs)
  const [total, setTotal] = useState<number>(initialTotal || initialLogs.length)
  const [page, setPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(10)
  const [collection, setCollection] = useState<string>('all')
  const [action, setAction] = useState<FilterAction>('all')
  const [datePreset, setDatePreset] = useState<DatePreset>('all')
  const [customFromDate, setCustomFromDate] = useState<string>('')
  const [customToDate, setCustomToDate] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [refreshing, setRefreshing] = useState<boolean>(false)

  const [, startTransition] = useTransition()

  // Fetch logic with parameters
  const loadLogs = useCallback(async (
    targetPage: number,
    targetPageSize: number,
    targetCol: string,
    targetAct: FilterAction,
    targetPreset: DatePreset,
    fromDateStr: string,
    toDateStr: string
  ) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('page', String(targetPage))
      params.set('pageSize', String(targetPageSize))
      if (targetCol !== 'all') params.set('collection', targetCol)
      if (targetAct !== 'all') params.set('action', targetAct)

      const now = new Date()
      const todayStr = now.toISOString().split('T')[0]

      if (targetPreset === 'today') {
        params.set('fromDate', todayStr)
        params.set('toDate', todayStr)
      } else if (targetPreset === '7days') {
        const d7 = new Date()
        d7.setDate(d7.getDate() - 7)
        params.set('fromDate', d7.toISOString().split('T')[0])
        params.set('toDate', todayStr)
      } else if (targetPreset === '30days') {
        const d30 = new Date()
        d30.setDate(d30.getDate() - 30)
        params.set('fromDate', d30.toISOString().split('T')[0])
        params.set('toDate', todayStr)
      } else if (targetPreset === 'custom') {
        if (fromDateStr) params.set('fromDate', fromDateStr)
        if (toDateStr) params.set('toDate', toDateStr)
      }

      const res = await fetch(`/api/audit-log?${params.toString()}`)
      if (res.ok) {
        const json = await res.json()
        startTransition(() => {
          setLogs(json.data || [])
          setTotal(json.total || 0)
          setPage(json.page || targetPage)
        })
      }
    } catch (err) {
      console.error('Failed to load audit logs:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Handlers for filter changes
  const handleActionChange = (newAction: FilterAction) => {
    setAction(newAction)
    setPage(1)
    loadLogs(1, pageSize, collection, newAction, datePreset, customFromDate, customToDate)
  }

  const handleCollectionChange = (newCol: string) => {
    setCollection(newCol)
    setPage(1)
    loadLogs(1, pageSize, newCol, action, datePreset, customFromDate, customToDate)
  }

  const handleDatePresetChange = (newPreset: DatePreset) => {
    setDatePreset(newPreset)
    setPage(1)
    loadLogs(1, pageSize, collection, action, newPreset, customFromDate, customToDate)
  }

  const handleCustomDateApply = () => {
    setPage(1)
    loadLogs(1, pageSize, collection, action, 'custom', customFromDate, customToDate)
  }

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    loadLogs(newPage, pageSize, collection, action, datePreset, customFromDate, customToDate)
  }

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setPage(1)
    loadLogs(1, newPageSize, collection, action, datePreset, customFromDate, customToDate)
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadLogs(page, pageSize, collection, action, datePreset, customFromDate, customToDate)
    setRefreshing(false)
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const fromItem = total > 0 ? (page - 1) * pageSize + 1 : 0
  const toItem = Math.min(total, page * pageSize)

  return (
    <section className="audit-stream-card" aria-labelledby="activity-heading">
      {/* ── Header ── */}
      <div className="audit-stream-card__header">
        <div>
          <div className="audit-stream-live-pill">
            <span className="audit-stream-dot" />
            <span>LIVE STREAM BẢO MẬT</span>
          </div>
          <h2 id="activity-heading" className="audit-stream-title">
            Nhật Ký Kiểm Toán Thời Gian Thực
          </h2>
          <p className="audit-stream-subtitle">
            Cơ chế kiểm toán tự động theo dõi biến động dữ liệu Supabase theo từng mili-giây.
          </p>
        </div>

        <div className="audit-stream-header-actions">
          <button
            type="button"
            data-class="btn"
            className="btn btn-outline btn-sm"
            onClick={handleRefresh}
            disabled={refreshing || loading}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
            title="Làm mới dòng kiểm toán"
          >
            <RotateCw size={13} className={refreshing || loading ? 'admin-spin' : ''} />
            <span>{refreshing ? 'Đang đọc...' : 'Làm mới'}</span>
          </button>

          <Link href="/admin/ca-bien" className="btn btn-outline btn-sm" data-class="btn" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
            <span>Duyệt CSDL</span>
            <ArrowRight size={13} aria-hidden="true" />
          </Link>
        </div>
      </div>

      {/* ── Filter Bar Tier 1: Action Chips ── */}
      <div className="audit-filter-bar">
        <div className="audit-filter-chips">
          <button
            type="button"
            data-class="chip-btn"
            className={`audit-filter-chip${action === 'all' ? ' active' : ''}`}
            onClick={() => handleActionChange('all')}
          >
            Tất cả hoạt động
          </button>
          <button
            type="button"
            data-class="chip-btn"
            className={`audit-filter-chip${action === 'update' ? ' active' : ''}`}
            onClick={() => handleActionChange('update')}
          >
            Cập nhật
          </button>
          <button
            type="button"
            data-class="chip-btn"
            className={`audit-filter-chip${action === 'merge' ? ' active' : ''}`}
            onClick={() => handleActionChange('merge')}
          >
            Hợp nhất tri thức
          </button>
          <button
            type="button"
            data-class="chip-btn"
            className={`audit-filter-chip${action === 'create' ? ' active' : ''}`}
            onClick={() => handleActionChange('create')}
          >
            Thêm mới
          </button>
          <button
            type="button"
            data-class="chip-btn"
            className={`audit-filter-chip${action === 'delete' ? ' active' : ''}`}
            onClick={() => handleActionChange('delete')}
          >
            Xóa
          </button>
        </div>

        <span className="audit-stream-counter">
          Hiển thị <strong>{logs.length}</strong> / <strong>{total}</strong> thao tác
        </span>
      </div>

      {/* ── Filter Bar Tier 2: Collection & Date Presets ── */}
      <div className="audit-filter-secondary">
        {/* Nhóm sinh vật */}
        <div className="audit-filter-group">
          <span className="audit-filter-label">
            <Layers size={13} style={{ color: '#0284c7' }} />
            <span>Phân hệ:</span>
          </span>
          <div className="audit-filter-select-wrap">
            <select
              value={collection}
              onChange={(e) => handleCollectionChange(e.target.value)}
              className="audit-filter-select"
              title="Lọc theo nhóm sinh vật"
            >
              {COLLECTIONS.map((c) => (
                <option key={c.slug} value={c.slug}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Mốc thời gian */}
        <div className="audit-filter-group">
          <span className="audit-filter-label">
            <Calendar size={13} style={{ color: '#00d4b8' }} />
            <span>Thời gian:</span>
          </span>
          <div className="audit-date-chips">
            <button
              type="button"
              data-class="chip-btn"
              className={`audit-date-chip${datePreset === 'all' ? ' active' : ''}`}
              onClick={() => handleDatePresetChange('all')}
            >
              Toàn thời gian
            </button>
            <button
              type="button"
              data-class="chip-btn"
              className={`audit-date-chip${datePreset === 'today' ? ' active' : ''}`}
              onClick={() => handleDatePresetChange('today')}
            >
              Hôm nay
            </button>
            <button
              type="button"
              data-class="chip-btn"
              className={`audit-date-chip${datePreset === '7days' ? ' active' : ''}`}
              onClick={() => handleDatePresetChange('7days')}
            >
              7 ngày qua
            </button>
            <button
              type="button"
              data-class="chip-btn"
              className={`audit-date-chip${datePreset === '30days' ? ' active' : ''}`}
              onClick={() => handleDatePresetChange('30days')}
            >
              30 ngày qua
            </button>
            <button
              type="button"
              data-class="chip-btn"
              className={`audit-date-chip${datePreset === 'custom' ? ' active' : ''}`}
              onClick={() => setDatePreset('custom')}
            >
              Tùy chỉnh...
            </button>
          </div>

          {/* Ô nhập ngày tùy chỉnh */}
          {datePreset === 'custom' && (
            <div className="audit-date-inputs">
              <input
                type="date"
                value={customFromDate}
                onChange={(e) => setCustomFromDate(e.target.value)}
                className="audit-date-input"
                title="Từ ngày"
              />
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>–</span>
              <input
                type="date"
                value={customToDate}
                onChange={(e) => setCustomToDate(e.target.value)}
                className="audit-date-input"
                title="Đến ngày"
              />
              <button
                type="button"
                data-class="btn"
                className="btn btn-outline btn-sm"
                onClick={handleCustomDateApply}
                style={{ padding: '0.15rem 0.5rem', fontSize: '0.74rem', height: 30 }}
              >
                Lọc
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Table Stream Container with Loading Mask ── */}
      <div className="audit-stream-container">
        {loading && (
          <div className="audit-stream-loading-mask">
            <div className="audit-stream-loading-badge">
              <RotateCw size={14} className="admin-spin" />
              <span>Đang đồng bộ dữ liệu kiểm toán...</span>
            </div>
          </div>
        )}

        <div className="admin-table-scroll" style={{ maxHeight: 520 }}>
          <table className="admin-table audit-table">
            <thead>
              <tr>
                <th style={{ width: 170 }}>Hành động</th>
                <th style={{ width: 220 }}>Người thực hiện</th>
                <th>Chi tiết biến động dữ liệu</th>
                <th style={{ width: 170, textAlign: 'right' }}>Thời gian</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: '3.5rem 1rem', color: '#94a3b8' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                      <Filter size={24} style={{ opacity: 0.5, color: '#64748b' }} />
                      <p style={{ margin: 0, fontWeight: 500 }}>Không tìm thấy bản ghi kiểm toán nào phù hợp với bộ lọc hiện tại.</p>
                      <button
                        type="button"
                        data-class="btn"
                        className="btn btn-outline btn-sm"
                        onClick={() => {
                          setAction('all')
                          setCollection('all')
                          setDatePreset('all')
                          setCustomFromDate('')
                          setCustomToDate('')
                          loadLogs(1, pageSize, 'all', 'all', 'all', '', '')
                        }}
                        style={{ marginTop: '0.5rem' }}
                      >
                        Đặt lại bộ lọc
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                logs.map(log => {
                  const act = ACTION_MAP[log.action] || {
                    label: log.action.replace(/_/g, ' '),
                    cls: 'audit-badge-pro--update',
                    icon: ShieldCheck,
                  }
                  const IconComponent = act.icon

                  // User parsing
                  const isSystem = !log.user_email || log.user_email.toLowerCase() === 'system'
                  const userInitial = isSystem ? 'S' : (log.user_email?.charAt(0).toUpperCase() || 'U')
                  const userName = isSystem ? 'Hệ thống' : (log.user_email?.split('@')[0] || 'User')
                  const userRole = isSystem ? 'BOT' : 'ADMIN'

                  // Time parsing
                  const d = new Date(log.created_at)
                  const timeStr = d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                  const dateStr = d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
                  const relativeTime = formatRelativeTime(log.created_at)

                  return (
                    <tr key={log.id}>
                      {/* Hành động */}
                      <td>
                        <span className={`audit-badge-pro ${act.cls}`}>
                          <IconComponent size={13} />
                          <span>{act.label}</span>
                        </span>
                      </td>

                      {/* Người thực hiện */}
                      <td>
                        <div className="audit-user-cell">
                          <div className="audit-user-avatar">
                            {userInitial}
                          </div>
                          <div className="audit-user-meta">
                            <div className="audit-user-name-line">
                              <span className="audit-user-name">{userName}</span>
                              <span className="audit-user-role">{userRole}</span>
                            </div>
                            <span className="audit-user-email">
                              {isSystem ? 'system@cron' : log.user_email}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Chi tiết thay đổi */}
                      <td>
                        <div>
                          {parseFormattedDetails(log.details)}
                          {log.species_id && (
                            <span className="audit-details-tag">#{log.species_id}</span>
                          )}
                          {log.collection_id && (
                            <span className="audit-details-tag" style={{ color: '#059669', borderColor: 'rgba(5, 150, 105, 0.2)' }}>
                              {log.collection_id}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Thời gian */}
                      <td>
                        <div className="audit-time-cell">
                          <span className="audit-time-main">
                            <Clock size={12} style={{ color: '#0284c7' }} />
                            <span>{timeStr}</span>
                          </span>
                          <span className="audit-time-date">
                            {relativeTime} · {dateStr}
                          </span>
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* ── Pagination Footer ── */}
        <div className="audit-pagination-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <span className="admin-pagination__info">
              Trang <strong>{page}</strong> / {totalPages} &nbsp;·&nbsp; Hiển thị <strong>{fromItem} – {toItem}</strong> trên tổng số <strong>{total}</strong> thao tác
            </span>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: '#64748b' }}>
              <span>Số dòng:</span>
              <select
                value={pageSize}
                onChange={e => handlePageSizeChange(Number(e.target.value))}
                className="audit-filter-select"
                style={{ padding: '0.15rem 1.5rem 0.15rem 0.5rem', height: 28, fontSize: '0.76rem' }}
                title="Số bản ghi mỗi trang"
              >
                <option value={10}>10 dòng</option>
                <option value={20}>20 dòng</option>
                <option value={50}>50 dòng</option>
              </select>
            </div>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <button
                className="btn btn-outline btn-sm"
                data-class="btn"
                disabled={page <= 1 || loading}
                onClick={() => handlePageChange(page - 1)}
                type="button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', padding: '0.3rem 0.6rem' }}
                title="Trang trước"
              >
                <ChevronLeft size={14} />
                <span>Trước</span>
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || Math.abs(p - page) <= 2)
                .map((p, idx, arr) => {
                  const showEllipsis = idx > 0 && p - arr[idx - 1] > 1
                  return (
                    <span key={p} style={{ display: 'inline-flex', alignItems: 'center' }}>
                      {showEllipsis && <span style={{ padding: '0 0.25rem', color: '#94a3b8' }}>...</span>}
                      <button
                        type="button"
                        data-class="btn"
                        onClick={() => handlePageChange(p)}
                        disabled={loading}
                        className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-outline'}`}
                        style={{ minWidth: 30, padding: '0 0.4rem', height: 28, fontSize: '0.78rem' }}
                      >
                        {p}
                      </button>
                    </span>
                  )
                })}

              <button
                className="btn btn-outline btn-sm"
                data-class="btn"
                disabled={page >= totalPages || loading}
                onClick={() => handlePageChange(page + 1)}
                type="button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', padding: '0.3rem 0.6rem' }}
                title="Trang sau"
              >
                <span>Sau</span>
                <ChevronRight size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
