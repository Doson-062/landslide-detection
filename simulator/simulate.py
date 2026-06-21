"""
<<<<<<< Updated upstream
Module Giả Lập Trạm Cảm Biến (Simulator).
Tự động sinh dữ liệu ngẫu nhiên và gửi POST lên FastAPI Server mỗi 5 giây.
Cứ sau 5 chu kỳ sẽ tiêm 1 Anomaly (dữ liệu bất thường) để kích hoạt cảnh báo.
=======
Module Giả Lập Trạm Cảm Biến (Simulator) — Phiên bản MQTT.
Tự động sinh dữ liệu ngẫu nhiên và PUBLISH lên MQTT Broker mỗi 5 giây.
Cứ sau 5 chu kỳ sẽ tiêm 1 Anomaly (dữ liệu bất thường) để kích hoạt cảnh báo.

Giao thức: MQTT (thay thế HTTP POST cũ) — chuẩn IoT công nghiệp.
>>>>>>> Stashed changes
"""

import time
import json
import requests
import random
import threading
import logging
from datetime import datetime

import paho.mqtt.client as mqtt

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
API_URL = "http://localhost:8000/api/sensor-data"  # Vẫn giữ để đăng ký trạm qua HTTP
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "landslide/sensors/data"

ALL_STATIONS = [
    {
        "id": "STATION_03",
        "name": "Sơn La 1",
        "latitude": 21.328,
        "longitude": 103.898,
        "is_active": True,
        "simulate": True
    },
    {
        "id": "STATION_04",
        "name": "Sơn La 2",
        "latitude": 21.350,
        "longitude": 103.950,
        "is_active": True,
        "simulate": True
    },
    {
        "id": "LAI_CHAU_1",
        "name": "Lai Châu 1",
        "latitude": 22.396,
        "longitude": 103.468,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "DIEN_BIEN_1",
        "name": "Điện Biên 1",
        "latitude": 21.385,
        "longitude": 103.022,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "LAO_CAI_1",
        "name": "Lào Cai 1",
        "latitude": 22.485,
        "longitude": 103.971,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "LAO_CAI_2",
        "name": "Lào Cai 2",
        "latitude": 22.336,
        "longitude": 103.843,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "HA_GIANG_1",
        "name": "Hà Giang 1",
        "latitude": 22.823,
        "longitude": 104.982,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "HA_GIANG_2",
        "name": "Hà Giang 2",
        "latitude": 23.279,
        "longitude": 105.312,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "YEN_BAI_1",
        "name": "Yên Bái 1",
        "latitude": 21.722,
        "longitude": 104.911,
        "is_active": True,
        "simulate": False
    },
    {
        "id": "CAO_BANG_1",
        "name": "Cao Bằng 1",
        "latitude": 22.678,
        "longitude": 106.258,
        "is_active": True,
        "simulate": False
    }
]

CYCLE_DELAY = 5  # Thời gian nghỉ sau mỗi lần gửi (giây)


