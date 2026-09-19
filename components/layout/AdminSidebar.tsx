'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import AuthStatus from '@/components/layout/AuthStatus'
import { 
  LayoutDashboard, BookOpen, ExternalLink, Fish, Leaf, 
  Shrimp, Turtle, Biohazard, Shell, Sparkles, Waves, 
  PanelLeftClose, PanelLeftOpen, Compass, ShieldCheck, Microscope
} from 'lucide-react'
import { db } from '@/lib/supabase-browser'

interface EcoNavItem {
  href: string
  label: string
  shortLabel: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  color: string
  slug: string
  defaultCount: number
}

const ECO_NAV: EcoNavItem[] = [
  { href: '/admin/ca-bien',       label: 'Cá biển Việt Nam',    shortLabel: 'Cá biển',       icon: Fish,      color: '#00f0d0', slug: 'ca-bien',       defaultCount: 1764 },
  { href: '/admin/thuc-vat-bien', label: 'Thực vật biển (Rong)', shortLabel: 'Thực vật',     icon: Leaf,      color: '#10b981', slug: 'thuc-vat-bien', defaultCount: 672 },
  { href: '/admin/giap-xac',      label: 'Giáp xác biển',       shortLabel: 'Giáp xác',      icon: Shrimp,    color: '#f87171', slug: 'giap-xac',      defaultCount: 132 },
  { href: '/admin/bo-sat-bien',   label: 'Bò sát biển (Rùa, Rắn)', shortLabel: 'Bò sát',     icon: Turtle,    color: '#f59e0b', slug: 'bo-sat-bien',   defaultCount: 33 },
  { href: '/admin/sinh-vat-doc',  label: 'Động vật độc biển',   shortLabel: 'Sinh vật độc',  icon: Biohazard, color: '#fb7185', slug: 'sinh-vat-doc',  defaultCount: 76 },
  { href: '/admin/than-mem',      label: 'Động vật thân mềm',   shortLabel: 'Thân mềm',      icon: Shell,     color: '#c084fc', slug: 'than-mem',      defaultCount: 74 },
  { href: '/admin/san-ho',        label: 'San hô Việt Nam',     shortLabel: 'San hô',        icon: Sparkles,  color: '#f472b6', slug: 'san-ho',        defaultCount: 42 },
  { href: '/admin/thu-bien',      label: 'Thú biển Việt Nam',   shortLabel: 'Thú biển',      icon: Waves,     color: '#38bdf8', slug: 'thu-bien',      defaultCount: 34 },
  { href: '/admin/dong-vat-phu-du', label: 'Động vật phù du',   shortLabel: 'Phù du',        icon: Microscope, color: '#38bdf8', slug: 'dong-vat-phu-du', defaultCount: 101 },
]

