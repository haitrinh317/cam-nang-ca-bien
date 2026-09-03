export interface FaqItem {
  id: string
  category: 'about' | 'sources' | 'tech' | 'rights'
  categoryLabel: string
  question: string
  questionEn?: string
  answer: string
  answerEn?: string
  highlights?: string[]
}

export const FAQ_DATA: FaqItem[] = [
  // ── Nhóm 1: Về Dự án & Lý do ra đời ──
  {
    id: 'about-1',
    category: 'about',
    categoryLabel: 'Về dự án',
    question: 'Cẩm nang Sinh vật biển Việt Nam là gì và vì sao dự án này được thực hiện?',
    questionEn: 'What is the Vietnam Marine Species Compendium and why was it created?',
    answer: 'Cẩm nang Sinh vật biển Việt Nam là dự án phi lợi nhuận hướng tới việc số hóa, hiện đại hóa và bảo tồn kho tàng tri thức phân loại học sinh vật biển Việt Nam. Nhiều ấn phẩm nghiên cứu kinh điển — tiêu biểu là bộ sách đồ sộ "Danh mục Cá biển Việt Nam" xuất bản từ thập niên 1990 — hiện nay chỉ còn lưu giữ dưới dạng sách in giấy cũ, giấy ố vàng, hư hại và cực kỳ khó tiếp cận đối với công chúng cũng như thế hệ nghiên cứu trẻ. Dự án ra đời nhằm chuyển hóa toàn bộ di sản khoa học quý giá này thành Cơ sở dữ liệu số Mở (Open Data), trực quan và dễ dàng tra cứu trên mọi thiết bị.',
    highlights: [
      'Bảo tồn di sản nghiên cứu sinh học biển quý báu của các thế hệ nhà khoa học tiền bối',
      'Chuyển đổi số toàn diện: Từ sách giấy in cũ sang cơ sở dữ liệu số hóa có cấu trúc',
      'Phi lợi nhuận, phục vụ cộng đồng nghiên cứu, giáo dục và bảo tồn thiên nhiên biển'
    ]
  },
  {
    id: 'about-2',
    category: 'about',
    categoryLabel: 'Về dự án',
    question: 'Dự án do đơn vị nào khởi xướng và phát triển?',
    questionEn: 'Who developed and manages this project?',
    answer: 'Dự án được khởi xướng và phát triển bởi Phòng Thông tin – Truyền thông, Viện Hải dương học (thuộc Viện Hàn lâm Khoa học và Công nghệ Việt Nam). Nền tảng được xây dựng nhằm tạo ra một công cụ hỗ trợ trực quan, nhanh chóng cho công tác chuyên môn tại Bảo tàng Hải dương học, đồng thời mở rộng cánh cửa tiếp cận đại dương cho toàn thể cộng đồng.',
    highlights: [
      'Đơn vị phát triển: Phòng Thông tin – Truyền thông, Viện Hải dương học',
      'Cơ quan chủ quản: Viện Hàn lâm Khoa học và Công nghệ Việt Nam (VAST)',
      'Địa điểm lưu trữ mẫu vật thực tế: Bảo tàng Hải dương học (Nha Trang, Khánh Hòa)'
    ]
  },

  // ── Nhóm 2: Nguồn tài liệu & Tính xác thực khoa học ──
  {
    id: 'sources-1',
    category: 'sources',
    categoryLabel: 'Nguồn tài liệu',
    question: 'Dữ liệu các loài cá và sinh vật biển trên website được trích xuất từ các công trình khoa học nào?',
    questionEn: 'What primary scientific literature is this database sourced from?',
    answer: 'Nguồn tài liệu xương sống của dự án là các công trình khảo sát, định loại chính quy của các chuyên gia hàng đầu Viện Hải dương học qua nhiều thập kỷ, bao gồm:\n\n• Bộ sách "Danh mục Cá biển Việt Nam" (Tập I đến Tập V, NXB Nông nghiệp, 1992–2007) do GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi và các cộng sự biên soạn.\n• Sách "Atlas cá rạn san hô Việt Nam" (Tập VI, NXB Khoa học Tự nhiên & Công nghệ) của TS. Đỗ Thị Cát Tường.\n• Sách "Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam" (The Common Marine Plants of Southern Vietnam) của TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao.',
    highlights: [
      'Danh mục Cá biển Việt Nam: Tập I, II, III, IV, V (1992–2007)',
      'Atlas Cá rạn san hô Việt Nam: Tập VI',
      'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam (The Common Marine Plants of Southern Vietnam)'
    ]
  },
  {
    id: 'sources-2',
    category: 'sources',
    categoryLabel: 'Nguồn tài liệu',
    question: 'Tại sao một số loài có tên khoa học khác với tên in trong sách gốc?',
    questionEn: 'Why are some scientific names different from the original printed books?',
    answer: 'Trải qua nhiều thập kỷ, ngành Ngư loại học và Hệ thống học sinh vật biển toàn cầu đã có những tiến bộ lớn nhờ phân tích sinh học phân tử (DNA) và rà soát phân loại học. Nhiều giống (genus) và loài (species) đã được chuyển đổi danh pháp hoặc sáp nhập danh pháp đồng nghĩa (Synonym).\n\nĐể đảm bảo tính hội nhập quốc tế mà vẫn tôn trọng nguyên bản lịch sử, hệ thống đã thực hiện đồng bộ 100% với Cơ sở dữ liệu Danh lục Sinh vật biển Thế giới (WoRMS - World Register of Marine Species). Tên in trong sách gốc được giữ nguyên trang trọng ở mục "Tên trong tài liệu", trong khi Tên khoa học hợp lệ hiện tại (Accepted Name) cùng mã định danh AphiaID toàn cầu được hiển thị rõ ràng với huy hiệu xác thực màu xanh lá.',
    highlights: [
      '100% loài cá biển được đối chiếu và xác thực với WoRMS (World Register of Marine Species)',
      'Lưu giữ song song cả Danh pháp gốc trong sách và Danh pháp khoa học quốc tế hợp lệ hiện đại',
      'Cung cấp liên kết trực tiếp đến trang gốc của từng loài trên CSDL WoRMS toàn cầu'
    ]
  },
  {
    id: 'sources-3',
    category: 'sources',
    categoryLabel: 'Nguồn tài liệu',
    question: 'Vì sao một số loài bị thiếu thông tin (như kích thước, số lượng mẫu vật, hoặc tên tiếng Việt)?',
    questionEn: 'Why do some species have missing fields (such as size, specimen count, or Vietnamese names)?',
    answer: 'Việc một số trường dữ liệu hiển thị dấu gạch ngang hoặc chưa có thông tin bắt nguồn từ các nguyên nhân khoa học và lịch sử thực tế:\n\n1. Tôn trọng tuyệt đối tính nguyên bản khoa học: Trong các chuyến khảo sát biển sâu từ thế kỷ trước, nhiều loài chỉ được ghi nhận qua quan sát thực địa hoặc trích dẫn lại từ tư liệu khảo sát trước đó mà tác giả chưa trực tiếp thu thập hay bảo quản được mẫu vật nguyên vẹn trong phòng thí nghiệm. Các nhà khoa học tiền bối luôn tuân thủ nguyên tắc trung thực: chỉ ghi chép những gì có bằng chứng vật lý rõ ràng, tuyệt đối không suy đoán hay bịa đặt số liệu.\n\n2. Loài quý hiếm hoặc sinh sống ở biển sâu (Data Deficient): Nhiều loài cá sống ở tầng đáy sâu hàng nghìn mét, cá mù hoặc loài di cư xa rất hiếm khi bắt gặp. Ngay cả trên các cơ sở dữ liệu quốc tế lớn như FishBase hay Sách Đỏ IUCN, dữ liệu sinh học của chúng vẫn đang thuộc diện thiếu hụt nghiên cứu.\n\n3. Chưa có tên tiếng Việt chính thức: Nhiều loài cá không có giá trị thương mại hoặc sống ngoài khơi xa chưa từng được ngư dân khai thác, do đó dân gian chưa từng đặt tên địa phương. Nhóm biên tập quyết định giữ nguyên tên khoa học La-tinh, tránh tùy tiện gán ghép tên tự phát có thể gây hiểu lầm hoặc xung đột định loại.\n\n4. Dự án CSDL sống (Living Compendium): Nền tảng liên tục được rà soát, đối soát và bổ sung dữ liệu qua từng giai đoạn từ kho mẫu vật lưu trữ thực tế của Bảo tàng Hải dương học và các nghiên cứu khoa học mới được công bố.',
    highlights: [
      'Tôn trọng tính chân thực lịch sử: Không tự ý bịa đặt số liệu nếu sách gốc không ghi nhận',
      'Đặc thù ngư học: Nhiều loài cá biển sâu hoặc loài cực hiếm trên toàn cầu vẫn thiếu dữ liệu',
      'Giữ nguyên tên La-tinh đối với những loài chưa có tên gọi dân gian chính thức',
      'Dự án CSDL sống: Liên tục được bổ sung, hiệu đính và làm giàu dữ liệu theo thời gian'
    ]
  },

  // ── Nhóm 3: Công nghệ số hóa & Dữ liệu bổ sung ──
  {
    id: 'tech-1',
    category: 'tech',
    categoryLabel: 'Công nghệ & Dữ liệu',
    question: 'Quy trình bóc tách và số hóa hàng nghìn trang tài liệu được tiến hành như thế nào?',
    questionEn: 'How was the OCR and digitization pipeline engineered?',
    answer: 'Dự án áp dụng quy trình xử lý thị giác máy tính và Trí tuệ nhân tạo (AI Vision & Deep Learning OCR) đa tầng:\n\n1. Xử lý ảnh scan độ phân giải cao, khử nhiễu giấy ố, nắn thẳng và tách cột tự động.\n2. Ứng dụng mô hình ngôn ngữ lớn chuyên sâu (Vision LLMs) để nhận diện cấu trúc học thuật phức tạp: công thức vây, tia vây, kích thước mẫu vật, địa điểm phân bố, trích dẫn tài liệu tham khảo.\n3. Đối soát 2 chiều (Cross-validation) giữa bản scan gốc và dữ liệu cấu trúc hóa Supabase, kết hợp dịch thuật học thuật chuẩn hóa song ngữ Việt - Anh.',
    highlights: [
      'Công nghệ OCR thị giác thông minh xử lý văn bản song ngữ và chữ in cổ',
      'Bóc tách hình vẽ nét giải phẫu hình thái học độc bản với độ sắc nét cao',
      'Định dạng dữ liệu chuẩn RESTful / PostgreSQL (Supabase) tối ưu hóa truy vấn'
    ]
  },
  {
    id: 'tech-2',
    category: 'tech',
    categoryLabel: 'Công nghệ & Dữ liệu',
    question: 'Các thông số sinh học (độ sâu, sinh thái, kích thước tối đa, tình trạng IUCN) lấy từ đâu?',
    questionEn: 'Where do additional biological and conservation data come from?',
    answer: 'Bên cạnh thông tin hình thái học nguyên bản từ các công trình nghiên cứu trong nước, mỗi loài sinh vật biển đều được tự động làm giàu (enrichment) dữ liệu sinh học từ hai kho tri thức lớn nhất hành tinh:\n\n• FishBase (Cơ sở dữ liệu ngư loại học thế giới): Cung cấp chiều dài tối đa, trọng lượng kỷ lục, tuổi thọ, tầng nước phân bố, tập tính sinh sản, kiểu dinh dưỡng và bậc dinh dưỡng trong chuỗi thức ăn.\n• GBIF & Sách Đỏ IUCN (International Union for Conservation of Nature): Cung cấp cấp độ nguy cấp và tình trạng bảo tồn (LC, NT, VU, EN, CR) được cập nhật định kỳ.',
    highlights: [
      'Dữ liệu sinh thái phong phú từ FishBase v25.04 (Local High-speed Cache)',
      'Tình trạng bảo tồn cập nhật theo Sách Đỏ Quốc tế IUCN Red List qua GBIF API',
      'Tích hợp tính năng dịch thuật ngữ sinh học song ngữ thông minh'
    ]
  },

  // ── Nhóm 4: Bản quyền & Đóng góp cộng đồng ──
  {
    id: 'rights-1',
    category: 'rights',
    categoryLabel: 'Bản quyền & Sử dụng',
    question: 'Tôi có thể sử dụng thông tin và hình ảnh trên website cho mục đích học tập, nghiên cứu không?',
    questionEn: 'Can I use the information and illustrations for academic or educational purposes?',
    answer: 'Dự án khuyến khích sử dụng toàn bộ thông tin cho mục đích phi thương mại, giảng dạy, học tập và nghiên cứu khoa học. Khi trích dẫn dữ liệu từ website, xin vui lòng ghi rõ nguồn trích dẫn từ công trình nghiên cứu gốc tương ứng và nền tảng Cẩm nang Sinh vật biển Việt Nam.',
    highlights: [
      'Miễn phí và mở rộng cho mục đích giáo dục, bảo tồn và nghiên cứu phi thương mại',
      'Tôn trọng quyền tác giả và công sức của các tác giả công trình nghiên cứu gốc',
      'Nghiêm cấm các hành vi sao chép toàn bộ dữ liệu để thương mại hóa mà không có sự đồng thuận'
    ]
  },
  {
    id: 'rights-2',
    category: 'rights',
    categoryLabel: 'Bản quyền & Sử dụng',
    question: 'Làm thế nào để phản hồi góp ý hoặc đóng góp hình ảnh mẫu vật thực tế?',
    questionEn: 'How can users submit feedback or contribute field specimen photographs?',
    answer: 'Chúng tôi rất trân trọng mọi đóng góp chuyên môn từ các nhà khoa học, chuyên gia sinh học, ngư dân, cũng như những thợ lặn chụp ảnh sinh vật biển dưới nước. Nếu phát hiện sai sót về định loại, lỗi gõ chữ hoặc muốn đóng góp tư liệu ảnh thực tế sống động của loài tại vùng biển Việt Nam, quý độc giả có thể liên hệ trực tiếp qua kênh phản hồi của Viện Hải dương học.',
    highlights: [
      'Tiếp nhận ý kiến phản hồi chuyên môn qua hòm thư điện tử của Viện Hải dương học',
      'Khuyến khích cộng đồng lặn biển và nhiếp ảnh gia đại dương đóng góp ảnh chụp loài ngoài tự nhiên'
    ]
  }
]
