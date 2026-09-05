import { 
  HeartPulse, 
  Scale, 
  Ruler, 
  Waves, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Compass, 
  Sparkles,
  Egg,
  Fish,
  Leaf
} from 'lucide-react'
import IucnBadge from './IucnBadge'
import BilingualNoteBlock from './BilingualNoteBlock'
import './BiologyDashboard.css'

export interface BiologyData {
  fbName?: string
  maxLength?: string
  maxWeight?: string
  longevity?: string
  depth?: string
  depthVn?: string
  habitat?: string
  habitatVn?: string
  iucnStatus?: string
  dangerous?: string
  feedingType?: string
  trophicLevel?: number
  reproduction?: string
  spawning?: string
  spawnAggregation?: boolean
  parentalCare?: string
  importance?: string
  importanceVn?: string
  aquaculture?: string
  vulnerability?: number
  priceCategory?: string
  biologySummary?: string
  biologySummaryVn?: string
  ecologyNotes?: string
  ecologyNotesVn?: string
  reproductionNotes?: string
  reproductionNotesVn?: string
  morphDescription?: string
  morphDescriptionVn?: string
  source?: string
  algaebaseId?: number
  algaebaseUrl?: string
}

interface Props {
  bio: BiologyData
  speciesId: string
  collectionId?: string | null
}

// ── Helpers Quy đổi & Định dạng Khoa Học ───────────────────────────

function parseNumber(str: string): number | null {
  const match = str.replace(/,/g, '').match(/[\d.]+/)
  return match ? parseFloat(match[0]) : null
}

/** Quy đổi gram sang kg nếu >= 1000g, format đẹp */
function formatWeight(raw?: string): { main: string; unit: string; note?: string } | null {
  if (!raw) return null
  const num = parseNumber(raw)
  if (num === null) return { main: raw, unit: '' }

  if (num >= 1000) {
    const kg = num / 1000
    const formatted = kg >= 10 ? Math.round(kg).toLocaleString() : kg.toFixed(1)
    return { main: formatted, unit: 'kg', note: `Ghi nhận FishBase (${num.toLocaleString()} g)` }
  }
  return { main: num.toLocaleString(), unit: 'g' }
}

/** Format chiều dài hiển thị gọn gàng */
function formatLength(raw?: string): { main: string; unit: string; type?: string } | null {
  if (!raw) return null
  const num = parseNumber(raw)
  if (num === null) return { main: raw, unit: '' }

  let type = ''
  if (raw.includes('SL')) type = 'Chiều dài chuẩn (SL)'
  else if (raw.includes('TL')) type = 'Chiều dài tổng cộng (TL)'
  else if (raw.includes('FL')) type = 'Chiều dài chẽ đuôi (FL)'
  else if (raw.includes('WD')) type = 'Chiều rộng đĩa (WD)'

  const formatted = num >= 10 ? Math.round(num).toLocaleString() : num.toFixed(1)
  return { main: formatted, unit: 'cm', type }
}

/** Format tuổi thọ */
function formatLongevity(raw?: string): string | null {
  if (!raw) return null
  const num = parseNumber(raw)
  if (num === null) return raw
  return `${Math.round(num)} năm`
}