def ensure_sensors_exist():
    """
    Kiểm tra và tự động tạo các trạm cảm biến trong Database
    nếu chúng chưa tồn tại. Tránh lỗi 404 khi Simulator gửi data.
    """
    for station in ALL_STATIONS:
        station_id = station["id"]
        try:
            response = requests.post(
                "http://localhost:8000/api/sensors/register",
                json={
                    "id": station_id,
                    "name": station["name"],
                    "location": f"Khu vực {station['name']}",
                    "latitude": station["latitude"],
                    "longitude": station["longitude"],
                    "is_active": station["is_active"]
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


def generate_random_data(level=1):
    """
    Sinh dữ liệu ngẫu nhiên cho cảm biến dựa theo mức cảnh báo (level):
    - level=1 (Bình thường): Dưới tất cả các ngưỡng cảnh báo.
    - level=2 (Cảnh báo - Vàng): Vượt ngưỡng Chú ý (10 độ) nhưng dưới Nguy hiểm (20 độ).
    - level=3 (Nguy hiểm - Đỏ): Vượt ngưỡng Nguy hiểm (20 độ).
    """
    if level == 1:
        do_nghieng = round(random.uniform(0.0, 5.0), 2)   # Ngưỡng warn là 10
        do_rung = round(random.uniform(0.0, 1.5), 2)      # Ngưỡng warn là 3
        luong_mua = round(random.uniform(0.0, 10.0), 2)   # Ngưỡng warn là 30
    elif level == 2:
        # Kích hoạt Cảnh báo Vàng: Độ nghiêng từ 11 đến 15 (vượt 10, dưới 20)
        do_nghieng = round(random.uniform(11.0, 15.0), 2)
        do_rung = round(random.uniform(0.0, 1.5), 2)
        luong_mua = round(random.uniform(0.0, 10.0), 2)
    else:
        # Kích hoạt Cảnh báo Đỏ: Độ nghiêng vượt 21 (vượt 20)
        do_nghieng = round(random.uniform(21.0, 30.0), 2)
        do_rung = round(random.uniform(0.0, 1.5), 2)
        luong_mua = round(random.uniform(0.0, 10.0), 2)

    return {
        "do_nghieng": do_nghieng,
        "do_rung": do_rung,
        "luong_mua": luong_mua
    }


def simulate_station(sensor_id, mqtt_client):
    """
    Hàm xử lý độc lập cho từng trạm.
    Mỗi trạm sẽ như một robot riêng, liên tục thức dậy -> đo data -> publish MQTT -> ngủ 5s.
    """
    cycle_count = 0
    logger.info(f"[{sensor_id}] Bắt đầu quy trình gửi dữ liệu qua MQTT...")

    while True:
        cycle_count += 1

        # Cứ 3 chu kỳ có 1 Vàng (level 2), cứ 6 chu kỳ có 1 Đỏ (level 3)
        if cycle_count % 6 == 0:
            level = 3
            logger.warning(f"[{sensor_id}] 🔴 Dữ liệu NGUY HIỂM (Cấp 3 - Đỏ) ở chu kỳ {cycle_count}!")
        elif cycle_count % 3 == 0:
            level = 2
            logger.warning(f"[{sensor_id}] 🟡 Dữ liệu CẢNH BÁO (Cấp 2 - Vàng) ở chu kỳ {cycle_count}!")
        else:
            level = 1

        # 1. Sinh data mô phỏng (Dictionary)
        mock_data = generate_random_data(level=level)

        # 2. Đắp thêm các trường bắt buộc
        mock_data["sensor_id"] = sensor_id
        mock_data["timestamp"] = datetime.now().isoformat()

        try:
            # 3. Chuyển đổi sang JSON string và PUBLISH lên MQTT Broker
            payload = json.dumps(mock_data)
            result = mqtt_client.publish(MQTT_TOPIC, payload, qos=1)

            # 4. Kiểm tra kết quả publish
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(
                    f"[{sensor_id}] 📡 MQTT Published | Nghiêng: {mock_data['do_nghieng']}° | "
                    f"Rung: {mock_data['do_rung']} | Mưa: {mock_data['luong_mua']}mm | "
                    f"Chu kỳ: {cycle_count} | Trạng thái: {level}"
                )
            else:
                logger.error(f"[{sensor_id}] MQTT Publish thất bại, mã lỗi: {result.rc}")

        except Exception as e:
            logger.error(f"[{sensor_id}] Lỗi MQTT: {str(e)}")

        # Nằm ngủ 5 giây rồi mới lặp lại
        time.sleep(CYCLE_DELAY)


def main():
    """Hàm khởi chạy chính của Simulator — Phiên bản MQTT."""
    logger.info("=" * 55)
    logger.info("  KHỞI ĐỘNG SIMULATOR (GIAO THỨC MQTT)")
    logger.info("=" * 55)

    # Bước 0: Tự động đăng ký trạm vào Database nếu chưa có (qua HTTP)
    if not ensure_sensors_exist():
        logger.error("Không thể đăng ký trạm. Hủy khởi động Simulator.")
        return

    # Bước 1: Kết nối tới MQTT Broker
    logger.info(f"Đang kết nối tới MQTT Broker tại {MQTT_BROKER}:{MQTT_PORT}...")

    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="landslide-simulator-publisher"
    )

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info(f"✅ Simulator đã kết nối MQTT Broker thành công!")
        else:
            logger.error(f"❌ Kết nối MQTT thất bại, mã lỗi: {reason_code}")

    def on_disconnect(client, userdata, flags, reason_code, properties=None):
        logger.warning(f"⚠️ Simulator bị ngắt kết nối MQTT (mã: {reason_code})")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except ConnectionRefusedError:
        logger.error(
            f"❌ Không thể kết nối MQTT Broker tại {MQTT_BROKER}:{MQTT_PORT}.\n"
            f"   Hãy đảm bảo Docker Mosquitto đang chạy!\n"
            f"   Lệnh: docker start mosquitto"
        )
        return

    # Bắt đầu vòng lặp MQTT network (non-blocking)
    mqtt_client.loop_start()

    # Bước 2: Chạy mỗi trạm trên 1 luồng độc lập
    threads = []
    active_stations = [s for s in ALL_STATIONS if s["simulate"]]
    for station in active_stations:
        t = threading.Thread(target=simulate_station, args=(station["id"], mqtt_client))
        t.daemon = True
        t.start()
        threads.append(t)

    logger.info(f"🚀 Đã khởi động {len(active_stations)} trạm cảm biến, publish lên topic: {MQTT_TOPIC}")
    logger.info("Nhấn Ctrl+C để dừng.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("🛑 Đã ngắt Simulator và MQTT an toàn bằng phím Ctrl+C.")


if __name__ == "__main__":
    main()
