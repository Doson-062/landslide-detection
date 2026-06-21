# BÁO CÁO KẾT QUẢ THỰC HIỆN ĐỒ ÁN
**Đề tài: Hệ thống giám sát và cảnh báo sớm nguy cơ sạt lở đất**

---

## LỜI MỞ ĐẦU
Trong bối cảnh biến đổi khí hậu diễn biến phức tạp, các thảm họa sạt lở đất gây ra nhiều thiệt hại nghiêm trọng về người và tài sản. Từ thực tiễn đó, nhóm đã thực hiện đề tài "Hệ thống giám sát và cảnh báo sạt lở đất" với mục tiêu ứng dụng công nghệ thông tin vào việc thu thập dữ liệu độ nghiêng, độ rung động và lượng mưa từ các vùng núi, từ đó xây dựng một trung tâm điều hành nòng cốt có khả năng cảnh báo sớm qua đa nền tảng. Đến thời điểm hiện tại, dự án đã cơ bản hoàn thiện toàn bộ quy trình luân chuyển dữ liệu từ thiết bị đầu cuối cho đến người quản trị.

---

## 1. MÔ HÌNH KIẾN TRÚC VÀ CÔNG NGHỆ SỬ DỤNG
Tuy là một đồ án môn học, nhưng hệ thống được thiết kế đầy đủ các tầng theo chuẩn kiến trúc Client - Server của một hệ thống IoT, đảm bảo khả năng mở rộng sau này:

*   **1.1. Lớp Thu nhận dữ liệu (Data Acquisition):** 
    Sử dụng kịch bản lập trình Python (Simulator) đóng vai trò thay thế cho vi điều khiển vật lý. Các trạm này sử dụng giao thức HTTP/REST để truyền tải dữ liệu dạng JSON.
*   **1.2. Lớp Xử lý lõi (Backend Logic):**
    Thiết kế bằng ngôn ngữ Python, sử dụng **FastAPI**. Đây là một framework hiện đại, xử lý bất đồng bộ (Asynchronous) giúp hệ thống có thể tiếp nhận hàng nghìn kết nối từ các trạm cảm biến cùng lúc mà không bị quá tải. Lớp này chịu trách nhiệm thu nhận, làm sạch dữ liệu và chấm điểm mức độ nguy hiểm đối với mỗi gói tin.
*   **1.3. Lớp Lưu trữ cơ sở dữ liệu (Database Layer):**
    Được vận hành bởi hệ quản trị cơ sở dữ liệu quan hệ **PostgreSQL**. Lý do chọn PostgreSQL là vì khả năng lưu trữ lượng lớn Time-series data (Dữ liệu chuỗi thời gian) rất mạnh của nó. Việc tương tác với CSDL không dùng mã SQL thủ công mà qua bộ ánh xạ Object-Relational Mapping (ORM) **SQLAlchemy**, giúp code dễ bảo trì hơn.
*   **1.4. Lớp Giao diện chuyên gia (Frontend / User Interface):**
    Phát triển trên nền tảng Web (HTML5/CSS/JS) với bộ khung giao diện Bootstrap 5. Để đảm bảo tính thời gian thực (real-time) của các biểu đồ đo lường, giao diện sử dụng **Javascript Fetch API** để thực hiện các luồng request chạy ngầm (AJAX), giúp nạp dữ liệu mới vào web nhanh gọn mà không phải làm mới (reload) toàn bộ trang.
*   **1.5. Lớp Tương tác đồ họa & Cảnh báo:**
    - Bản đồ (Web GIS): Sử dụng **Leaflet.js**, giúp nhúng bản đồ vệ tinh OpenStreetMap trực tiếp vào đồ án.
    - Vẽ biểu đồ: Dùng **Chart.js** để minh họa đường đi của các thông số.
    - Cảnh báo nhanh: Tích hợp API của **Telegram Bot** giúp hệ thống có thể liên lạc trực tiếp đến điện thoại cá nhân.

---

## 2. CÁC PHÂN HỆ CHỨC NĂNG CHI TIẾT ĐÃ HOÀN THÀNH

### 2.1. Phân hệ Sinh dữ liệu mô phỏng (Data Generator & Simulator)
Để phục vụ việc trình diễn và kiểm thử khả năng xử lý luồng dữ liệu của phần mềm lõi, đồ án đã xây dựng riêng một module sinh dữ liệu tự động (Data Generator). Chương trình lập trình này tạo ra 2 điểm trạm đo với lộ trình và tọa độ vị trí địa lý được xác định từ trước.
*   **Nguyên lý hoạt động:** Lõi mô phỏng vận hành một vòng lặp thời gian vô hạn. Cứ mỗi vài giây, nó tự động sinh ra các gói dữ liệu số (Mock Data) về: (1) Trục đo góc nghiêng, (2) Trục đo gia tốc rung động, và (3) Tổng lượng mưa hiện tại. Đặc biệt, chương trình có tích hợp luồng "Bơm dữ liệu bất thường" (Inject anomalies) có chủ đích, ví dụ tự động dội lượng mưa lên ngưỡng 60mm để kích hoạt thử nghiệm tính năng phản ứng báo động khẩn cấp của thuật toán Detection Engine.

