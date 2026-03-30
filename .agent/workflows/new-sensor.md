---
description: Thêm cảm biến mới vào hệ thống
---

# Quy trình thêm cảm biến (Sensor)

Thực hiện lần lượt các yêu cầu sau để thêm mới một trạm quan trắc vào hệ thống sạt lở:

1. Insert dữ liệu thông tin sensor mới vào bảng `sensors` qua SQLAlchemy (ORM).
2. Insert ngưỡng cảnh báo mặc định vào bảng `thresholds` cho sensor id đó:
   - `nghieng_warn`: 10
   - `nghieng_danger`: 20
   - `rung_warn`: 3
   - `rung_danger`: 6
   - `mua_warn`: 30
   - `mua_danger`: 60
3. Gửi request kiểm tra đến API `GET /api/sensor-data/latest`.
4. Đảm bảo API trả về đúng chuỗi Data có chứa `sensor_id` của sensor vừa tạo trong payload Json.
