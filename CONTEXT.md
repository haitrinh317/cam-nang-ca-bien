# Cẩm Nang Sinh Vật Biển Việt Nam (Domain Context)

Nền tảng cẩm nang số hóa, tra cứu phân loại học và sinh thái học đa chuyên đề cho toàn bộ sinh vật biển Việt Nam, kết nối dữ liệu thực địa từ Viện Hải dương học Nha Trang với các cơ sở dữ liệu hải dương quốc tế (WoRMS, FishBase, AlgaeBase, iNaturalist, GBIF).

## Ngữ cảnh & Thuật ngữ chuẩn (Ubiquitous Language)

### 1. Phân loại & Thực thể Sinh học

**Loài (Species / Taxon)**:
Thực thể sinh học đơn vị cơ bản trong hệ thống phân loại, được xác định bằng danh pháp khoa học nhị thức Latinh độc nhất và gắn liền với một Bộ sưu tập cụ thể.
_Avoid_: Con vật, Cây cỏ, Bản ghi, Item

**Bộ sưu tập (Collection)**:
Không gian phân vùng dữ liệu cấp cao nhất dựa trên nhóm đối tượng sinh học hoặc đầu sách chuyên khảo thực địa (ví dụ: `ca-bien`, `thuc-vat-bien`, `san-ho`), định tuyến URL độc lập.
_Avoid_: Chuyên mục, Thể loại, Phân loại, Category

**Tập sách (Volume / Book Part)**:
Đơn vị phân đoạn ấn phẩm xuất bản gốc của Viện Hải dương học hoặc tác giả nghiên cứu (ví dụ: Tập I đến Tập VI của Cá biển; Phần I đến IV của GS. Phạm Hoàng Hộ).
_Avoid_: Quyển, Chương, Kỳ

**Danh pháp hợp lệ (Accepted Scientific Name)**:
Tên khoa học nhị thức Latinh chính thức được thẩm định và công nhận giá trị pháp lý bởi World Register of Marine Species (WoRMS) hoặc AlgaeBase theo luật danh pháp quốc tế ICZN / ICN.
_Avoid_: Tên chuẩn, Tên chính thức, Tên đúng

**Đồng danh (Synonymy)**:
Tập hợp các danh pháp lịch sử từng được các tác giả đặt cho loài này qua các thời kỳ nhưng nay đã được hợp nhất vào danh pháp hợp lệ.
_Avoid_: Tên cũ, Tên khác, Tên phụ

**Mã AphiaID (WoRMS AphiaID)**:
Mã định danh số học duy nhất toàn cầu do CSDL WoRMS cấp, dùng làm khóa ngoại liên kết kiểm định phân loại học hải dương.
_Avoid_: WoRMS Code, ID loài, Mã phân loại

### 2. Dữ liệu Thực địa & Bảo tồn

**Tiêu bản / Mẫu vật (Specimen)**:
Vật phẩm sinh học vật lý thực tế được thu thập ngoài tự nhiên, hiện đang bảo quản lưu trữ tại các bảo tàng hải dương (Nha Trang, Hải Phòng).
_Avoid_: Mẫu thử, Mẫu lưu trữ, Hiện vật

**Sinh trắc & Phân bố (Biometrics & Distribution)**:
Tập hợp các thông số đo đạc thực tế gồm Chiều dài lớn nhất/thường gặp, Dải độ sâu tầng nước sinh sống (Epipelagic, Mesopelagic, Bathypelagic), và Vùng biển ghi nhận sự xuất hiện.
_Avoid_: Kích cỡ, Nơi ở, Độ sâu

**Tình trạng bảo tồn (Conservation Status)**:
Cấp bậc đánh giá nguy cơ tuyệt chủng theo Sách Đỏ IUCN (CR, EN, VU, NT, LC, DD) hoặc Sách Đỏ Việt Nam.
_Avoid_: Tình trạng nguy cấp, Mức độ quý hiếm

### 3. Giao diện & Trình bày (Design System)

**Hồ sơ Thẩm định WoRMS (WoRMS Dossier)**:
Khối giao diện 3 cột chuyên biệt hiển thị tình trạng danh pháp, mã AphiaID và đường dẫn đối soát CSDL quốc tế.
_Avoid_: Khối WoRMS, Hộp kiểm định

**Thẻ Định Danh Tên Gọi (Identity Card)**:
Băng chuyền thông tin đầu thẻ chứa Tên gọi khác (tiếng Việt địa phương) và Tên tiếng Anh thường gọi (Common Name).
_Avoid_: Khối tên, Header phụ

**Thước đo Kích thước Tương quan (Visual Scale Widget)**:
Widget đồ họa trực quan hóa chiều dài loài cá đối chiếu với các vật chuẩn quen thuộc (Bàn tay 15cm, Nửa mét 50cm, Một mét 100cm).
_Avoid_: Thanh độ dài, Size bar