> *[📸 Hình minh họa 1: Chụp màn hình cửa sổ đen Terminal/CMD đang chạy file simulator thể hiện quá trình gửi request Post thành công]*

### 2.2. Phân hệ Bảng điều khiển Giám sát trung tâm (Live Dashboard)
Đây là màn hình giao diện làm việc chính yếu của người vận hành.
*   **Tính năng hiện tại:** Gồm bộ thẻ hiển thị con số kỹ thuật mới nhất lấy về từ trạm chỉ định. Phía dưới là đồ thị đường (Line Chart) kéo dài dữ liệu lên tới 20 bản ghi tự động cuộn về phía trước. 
*   **Điểm nhấn kỹ thuật:** Dashboard có hệ thống cấp độ Badge màu tự động (Xanh/Vàng/Đỏ) hoạt động độc lập để đánh giá khái quát tình hình của trạm. Nhờ kỹ thuật Fetch vòng lặp, màn hình đem lại cảm giác sống động như màn hình điện tâm đồ của cảm biến vật lý.
> *[📸 Hình minh họa 2: Mở rộng trang Web Dashboard, chụp khi các đường biểu đồ đang có các nếp gấp biến thiên và phần Cảnh báo đang hiện chữ Nguy hiểm]*

### 2.3. Bản đồ Không gian số (Interactive Web Map)
Để hỗ trợ việc trực quan hóa khái niệm không gian địa lý, các tọa độ của trạm không được giữ dưới dạng những con số vô hồn, mà được vẽ thẳng lên bản đồ hệ toạ độ WGS84.
*   **Cách thức thực hiện:** Mã nguồn JS tại giao diện sẽ gửi request hỏi Backend xin tọa độ của hệ thống cảm biến lưới. Leaflet.js tiếp nhận danh sách vĩ độ/kinh độ và cắm các Điểm đánh dấu (Marker). 
*   **Xử lý đa luồng:** Điểm thành công của chức năng này là các Marker sẽ liên kết trói buộc vào thông số cảm biến. Nếu một trạm đo bỗng dưng lở đất, chấm Marker của nó trên bản đồ sẽ lập tức chuyển màu đỏ mà người trực không cần thao tác gì.
> *[📸 Hình minh họa 3: Chụp ảnh nửa phải màn hình trang Bản đồ, thấy rõ các cờ đánh dấu đang được xếp ở khu vực Hà Nội / Sơn La. Nên có một trạm màu chú ý/cảnh báo]*

### 2.4. Phân hệ Tùy chỉnh Ngưỡng cảnh báo Động (Dynamic Thresholds Adjustment)
Một trong những điểm cứng nhắc của các ứng dụng đo lường trước đây là việc "code chết" một con số rủi ro (Ví dụ: đặt cứng biến lượng mưa > 50 là sạt lở). Tuy nhiên, mỗi ngọn đồi thực tế lại có những ngưỡng chịu đựng khác nhau.
*   **Giải pháp của đồ án:** Xây dựng riêng một trang "Cài đặt Ngưỡng" cho quản trị viên. Trang này lấy biểu mẫu (Form) thông số và cập nhật thằng vào Cơ sở dữ liệu. Lõi thuật toán phát hiện (Detection Engine) sẽ luôn đọc con số này trước khi chấm điểm. Nhờ vậy, người vận hành có thể tự do siết độ khó hoặc nới lỏng mức độ cảnh báo bất cứ lúc nào.
> *[📸 Hình minh họa 4: Chụp màn hình trang Cài đặt Ngưỡng với đầy đủ 6 thông số: Rung/Mưa/Nghiêng ở bên Mức 1 và Mức 2]*

