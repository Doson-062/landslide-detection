"""
Module quản lý Giao Diện Jinja2 HTML Dashboard dành cho Admin.
Trỏ tới các file trong thư mục templates/.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/admin", tags=["Admin Frontend UI"])

# Cấu hình Jinja2 trỏ về thư mục `templates` ở project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/overview", response_class=HTMLResponse)
async def admin_overview(request: Request):
    """Trang Tổng quan (Overview) hệ thống."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Tổng quan",
        "system_status": "Hoạt động (Normal)"
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Trang Dashboard hiển thị biểu đồ."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "page_title": "Trung Tâm Giám Sát",
        "system_status": "Hoạt động (Normal)"
    })

@router.get("/sensors", response_class=HTMLResponse)
async def admin_sensors(request: Request):
    """Trang quản lý các cảm biến."""
    # Sẽ cần template sensors.html
    return templates.TemplateResponse("base.html", {
        "request": request,
        "page_title": "Thiết bị Cảm biến",
        "system_status": "Hoạt động"
    })

@router.get("/alerts", response_class=HTMLResponse)
async def admin_alerts(request: Request):
    """Trang Bảng cảnh báo Alert log."""
    return templates.TemplateResponse("alerts.html", {
        "request": request,
        "page_title": "Nhật ký Cảnh báo",
        "system_status": "Hoạt động"
    })

@router.get("/thresholds", response_class=HTMLResponse)
async def admin_thresholds(request: Request):
    """Trang Cài đặt cấu hình ngưỡng."""
    # Sẽ cần template thresholds.html
    return templates.TemplateResponse("base.html", {
        "request": request,
        "page_title": "Cài đặt Ngưỡng hệ thống",
        "system_status": "Hoạt động"
    })

@router.get("/grafana", response_class=HTMLResponse)
async def admin_grafana(request: Request):
    """Trang Grafana nhúng iframe."""
    return templates.TemplateResponse("grafana.html", {
        "request": request,
        "page_title": "Phân tích Grafana",
        "system_status": "Hoạt động"
    })
