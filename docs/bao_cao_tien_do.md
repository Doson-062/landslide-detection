# 📋 BÁO CÁO TIẾN ĐỘ DỰ ÁN
## Hệ Thống Phát Hiện và Cảnh Báo Sạt Lở Đất (Landslide Detection System)

> Xem file đầy đủ tại artifact walkthrough.md hoặc mở file này trong VS Code.

---

## 1. TỔNG QUAN DỰ ÁN

### Mục tiêu
Xây dựng hệ thống phần mềm có khả năng:
- Thu nhận dữ liệu từ cảm biến (độ nghiêng, độ rung, lượng mưa)
- Phân tích và so sánh dữ liệu với ngưỡng cảnh báo
- Tự động phát cảnh báo khi phát hiện bất thường (3 mức: Xanh / Vàng / Đỏ)
- Gửi thông báo khẩn cấp qua Telegram Bot
- Hiển thị toàn bộ dữ liệu trên giao diện Web Dashboard
- Phân quyền người dùng (Admin quản trị / Viewer chỉ xem)

### Công nghệ sử dụng

| Thành phần | Công nghệ | Vai trò |
|------------|-----------|---------|
| Ngôn ngữ | Python 3.11 | Backend |
| Web Framework | FastAPI 0.115.6 | REST API |
| Web Server | Uvicorn 0.34.0 | ASGI Server |
| Cơ sở dữ liệu | PostgreSQL 16 | Lưu trữ |
| ORM | SQLAlchemy 2.0.36 | Thao tác DB |
| Validate | Pydantic | Kiểm tra dữ liệu |
| Template | Jinja2 3.1.5 | Ghép data vào HTML |
| CSS | Bootstrap 5.3.3 | Giao diện |
| Xác thực | Starlette Session | Đăng nhập cookie |
| Mã hóa | SHA-256 | Hash mật khẩu |
| Cảnh báo | Telegram Bot API | Gửi tin nhắn |

---

## 2. SÁU OUTPUT BẮT BUỘC

| # | Output | Trạng thái | Đối ứng (Files) |
|---|--------|------------|-----------------|
| 1 | Module phân tích dữ liệu cảm biến | ✅ Hoàn thành | `engine.py`, `sensors.py` |
| 2 | Module phát hiện và sinh cảnh báo | ✅ Hoàn thành | `engine.py`, `alerts.py` |
| 3 | Bộ tiêu chí / ngưỡng cảnh báo | ✅ Hoàn thành | `thresholds.py`, `thresholds.html` |
| 4 | Bộ dữ liệu kiểm thử | ✅ Hoàn thành | `simulate.py`, `test_engine.py` |
| 5 | Giao diện hiển thị cảnh báo | ✅ Hoàn thành | `index.html`, `map.html`, `alerts.html` |
| 6 | Báo cáo thuật toán | ✅ Hoàn thành | `Bao_Cao_Tong_Ket_Du_An.md` |

---

## 3. CHI TIẾT FILE VÀ THƯ MỤC

### app/ — Backend

| File | Dòng | Chức năng | Output | Trạng thái |
|------|------|-----------|--------|------------|
| main.py | 85 | Khởi động Server, gom router, session middleware | Chung | ✅ |
| database.py | 57 | Kết nối PostgreSQL/SQLite, hàm get_db() | Chung | ✅ |
| models.py | 127 | 6 bảng: sensors, sensor_data, alerts, thresholds, users, test_results | 1,2,3,4,5 | ✅ |
| schemas.py | 65 | 3 bộ lọc: SensorDataIn, AlertOut, ThresholdUpdate | 1,3 | ✅ |

### app/routers/ — API

| File | Dòng | Đường link | Output | Trạng thái |
|------|------|------------|--------|------------|
| sensors.py | 222 | POST /api/sensor-data, GET /api/sensor-data/latest, POST /api/sensors/register | 1,2 | ✅ |
| admin.py | 127 | GET /admin/overview,dashboard,alerts,sensors,thresholds,users,grafana | 5 | ✅ |
| auth.py | 172 | GET,POST /login, GET /logout, GET,POST /api/users | 5 | ✅ |
| alerts.py | 45 | GET /api/alerts (đã có logic lọc) | 2 | ✅ |
| thresholds.py | 55 | GET,PUT /api/thresholds | 3 | ✅ |

### detection/ — Thuật toán

| File | Dòng | Chức năng | Output | Trạng thái |
|------|------|-----------|--------|------------|
| engine.py | 60 | check_alert_level(): so sánh data vs ngưỡng → green/yellow/red | 2,6 | ✅ |

### simulator/ — Giả lập

| File | Dòng | Chức năng | Output | Trạng thái |
|------|------|-----------|--------|------------|
| simulate.py | 162 | 2 trạm, 5s/lần, anomaly mỗi 5 chu kỳ | 1,4 | ✅ |

### templates/ — Giao diện

| File | Chức năng | Output | Trạng thái |
|------|-----------|--------|------------|
| base.html | Khung sườn: sidebar + navbar + footer, phân quyền menu | 5 | ✅ |
| login.html | Trang đăng nhập | 5 | ✅ |
| users.html | Quản lý tài khoản (Admin) | 5 | ✅ |
| index.html | Tổng quan (Dashboard chính) | 5 | ✅ Gắn data sống |
| dashboard.html | Biểu đồ Chart.js (Chi tiết trạm) | 5 | ✅ Gắn data sống |
| alerts.html | Nhật ký cảnh báo | 5 | ✅ Gắn data sống & Filter |
| map.html | Bản đồ Leaflet.js (Trực quan trạm) | 5 | ✅ Gắn data sống |
| sensors.html | Quản lý danh sách thiết bị đo | 5 | ✅ Hoàn thành |
| grafana.html | Nhúng Grafana iframe | 5 | 🟡 Sẵn sàng nhúng |

---

## 4. PHÂN QUYỀN

| Trang | Admin | Viewer |
|-------|-------|--------|
| Tổng quan, Dashboard, Cảnh báo, Grafana | ✅ | ✅ |
| Thiết bị đo, Chỉnh Ngưỡng, Tài khoản | ✅ | ❌ |

---

## 5. TIẾN ĐỘ TỔNG: ~90%

| Phần | % |
|------|---|
| Database | 100% |
| Thuật toán | 100% |
| Simulator | 100% |
| API Sensors/Alerts/Thresholds | 100% |
| Telegram Alert | 100% |
| Login + Phân quyền | 100% |
| Giao diện Web (Jinja2) | 100% |
| Grafana Integration | 30% |
| QA Test 4 kịch bản | 20% |
| Báo cáo tổng kết | 100% |