### 2.5. Phân hệ Xử lý Khẩn cấp & Ghi nhật ký (Alerting & Auditing)
Sạt lở đất là tài họa nguy hiểm cần phản ứng tính bằng giây, do vậy việc chỉ để người trực ngồi nhìn màn hình web là không đủ.
*   **Phản ứng nhanh (Telegram):** Ngay tại điểm Engine thuật toán bắt được sự thay đổi dị thường vượt ngưỡng Đỏ/Vàng, Backend sẽ mở một luồng HTTP phụ nhắn dữ liệu sang cổng API của Telegram. Điện thoại của kỹ sư/quản lý sẽ nhận được thông báo "CẢNH BÁO SẠT LỞ" ngay lập tức.
*   **Truy xuất vết (Audit):** Song song với nhắn tin, hệ thống tự động ghi nhật ký vào bảng Alerts. Trên giao diện Web có kèm trang "Danh sách Cảnh báo" giúp người quản lý có thể phân tích ca trực xem giờ nào hay lở đất nhất.
> *[📸 Hình minh họa 5: Chụp ảnh trang Lịch sử cảnh báo có nhiều dòng log màu Đỏ/Vàng, sau đó chụp màn hình điện thoại ghép sang bên cạnh để chứng tỏ hệ thống Bot cũng đã nhận được tin báo]*

### 2.6. Phân hệ Xác thực và Phân quyền Người dùng (Auth & RBAC)
Một hệ thống IoT công nghiệp không thể để cho ai cũng có quyền can thiệp vào cấu hình hoạt động. Việc bổ sung lớp bảo mật đăng nhập chứng minh được tính ứng dụng thực tế của dự án.
*   **Chiến lược phân quyền:** Hệ thống chia làm 2 cấp bậc Người dùng. 
    1. Cấp Khách (Guest / Viewer): Có thể truy cập tự do vào các trang xem biểu đồ Tổng quan, xem Bản đồ vị trí sự cố để cập nhật thông tin kịp thời.
    2. Cấp Quản trị (Super Admin): Bắt buộc phải đăng nhập. Cấp này mới có quyền chỉnh sửa các thông số báo động quan trọng hoặc thêm, sửa, xóa Thiết bị cảm biến và cấp mật khẩu cho người khác.
*   **Công nghệ bảo mật:** Việc trao đổi xác thực không sử dụng mã plaintext thông thường mà sử dụng mã băm `SHA-256` cùng với hệ thống Session Cookies mã hoá sinh tự động bằng thư viện `Itsdangerous` của Python, chống lại các cuộc tấn công đánh cắp Cookie.
> *[📸 Hình minh họa 6: Chụp màn hình trang Đăng Nhập (Login) của hệ thống web]*

---

## 3. KẾT LUẬN VÀ ĐỊNH HƯỚNG PHÁT TRIỂN
### 3.1. Tổng kết dự án
Đến thời điểm này, nhóm đã hoàn thành toàn bộ khối lượng công việc cốt lõi của đề tài. Thay vì phụ thuộc vào thiết bị vật lý, đồ án đã đi sâu giải quyết bài toán về mặt cấu trúc phần mềm: xây dựng thành công một bộ máy (Backend) có khả năng tiếp nhận luồng dữ liệu liên tục từ bộ sinh dữ liệu tự động (Simulator), đánh giá mức độ rủi ro bằng thuật toán và phản hồi cảnh báo khẩn cấp. 

Điểm sáng của dự án là dữ liệu được đẩy mượt mà lên bản đồ và biểu đồ mà không bị nghẽn ngõ, luồng tin nhắn Telegram hoạt động nhạy bén đúng với các kịch bản kiểm thử (test scenarios) đã đặt ra. Việc thêm/bớt thông số giới hạn cũng được làm chủ động thông qua quyền Admin.

### 3.2. Định hướng mở rộng (Tương lai)
Nếu có thêm thời gian phát triển, dự án phần mềm này có thể được nâng cấp thêm chuyên sâu về mặt xử lý dữ liệu:
1. **Nâng cấp kịch bản giả lập (Simulator):** Cho phép Simulator sinh ra khối lượng dữ liệu khổng lồ (vài trăm trạm) mô phỏng các đợt bão lớn hoặc áp thấp nhiệt đới kéo dài để kiểm tra độ trễ (latency) của máy chủ phần mềm.
2. **Áp dụng Học máy (Machine Learning):** Lõi thuật toán hiện đang đánh giá dựa trên luật (Rule-based: lớn hơn/nhỏ hơn ngưỡng). Về sau có thể dạy cho AI học lịch sử biểu đồ để dự báo sớm thời điểm chuẩn bị đứt gãy sườn núi thay vì đợi nó vượt số mới báo.
3. **Mở rộng báo cáo bằng Grafana:** Đồng bộ hóa dữ liệu từ PostgreSQL sang Grafana để tạo thành các hệ thống báo cáo chuyên ngành cho giới phân tích địa chất (Ví dụ vẽ biểu đồ nhiệt Heatmap hiển thị vùng rủi ro trượt lở qua từng năm).

Nhìn chung, kiến trúc phần mềm của dự án đã rất sẵn sàng để làm ứng dụng trung tâm (Core) cho các hệ thống quan trắc môi trường thực tế khác nếu được đưa vào triển khai.

