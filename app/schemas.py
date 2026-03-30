"""
Module khai báo các Schemas (Pydantic Models) để validate dữ liệu đầu vào và hiển thị dữ liệu đầu ra cho FastAPI.
Giúp kiểm soát chặt chẽ kiểu type hints, cấu trúc json trả về.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ==========================================
# Schema cho API nhận dữ liệu Cảm biến (Input)
# ==========================================

class SensorDataIn(BaseModel):
    """
    Mô hình Validate dữ liệu bắn lên từ Simulator/MQTT/Hardware Device.
    Yêu cầu các trường dữ liệu quan trọng không bị trống.
    """
    sensor_id: str = Field(..., title="Mã trạm cảm biến", description="ID định danh thiết bị", example="SENSOR_01")
    do_nghieng: Optional[float] = Field(None, description="Góc độ nghiêng cảm biến", example=1.5)
    do_rung: Optional[float] = Field(None, description="Gia tốc / Độ rung cảm biến", example=0.2)
    luong_mua: Optional[float] = Field(None, description="Lượng mưa nhận được mm/h", example=10.5)
    timestamp: datetime = Field(..., description="Thời gian thu nhận bản ghi từ Hardware")

    class Config:
        orm_mode = True # Hỗ trợ serialize Object của SQLAlchemy trực tiếp


# ==========================================
# Schema cho API trả về Cảnh báo (Output)
# ==========================================

class AlertOut(BaseModel):
    """
    Mô hình Validate dữ liệu gửi trả Frontend về chi tiết Cảnh báo.
    """
    id: int = Field(..., description="ID sự kiện")
    sensor_id: Optional[str] = Field(None, description="Trạm kích hoạt")
    level: int = Field(..., description="Mức 1, 2, 3")
    message: str = Field(..., description="Chi tiết lý do")
    is_resolved: bool = Field(False, description="Tình trạng khắc phục chưa?")
    timestamp: datetime = Field(..., description="Giờ kích hoạt")

    class Config:
        orm_mode = True


# ==========================================
# Schema cho API cập nhật Ngưỡng động (Input)
# ==========================================

class ThresholdUpdate(BaseModel):
    """
    Mô hình Validate Request Body từ phía Admin khi Cập nhật thủ công cấu hình Threshold
    bằng Dashboard thay vì tệp YAML.
    """
    nghieng_warn: float = Field(..., description="Ngưỡng chú ý độ nghiêng", gt=0)
    nghieng_danger: float = Field(..., description="Ngưỡng nguy hiểm độ nghiêng", gt=0)
    
    rung_warn: float = Field(..., description="Ngưỡng chú ý độ rung", gt=0)
    rung_danger: float = Field(..., description="Ngưỡng nguy hiểm độ rung", gt=0)
    
    mua_warn: float = Field(..., description="Ngưỡng chú ý lượng mưa", gt=0)
    mua_danger: float = Field(..., description="Ngưỡng nguy hiểm lượng mưa", gt=0)
