"""
Module Giả Lập Trạm Cảm Biến (Simulator).
Tự động sinh dữ liệu ngẫu nhiên và gửi POST lên FastAPI Server mỗi 5 giây.
Cứ sau 20 chu kỳ sẽ tiêm 1 Anomaly (dữ liệu bất thường) để kích hoạt cảnh báo.
"""

import time
import requests
import random
import threading
import logging
from datetime import datetime

# ==========================================
# Cấu hình Logging (Theo quy ước dự án - KHÔNG dùng print)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("Simulator")

# ==========================================
# Cấu hình Simulator
# ==========================================
API_URL = "http://localhost:8000/api/sensor-data"
STATIONS = ["STATION_01", "STATION_02"]
CYCLE_DELAY = 5  # Thời gian nghỉ sau mỗi lần gửi (giây)


def ensure_sensors_exist():
    """
    Kiểm tra và tự động tạo các trạm cảm biến trong Database
    nếu chúng chưa tồn tại. Tránh lỗi 404 khi Simulator gửi data.
    """
    for station_id in STATIONS:
        try:
            response = requests.post(
                "http://localhost:8000/api/sensors/register",
                json={
                    "id": station_id,
                    "name": f"Trạm {station_id}",
                    "location": "Sườn núi giả lập",
                    "latitude": 21.028 + random.uniform(-0.01, 0.01),
                    "longitude": 105.854 + random.uniform(-0.01, 0.01),
                    "is_active": True
                },
                timeout=3
            )
            if response.status_code == 200:
                logger.info(f"[{station_id}] Đăng ký trạm thành công.")
            elif response.status_code == 409:
                logger.info(f"[{station_id}] Trạm đã tồn tại, bỏ qua.")
            else:
                logger.warning(f"[{station_id}] Đăng ký trạm thất bại: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"[{station_id}] Không kết nối được Server. Hãy chạy 'run_server.bat' trước!")
            return False
    return True


def generate_random_data(normal=True):
    """
    Sinh dữ liệu ngẫu nhiên cho cảm biến.
    - normal=True: Sinh dữ liệu trong khoảng an toàn (dưới ngưỡng Warn).
    - normal=False: Sinh mã độc (Anomaly) với góc nghiêng vượt trần Danger.
    """
    if normal:
        do_nghieng = round(random.uniform(0.0, 5.0), 2)   # An toàn: 0 - 5 độ
        do_rung = round(random.uniform(0.0, 1.5), 2)      # Rất ít rung: 0 - 1.5
        luong_mua = round(random.uniform(0.0, 10.0), 2)   # Lượng mưa nhỏ: 0 - 10 mm/h
    else:
        # Anomaly -> Kích hoạt Alert Đỏ (Nghiêng >= 20 theo SKILL.md)
        do_nghieng = round(random.uniform(21.0, 30.0), 2)
        do_rung = round(random.uniform(0.0, 1.5), 2)
        luong_mua = round(random.uniform(0.0, 10.0), 2)

    return {
        "do_nghieng": do_nghieng,
        "do_rung": do_rung,
        "luong_mua": luong_mua
    }


def simulate_station(sensor_id):
    """
    Hàm xử lý độc lập cho từng trạm.
    Mỗi trạm sẽ như một robot riêng, liên tục thức dậy -> đo data -> gửi server -> ngủ 5s.
    """
    cycle_count = 0
    logger.info(f"[{sensor_id}] Bắt đầu quy trình gửi dữ liệu...")

    while True:
        cycle_count += 1

        # Logic: Cứ mỗi 20 chu kỳ thì đánh úp hệ thống bằng 1 Anomaly
        is_normal = True
        if cycle_count % 20 == 0:
            is_normal = False
            logger.warning(f"[{sensor_id}] ĐANG BƠM MÃ ĐỘC (ANOMALY) VÀO CHU KỲ {cycle_count}!")

        # 1. Sinh data mô phỏng (Dictionary)
        mock_data = generate_random_data(normal=is_normal)

        # 2. Đắp thêm các trường bắt buộc thỏa mãn Validation Pydantic (schemas.py)
        mock_data["sensor_id"] = sensor_id
        mock_data["timestamp"] = datetime.now().isoformat()

        try:
            # 3. Dùng thư viện requests 'bắn' gói JSON lên backend
            response = requests.post(API_URL, json=mock_data, timeout=3)

            # 4. Kiểm tra phản hồi từ Server
            if response.status_code == 200:
                result = response.json()
                level = result.get("detection_level", "unknown")
                detect_ms = result.get("detect_time_ms", 0)
                logger.info(
                    f"[{sensor_id}] Gửi OK | Nghiêng: {mock_data['do_nghieng']}° | "
                    f"Rung: {mock_data['do_rung']} | Level: {level} | "
                    f"Detect: {detect_ms}ms | Chu kỳ: {cycle_count}"
                )
            else:
                logger.error(f"[{sensor_id}] Lỗi HTTP {response.status_code} | {response.text}")

        except requests.exceptions.ConnectionError:
            logger.error(f"[{sensor_id}] Kịt đường kết nối. Đã bật 'run_server.bat' chưa?")
        except Exception as e:
            logger.error(f"[{sensor_id}] Lỗi không rõ: {str(e)}")

        # Nằm ngủ 5 giây rồi mới lặp lại
        time.sleep(CYCLE_DELAY)


def main():
    """Hàm khởi chạy chính của Simulator."""
    logger.info("ĐANG KHỞI ĐỘNG HỆ THỐNG GIẢ LẬP TRẠM CẢM BIẾN (SIMULATOR)...")

    # Bước 0: Tự động đăng ký trạm vào Database nếu chưa có
    if not ensure_sensors_exist():
        logger.error("Không thể đăng ký trạm. Hủy khởi động Simulator.")
        return

    threads = []

    # Duyệt qua danh sách trạm và mồi mỗi trạm chạy song song trên 1 luồng độc lập
    for station in STATIONS:
        t = threading.Thread(target=simulate_station, args=(station,))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Đã ngắt Simulator an toàn bằng phím Ctrl+C.")


if __name__ == "__main__":
    main()
