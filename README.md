# 🏔️ Hệ Thống Phát Hiện và Cảnh Báo Sạt Lở Đất

> Đồ án chuyên ngành — Ứng dụng IoT giám sát sạt lở đất thời gian thực.

## 📋 Mô tả

Hệ thống tiếp nhận dữ liệu từ các trạm cảm biến (độ nghiêng, độ rung, lượng mưa), phân tích tự động bằng thuật toán Rule-based, và đưa ra cảnh báo theo 3 mức độ:

- 🟢 **Green** — An toàn
- 🟡 **Yellow** — Cảnh báo sớm (vượt ngưỡng Warn)
- 🔴 **Red** — Báo động khẩn cấp (vượt ngưỡng Danger)

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 (ORM) |
| Validation | Pydantic BaseModel |
| Frontend | Jinja2 (Server-Side Rendering) + Bootstrap 5 |
| Detection | Rule-based `check_alert_level()` |
| Simulator | REST API (`requests` POST trực tiếp) |
| Notification | Telegram Bot API *(đang phát triển)* |
| Dashboard | Grafana Docker + iframe *(đang phát triển)* |

## 📁 Cấu trúc thư mục

```
PRJ_II/
├── app/                        # Backend Core
│   ├── main.py                 # Entry point — Khởi động FastAPI Server
│   ├── database.py             # Kết nối PostgreSQL (Engine, Session, get_db)
│   ├── models.py               # 5 bảng Database (Sensor, SensorData, Alert, Threshold, TestResult)
│   ├── schemas.py              # Pydantic Validation (SensorDataIn, AlertOut, ThresholdUpdate)
│   └── routers/
│       ├── sensors.py          # API nhận data từ Simulator + Đăng ký trạm
│       ├── admin.py            # Render giao diện HTML Jinja2
│       ├── alerts.py           # API lịch sử cảnh báo
│       └── thresholds.py       # API đọc/sửa ngưỡng cảnh báo
│
├── detection/
│   └── engine.py               # Thuật toán phát hiện sạt lở (green/yellow/red)
│
├── simulator/
│   └── simulate.py             # Giả lập trạm cảm biến, gửi data mỗi 5 giây
│
├── templates/                  # Giao diện Web (Jinja2 + Bootstrap 5)
│   ├── base.html               # Layout chung (Sidebar, Header, Footer)
│   ├── index.html              # Trang Tổng quan
│   ├── dashboard.html          # Trang Biểu đồ realtime
│   ├── alerts.html             # Trang Nhật ký cảnh báo
│   └── grafana.html            # Trang nhúng Grafana
│
├── static/css/                 # File CSS trang trí
├── tests/                      # Kiểm thử tự động
├── .env.example                # Mẫu cấu hình môi trường
├── requirements.txt            # Danh sách thư viện Python
├── run_server.bat              # Khởi động nhanh trên Windows
└── README.md                   # File này
```

## 🚀 Hướng dẫn cài đặt

### 1. Cài đặt môi trường

```bash
# Clone dự án
git clone https://github.com/Doson-062/landslide-detection.git
cd landslide-detection

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình Database

- Cài đặt [PostgreSQL](https://www.postgresql.org/download/)
- Tạo database tên `landslide_db`
- Copy file `.env.example` thành `.env` và điền thông tin kết nối:

```env
POSTGRES_URL=postgresql://postgres:your_password@localhost:5432/landslide_db
USE_SQLITE=False
```

### 3. Khởi động Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Hoặc nhấp đúp file `run_server.bat` trên Windows.

### 4. Chạy Simulator (Terminal thứ 2)

```bash
python simulator/simulate.py
```

### 5. Truy cập giao diện

Mở trình duyệt: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📊 Ngưỡng cảnh báo mặc định

| Chỉ số | Warn (Vàng) | Danger (Đỏ) |
|--------|-------------|-------------|
| Độ nghiêng | ≥ 10° | ≥ 20° |
| Độ rung | ≥ 3.0 m/s² | ≥ 6.0 m/s² |
| Lượng mưa | ≥ 30 mm/h | ≥ 60 mm/h |

## 🧪 Kịch bản kiểm thử

| # | Kịch bản | Kết quả mong đợi |
|---|----------|------------------|
| 1 | Dữ liệu bình thường | Green — Không có cảnh báo |
| 2 | Vượt ngưỡng Warn | Yellow — Gửi cảnh báo Telegram |
| 3 | Vượt ngưỡng Danger | Red — Gửi báo động khẩn cấp |
| 4 | Admin đổi ngưỡng | Ngưỡng mới hoạt động đúng |

## 📌 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/sensor-data` | Nhận dữ liệu từ Simulator |
| GET | `/api/sensor-data/latest` | 100 bản ghi mới nhất |
| POST | `/api/sensors/register` | Đăng ký trạm cảm biến mới |
| GET | `/api/alerts` | Lịch sử cảnh báo |
| GET | `/api/thresholds` | Đọc ngưỡng hiện tại |
| PUT | `/api/thresholds` | Cập nhật ngưỡng |

## 👤 Tác giả

- **Đỗ Thanh Sơn** — IT2-02-k68

## 📄 License

Dự án phục vụ mục đích học tập và nghiên cứu.
