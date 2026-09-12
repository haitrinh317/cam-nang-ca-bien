'use client'

import {
  Tag,
  Globe,
  Fish,
  Compass,
  Sparkles,
  Archive,
  Building2,
  CheckCircle2,
  MapPin,
  Calendar,
  BookOpen,
  Waves,
} from 'lucide-react'
import SpecimenVisualWidgets from '../SpecimenVisualWidgets'
import ToxicologyWidget from '../ToxicologyWidget'
import {
  getResolvedMorphologyVn,
  getResolvedEcologyVn,
  getResolvedEconomicValueVn
} from '@/lib/species-text'
import {
  parseLiterature,
  parseLocations,
  parseStatus,
  formatAlternateNames,
} from '@/lib/species-parsers'
import type { Species } from '../SpecimenCard'
import type { BiologyData } from '../BiologyDashboard'

interface ThongsoTabProps {
  sp: Species
  bio: BiologyData | null
}

export default function ThongsoTab({ sp, bio }: ThongsoTabProps) {
  return (
    <div
      id="tab-panel-thongso"
      role="tabpanel"
      aria-labelledby="tab-thongso"
      className="detail-tab-panel active"
    >
      <div className="specimen-thongso-container">
        {/* 1. Thẻ Định Danh Tên Gọi (Identifier Card) */}
        {(sp.vn_alternate_names || sp.en_common_name) && (
          <div className="specimen-identity-card">
            {sp.vn_alternate_names && (
              <div className="specimen-identity-col">
                <span className="specimen-identity-label">
                  <Tag size={13} />
                  <span>Tên gọi khác:</span>
                </span>
                <span className="specimen-identity-val">{formatAlternateNames(sp.vn_alternate_names)}</span>
              </div>
            )}
            {sp.en_common_name && (
              <div className="specimen-identity-col">
                <span className="specimen-identity-label">
                  <Globe size={13} />
                  <span>Common Name:</span>
                </span>
                <span className="specimen-identity-val specimen-identity-val--en">{sp.en_common_name}</span>
              </div>
            )}
          </div>
        )}

        {/* 2. Trực quan hóa dữ liệu sinh trắc học (Kích thước, Độ sâu sinh thái, Vùng biển phân bố) */}
        <SpecimenVisualWidgets
          vnSizeStr={sp.vn_size}
          enSizeStr={sp.en_size}
          maxLengthStr={bio?.maxLength}
          depthStr={bio?.depth}
          depthVnStr={bio?.depthVn}
          distributionStr={sp.vn_distribution || sp.en_distribution}
        />

        {/* 3. Lưới Bento 2 cột (Hình thái học & Sinh thái dinh dưỡng từ sách gốc OCR) */}
        {(() => {
          const displayMorph = getResolvedMorphologyVn(sp, bio)
          const displayEcology = getResolvedEcologyVn(sp)
          if (!displayMorph && !displayEcology) return null

          return (
            <div className="specimen-bento-grid">
              {displayMorph && (
                <div className="specimen-bento-card">
                  <div className="specimen-bento-card__header">
                    <div className="specimen-bento-card__title-group">
                      <span className="specimen-bento-card__icon">
                        <Fish size={16} />
                      </span>
                      <h3 className="specimen-bento-card__title">Đặc điểm hình thái</h3>
                    </div>
                    <span className="specimen-bento-card__badge">Hình thái học</span>
                  </div>
                  <p
                    className="specimen-bento-card__content"
                    style={{
                      maxWidth: 'none',
                      width: '100%',
                      textWrap: 'pretty',
                    }}
                  >
                    {displayMorph}
                  </p>
                </div>
              )}

              {displayEcology && (
                <div className="specimen-bento-card">
                  <div className="specimen-bento-card__header">
                    <div className="specimen-bento-card__title-group">
                      <span className="specimen-bento-card__icon specimen-bento-card__icon--blue">
                        <Compass size={16} />
                      </span>
                      <h3 className="specimen-bento-card__title">Sinh thái &amp; Dinh dưỡng</h3>
                    </div>
                    <span className="specimen-bento-card__badge">Tập tính sinh thái</span>
                  </div>
                  <p
                    className="specimen-bento-card__content"
                    style={{
                      maxWidth: 'none',
                      width: '100%',
                      textWrap: 'pretty',
                    }}
                  >
                    {displayEcology}
                  </p>
                </div>
              )}
            </div>
          )
        })()}

        {/* 4. Giá trị kinh tế & Sử dụng (Từ sách gốc OCR) */}
        {(() => {
          const displayEconomic = getResolvedEconomicValueVn(sp)
          if (!displayEconomic) return null

          const lower = displayEconomic.toLowerCase()
          const isAquarium = lower.includes('cá cảnh') || lower.includes('làm cảnh') || lower.includes('thủy sinh')
          const isFood = lower.includes('thực phẩm') || lower.includes('thương phẩm') || lower.includes('hải sản') || lower.includes('tươi sống') || lower.includes('ăn thịt')

          return (
            <div className="specimen-value-card">
              <div className="specimen-bento-card__header">
                <div className="specimen-bento-card__title-group">
                  <span className="specimen-bento-card__icon specimen-bento-card__icon--amber">
                    <Sparkles size={16} />
                  </span>
                  <h3 className="specimen-bento-card__title">Giá trị sử dụng &amp; Kinh tế</h3>
                </div>
                <div className="specimen-value-tags">
                  {isAquarium && <span className="specimen-value-tag specimen-value-tag--aquarium">Cá cảnh</span>}
                  {isFood && <span className="specimen-value-tag specimen-value-tag--food">Thực phẩm</span>}
                </div>
              </div>
              <p
                className="specimen-bento-card__content"
                style={{
                  maxWidth: 'none',
                  width: '100%',
                  textWrap: 'pretty',
                }}
              >
                {displayEconomic}
              </p>
            </div>
          )
        })()}

        {/* Hồ sơ Độc học & Phác đồ Cấp cứu (Chuyên khảo Động vật độc biển VN) */}
        {bio?.toxicology && (
          <ToxicologyWidget
            toxicology={bio.toxicology}
            speciesName={sp.vn_name}
            scientificName={sp.scientific_name}
          />
        )}

        {/* 5. Hồ sơ Mẫu vật & Tài liệu dẫn (Specimen Archive Vault) */}
        {(() => {
          const spec = sp.vn_specimen || sp.en_specimen
          const stat = sp.vn_status || sp.en_status
          const lit = sp.vn_literature || sp.en_literature
          const hasField = sp.photo_place || sp.photo_depth || sp.photo_date
          if (!spec && !stat && !lit && !hasField) return null

          const specList = spec ? parseLocations(spec) : []
          const statusItems = stat ? parseStatus(stat) : []
          const litList = lit ? parseLiterature(lit) : []

          return (
            <div className="specimen-vault-card">
              <div className="specimen-bento-card__header">
                <div className="specimen-bento-card__title-group">
                  <span className="specimen-bento-card__icon specimen-bento-card__icon--purple">
                    <Archive size={16} />
                  </span>
                  <h3 className="specimen-bento-card__title">Hồ sơ Mẫu vật &amp; Tài liệu dẫn</h3>
                </div>
                {litList.length > 0 && (
                  <span className="specimen-bento-card__badge">
                    <BookOpen size={12} style={{ marginRight: 3 }} />
                    {litList.length} tài liệu dẫn
                  </span>
                )}
              </div>

              {(specList.length > 0 || statusItems.length > 0) && (
                <div className={`specimen-vault-grid ${specList.length > 0 && statusItems.length > 0 ? 'specimen-vault-grid--2cols' : 'specimen-vault-grid--1col'}`}>
                  {specList.length > 0 && (
                    <div className="specimen-vault-item">
                      <span className="specimen-vault-item__label">
                        <Building2 size={13} />
                        <span>Nơi lưu trữ mẫu vật</span>
                      </span>
                      {specList.length === 1 ? (
                        <span className="specimen-vault-item__val">{specList[0]}</span>
                      ) : (
                        <div className="specimen-vault-locations">
                          {specList.map((loc, i) => (
                            <div key={i} className="specimen-vault-location-row">
                              <span className="specimen-vault-dot" />
                              <span>{loc}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {statusItems.length > 0 && (
                    <div className="specimen-vault-item">
                      <span className="specimen-vault-item__label">
                        <CheckCircle2 size={13} />
                        <span>Tình trạng mẫu / ghi nhận</span>
                      </span>
                      {statusItems.length === 1 && !statusItems[0].label ? (
                        <span className="specimen-vault-item__val">{statusItems[0].text}</span>
                      ) : (
                        <div className="specimen-vault-status-list">
                          {statusItems.map((item, i) => (
                            <div key={i} className="specimen-vault-status-row">
                              {item.label ? (
                                <>
                                  <span className="specimen-vault-status-label">{item.label}:</span>{' '}
                                  <span className="specimen-vault-status-text">{item.text}</span>
                                </>
                              ) : (
                                <span className="specimen-vault-status-text">{item.text}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Thông tin thu mẫu thực địa nếu có */}
              {hasField && (
                <div className="specimen-vault-meta">
                  {sp.photo_place && (
                    <span className="specimen-meta-pill">
                      <MapPin size={12} />
                      <span>{sp.photo_place}</span>
                    </span>
                  )}
                  {sp.photo_depth && (
                    <span className="specimen-meta-pill">
                      <Waves size={12} />
                      <span>Độ sâu: {sp.photo_depth}</span>
                    </span>
                  )}
                  {sp.photo_date && (
                    <span className="specimen-meta-pill">
                      <Calendar size={12} />
                      <span>Ngày thu mẫu: {sp.photo_date}</span>
                    </span>
                  )}
                </div>
              )}

              {/* Danh mục tài liệu tham khảo */}
              {litList.length > 0 && (
                <div className="specimen-literature-box">
                  {litList.map((item, idx) => (
                    <div key={idx} className="specimen-lit-item">
                      <span className="specimen-lit-idx">[{idx + 1}]</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })()}
      </div>
    </div>
  )
}