export default function AdminSidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState<boolean>(false)
  const [counts, setCounts] = useState<Record<string, number>>({
    'ca-bien': 1764,
    'thuc-vat-bien': 672,
    'giap-xac': 132,
    'bo-sat-bien': 33,
    'sinh-vat-doc': 76,
    'than-mem': 74,
    'san-ho': 42,
    'thu-bien': 34,
    'dong-vat-phu-du': 101,
  })

  // Read saved collapse state from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('admin_sidebar_collapsed')
      if (saved === 'true') {
        setCollapsed(true)
      }
    } catch {
      // Ignore localStorage errors in SSR or restricted environments
    }
  }, [])

  // Sync collapsed class to admin-wrapper parent for smooth grid transition
  useEffect(() => {
    const wrapper = document.querySelector('.admin-wrapper')
    if (wrapper) {
      if (collapsed) {
        wrapper.classList.add('has-collapsed-sidebar')
      } else {
        wrapper.classList.remove('has-collapsed-sidebar')
      }
    }
  }, [collapsed])

  // Auto-sync fresh counts in background using exact DB count
  useEffect(() => {
    async function syncExactCounts() {
      try {
        const cols = ['ca-bien', 'thuc-vat-bien', 'giap-xac', 'bo-sat-bien', 'sinh-vat-doc', 'than-mem', 'san-ho', 'thu-bien']
        const results = await Promise.all(
          cols.map(c => db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', c).is('deleted_at', null))
        )
        const updated: Record<string, number> = {}
        cols.forEach((c, idx) => {
          if (typeof results[idx].count === 'number') {
            updated[c] = results[idx].count!
          }
        })
        setCounts(prev => ({ ...prev, ...updated }))
      } catch {
        // Silent fallback to default counts
      }
    }
    syncExactCounts()
  }, [])

  const toggleCollapsed = () => {
    setCollapsed(prev => {
      const next = !prev
      try {
        localStorage.setItem('admin_sidebar_collapsed', String(next))
      } catch {
        // Ignore
      }
      return next
    })
  }

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href)

  return (
    <aside 
      className={`admin-sidebar${collapsed ? ' collapsed' : ''}`} 
      aria-label="Thanh điều hướng quản trị"
    >
      {/* ── Brand Header ── */}
      <div className="admin-sidebar__brand">
        <div className="admin-sidebar__brand-content">
          <div className="brand-icon" aria-hidden="true" title="Trung tâm Chỉ huy Đa dạng Sinh học Biển VN">
            <Compass size={20} />
          </div>
          {!collapsed && (
            <div className="admin-sidebar__brand-text">
              <span className="brand-label">TRUNG TÂM CHỈ HUY</span>
              <span className="brand-sub">Sinh vật biển Việt Nam</span>
            </div>
          )}
        </div>

        {/* Toggle Collapse Button */}
        <button
          type="button"
          data-class="btn"
          className="admin-sidebar__toggle-btn"
          onClick={toggleCollapsed}
          title={collapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng (Icon mode)'}
          aria-label={collapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
        >
          {collapsed ? <PanelLeftOpen size={15} /> : <PanelLeftClose size={15} />}
        </button>
      </div>

      {/* ── Quick Link to Public Portal ── */}
      <div className="admin-sidebar__extlink">
        {collapsed ? (
          <Link href="/" className="admin-back-btn admin-back-btn--mini" title="Mở trang tra cứu công cộng">
            <ExternalLink size={14} aria-hidden="true" />
          </Link>
        ) : (
          <Link href="/" className="admin-back-btn" title="Mở trang tra cứu công cộng">
            <span>Tra cứu người dùng</span>
            <ExternalLink size={12} aria-hidden="true" />
          </Link>
        )}
      </div>

      {/* ── Navigation Tree ── */}
      <nav className="admin-sidebar__nav">
        {/* SECTION 1: CORE OPERATIONS */}
        <div className="admin-nav-group">
          {!collapsed ? (
            <span className="admin-nav-section-label">Quản Trị Cốt Lõi</span>
          ) : (
            <div className="admin-nav-mini-divider" title="Quản Trị Cốt Lõi" />
          )}

          {/* 1. Tổng quan */}
          <Link
            href="/admin"
            className={`admin-nav-link${isActive('/admin', true) ? ' active' : ''}`}
            aria-current={isActive('/admin', true) ? 'page' : undefined}
            title={collapsed ? 'Thống kê tổng quan' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">
              <LayoutDashboard size={18} />
            </span>
            {!collapsed && <span className="nav-label">Thống kê tổng quan</span>}
          </Link>

          {/* 2. Tài liệu gốc */}
          <Link
            href="/admin/literature"
            className={`admin-nav-link${isActive('/admin/literature') ? ' active' : ''}`}
            aria-current={isActive('/admin/literature') ? 'page' : undefined}
            title={collapsed ? 'Tài liệu & Chuyên khảo nguồn' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">
              <BookOpen size={18} />
            </span>
            {!collapsed && <span className="nav-label">Tài liệu &amp; Chuyên khảo</span>}
          </Link>
        </div>

        {/* SECTION 2: 8 BIODIVERSITY PHYLA */}
        <div className="admin-nav-group" style={{ marginTop: '0.5rem' }}>
          {!collapsed ? (
            <span className="admin-nav-section-label">8 Phân Hệ Sinh Thái</span>
          ) : (
            <div className="admin-nav-mini-divider" title="8 Phân Hệ Sinh Thái" />
          )}

          {ECO_NAV.map((item) => {
            const active = isActive(item.href)
            const count = counts[item.slug] || item.defaultCount
            const IconComponent = item.icon

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`admin-nav-link admin-nav-link--eco${active ? ' active' : ''}`}
                aria-current={active ? 'page' : undefined}
                title={collapsed ? `${item.label} (${count.toLocaleString('vi-VN')} loài)` : undefined}
              >
                {/* Ecological Dot Indicator */}
                <span 
                  className="eco-nav-dot" 
                  style={{ backgroundColor: item.color, boxShadow: `0 0 8px ${item.color}88` }}
                  aria-hidden="true" 
                />

                <span className="nav-icon" aria-hidden="true" style={{ color: active ? item.color : undefined }}>
                  <IconComponent size={17} />
                </span>

                {!collapsed && (
                  <>
                    <span className="nav-label" style={{ flex: 1 }}>{item.label}</span>
                    <span className="eco-nav-badge">
                      {count.toLocaleString('vi-VN')}
                    </span>
                  </>
                )}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* ── Footer / Security Status & Auth Profile ── */}
      <div className="admin-sidebar__footer">
        <AuthStatus collapsed={collapsed} />

        {!collapsed ? (
          <div className="admin-sidebar__live-status">
            <span className="admin-sidebar__live-dot" />
            <span>CSDL TRỰC TUYẾN · RLS BẢO VỆ</span>
          </div>
        ) : (
          <div className="admin-sidebar__live-status-mini" title="CSDL Trực Tuyến · Supabase RLS Protected">
            <span className="admin-sidebar__live-dot" />
          </div>
        )}
      </div>
    </aside>
  )
}
