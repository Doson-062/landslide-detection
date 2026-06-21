"""
Module quản lý Giao Diện Jinja2 HTML Dashboard dành cho Admin và Viewer.
Kiểm tra đăng nhập và phân quyền trước khi trả trang.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
import os

router = APIRouter(prefix="/admin", tags=["Admin Frontend UI"])

# Cấu hình Jinja2 trỏ về thư mục `templates` ở project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _check_login(request: Request, db: Session):
    """Kiểm tra user đã đăng nhập chưa. Trả về user dict hoặc None."""
    return get_current_user(request, db)


@router.get("/overview", response_class=HTMLResponse)
async def admin_overview(request: Request, db: Session = Depends(get_db)):
    """Trang Tổng quan (Overview) hệ thống - Tự do truy cập."""
    user = _check_login(request, db)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Tổng quan",
        "system_status": "Hoạt động (Normal)",
        "user": user
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Trang Dashboard hiển thị biểu đồ - Tự do truy cập."""
    user = _check_login(request, db)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "page_title": "Trung Tâm Giám Sát",
        "system_status": "Hoạt động (Normal)",
        "user": user
    })

@router.get("/sensors", response_class=HTMLResponse)
async def admin_sensors(request: Request, db: Session = Depends(get_db)):
    """Trang quản lý các cảm biến — Bắt buộc là Admin."""
    user = _check_login(request, db)
    if not user or user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("sensors.html", {
        "request": request,
        "page_title": "Thiết bị Cảm biến",
        "system_status": "Hoạt động",
        "user": user
    })

@router.get("/alerts", response_class=HTMLResponse)
async def admin_alerts(request: Request, db: Session = Depends(get_db)):
    """Trang Bảng cảnh báo Alert log - Tự do truy cập."""
    user = _check_login(request, db)
    
    return templates.TemplateResponse("alerts.html", {
        "request": request,
        "page_title": "Nhật ký Cảnh báo",
        "system_status": "Hoạt động",
        "user": user
    })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    """Trang Quản lý người dùng — Bắt buộc là Admin."""
    user = _check_login(request, db)
    if not user or user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "page_title": "Quản lý Tài khoản",
        "system_status": "Hoạt động",
        "user": user
    })

@router.get("/thresholds", response_class=HTMLResponse)
async def admin_thresholds(request: Request, db: Session = Depends(get_db)):
    """Trang Cài đặt cấu hình ngưỡng — Bắt buộc là Admin."""
    user = _check_login(request, db)
    if not user or user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("thresholds.html", {
        "request": request,
        "page_title": "Cài đặt Ngưỡng hệ thống",
        "system_status": "Hoạt động",
        "user": user
    })


@router.get("/map", response_class=HTMLResponse)
async def admin_map(request: Request, db: Session = Depends(get_db)):
    """Trang Bản đồ số trực quan - Tự do truy cập."""
    user = _check_login(request, db)
    
    return templates.TemplateResponse("map.html", {
        "request": request,
        "page_title": "Bản đồ Giám sát",
        "system_status": "Hoạt động",
        "user": user
    })
