/**
 * special-groups.ts — Định nghĩa 4 bộ sưu tập chuyên đề sinh thái & bảo tồn
 * Ánh xạ trực tiếp tới các trường dữ liệu thực tế trong CSDL Supabase
 */

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
}

export const SPECIAL_GROUPS_LIST: SpecialGroupConfig[] = Object.values(SPECIAL_GROUPS)

export function getSpecialGroup(groupId: string): SpecialGroupConfig | null {
  return SPECIAL_GROUPS[groupId] || null
}
