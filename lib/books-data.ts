/**
 * books-data.ts — Cấu trúc đầu sách và tập sách khoa học gốc
 * Phân chia theo 2 đầu sách chính cho Cá biển:
 *  1. Bộ sách "Danh mục Cá biển Việt Nam" (Tập I - V)
 *  2. Bộ sách "Atlas Cá rạn san hô Việt Nam" (Tập VI)
 */

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

export const BOOKS_BY_COLLECTION: Record<string, BookMetadata[]> = {
  'ca-bien': [
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
  'thuc-vat-bien': [
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
  ],
}

export function getBooksForCollection(collectionSlug: string): BookMetadata[] {
  return BOOKS_BY_COLLECTION[collectionSlug] || []
}
