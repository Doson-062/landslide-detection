"""
Phần mềm Giám sát Sạt lở Đất (RESTful API Architecture).
Entry Point của hệ thống FastAPI (Tuần 4).
Khởi động bằng lệnh: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import logging
from app.routers import sensors, admin
from contextlib import asynccontextmanager

# Cấu hình logging global
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger("LandslideServer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup lúc Uvicorn khởi động
    logger.info("============== KHỞI ĐỘNG HỆ THỐNG =============")
    logger.info("Hệ thống phát hiện sạt lở bằng Database Threshold")
    yield
    # Cleanup lúc shutdown
    logger.info("=========== TẮT HỆ THỐNG AN TOÀN ============")

# Cấu hình API Metadata
app = FastAPI(
    title="Landslide Detection REST API",
    description="Hệ thống tiếp nhận dữ liệu sạt lở từ Simulator (POST) và xuất Dashboard HTML + JSON Alert.",
    version="3.0",
    tags=["API"],
    lifespan=lifespan
)

# Lấy đường dẫn thư mục Gốc chứa `templates/` và `static/`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH = os.path.join(BASE_DIR, "static")

# Mount thư mục Static File (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# Cài đặt Route gốc `GET /` -> Redirect về admin overview
@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url="/admin/overview")

# Gộp các Routers chia nhỏ vào Main App
# --- JSON API Routers ---
app.include_router(sensors.router)

# --- Jinja2 HTML Routers ---
app.include_router(admin.router)

# Tương lai gắn thêm alerts, thresholds API
