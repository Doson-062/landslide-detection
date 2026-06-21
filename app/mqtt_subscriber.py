"""
Module MQTT Subscriber — Lắng nghe dữ liệu cảm biến từ MQTT Broker.

Khi Simulator publish bản tin JSON lên topic "landslide/sensors/data",
module này sẽ tự động nhận, phân tích và lưu vào PostgreSQL.
Luồng xử lý giống hệt API POST /api/sensor-data nhưng qua giao thức MQTT.
"""

import os
import json
import time
import threading
import logging
from datetime import datetime

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Sensor, SensorData, Alert, Threshold
from detection.engine import check_alert_level

load_dotenv()
logger = logging.getLogger("MQTT.Subscriber")

# Đọc cấu hình từ biến môi trường
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "landslide/sensors/data")


def _process_sensor_message(payload: dict):
    """
    Xử lý một bản tin cảm biến nhận được từ MQTT.
    Logic tái sử dụng từ router sensors.py (receive_sensor_data).
    """
    db = SessionLocal()
    try:
        start_time = time.time()

        sensor_id = payload.get("sensor_id")
        if not sensor_id:
            logger.warning("Bản tin MQTT thiếu trường 'sensor_id', bỏ qua.")
            return

        # 1. Kiểm tra trạm cảm biến tồn tại
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not sensor:
            logger.warning(f"Trạm {sensor_id} chưa đăng ký trong DB, bỏ qua bản tin.")
            return

        # 2. Phân tích timestamp
        timestamp_str = payload.get("timestamp")
        if timestamp_str:
            try:
                ts = datetime.fromisoformat(timestamp_str)
            except ValueError:
                ts = datetime.utcnow()
        else:
            ts = datetime.utcnow()

        # 3. Lưu vào bảng sensor_data
        db_data = SensorData(
            sensor_id=sensor.id,
            do_nghieng=payload.get("do_nghieng", 0),
            do_rung=payload.get("do_rung", 0),
            luong_mua=payload.get("luong_mua", 0),
            timestamp=ts
        )
        db.add(db_data)
        db.commit()
        db.refresh(db_data)

        # 4. Lấy ngưỡng cảnh báo
        thres_db = db.query(Threshold).first()
        if not thres_db:
            thres_db = Threshold()
            db.add(thres_db)
            db.commit()
            db.refresh(thres_db)

        thres_dict = {
            'nghieng_warn': thres_db.nghieng_warn,
            'nghieng_danger': thres_db.nghieng_danger,
            'rung_warn': thres_db.rung_warn,
            'rung_danger': thres_db.rung_danger,
            'mua_warn': thres_db.mua_warn,
            'mua_danger': thres_db.mua_danger,
        }

        # 5. Chạy Detection Engine
        level, msg = check_alert_level(payload, thres_dict)

        # 6. Lưu Alert nếu vượt ngưỡng
        if level in ['yellow', 'red']:
            db_alert = Alert(
                sensor_id=sensor.id,
                level=2 if level == 'yellow' else 3,
                message=msg,
                is_resolved=False,
                timestamp=datetime.utcnow()
            )
            db.add(db_alert)
            db.commit()

            # Gửi cảnh báo Telegram
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if bot_token and chat_id:
                try:
                    import requests
                    icon = "🔴" if level == 'red' else "🟡"
                    message_text = f"{icon} CẢNH BÁO SẠT LỞ TRẠM {sensor.id} {icon}\n\nChi tiết: {msg}"
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    requests.post(url, json={"chat_id": chat_id, "text": message_text}, timeout=2)
                except Exception as e:
                    logger.error(f"Lỗi gửi Telegram: {e}")

        detect_ms = (time.time() - start_time) * 1000
        logger.info(
            f"[MQTT] {sensor_id} | Nghiêng: {payload.get('do_nghieng')}° | "
            f"Rung: {payload.get('do_rung')} | Level: {level} | "
            f"Detect: {round(detect_ms, 2)}ms"
        )

    except Exception as e:
        logger.error(f"[MQTT] Lỗi xử lý bản tin: {e}")
        db.rollback()
    finally:
        db.close()


# ==========================================
# Callback functions cho MQTT Client
# ==========================================

def _on_connect(client, userdata, flags, reason_code, properties=None):
    """Callback khi kết nối thành công tới Broker."""
    if reason_code == 0:
        logger.info(f"✅ MQTT Subscriber đã kết nối tới Broker {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe vào topic ngay khi kết nối (tự động re-subscribe nếu mất kết nối)
        client.subscribe(MQTT_TOPIC)
        logger.info(f"📡 Đang lắng nghe topic: {MQTT_TOPIC}")
    else:
        logger.error(f"❌ MQTT kết nối thất bại, mã lỗi: {reason_code}")


def _on_message(client, userdata, msg):
    """Callback khi nhận được bản tin từ Broker."""
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        _process_sensor_message(payload)
    except json.JSONDecodeError:
        logger.error(f"[MQTT] Bản tin không phải JSON hợp lệ: {msg.payload}")
    except Exception as e:
        logger.error(f"[MQTT] Lỗi khi xử lý message: {e}")


def _on_disconnect(client, userdata, flags, reason_code, properties=None):
    """Callback khi mất kết nối tới Broker."""
    logger.warning(f"⚠️ MQTT Subscriber bị ngắt kết nối (mã: {reason_code}). Đang thử kết nối lại...")


# ==========================================
# Hàm khởi động & dừng MQTT Subscriber
# ==========================================

_mqtt_client = None


def start_mqtt_subscriber():
    """
    Khởi tạo MQTT Client và chạy vòng lặp lắng nghe trong một luồng riêng (daemon thread).
    Hàm này được gọi 1 lần duy nhất khi FastAPI khởi động (lifespan).
    """
    global _mqtt_client

    _mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="landslide-fastapi-subscriber"
    )

    # Gắn các callback
    _mqtt_client.on_connect = _on_connect
    _mqtt_client.on_message = _on_message
    _mqtt_client.on_disconnect = _on_disconnect

    # Tự động reconnect khi mất kết nối (tối thiểu 1s, tối đa 30s)
    _mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        # Sử dụng connect_async để kết nối bất đồng bộ trong background thread.
        # Điều này giúp Server khởi động thành công ngay cả khi Docker Mosquitto chưa chạy,
        # và tự động kết nối lại khi Mosquitto được bật.
        _mqtt_client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=60)
        _mqtt_client.loop_start()
        logger.info(f"🚀 MQTT Subscriber đang kết nối tới {MQTT_BROKER}:{MQTT_PORT} (background)...")
    except Exception as e:
        logger.error(f"❌ Không thể cấu hình kết nối MQTT: {e}")


def stop_mqtt_subscriber():
    """Ngắt kết nối MQTT sạch sẽ khi FastAPI shutdown."""
    global _mqtt_client
    if _mqtt_client:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
        logger.info("🛑 MQTT Subscriber đã ngắt kết nối an toàn.")
