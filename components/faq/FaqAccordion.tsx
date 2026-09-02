'use client'

import { useState, useMemo } from 'react'
import { Search, ChevronDown, BookOpen, Database, Sparkles, ShieldCheck, HelpCircle } from 'lucide-react'
import { FAQ_DATA, FaqItem } from '@/lib/faq-data'

export default function FaqAccordion() {
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({
    'about-1': true, // Open the first question by default
    'sources-1': true
  })

  const toggleItem = (id: string) => {
    setOpenItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  const expandAll = () => {
    const allOpen: Record<string, boolean> = {}
    FAQ_DATA.forEach(item => { allOpen[item.id] = true })
    setOpenItems(allOpen)
  }

  const collapseAll = () => {
    setOpenItems({})
  }

  // Filter items based on activeCategory and searchQuery
  const filteredItems = useMemo(() => {
    return FAQ_DATA.filter(item => {
      const matchesCat = activeCategory === 'all' || item.category === activeCategory
      if (!matchesCat) return false
      if (!searchQuery.trim()) return true

      const q = searchQuery.toLowerCase().trim()
      return (
        item.question.toLowerCase().includes(q) ||
        item.answer.toLowerCase().includes(q) ||
        (item.highlights && item.highlights.some(h => h.toLowerCase().includes(q)))
      )
    })
  }, [activeCategory, searchQuery])

  return (
    <div className="faq-container">
      {/* Search & Category Filter Controls */}
      <div className="faq-controls">
        <div className="faq-search-wrapper">
          <Search className="faq-search-icon" size={18} />
          <input
            type="text"
            className="faq-search-input"
            placeholder="Tìm kiếm câu hỏi (ví dụ: WoRMS, bản quyền, sách gốc, FishBase...)"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            aria-label="Tìm kiếm câu hỏi thường gặp"
          />
          {searchQuery && (
            <button
              className="faq-search-clear"
              onClick={() => setSearchQuery('')}
              type="button"
              aria-label="Xóa từ khóa tìm kiếm"
            >
              ✕
            </button>
          )}
        </div>

        <div className="faq-categories" role="tablist" aria-label="Nhóm câu hỏi">
          <button
            role="tab"
            aria-selected={activeCategory === 'all'}
            className={`faq-cat-btn${activeCategory === 'all' ? ' active' : ''}`}
            onClick={() => setActiveCategory('all')}
            type="button"
          >
            Tất cả ({FAQ_DATA.length})
          </button>
          <button
            role="tab"
            aria-selected={activeCategory === 'about'}
            className={`faq-cat-btn${activeCategory === 'about' ? ' active' : ''}`}
            onClick={() => setActiveCategory('about')}
            type="button"
          >
            <HelpCircle size={15} /> Về dự án
          </button>
          <button
            role="tab"
            aria-selected={activeCategory === 'sources'}
            className={`faq-cat-btn${activeCategory === 'sources' ? ' active' : ''}`}
            onClick={() => setActiveCategory('sources')}
            type="button"
          >
            <BookOpen size={15} /> Nguồn tài liệu
          </button>
          <button
            role="tab"
            aria-selected={activeCategory === 'tech'}
            className={`faq-cat-btn${activeCategory === 'tech' ? ' active' : ''}`}
            onClick={() => setActiveCategory('tech')}
            type="button"
          >
            <Sparkles size={15} /> Công nghệ & Dữ liệu
          </button>
          <button
            role="tab"
            aria-selected={activeCategory === 'rights'}
            className={`faq-cat-btn${activeCategory === 'rights' ? ' active' : ''}`}
            onClick={() => setActiveCategory('rights')}
            type="button"
          >
            <ShieldCheck size={15} /> Bản quyền & Đóng góp
          </button>
        </div>

        <div className="faq-actions">
          <span className="faq-result-count">
            Hiển thị <strong>{filteredItems.length}</strong> câu hỏi
          </span>
          <div className="faq-toggle-btns">
            <button type="button" onClick={expandAll} className="faq-text-action">
              Mở tất cả
            </button>
            <span className="faq-action-divider">•</span>
            <button type="button" onClick={collapseAll} className="faq-text-action">
              Thu gọn
            </button>
          </div>
        </div>
      </div>

      {/* Questions Accordion List */}
      {filteredItems.length === 0 ? (
        <div className="faq-empty">
          <HelpCircle size={36} className="faq-empty-icon" />
          <p className="faq-empty-title">Không tìm thấy câu hỏi phù hợp</p>
          <p className="faq-empty-desc">
            Không có kết quả nào khớp với từ khóa <em>&ldquo;{searchQuery}&rdquo;</em>. Chú ý kiểm tra lại chính tả hoặc chuyển sang nhóm câu hỏi khác.
          </p>
          <button
            type="button"
            className="faq-empty-reset"
            onClick={() => { setSearchQuery(''); setActiveCategory('all') }}
          >
            Xem tất cả câu hỏi
          </button>
        </div>
      ) : (
        <div className="faq-accordion-list">
          {filteredItems.map(item => {
            const isOpen = !!openItems[item.id]
            return (
              <article key={item.id} className={`faq-card${isOpen ? ' is-open' : ''}`}>
                <button
                  type="button"
                  className="faq-card__header"
                  onClick={() => toggleItem(item.id)}
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${item.id}`}
                >
                  <div className="faq-card__title-group">
                    <span className={`faq-badge faq-badge--${item.category}`}>
                      {item.categoryLabel}
                    </span>
                    <h3 className="faq-card__question">{item.question}</h3>
                  </div>
                  <span className={`faq-card__chevron${isOpen ? ' rotated' : ''}`} aria-hidden="true">
                    <ChevronDown size={20} />
                  </span>
                </button>

                {isOpen && (
                  <div id={`faq-answer-${item.id}`} className="faq-card__body">
                    <div className="faq-card__answer">
                      {item.answer.split('\n\n').map((paragraph, pIdx) => (
                        <p key={pIdx}>{paragraph}</p>
                      ))}
                    </div>

                    {item.highlights && item.highlights.length > 0 && (
                      <div className="faq-card__highlights">
                        <div className="faq-highlights-label">Điểm cốt lõi:</div>
                        <ul>
                          {item.highlights.map((point, ptIdx) => (
                            <li key={ptIdx}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </article>
            )
          })}
        </div>
      )}
    </div>
  )
}
