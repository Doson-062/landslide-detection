"""
Module cấu hình RESTful Routers cho Sensor.
Thực hiện các API Endpoint liên quan đến việc tạo/đọc/lưu dữ liệu Thiết bị cảm biến và gửi POST Simulator.
"""

import time
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Sensor, SensorData, Alert, Threshold
from app.schemas import SensorDataIn
from detection.engine import check_alert_level
from datetime import datetime
import logging

logger = logging.getLogger("Router.Sensors")
router = APIRouter()

@router.post("/api/sensor-data", tags=["Simulator"], summary="API nhận dữ liệu từ Simulator mô phỏng sạt lở.")
def receive_sensor_data(data: SensorDataIn, db: Session = Depends(get_db)):
    """
    Lưu trữ dữ liệu giả lập/thực tế từ cảm biến vào Database.
    Quá trình: Lưu SensorData -> Chạy logic Detection Engine -> Lưu Alert nếu bất thường.
    """
    start_time = time.time()
    
    # 1. Kiểm tra Sensor tồn tại chưa, nếu chưa có thể bỏ qua hoặc báo lỗi
    sensor = db.query(Sensor).filter(Sensor.id == data.sensor_id).first()
    if not sensor:
        # Tạm thời cho phép bypass hoặc tự tạo rỗng nếu workflow test-scenario gọi mà chưa config DB? 
        # Hoặc throw lỗi
        raise HTTPException(status_code=404, detail="Trạm cảm biến không tồn tại trong hệ thống. Hãy tạo trước.")
        
    # 2. Đổ vào Database bảng sensor_data
    db_data = SensorData(
        sensor_id=sensor.id,
        do_nghieng=data.do_nghieng,
        do_rung=data.do_rung,
        luong_mua=data.luong_mua,
        timestamp=data.timestamp
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    # 3. Kéo bộ Ngưỡng cài đặt của Cảm biến này
    # Lấy ID Threshold cao nhất (Mới nhất) hoặc Threshold default
    # Tạm thời query record threshold đầu tiên (Trong SKILL.md ghi Threshold ko khoá ngoại, nên xài record ID=1 chung)
    thres_db = db.query(Threshold).first()
    if not thres_db:
        # Nếu DB trống, tạo mốc default
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
    
    # 4. Chạy Detection Engine
    level, msg = check_alert_level(data.dict(), thres_dict)
    
    # 5. Lưu vào bảng Alerts nếu khác Green
    if level in ['yellow', 'red']:
        db_alert = Alert(
            sensor_id=sensor.id,
            level=2 if level == 'yellow' else 3,  # Map Int Level (1: green, 2: yellow, 3: red)
            message=msg,
            is_resolved=False,
            timestamp=datetime.utcnow()
        )
        db.add(db_alert)
        db.commit()
        
        # Gửi Telegram Alert
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if bot_token and chat_id:
            try:
                import requests
                # Dùng cờ cảnh báo (icon) để làm màu mè bản tin telegram
                icon = "🔴" if level == 'red' else "🟡"
                message_text = f"{icon} CẢNH BÁO SẠT LỞ TRẠM {sensor.id} {icon}\n\nChi tiết: {msg}"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                # Đặt timeout ngắn (2 giây) tránh làm lag Cổng API chính
                requests.post(url, json={"chat_id": chat_id, "text": message_text}, timeout=2)
            except Exception as e:
                logger.error(f"Lỗi khi gửi Telegram: {e}")

    detect_time_ms = (time.time() - start_time) * 1000
    
    return {
        "status": "success", 
        "sensor_data_id": db_data.id,
        "detection_level": level,
        "detect_time_ms": round(detect_time_ms, 2)
    }

@router.get("/api/sensor-data/latest", tags=["Dashboard"], summary="Lấy 100 bản ghi mới nhất hiển thị.")
def get_latest_data(sensor_id: str = None, limit: int = 100, db: Session = Depends(get_db)):
    """Trả JSON 100 data point mới nhất để hiển thị ra Chart.js."""
    query = db.query(SensorData).order_by(SensorData.timestamp.desc())
    if sensor_id:
         query = query.filter(SensorData.sensor_id == sensor_id)
         
    records = query.limit(limit).all()
    return {"data": records}


@router.post("/api/sensors/register", tags=["Sensors"], summary="Đăng ký trạm cảm biến mới vào hệ thống.")
def register_sensor(sensor_data: dict, db: Session = Depends(get_db)):
    """
    Tạo mới 1 trạm cảm biến trong Database.
    Nếu trạm đã tồn tại (trùng ID), trả về 409 Conflict.
    """
    sensor_id = sensor_data.get("id")
    if not sensor_id:
        raise HTTPException(status_code=400, detail="Thiếu trường 'id' cho trạm cảm biến.")

    # Kiểm tra trùng lặp
    existing = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if existing:
        return {"status": "exists", "detail": f"Trạm {sensor_id} đã tồn tại."}

    # Tạo mới
    new_sensor = Sensor(
        id=sensor_id,
        name=sensor_data.get("name", sensor_id),
        location=sensor_data.get("location", "Chưa xác định"),
        latitude=sensor_data.get("latitude"),
        longitude=sensor_data.get("longitude"),
        is_active=sensor_data.get("is_active", True)
    )
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)

    logger.info(f"Đã đăng ký trạm mới: {sensor_id}")
    return {"status": "created", "sensor_id": new_sensor.id}

