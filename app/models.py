"""
Module định nghĩa cấu trúc các bảng trong Cơ sở dữ liệu bằng SQLAlchemy ORM.
Bao gồm 5 bảng: Sensor, SensorData, Alert, Threshold, TestResult.
Chạy file này trực tiếp sẽ thực hiện lệnh tạo bảng tự động.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime

# Import đối tượng Base và engine từ module database mới tạo
from app.database import Base, engine


class Sensor(Base):
    """
    Bảng lưu trữ thông tin về các trạm cảm biến vật lý.
    """
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, index=True, comment="Mã ID trạm cảm biến (VD: SENSOR_01)")
    name = Column(String, index=True, comment="Tên gợi nhớ của trạm")
    location = Column(String, comment="Mô tả vị trí địa lý lắp đặt trạm")
    latitude = Column(Float, nullable=True, comment="Vĩ độ")
    longitude = Column(Float, nullable=True, comment="Kinh độ")
    is_active = Column(Boolean, default=True, comment="Trạng thái hhoạt động của trạm")

    # Mối quan hệ với các bảng khác để truy vấn join tự động
    data_records = relationship("SensorData", back_populates="sensor")
    alerts = relationship("Alert", back_populates="sensor")


class SensorData(Base):
    """
    Bảng lưu trữ lịch sử dữ liệu thu thập được từ cảm biến (Time-series data).
    """
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), index=True, nullable=False)
    
    do_nghieng = Column(Float, nullable=True, comment="Góc nghiêng đo được (tilt_angle)")
    do_rung = Column(Float, nullable=True, comment="Độ rung/Gia tốc đo được (vibration)")
    luong_mua = Column(Float, nullable=True, comment="Lượng mưa đo được (rainfall)")
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True, comment="Thời gian ghi nhận bản ghi")

    # Liên kết ngược (back population)
    sensor = relationship("Sensor", back_populates="data_records")


class Alert(Base):
    """
    Bảng lưu trữ nhật ký các cảnh báo được sinh ra bởi hệ thống.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), index=True, nullable=True)
    
    level = Column(Integer, nullable=False, comment="Mức độ cảnh báo: 1 (Warning), 2 (Alert), 3 (Critical)")
    message = Column(Text, nullable=False, comment="Nội dung/Lý do kích hoạt cảnh báo")
    is_resolved = Column(Boolean, default=False, comment="Cờ đánh dấu sự cố đã được con người ghi nhận và khắc phục")
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True, comment="Thời gian phát sinh cảnh báo")

    # Liên kết ngược
    sensor = relationship("Sensor", back_populates="alerts")


class Threshold(Base):
    """
    Bảng lưu trữ cấu hình ngưỡng động cho hệ thống cảnh báo, cho phép Admin chỉnh sửa realtime
    thay vì phải phụ thuộc vào file yaml tĩnh hoàn toàn.
    """
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    nghieng_warn = Column(Float, nullable=False, default=5.0, comment="Ngưỡng nghiêng mức chú ý")
    nghieng_danger = Column(Float, nullable=False, default=15.0, comment="Ngưỡng nghiêng mức nguy hiểm")
    
    rung_warn = Column(Float, nullable=False, default=0.5, comment="Ngưỡng rung mức chú ý")
    rung_danger = Column(Float, nullable=False, default=2.0, comment="Ngưỡng rung mức nguy hiểm")
    
    mua_warn = Column(Float, nullable=False, default=30.0, comment="Ngưỡng mưa mức chú ý (mm/h)")
    mua_danger = Column(Float, nullable=False, default=80.0, comment="Ngưỡng mưa mức nguy hiểm (mm/h)")


class TestResult(Base):
    """
    Bảng lưu trữ phân tích và kết quả kiểm thử (Unit test/Simulation).
    Lưu vết các kịch bản thực nghiệm từ lúc bắt đầu cho đến lúc phát cảnh báo.
    """
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scenario_name = Column(String, index=True, nullable=False, comment="Tên kịch bản (VD: landslide_spiking_rain)")
    input_data = Column(Text, nullable=True, comment="Dữ liệu cảm biến đầu vào dạng JSON String")
    
    expected_level = Column(Integer, nullable=False, comment="Level cảnh báo kỳ vọng theo rule (ground truth)")
    actual_level = Column(Integer, nullable=False, comment="Level cảnh báo thực tế mà hệ thống đã Detect ra được")
    
    detect_time_ms = Column(Float, nullable=True, comment="Thời gian hệ thống mất để xử lý bản ghi này (ms)")
    passed = Column(Boolean, nullable=False, comment="Passed (true) nếu expected == actual")
    
    tested_at = Column(DateTime, default=datetime.datetime.utcnow, comment="Thời gian chạy bài kiểm thử")

# Gọi lệnh tạo tất cả các bảng khai báo ở trên vào Database
# Hàm này an toàn và sẽ không xóa bảng nếu bảng đã tồn tại
Base.metadata.create_all(bind=engine)
