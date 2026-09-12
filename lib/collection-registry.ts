/**
 * collection-registry.ts — Unified Deep Registry for Collections, Books & Special Groups
 *
 * Client-safe: No Supabase imports. Safe for 'use client' components.
 * For server-side DB fetching with fallback, use lib/collection-registry-server.ts.
 *
 * Consolidated from:
 *   - lib/collections.ts
 *   - lib/books-data.ts
 *   - lib/special-groups.ts
 */

// ─── TYPES & INTERFACES ──────────────────────────────────────────────

export interface VolumeMetadata {
  volume: number
  roman: string
  year?: string
  title: string
  subTitle: string
  author: string
  speciesCount: number
}

export interface BookMetadata {
  id: string
  title: string
  badge: string
  author: string
  publisher: string
  yearRange: string
  totalSpecies: number
  description: string
  volumes: VolumeMetadata[]
}

export interface SpecialGroupConfig {
  id: string
  title: string
  subTitle: string
  badge: string
  badgeColor: 'cyan' | 'rose' | 'amber' | 'emerald'
  collection: string
  targetUrl: string
  approxCount: number
  filterType: 'families' | 'orders' | 'iucn' | 'collection' | 'archipelago'
  filterValues?: string[]
}

export interface Collection {
  id: string
  slug: string
  nameVn: string
  nameEn: string
  icon: string
  accentColor: string
  volumeCount: number
  status: 'active' | 'draft' | 'archived'
  sortOrder: number
}

export interface CollectionDef extends Collection {
  books: BookMetadata[]
  specialGroups?: SpecialGroupConfig[]
}

// ─── SPECIAL GROUPS (THEMATIC COLLECTIONS) ───────────────────────────

export const SPECIAL_GROUPS: Record<string, SpecialGroupConfig> = {
  'san-ho': {
    id: 'san-ho',
    title: 'Cá Rạn San Hô Việt Nam',
    subTitle: 'Các loài cá đặc trưng sinh sống tại các rạn san hô Nha Trang, Côn Đảo, Trường Sa, Hoàng Sa (Họ Thia, Bướm, Bàng chài, Mú, Mó, Đuôi gai...)',
    badge: 'Đa Dạng Sinh Học Rạn San Hô',
    badgeColor: 'cyan',
    collection: 'ca-bien',
    targetUrl: '/ca-bien?group=san-ho',
    approxCount: 195,
    filterType: 'families',
    filterValues: [
      'Pomacentridae',
      'Chaetodontidae',
      'Labridae',
      'Serranidae',
      'Scaridae',
      'Acanthuridae',
      'Lutjanidae',
      'Holocentridae',
      'Mullidae',
      'Apogonidae',
    ],
  },
  'nguy-cap': {
    id: 'nguy-cap',
    title: 'Loài Nguy Cấp & Cần Bảo Vệ',
    subTitle: 'Các loài sinh vật biển Việt Nam đang đứng trước nguy cơ đe dọa tuyệt chủng theo Danh lục đỏ Quốc tế IUCN (CR: Cực kỳ nguy cấp, EN: Nguy cấp, VU: Sắp nguy cấp, NT: Gần bị đe dọa)',
    badge: 'Bảo Tồn Nguồn Lợi Sinh Học',
    badgeColor: 'rose',
    collection: 'ca-bien',
    targetUrl: '/ca-bien?group=nguy-cap',
    approxCount: 120,
    filterType: 'iucn',
    filterValues: ['CR', 'EN', 'VU', 'NT'],
  },
  'hoang-sa-truong-sa': {
    id: 'hoang-sa-truong-sa',
    title: 'Sinh Vật Vùng Biển Hoàng Sa – Trường Sa',
    subTitle: 'Các loài sinh vật biển đặc trưng ghi nhận tại hai quần đảo Hoàng Sa và Trường Sa (Cá rạn san hô, cá mó, cá bàng chài, cá mao tiên, rong biển tiêu bản lịch sử...)',
    badge: 'SINH VẬT VÙNG BIỂN HOÀNG SA - TRƯỜNG SA',
    badgeColor: 'amber',
    collection: 'ca-bien',
    targetUrl: '/ca-bien?group=hoang-sa-truong-sa',
    approxCount: 148,
    filterType: 'archipelago',
  },
  'thuc-vat-bien': {
    id: 'thuc-vat-bien',
    title: 'Rong Biển & Thực Vật Biển',
    subTitle: 'Toàn bộ hệ thực vật biển Việt Nam bao gồm Rong Lục, Rong Nâu, Rong Đỏ và Cỏ biển phục vụ kinh tế, dược liệu và cân bằng sinh thái biển',
    badge: 'Tài Nguyên Thực Vật Biển',
    badgeColor: 'emerald',
    collection: 'thuc-vat-bien',
    targetUrl: '/thuc-vat-bien',
    approxCount: 672,
    filterType: 'collection',
  },
  'sinh-vat-doc': {
    id: 'sinh-vat-doc',
    title: 'Động Vật Biển Độc & Phác Đồ Cứu Hộ',
    subTitle: '76 loài động vật độc biển Việt Nam (Bạch tuộc đốm xanh, Ốc cối, Cá nóc, Rắn biển, Sứa lửa, Cá đuối...) kèm độc tố nhận diện và phác đồ sơ cứu',
    badge: 'Cảnh Báo Độc Tố & Cấp Cứu Y Tế',
    badgeColor: 'rose',
    collection: 'sinh-vat-doc',
    targetUrl: '/sinh-vat-doc',
    approxCount: 76,
    filterType: 'collection',
  },
}

