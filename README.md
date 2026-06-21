# 🏔️ Hệ Thống Phát Hiện và Cảnh Báo Sạt Lở Đất

> Đồ án chuyên ngành — Ứng dụng IoT giám sát sạt lở đất thời gian thực.

## 📋 Mô tả

Hệ thống tiếp nhận dữ liệu từ các trạm cảm biến (độ nghiêng, độ rung, lượng mưa) qua **MQTT**, phân tích tự động bằng thuật toán Rule-based, và đưa ra cảnh báo theo 3 mức độ:

- 🟢 **Green** — An toàn
- 🟡 **Yellow** — Cảnh báo sớm (vượt ngưỡng Warn)
- 🔴 **Red** — Báo động khẩn cấp (vượt ngưỡng Danger)

## 🔁 Luồng dữ liệu (MQTT)

```
Simulator / Trạm IoT
        │  publish JSON
        ▼
  Mosquitto Broker  (topic: landslide/sensors/data)
        │
        ▼
  app/mqtt_subscriber.py  →  PostgreSQL  →  check_alert_level()
        │
        ▼
  Dashboard HTML + API JSON + Cảnh báo
```

- **Luồng chính:** Simulator publish lên MQTT; FastAPI khởi động MQTT Subscriber cùng lúc với server.
- **REST:** Dùng cho đăng ký trạm, quản trị, dashboard JSON và fallback `POST /api/sensor-data`.

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 (ORM) |
| Messaging | MQTT — Eclipse Mosquitto (Docker) |
| Validation | Pydantic BaseModel |
| Frontend | Jinja2 (Server-Side Rendering) + Bootstrap 5 |
| Auth | Session cookie, phân quyền admin / viewer |
| Detection | Rule-based `check_alert_level()` |
| Simulator | `paho-mqtt` publish JSON mỗi 5 giây |
| Notification | Telegram Bot API *(đang phát triển)* |
| Dashboard | Grafana Docker + iframe *(đang phát triển)* |

## 📁 Cấu trúc thư mục

```
PRJ_II/
├── app/                        # Backend Core
│   ├── main.py                 # Entry point — FastAPI + MQTT Subscriber lifespan
│   ├── database.py             # Kết nối PostgreSQL (Engine, Session, get_db)
│   ├── models.py               # 6 bảng DB (Sensor, SensorData, Alert, Threshold, TestResult, User)
│   ├── schemas.py              # Pydantic Validation (SensorDataIn, AlertOut, ThresholdUpdate)
│   ├── mqtt_subscriber.py      # Lắng nghe MQTT, xử lý và lưu dữ liệu cảm biến
│   └── routers/
│       ├── auth.py             # Đăng nhập, session, quản lý user
│       ├── sensors.py          # REST nhận data (fallback) + đăng ký trạm
│       ├── admin.py            # Render giao diện HTML Jinja2
│       ├── alerts.py           # API lịch sử cảnh báo
│       └── thresholds.py       # API đọc/sửa ngưỡng cảnh báo
│
├── detection/
│   └── engine.py               # Thuật toán phát hiện sạt lở (green/yellow/red)
│
├── simulator/
│   └── simulate.py             # Giả lập trạm, publish MQTT mỗi 5 giây
│
├── mosquitto/
│   └── mosquitto.conf          # Cấu hình MQTT Broker (Docker mount)
│
├── templates/                  # Giao diện Web (Jinja2 + Bootstrap 5)
│   ├── base.html               # Layout chung (Sidebar, Header, Footer)
│   ├── login.html              # Trang đăng nhập
│   ├── index.html              # Trang Tổng quan
│   ├── dashboard.html          # Trang Biểu đồ realtime
│   ├── alerts.html             # Trang Nhật ký cảnh báo
│   ├── sensors.html            # Quản lý trạm cảm biến
│   ├── thresholds.html         # Cấu hình ngưỡng
│   ├── users.html              # Quản lý tài khoản (admin)
│   ├── map.html                # Bản đồ trạm
│   └── grafana.html            # Trang nhúng Grafana
│
├── static/css/                 # File CSS trang trí
├── tests/                      # Kiểm thử tự động
├── .env.example                # Mẫu cấu hình môi trường
├── requirements.txt            # Danh sách thư viện Python
├── run_server.bat              # Khởi động Mosquitto + Grafana + FastAPI + Simulator
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

Yêu cầu thêm: [Docker Desktop](https://www.docker.com/products/docker-desktop/) (chạy Mosquitto và Grafana).

### 2. Cấu hình Database & MQTT

- Cài đặt [PostgreSQL](https://www.postgresql.org/download/)
- Tạo database tên `landslide_db`
- Copy file `.env.example` thành `.env` và điền thông tin kết nối:

```env
POSTGRES_URL=postgresql://postgres:your_password@localhost:5432/landslide_db
USE_SQLITE=False

MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=landslide/sensors/data
SECRET_KEY=your-secret-key-here
```

### 3. Khởi động hệ thống

**Cách nhanh (Windows):** nhấp đúp `run_server.bat` — script sẽ tự khởi động Mosquitto, Grafana, FastAPI và Simulator.

**Cách thủ công:**

```bash
# Terminal 1 — MQTT Broker
docker run -d --name mosquitto -p 1883:1883 -p 9001:9001 \
  -v ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto:2

# Terminal 2 — FastAPI (MQTT Subscriber tự bật khi server khởi động)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 3 — Simulator
python simulator/simulate.py
```

### 4. Truy cập giao diện

| Dịch vụ | URL |
|---------|-----|
| Web app | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| Grafana | [http://127.0.0.1:3000](http://127.0.0.1:3000) (mật khẩu mặc định: `admin123`) |

Tài khoản mặc định lần đầu chạy: **admin** / **admin123**

## 📊 Ngưỡng cảnh báo mặc định

| Chỉ số | Warn (Vàng) | Danger (Đỏ) |
|--------|-------------|-------------|
| Độ nghiêng | ≥ 10° | ≥ 20° |
| Độ rung | ≥ 3.0 m/s² | ≥ 6.0 m/s² |
| Lượng mưa | ≥ 30 mm/h | ≥ 60 mm/h |

Admin có thể chỉnh ngưỡng qua giao diện web hoặc API `PUT /api/thresholds`.

## 🧪 Kịch bản kiểm thử

| # | Kịch bản | Kết quả mong đợi |
|---|----------|------------------|
| 1 | Dữ liệu bình thường (MQTT) | Green — Không có cảnh báo |
| 2 | Vượt ngưỡng Warn | Yellow — Ghi nhận cảnh báo |
| 3 | Vượt ngưỡng Danger | Red — Báo động khẩn cấp |
| 4 | Admin đổi ngưỡng | Ngưỡng mới áp dụng cho bản tin MQTT tiếp theo |
| 5 | Trạm chưa đăng ký publish MQTT | Bản tin bị bỏ qua (log cảnh báo) |

## 📌 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/sensor-data` | Nhận dữ liệu qua REST *(fallback, không phải luồng chính)* |
| GET | `/api/sensor-data/latest` | 100 bản ghi mới nhất |
| POST | `/api/sensors/register` | Đăng ký trạm cảm biến mới |
| GET | `/api/alerts` | Lịch sử cảnh báo |
| GET | `/api/thresholds` | Đọc ngưỡng hiện tại |
| PUT | `/api/thresholds` | Cập nhật ngưỡng |

### MQTT Topic

| Hướng | Topic mặc định | Payload |
|-------|----------------|---------|
| Publish (Simulator) | `landslide/sensors/data` | JSON: `sensor_id`, `do_nghieng`, `do_rung`, `luong_mua` |
| Subscribe (Backend) | `landslide/sensors/data` | Cùng format; xử lý qua `mqtt_subscriber.py` |

## 👤 Tác giả

- **Đỗ Thanh Sơn** — IT2-02-k68

## 📄 License

Dự án phục vụ mục đích học tập và nghiên cứu.
