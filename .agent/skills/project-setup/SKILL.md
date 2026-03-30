---
name: Landslide Detection System — Final
description: Hệ thống phát hiện sạt lở theo đúng hướng dẫn đề tài.
---

## Stack công nghệ
- Backend: Python 3.11, FastAPI, Uvicorn
- ORM: SQLAlchemy 2.0
- Database: PostgreSQL duy nhất (KHÔNG dùng InfluxDB)
- Template: Jinja2 + Bootstrap 5 (server-side render)
- Validate: Pydantic BaseModel
- Detection: Rule-based check_alert_level() (ML là điểm cộng sau)
- Simulator: requests POST trực tiếp (KHÔNG dùng MQTT)
- Notification: Telegram Bot API
- Dashboard: Grafana qua Docker, kết nối PostgreSQL, embed iframe
- Config: python-dotenv đọc .env

## Cấu trúc thư mục chuẩn
- app/
  - database.py     → SQLAlchemy engine, SessionLocal, Base, get_db()
  - models.py       → 5 bảng: Sensor, SensorData, Alert, Threshold, TestResult
  - schemas.py      → Pydantic: SensorDataIn, AlertOut, ThresholdUpdate
  - main.py         → FastAPI app, mount static, templates, include routers
  - routers/
    - sensors.py    → CRUD cảm biến + API lấy data
    - alerts.py     → lịch sử cảnh báo
    - admin.py      → trang quản trị HTML Jinja2
    - thresholds.py → đọc và cập nhật ngưỡng
- detection/
  - engine.py       → check_alert_level(data, threshold) → green/yellow/red
- simulator/
  - simulate.py     → gửi POST /api/sensor-data mỗi 5 giây, inject anomaly mỗi 20 chu kỳ
- templates/
  - base.html       → navbar Bootstrap 5, sidebar, footer
  - dashboard.html  → Chart.js fetch /api/sensor-data/latest
  - sensors.html    → CRUD bảng cảm biến
  - alerts.html     → bảng lịch sử cảnh báo, badge màu
  - thresholds.html → form admin chỉnh ngưỡng
  - grafana.html    → iframe nhúng Grafana
- static/
  - css/custom.css
  - js/dashboard.js
- tests/
  - test_detection.py
  - test_api.py
- docs/
  - report.md

## 5 bảng database (SQLAlchemy)
- Sensor: id, name, location, latitude, longitude, is_active
- SensorData: id, sensor_id(FK), do_nghieng, do_rung, luong_mua, timestamp
- Alert: id, sensor_id(FK), level, message, is_resolved, timestamp
- Threshold: id, nghieng_warn(10), nghieng_danger(20), rung_warn(3), rung_danger(6), mua_warn(30), mua_danger(60)
- TestResult: id, scenario_name, input_data, expected_level, actual_level, detect_time_ms, passed, tested_at

## Ngưỡng cảnh báo mặc định
- Độ nghiêng: warn=10°, danger=20°
- Độ rung: warn=3.0, danger=6.0
- Lượng mưa: warn=30mm, danger=60mm
- Level: green=bình thường, yellow=cảnh báo, red=nguy hiểm

## API routes (JSON)
- POST /api/sensor-data        → nhận data từ simulator, chạy detection, lưu DB
- GET  /api/sensor-data/latest → 100 bản ghi mới nhất
- GET  /api/alerts             → lịch sử cảnh báo
- GET  /api/thresholds         → đọc ngưỡng hiện tại
- PUT  /api/thresholds         → cập nhật ngưỡng

## HTML routes (Jinja2)
- GET /admin/dashboard    → dashboard.html
- GET /admin/sensors      → sensors.html
- GET /admin/alerts       → alerts.html
- GET /admin/thresholds   → thresholds.html
- GET /admin/grafana      → grafana.html

## Quy ước code
- Không hardcode credentials, đọc từ .env
- Dùng logging, không dùng print
- Mọi function có docstring tiếng Việt
- Dùng SQLAlchemy ORM, không viết SQL thuần
- Validate input bằng Pydantic trước khi lưu DB
- Không commit .env lên Git

## Lịch thực hiện
- Tuần 1-2: môi trường + DB schema (database.py, models.py, schemas.py)
- Tuần 3: simulator/simulate.py
- Tuần 4: FastAPI main.py + routers
- Tuần 5: detection/engine.py
- Tuần 6: Telegram alert
- Tuần 7-8: templates HTML Jinja2
- Tuần 9: Grafana Docker + embed iframe
- Tuần 10-11: test 4 kịch bản + viết báo cáo

## 4 kịch bản test bắt buộc
- Kịch bản 1: data bình thường → expect green, không có alert
- Kịch bản 2: vượt ngưỡng vàng → expect yellow, Telegram gửi tin
- Kịch bản 3: vượt ngưỡng đỏ → expect red, Telegram gửi ngay
- Kịch bản 4: admin đổi ngưỡng → kiểm tra ngưỡng mới hoạt động đúng