export const SPECIAL_GROUPS_LIST: SpecialGroupConfig[] = Object.values(SPECIAL_GROUPS)

// ─── UNIFIED REGISTRY DEFINITION ──────────────────────────────────────

export const REGISTRY: Record<string, CollectionDef> = {
  'ca-bien': {
    id: 'ca-bien',
    slug: 'ca-bien',
    nameVn: 'Cá biển Việt Nam',
    nameEn: 'Vietnamese Marine Fish',
    icon: '🐟',
    accentColor: '#6fffe8',
    volumeCount: 6,
    status: 'active',
    sortOrder: 1,
    specialGroups: [
      SPECIAL_GROUPS['san-ho'],
      SPECIAL_GROUPS['nguy-cap'],
      SPECIAL_GROUPS['hoang-sa-truong-sa'],
    ],
    books: [
      {
        id: 'danh-muc-ca-bien',
        title: 'Danh mục Cá biển Việt Nam',
        badge: '5 tập (1,501 loài)',
        author: 'GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi & CS',
        publisher: 'NXB Nông nghiệp',
        yearRange: '1992 – 2007',
        totalSpecies: 1501,
        description: 'Công trình định loại học cơ bản toàn diện và đồ sộ nhất về các loài cá biển tại các vùng biển Việt Nam.',
        volumes: [
          {
            volume: 1,
            roman: 'I',
            year: '1992',
            title: 'Tập I: Cá Nhám, Cá Đuối, Cá Trích, Cá Chình',
            subTitle: 'Bộ cá Nhám, Bộ cá Đuối, Bộ cá Trích, Bộ cá Chình',
            author: 'GS. Nguyễn Khắc Hường',
            speciesCount: 100,
          },
          {
            volume: 2,
            roman: 'II',
            year: '1994',
            title: 'Tập II: Cá Mối, Cá Suốt, Cá Chích, Cá Chai',
            subTitle: 'Bộ cá Mối, Bộ cá Suốt, Bộ cá Chai...',
            author: 'GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi',
            speciesCount: 266,
          },
          {
            volume: 3,
            roman: 'III',
            year: '2000',
            title: 'Tập III: Cá Hồng, Cá Mú, Cá Đù, Cá Mối',
            subTitle: 'Bộ cá Vược (phần I) — các họ cá kinh tế rạn san hô và đáy',
            author: 'GS. Nguyễn Khắc Hường',
            speciesCount: 518,
          },
          {
            volume: 4,
            roman: 'IV',
            year: '2004',
            title: 'Tập IV: Cá Bướm, Cá Thiên nga, Cá Tai tượng',
            subTitle: 'Bộ cá Vược (phần II) — các họ cá cảnh và rạn san hô',
            author: 'TS. Nguyễn Nhật Thi',
            speciesCount: 338,
          },
          {
            volume: 5,
            roman: 'V',
            year: '2007',
            title: 'Tập V: Cá Bống, Cá Bơn, Cá Nóc, Cá Cóc biển',
            subTitle: 'Bộ cá Bống, Bộ cá Bơn, Bộ cá Nóc, Bộ cá Cóc biển...',
            author: 'TS. Nguyễn Nhật Thi',
            speciesCount: 279,
          },
        ],
      },
      {
        id: 'atlas-ca-ran-san-ho',
        title: 'Atlas Cá rạn san hô Việt Nam',
        badge: 'Tập VI (263 loài)',
        author: 'TS. Đỗ Thị Cát Tường',
        publisher: 'NXB Khoa học Tự nhiên & Công nghệ',
        yearRange: '2020',
        totalSpecies: 263,
        description: 'Bộ sưu tầm hình ảnh mẫu vật và định loại chi tiết các loài cá đặc trưng thuộc rạn san hô biển Việt Nam.',
        volumes: [
          {
            volume: 6,
            roman: 'VI',
            year: '2020',
            title: 'Atlas Cá rạn san hô Việt Nam',
            subTitle: 'Bộ ảnh mẫu nghiên cứu và định danh cá rạn san hô',
            author: 'TS. Đỗ Thị Cát Tường',
            speciesCount: 263,
          },
        ],
      },
    ],
  },
  'thuc-vat-bien': {
    id: 'thuc-vat-bien',
    slug: 'thuc-vat-bien',
    nameVn: 'Thực vật biển',
    nameEn: 'Marine Plants & Algae of Vietnam',
    icon: '🌿',
    accentColor: '#a7f3d0',
    volumeCount: 2,
    status: 'active',
    sortOrder: 2,
    specialGroups: [
      SPECIAL_GROUPS['thuc-vat-bien'],
    ],
    books: [
      {
        id: 'rong-bien',
        title: 'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam',
        badge: '1 tập (201 loài)',
        author: 'TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao',
        publisher: 'Japan Seaweed Association',
        yearRange: 'Chuyên khảo',
        totalSpecies: 201,
        description: 'Danh mục định loại và đặc điểm sinh thái, kinh tế của các loài rong và thực vật biển ven bờ phía Nam Việt Nam (The Common Marine Plants of Southern Vietnam).',
        volumes: [
          {
            volume: 1,
            roman: 'I',
            year: '',
            title: 'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam',
            subTitle: 'The Common Marine Plants of Southern Vietnam',
            author: 'TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao',
            speciesCount: 201,
          },
        ],
      },
      {
        id: 'rong-bien-pham-hoang-ho',
        title: 'Rong biển Việt Nam',
        badge: 'Tập II (~500 loài)',
        author: 'GS. Phạm Hoàng Hộ',
        publisher: 'Bộ Giáo-dục và Thanh-niên — Trung-tâm Học-liệu Xuất-bản',
        yearRange: '1969',
        totalSpecies: 497,
        description: 'Công trình định loại cơ bản và giải phẫu thực vật toàn diện đầu tiên về các loài rong biển Việt Nam (Marine Algae of South Vietnam).',
        volumes: [
          {
            volume: 2,
            roman: 'II',
            year: '1969',
            title: 'Rong biển Việt Nam (Marine Algae of South Vietnam)',
            subTitle: 'Thanh-tảo, Lục-tảo, Hoàng-tảo, Hồng-tảo bờ biển Việt Nam',
            author: 'GS. Phạm Hoàng Hộ',
            speciesCount: 497,
          },
        ],
      },
    ],
  },
  'giap-xac': {
    id: 'giap-xac',
    slug: 'giap-xac',
    nameVn: 'Giáp xác biển',
    nameEn: 'Marine Crustaceans of Vietnam',
    icon: '🦐',
    accentColor: '#fca5a5',
    volumeCount: 1,
    status: 'active',
    sortOrder: 3,
    books: [
      {
        id: 'dong-vat-chi-tom-bien',
        title: 'Động vật chí Việt Nam: Tôm biển',
        badge: 'Tập 1 (132 loài)',
        author: 'Nguyễn Văn Chung, Đặng Ngọc Thanh, Phạm Thị Dự',
        publisher: 'NXB Khoa học và Kỹ thuật',
        yearRange: '2000',
        totalSpecies: 132,
        description: 'Công trình định loại học cơ bản và giải phẫu toàn diện về khu hệ Tôm biển và Tôm tít Việt Nam thuộc bộ Mười Chân (Decapoda) và bộ Chân Miệng (Stomatopoda).',
        volumes: [
          {
            volume: 1,
            roman: '1',
            year: '2000',
            title: 'Động vật chí Việt Nam — Tập 1: Tôm biển',
            subTitle: 'Penaeoidea, Nephropoidea, Palinuroidea, Gonodactyloidea, Lysiosquilloidea, Squilloidea',
            author: 'Nguyễn Văn Chung, Đặng Ngọc Thanh, Phạm Thị Dự',
            speciesCount: 132,
          },
        ],
      },
    ],
  },
  'ran-bien': {
    id: 'ran-bien',
    slug: 'ran-bien',
    nameVn: 'Rắn biển Việt Nam',
    nameEn: 'Sea Snakes of Vietnam',
    icon: '🐍',
    accentColor: '#f59e0b',
    volumeCount: 1,
    status: 'active',
    sortOrder: 4,
    books: [
      {
        id: 'ran-bien-viet-nam',
        title: 'Rắn biển Việt Nam',
        badge: 'Chuyên khảo (27 loài)',
        author: 'Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng, Phan Kim Hồng, Võ Văn Quang, John C. Murphy',
        publisher: 'Viện Hải dương học Nha Trang — WAR — IOC VN',
        yearRange: '2016',
        totalSpecies: 27,
        description: 'Tài liệu hướng dẫn định loại cơ bản, phân bố địa lý, độc tố học và bảo tồn các loài Rắn biển (Hydrophiinae & Acrochordidae) tại các vùng biển Việt Nam.',
        volumes: [
          {
            volume: 1,
            roman: 'I',
            year: '2016',
            title: 'Rắn biển Việt Nam (Sea Snakes in Vietnam)',
            subTitle: 'Phân loại, phân bố, tình trạng bảo tồn và độc tố rắn biển',
            author: 'Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng & CS',
            speciesCount: 27,
          },
        ],
      },
    ],
  },
  'sinh-vat-doc': {
    id: 'sinh-vat-doc',
    slug: 'sinh-vat-doc',
    nameVn: 'Động vật độc biển',
    nameEn: 'Venomous & Poisonous Marine Animals',
    icon: '☣️',
    accentColor: '#fb7185',
    volumeCount: 1,
    status: 'active',
    sortOrder: 5,
    specialGroups: [
      SPECIAL_GROUPS['sinh-vat-doc'],
    ],
    books: [
      {
        id: 'dong-vat-doc-bien-vn',
        title: 'Động vật độc biển Việt Nam',
        badge: 'Chuyên khảo (76 loài)',
        author: 'PGS.TS. Đào Việt Hà (Chủ biên) & CS',
        publisher: 'NXB Khoa học Tự nhiên và Công nghệ',
        yearRange: '2021',
        totalSpecies: 76,
        description: 'Công trình chuyên khảo toàn diện về các loài sinh vật biển có nọc độc tiếp xúc và độc tố tích lũy thực phẩm tại Việt Nam, bao gồm cơ chế độc tính, triệu chứng lâm sàng và phác đồ sơ cứu ban đầu.',
        volumes: [
          {
            volume: 1,
            roman: '1',
            year: '2021',
            title: 'Động vật độc biển Việt Nam',
            subTitle: 'Nhiễm độc qua tiếp xúc & Ngộ độc thực phẩm — Phác đồ sơ cứu tai nạn biển',
            author: 'PGS.TS. Đào Việt Hà (Chủ biên) & CS (Viện Hải dương học)',
            speciesCount: 76,
          },
        ],
      },
    ],
  },
  'than-mem': {
    id: 'than-mem',
    slug: 'than-mem',
    nameVn: 'Động vật thân mềm',
    nameEn: 'Marine Molluscs of Vietnam',
    icon: '🐚',
    accentColor: '#e8c4ff',
    volumeCount: 1,
    status: 'active',
    sortOrder: 6,
    books: [
      {
        id: 'molluscs-of-vietnam-2003',
        title: 'Checklist of Marine Molluscs of Vietnam',
        badge: 'Danh lục chuyên khảo (2.500+ loài)',
        author: 'Jørgen Hylleberg & Richard N. Kilburn',
        publisher: 'Phuket Marine Biological Center Special Publication (Vol. 28)',
        yearRange: '2003',
        totalSpecies: 2500,
        description: 'Công trình tổng điều tra, hệ thống hóa và lập danh mục phân loại học toàn diện nhất về các loài Động vật thân mềm biển (Ốc, Sò, Mực, Bạch tuộc...) tại các vùng biển Việt Nam.',
        volumes: [
          {
            volume: 1,
            roman: '1',
            year: '2003',
            title: 'Marine Molluscs of Vietnam',
            subTitle: 'Danh mục phân loại học, đồng danh, phân bố và dẫn liệu mẫu vật',
            author: 'J. Hylleberg & R.N. Kilburn',
            speciesCount: 2500,
          },
        ],
      },
    ],
  },
  'san-ho': {
    id: 'san-ho',
    slug: 'san-ho',
    nameVn: 'San hô Việt Nam',
    nameEn: 'Corals of Vietnam',
    icon: '🪸',
    accentColor: '#f9a8d4',
    volumeCount: 1,
    status: 'active',
    sortOrder: 7,
    books: [
      {
        id: 'san-ho-8-ngan',
        title: 'Đa dạng sinh học san hô tám ngăn vùng biển phía Nam Việt Nam',
        badge: 'Chuyên khảo (42 loài)',
        author: 'TS. Hoàng Xuân Bền',
        publisher: 'Viện Hải dương học Nha Trang',
        yearRange: 'Chuyên khảo',
        totalSpecies: 42,
        description: 'Công trình nghiên cứu định loại hình thái, cấu trúc trâm xương, sinh thái và phân bố các loài San hô tám ngăn (Octocorallia) tại vùng biển phía Nam Việt Nam.',
        volumes: [
          {
            volume: 1,
            roman: 'I',
            year: '',
            title: 'San hô tám ngăn vùng biển phía Nam Việt Nam',
            subTitle: 'Octocorallia — Hình thái ngoài, trâm xương, sinh thái và phân bố',
            author: 'TS. Hoàng Xuân Bền',
            speciesCount: 42,
          },
        ],
      },
    ],
  },
}

