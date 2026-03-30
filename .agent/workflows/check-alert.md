---
description: Kiểm tra toàn bộ luồng cảnh báo end-to-end (từ Simulator tới Dashboard/Bot)
---

# Quy trình Check Alert End-to-End

Với bất cứ lúc nào Admin/User muốn kiểm tra khả năng Alerting của hệ thống, chạy workflow này:

1. Kích hoạt tính năng Simulator: Gửi mock data sạt lở bất thường (vượt biên giới hạn) đến Web Server thông qua API `POST /api/sensor-data`.
2. Kiểm tra/Console log xác nhận module `detection engine` đã can thiệp và bám trả về đúng cấp độ level tương ứng (VD: red=3).
3. Đọc database thông qua get_db() -> SQLAlchemy `Alert` truy vấn và xác nhận log alert vượt ngưỡng đã được persist/lưu trữ an toàn vào DB (bảng alerts).
4. Kiểm tra mạng Webhook: Xác nhận Telegram bot báo là đã nhận được tin nhắn text chứa đúng định dạng nội dung số liệu cảnh báo.
5. Kiểm tra GUI: Mở URL duyệt web tới trình đơn Dashboard/Quản trị qua route `GET /admin/alerts`, phải nhìn thấy alert record mới sinh nằm đầu tiên trên table kèm *badge màu* chuẩn xác.
