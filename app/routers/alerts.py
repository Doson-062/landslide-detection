from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert, Sensor
from sqlalchemy import desc

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts(level: int = None, limit: int = 100, db: Session = Depends(get_db)):
    """
    API lấy danh sách lịch sử cảnh báo sạt lở (Mức vàng/đỏ).
    """
    query = db.query(Alert).order_by(desc(Alert.timestamp))
    
    if level:
        query = query.filter(Alert.level == level)
        
    alerts = query.limit(limit).all()
    
    # Kết hợp thêm thông tin tên trạm để hiển thị
    result = []
    for a in alerts:
        sensor = db.query(Sensor).filter(Sensor.id == a.sensor_id).first()
        result.append({
            "id": a.id,
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "sensor_id": a.sensor_id,
            "sensor_name": sensor.name if sensor else "Unknown",
            "level": a.level,
            "message": a.message,
            "is_resolved": a.is_resolved
        })
        
    return {"data": result}