// ─── DERIVED COMPATIBILITY EXPORTS ────────────────────────────────────

/** Static collection array sorted by sortOrder */
export const STATIC_COLLECTIONS: Collection[] = Object.values(REGISTRY).map(
  ({ books, specialGroups, ...col }) => col
).sort((a, b) => a.sortOrder - b.sortOrder)

/** Books mapped by collection slug */
export const BOOKS_BY_COLLECTION: Record<string, BookMetadata[]> = Object.fromEntries(
  Object.values(REGISTRY).map(c => [c.slug, c.books])
)

// ─── LOOKUP HELPERS ───────────────────────────────────────────────────

/** Get unified collection definition (including books and special groups) */
export function getCollection(slug: string): CollectionDef | undefined {
  return REGISTRY[slug]
}

/** Get basic collection metadata by slug */
export function getCollectionBySlug(slug: string): Collection | undefined {
  return REGISTRY[slug]
}

/** Get all collections */
export function getAllCollections(): Collection[] {
  return STATIC_COLLECTIONS
}

/** Get active collections only */
export function getActiveCollections(): Collection[] {
  return STATIC_COLLECTIONS.filter(c => c.status === 'active')
}

/** Get books metadata list for a collection */
export function getBooksForCollection(collectionSlug: string): BookMetadata[] {
  return BOOKS_BY_COLLECTION[collectionSlug] || []
}

/** Get special group definition by ID */
export function getSpecialGroup(groupId: string): SpecialGroupConfig | null {
  return SPECIAL_GROUPS[groupId] || null
}

/** Get all special groups as array */
export function getSpecialGroupsList(): SpecialGroupConfig[] {
  return SPECIAL_GROUPS_LIST
}
