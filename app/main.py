"""
Phần mềm Giám sát Sạt lở Đất (RESTful API + MQTT Architecture).
Entry Point của hệ thống FastAPI.
Khởi động bằng lệnh: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os
import logging
from dotenv import load_dotenv
from app.routers import sensors, admin, alerts, thresholds, auth
from app.database import SessionLocal
from app.routers.auth import create_default_users
from app.mqtt_subscriber import start_mqtt_subscriber, stop_mqtt_subscriber
from contextlib import asynccontextmanager

# Nạp cấu hình từ file .env
load_dotenv()


# Cấu hình logging global
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger("LandslideServer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Xử lý khởi động và tắt hệ thống."""
    logger.info("============== KHỞI ĐỘNG HỆ THỐNG ==============")
    logger.info("Hệ thống phát hiện sạt lở bằng Database Threshold + MQTT")
    
    # Tạo tài khoản mặc định (admin/viewer) nếu chưa có
    db = SessionLocal()
    try:
        create_default_users(db)
    finally:
        db.close()
    
    # Khởi động MQTT Subscriber (lắng nghe dữ liệu cảm biến qua giao thức MQTT)
    start_mqtt_subscriber()
    
    yield
    # Cleanup lúc shutdown
    stop_mqtt_subscriber()
    logger.info("=========== TẮT HỆ THỐNG AN TOÀN ==============")

# Cấu hình API Metadata
app = FastAPI(
    title="Landslide Detection REST API",
    description="Hệ thống tiếp nhận dữ liệu sạt lở từ Simulator qua MQTT/REST API và xuất Dashboard HTML + JSON Alert.",
    version="3.0",
    tags=["API"],
    lifespan=lifespan
)

# Thêm Session Middleware để hỗ trợ đăng nhập bằng cookie
# SECRET_KEY dùng để mã hóa cookie session
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "landslide-secret-key-2025")
)

# Lấy đường dẫn thư mục Gốc chứa `templates/` và `static/`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH = os.path.join(BASE_DIR, "static")

# Mount thư mục Static File (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# Cài đặt Route gốc `GET /` -> Redirect về trang login hoặc overview
@app.get("/", include_in_schema=False)
async def read_root():
    """Chuyển hướng trang gốc về tổng quan."""
    return RedirectResponse(url="/admin/overview")

# Gộp các Routers chia nhỏ vào Main App
# --- Authentication Router ---
app.include_router(auth.router)

# --- JSON API Routers ---
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(thresholds.router)

# --- Jinja2 HTML Routers ---
app.include_router(admin.router)