// ── Từ điển dịch thuật sinh học chuẩn mực ─────────────────────────
const BIO_TRANSLATIONS: Record<string, string> = {
  // Feeding Type
  'hunting macrofauna (predator)': 'Săn mồi lớn (Động vật ăn thịt)',
  'browsing on substrate': 'Kiếm ăn trên nền đáy',
  'grazing on substrate': 'Gặm thức ăn trên rạn / nền đáy',
  'filter feeding': 'Lọc thức ăn phù du',
  'herbivores': 'Ăn thực vật / rong tảo',
  'omnivores': 'Ăn tạp',
  'carnivores': 'Ăn thịt',
  'planktivores': 'Ăn sinh vật phù du',
  'corallivores': 'Ăn polyp san hô',
  'detritivores': 'Ăn mùn bã hữu cơ',
  // Reproduction
  'dioecism, internal (oviduct) fertilization': 'Phân tính, thụ tinh trong (ống dẫn trứng)',
  'dioecism, external fertilization': 'Phân giới tính, thụ tinh ngoài',
  'protogyny, external fertilization': 'Chuyển giới tính (cái sang đực), thụ tinh ngoài',
  'protandry, external fertilization': 'Chuyển giới tính (đực sang cái), thụ tinh ngoài',
  'hermaphroditic': 'Lưỡng tính',
  'oviparous': 'Đẻ trứng (Oviparous)',
  'viviparous': 'Đẻ con (Viviparous)',
  'ovoviviparous': 'Noãn thai sinh (Trứng nở trong bụng mẹ)',
  'none': 'Không có',
  'paternal': 'Cá bố chăm sóc trứng / tổ',
  'maternal': 'Cá mẹ ấp trứng',
  'one clear seasonal peak per year': 'Một đỉnh sinh sản chính trong năm',
  'multiple spawning per year': 'Đẻ trứng nhiều đợt trong năm',
  // Commercial & Aquaculture
  'commercial': 'Khai thác thương mại',
  'highly commercial': 'Khai thác thương mại giá trị cao',
  'minor commercial': 'Khai thác thương mại nhỏ / địa phương',
  'subsistence fisheries': 'Khai thác tự cung tự cấp',
  'gamefish': 'Đối tượng câu cá thể thao',
  'of no interest': 'Ít hoặc không có giá trị thương phẩm',
  'no interest': 'Không có giá trị khai thác',
  'experimental': 'Nuôi thử nghiệm',
  'never/rarely': 'Không / Hiếm khi nuôi',
  // Danger
  'harmless': 'Vô hại đối với con người',
  'reports of ciguatera poisoning': 'Có nguy cơ tích lũy độc tố Ciguatera',
  'poisonous to eat': 'Thịt có độc, không ăn được',
  'venomous': 'Có nọc độc (gai/vây có độc)',
  'traumatogenic': 'Có khả năng gây thương tích cơ học',
  'potential pest': 'Nguy cơ gây hại sinh thái tiềm tàng',
}

function translateBio(val?: string | null): string {
  if (!val) return ''
  const key = val.toLowerCase().trim()
  return BIO_TRANSLATIONS[key] || val
}

