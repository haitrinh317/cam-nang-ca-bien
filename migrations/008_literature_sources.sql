-- 008_literature_sources.sql
-- Bảng quản lý sách tham khảo hiển thị trên trang chủ
-- Thay thế hardcode trong LiteratureSection.tsx

CREATE TABLE IF NOT EXISTS literature_sources (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title       text NOT NULL,
  subtitle    text,
  author      text NOT NULL,
  publisher   text,
  year        text,
  stats_count text,
  pill_text   text,
  description text,
  href        text NOT NULL,
  chips       text[] DEFAULT '{}',
  icon_name   text DEFAULT 'book-open',
  sort_order  int DEFAULT 0,
  is_visible  boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- Index for sorted visible listing
CREATE INDEX idx_literature_visible_sort ON literature_sources (is_visible, sort_order);

-- RLS: public can read visible rows, admin can do everything
ALTER TABLE literature_sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read visible literature"
  ON literature_sources FOR SELECT
  USING (is_visible = true);

CREATE POLICY "Admin full access to literature"
  ON literature_sources FOR ALL
  USING (
    auth.role() = 'service_role'
    OR EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- Seed: chuyển 3 bộ sách hiện có từ hardcode
INSERT INTO literature_sources (title, subtitle, author, publisher, year, stats_count, pill_text, description, href, chips, icon_name, sort_order) VALUES
(
  'Danh mục Cá biển Việt Nam',
  'Tập I – V (1992 – 2007)',
  'GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi và CS',
  'Nhà xuất bản Nông nghiệp',
  '1992 – 2007',
  '1,501 loài cá biển',
  '5 Tập Chuyên Khảo',
  'Công trình điều tra định loại học nền tảng toàn diện nhất về thành phần loài cá tại các vùng biển Việt Nam, phân định chi tiết từ cá sụn đến cá xương.',
  '/ca-bien?vol=1',
  ARRAY['T.I: Cá nhám, cá đuối', 'T.II: Cá trích, cá chình', 'T.III: Cá bơn, cá chai', 'T.IV: Cá mú, cá thia', 'T.V: Cá đù, cá khế'],
  'fish',
  1
),
(
  'Atlas Cá rạn san hô Việt Nam',
  'Tập VI (2020)',
  'TS. Đỗ Thị Cát Tường',
  'NXB Khoa học Tự nhiên và Công nghệ',
  '2020',
  '263 loài cá rạn',
  'Tập VI • Atlas Màu',
  'Bộ tư liệu hình thái và mẫu ảnh thực địa chuyên sâu về các loài cá đặc trưng thuộc hệ sinh thái rạn san hô, gắn liền dữ liệu quan trắc sinh thái học.',
  '/ca-bien?vol=6',
  ARRAY['263 loài cá rạn san hô', '1,069 ảnh Research-grade', 'Độ phủ ảnh 98.5%', '100% dịch tóm tắt sinh học'],
  'compass',
  2
),
(
  'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam',
  'The Common Marine Plants of Southern Vietnam',
  'TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao',
  'Japan Seaweed Association',
  'Chuyên khảo chuẩn',
  '201 loài thực vật',
  '1 Tập Chuyên Khảo',
  'Tài liệu định loại hệ Thực vật biển Việt Nam: khóa phân loại, đặc điểm hiển vi, giá trị kinh tế và sinh thái của các loài rong ven bờ và hải đảo.',
  '/thuc-vat-bien',
  ARRAY['Rhodophyta (Rong đỏ): 111 loài', 'Phaeophyceae (Rong nâu): 46', 'Chlorophyta (Rong lục): 38', 'Cyanobacteria: 6'],
  'leaf',
  3
);
