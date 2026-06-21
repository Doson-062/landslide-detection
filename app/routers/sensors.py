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
from datetime import datetime, timedelta
from sqlalchemy import func
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


@router.get("/api/stats", tags=["Dashboard"], summary="Lấy thống kê tổng hợp cho trang Tổng quan.")
def get_system_stats(db: Session = Depends(get_db)):
    """Trả về số lượng trạm, cảnh báo hôm nay và mức độ rủi ro."""
    total_sensors = db.query(Sensor).count()
    
    # Cảnh báo trong 24h qua
    yesterday = datetime.utcnow() - timedelta(days=1)
    today_alerts = db.query(Alert).filter(Alert.timestamp >= yesterday).count()
    
    # Mức độ rủi ro (Dựa trên alert cao nhất chưa resolved)
    latest_danger = db.query(Alert).filter(Alert.level == 3, Alert.is_resolved == False).first()
    risk_text = "Cao" if latest_danger else "Thấp"
    risk_class = "text-danger" if latest_danger else "text-success"
    
    return {
        "total_sensors": total_sensors,
        "today_alerts": today_alerts,
        "risk_level": risk_text,
        "risk_class": risk_class
    }

@router.post("/api/sensors/register", tags=["Sensors"], summary="Đăng ký trạm cảm biến mới vào hệ thống.")
def register_sensor(sensor_data: dict, db: Session = Depends(get_db)):
    """
    Tạo mới 1 trạm cảm biến trong Database.
    Nếu trạm đã tồn tại (trùng ID), trả về 409 Conflict.
    """
    sensor_id = sensor_data.get("id")
    if not sensor_id:
        raise HTTPException(status_code=400, detail="Thiếu trường 'id' cho trạm cảm biến.")

    # Kiểm tra trùng lặp và cập nhật nếu có thay đổi cấu hình
    existing = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if existing:
        existing.name = sensor_data.get("name", existing.name)
        existing.location = sensor_data.get("location", existing.location)
        existing.latitude = sensor_data.get("latitude", existing.latitude)
        existing.longitude = sensor_data.get("longitude", existing.longitude)
        existing.is_active = sensor_data.get("is_active", existing.is_active)
        db.commit()
        logger.info(f"Đã cập nhật cấu hình trạm: {sensor_id}")
        return {"status": "updated", "sensor_id": existing.id}

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

@router.delete("/api/sensors/{sensor_id}", tags=["Sensors"], summary="Xóa trạm cảm biến và các dữ liệu liên quan.")
def delete_sensor(sensor_id: str, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Không tìm thấy trạm cảm biến.")
    
    # Xóa dữ liệu liên quan
    db.query(Alert).filter(Alert.sensor_id == sensor_id).delete(synchronize_session=False)
    db.query(SensorData).filter(SensorData.sensor_id == sensor_id).delete(synchronize_session=False)
    db.delete(sensor)
    db.commit()
    logger.info(f"Đã xóa trạm cảm biến và các dữ liệu liên quan: {sensor_id}")
    return {"status": "deleted", "sensor_id": sensor_id}


@router.get("/api/sensors", tags=["Sensors"], summary="Lấy danh sách trạm và trạng thái hiện tại phục vụ Bản đồ.")
def get_sensors_status(db: Session = Depends(get_db)):
    """
    Trả về danh sách toàn bộ trạm kèm theo tọa độ và trạng thái màu sắc.
    """
    sensors = db.query(Sensor).all()
    
    # Lấy ngưỡng mặc định để so sánh
    thres_db = db.query(Threshold).first()
    if not thres_db:
        thres_db = Threshold()
    
    thres_dict = {
        'nghieng_warn': thres_db.nghieng_warn,
        'nghieng_danger': thres_db.nghieng_danger,
        'rung_warn': thres_db.rung_warn,
        'rung_danger': thres_db.rung_danger,
        'mua_warn': thres_db.mua_warn,
        'mua_danger': thres_db.mua_danger,
    }

    from sqlalchemy import desc
    result = []
    for s in sensors:
        # Lấy bản ghi dữ liệu mới nhất
        last_data = db.query(SensorData).filter(SensorData.sensor_id == s.id).order_by(desc(SensorData.timestamp)).first()
        
        status = "green"
        data_values = {}
        
        if last_data:
            data_values = {
                "do_nghieng": last_data.do_nghieng,
                "do_rung": last_data.do_rung,
                "luong_mua": last_data.luong_mua
            }
            status, _ = check_alert_level(data_values, thres_dict)

        result.append({
            "id": s.id,
            "name": s.name,
            "location": s.location,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "status": status,
            "last_data": data_values,
            "last_seen": last_data.timestamp.isoformat() if last_data else None
        })
        
    return {"data": result}