export default function BiologyDashboard({ bio, speciesId, collectionId }: Props) {
  const isSeaweed = collectionId === 'thuc-vat-bien' || speciesId.startsWith('thucvat-')
  const srcName = isSeaweed ? 'AlgaeBase' : (bio.source || 'FishBase')

  // Formatted Quick Metrics
  const weightData = formatWeight(bio.maxWeight)
  const lengthData = formatLength(bio.maxLength)
  const longevityStr = formatLongevity(bio.longevity)
  const trophicStr = bio.trophicLevel != null ? `${bio.trophicLevel.toFixed(2)}` : null

  const hasMetrics = Boolean(weightData || lengthData || longevityStr || trophicStr)

  // Cảnh báo độc học / nguy hiểm
  const isCiguatera = bio.dangerous?.toLowerCase().includes('ciguatera')
  const isVenomous = bio.dangerous?.toLowerCase().includes('venom') || bio.dangerous?.toLowerCase().includes('poison')
  const isHarmless = bio.dangerous?.toLowerCase().includes('harmless')

  return (
    <div className="bio-dashboard">
      {/* ─── HEADER BAR ─── */}
      <div className="bio-dashboard__header">
        <h3 className="bio-dashboard__title">
          {isSeaweed ? <Leaf size={20} className="text-emerald-500" /> : <Fish size={20} className="text-cyan-500" />}
          <span>Thông Số Sinh Học & Sinh Thái</span>
        </h3>
        <span className="bio-dashboard__source-pill">
          <Sparkles size={12} aria-hidden="true" />
          <span>Dữ liệu {srcName}</span>
        </span>
      </div>

      {/* ─── TẦNG 1: HERO METRIC CARDS (4 CHỈ SỐ SINH TRẮC HỌC NỔI BẬT) ─── */}
      {hasMetrics && (
        <div className="bio-stats-grid">
          {longevityStr && (
            <div className="bio-stat-card">
              <div className="bio-stat-card__top">
                <span>Tuổi Thọ Tối Đa</span>
                <HeartPulse size={16} className="bio-stat-card__icon" />
              </div>
              <div className="bio-stat-card__val">{longevityStr}</div>
              <div className="bio-stat-card__sub">Tuổi thọ ghi nhận tự nhiên</div>
            </div>
          )}

          {weightData && (
            <div className="bio-stat-card">
              <div className="bio-stat-card__top">
                <span>Khối Lượng Tối Đa</span>
                <Scale size={16} className="bio-stat-card__icon" />
              </div>
              <div className="bio-stat-card__val">
                {weightData.main} <small style={{ fontSize: '0.9rem', fontWeight: 600 }}>{weightData.unit}</small>
              </div>
              <div className="bio-stat-card__sub">{weightData.note || 'Trọng lượng cá thể lớn nhất'}</div>
            </div>
          )}

          {lengthData && (
            <div className="bio-stat-card">
              <div className="bio-stat-card__top">
                <span>Chiều Dài Tối Đa</span>
                <Ruler size={16} className="bio-stat-card__icon" />
              </div>
              <div className="bio-stat-card__val">
                {lengthData.main} <small style={{ fontSize: '0.9rem', fontWeight: 600 }}>{lengthData.unit}</small>
              </div>
              <div className="bio-stat-card__sub">{lengthData.type || 'Kích thước tiêu bản lớn nhất'}</div>
            </div>
          )}

          {trophicStr && (
            <div className="bio-stat-card">
              <div className="bio-stat-card__top">
                <span>Bậc Dinh Dưỡng</span>
                <Waves size={16} className="bio-stat-card__icon" />
              </div>
              <div className="bio-stat-card__val">
                {trophicStr} <small style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--color-ink-3)' }}>/ 5.0</small>
              </div>
              <div className="bio-stat-card__sub">
                {bio.trophicLevel && bio.trophicLevel >= 3.5 ? 'Động vật ăn thịt bậc cao' : 'Sinh vật ăn tạp / phù du'}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ─── TẦNG 2: 3 KHỐI THẺ CHUYÊN ĐỀ PHÂN NHÓM KHOA HỌC ─── */}
      <div className="bio-thematic-grid">
        {/* Khối 1: Sinh Thái & Môi Trường Sống */}
        <div className="bio-group-card">
          <div className="bio-group-card__header">
            <Waves size={18} className="bio-group-card__icon" />
            <span>Sinh Thái & Môi Trường Sống</span>
          </div>
          <div className="bio-group-card__list">
            {(bio.habitatVn || bio.habitat) && (
              <div className="bio-item-row">
                <span className="bio-item-label">Môi trường sống (Habitat)</span>
                <div className="bio-tag-cloud">
                  {(bio.habitatVn || bio.habitat || '').split(',').map((h, i) => (
                    <span key={i} className={`bio-tag ${i === 0 ? 'bio-tag--primary' : ''}`}>
                      {translateBio(h.trim())}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {(bio.depthVn || bio.depth) && (
              <div className="bio-item-row">
                <span className="bio-item-label">Phạm vi độ sâu phân bố</span>
                <span className="bio-item-val">{bio.depthVn || bio.depth}</span>
              </div>
            )}

            {bio.feedingType && (
              <div className="bio-item-row">
                <span className="bio-item-label">Tập tính dinh dưỡng</span>
                <span className="bio-item-val">{translateBio(bio.feedingType)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Khối 2: Sinh Sản & Vòng Đời */}
        <div className="bio-group-card">
          <div className="bio-group-card__header">
            <Egg size={18} className="bio-group-card__icon" />
            <span>Sinh Sản & Tập Tính Bầy Đàn</span>
          </div>
          <div className="bio-group-card__list">
            {bio.reproduction && (
              <div className="bio-item-row">
                <span className="bio-item-label">Hình thức sinh sản</span>
                <span className="bio-item-val">{translateBio(bio.reproduction)}</span>
              </div>
            )}

            {bio.spawning && (
              <div className="bio-item-row">
                <span className="bio-item-label">Mùa vụ sinh sản</span>
                <span className="bio-item-val">{translateBio(bio.spawning)}</span>
              </div>
            )}

            {bio.spawnAggregation !== undefined && (
              <div className="bio-item-row">
                <span className="bio-item-label">Tập hợp sinh sản</span>
                <span className="bio-item-val">
                  {bio.spawnAggregation ? 'Có — Tạo đàn tập trung khi sinh sản' : 'Không tạo đàn lớn'}
                </span>
              </div>
            )}

            {bio.parentalCare && (
              <div className="bio-item-row">
                <span className="bio-item-label">Chăm sóc con non</span>
                <span className="bio-item-val">{translateBio(bio.parentalCare)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Khối 3: Bảo Tồn, An Toàn & Giá Trị Thương Mại */}
        <div className="bio-group-card">
          <div className="bio-group-card__header">
            <ShieldAlert size={18} className="bio-group-card__icon" />
            <span>Bảo Tồn & An Toàn Thực Phẩm</span>
          </div>
          <div className="bio-group-card__list">
            {bio.iucnStatus && (
              <div className="bio-item-row">
                <span className="bio-item-label">Tình trạng Sách Đỏ Quốc Tế</span>
                <div>
                  <IucnBadge status={bio.iucnStatus} />
                </div>
              </div>
            )}

            {/* Hộp Cảnh Báo An Toàn & Độc Tố Chuyên Biệt */}
            {isCiguatera && (
              <div className="bio-alert-box bio-alert-box--warning">
                <AlertTriangle size={20} className="bio-alert-box__icon" />
                <div className="bio-alert-box__content">
                  <span className="bio-alert-box__title">Cảnh báo ngộ độc Ciguatera</span>
                  <p className="bio-alert-box__desc">
                    Loài cá này có thể tích lũy độc tố Ciguatera trong thịt do chuỗi thức ăn từ rạn san hô, có nguy cơ ngộ độc nghiêm trọng khi ăn thịt cá thể lớn.
                  </p>
                </div>
              </div>
            )}

            {isVenomous && !isCiguatera && (
              <div className="bio-alert-box bio-alert-box--danger">
                <AlertTriangle size={20} className="bio-alert-box__icon" />
                <div className="bio-alert-box__content">
                  <span className="bio-alert-box__title">Cảnh báo có nọc độc</span>
                  <p className="bio-alert-box__desc">
                    Gai vây hoặc mô của loài này có độc tố, có thể gây tổn thương nghiêm trọng khi tiếp xúc trực tiếp.
                  </p>
                </div>
              </div>
            )}

            {isHarmless && !isCiguatera && (
              <div className="bio-alert-box bio-alert-box--safe">
                <CheckCircle2 size={18} className="bio-alert-box__icon" />
                <div className="bio-alert-box__content">
                  <span className="bio-alert-box__title">Vô hại đối với con người</span>
                  <p className="bio-alert-box__desc">
                    Không ghi nhận độc tính hoặc nguy cơ gây hại đối với thợ lặn và người bơi lội.
                  </p>
                </div>
              </div>
            )}

            {/* Chỉ số tổn thương sinh thái nếu có */}
            {bio.vulnerability != null && (
              <div className="bio-item-row">
                <span className="bio-item-label">Chỉ số dễ bị tổn thương sinh thái</span>
                <div className="bio-vulnerability">
                  <div className="bio-vulnerability__bar">
                    <div 
                      className="bio-vulnerability__fill" 
                      style={{ 
                        width: `${Math.min(100, Math.round(bio.vulnerability))}%`,
                        background: bio.vulnerability > 65 ? '#ef4444' : bio.vulnerability > 40 ? '#f59e0b' : '#10b981'
                      }} 
                    />
                  </div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--color-ink-3)' }}>
                    {bio.vulnerability.toFixed(1)} / 100 ({bio.vulnerability > 65 ? 'Rất dễ bị tổn thương' : bio.vulnerability > 40 ? 'Mức độ trung bình' : 'Ít tổn thương'})
                  </span>
                </div>
              </div>
            )}

            {(bio.importanceVn || bio.importance) && (
              <div className="bio-item-row">
                <span className="bio-item-label">Giá trị thương mại & Nuôi trồng</span>
                <span className="bio-item-val">
                  {bio.importanceVn || translateBio(bio.importance)}
                  {bio.aquaculture ? ` • Nuôi trồng: ${translateBio(bio.aquaculture)}` : ''}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── TẦNG 3: GHI CHÚ KHOA HỌC DÀI (CHI TIẾT VĂN BẢN TIẾNG VIỆT & TIẾNG ANH) ─── */}
      {(bio.biologySummary || bio.ecologyNotes || bio.reproductionNotes || bio.morphDescription) && (
        <div className="bio-notes-section">
          <h4 className="bio-notes-section__title">Tư Liệu Khoa Học & Ghi Chú Chuyên Sâu</h4>

          {bio.biologySummary && (
            <BilingualNoteBlock
              labelEn={`Biology summary (${srcName})`}
              labelVn={`Tóm tắt sinh học (${srcName})`}
              text={bio.biologySummary}
              textVn={bio.biologySummaryVn}
              cacheKey={`bio_summary_${speciesId}`}
            />
          )}

          {bio.ecologyNotes && (
            <BilingualNoteBlock
              labelEn="Ecology notes"
              labelVn="Ghi chú sinh thái học"
              text={bio.ecologyNotes}
              textVn={bio.ecologyNotesVn}
              cacheKey={`ecology_${speciesId}`}
            />
          )}

          {bio.reproductionNotes && (
            <BilingualNoteBlock
              labelEn="Reproduction notes"
              labelVn="Ghi chú sinh sản & Vòng đời"
              text={bio.reproductionNotes}
              textVn={bio.reproductionNotesVn}
              cacheKey={`repro_${speciesId}`}
            />
          )}

          {bio.morphDescription && (
            <BilingualNoteBlock
              labelEn="Morphological description (GBIF)"
              labelVn="Mô tả hình thái học chuẩn (GBIF)"
              text={bio.morphDescription}
              textVn={bio.morphDescriptionVn}
              cacheKey={`morph_${speciesId}`}
            />
          )}
        </div>
      )}
    </div>
  )
}
