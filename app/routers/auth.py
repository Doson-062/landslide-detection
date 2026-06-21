"""
Module xử lý Đăng nhập / Đăng xuất và Phân quyền người dùng.
Sử dụng Cookie-based Session để lưu trạng thái đăng nhập.
"""

import hashlib
import logging
import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

logger = logging.getLogger("Router.Auth")
router = APIRouter(tags=["Authentication"])

# Cấu hình Jinja2 trỏ về thư mục templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def hash_password(password: str) -> str:
    """Mã hóa mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_default_users(db: Session):
    """
    Tạo 1 tài khoản mặc định khi hệ thống khởi động lần đầu:
    - admin / admin123 (quyền admin)
    """
    defaults = [
        {"username": "admin", "password": "admin123", "role": "admin"},
    ]
    for user_info in defaults:
        existing = db.query(User).filter(User.username == user_info["username"]).first()
        if not existing:
            new_user = User(
                username=user_info["username"],
                password_hash=hash_password(user_info["password"]),
                role=user_info["role"]
            )
            db.add(new_user)
            logger.info(f"Tạo tài khoản mặc định: {user_info['username']} ({user_info['role']})")
    db.commit()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Lấy thông tin user hiện tại từ session cookie.
    Trả về dict {'username': ..., 'role': ...} hoặc None nếu chưa đăng nhập.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return {"id": user.id, "username": user.username, "role": user.role}


def require_login(request: Request, db: Session = Depends(get_db)):
    """
    Dependency kiểm tra đã đăng nhập chưa.
    Nếu chưa → redirect về trang login.
    """
    user = get_current_user(request, db)
    if not user:
        return None
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    """
    Dependency kiểm tra quyền admin.
    Trả về user nếu là admin, None nếu không.
    """
    user = get_current_user(request, db)
    if not user or user["role"] != "admin":
        return None
    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Hiển thị trang đăng nhập."""
    # Nếu đã đăng nhập rồi thì chuyển thẳng về tổng quan
    if request.session.get("user_id"):
        return RedirectResponse(url="/admin/overview", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Xử lý đăng nhập: kiểm tra username + password."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user or user.password_hash != hash_password(password):
        logger.warning(f"Đăng nhập thất bại: {username}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Tên đăng nhập hoặc mật khẩu không đúng!"
        })
    
    # Lưu thông tin vào session cookie
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    
    logger.info(f"Đăng nhập thành công: {username} ({user.role})")
    return RedirectResponse(url="/admin/overview", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    """Đăng xuất: xóa session cookie."""
    username = request.session.get("username", "unknown")
    request.session.clear()
    logger.info(f"Đăng xuất: {username}")
    return RedirectResponse(url="/login", status_code=302)

@router.get("/api/users", tags=["Users"])
def get_users(admin_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """API lấy danh sách người dùng. Chỉ Admin mới sử dụng được."""
    if not admin_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền truy cập.")
    users = db.query(User).all()
    return {"data": [{"id": u.id, "username": u.username, "role": u.role} for u in users]}

@router.post("/api/users", tags=["Users"])
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """API tạo tài khoản quản trị mới. Mặc định là admin."""
    admin_user = get_current_user(request, db)
    if not admin_user or admin_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền truy cập.")

    # Kiểm tra xem user đã tồn tại chưa
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return RedirectResponse(url="/admin/users?error=Tên đăng nhập đã tồn tại", status_code=302)

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role="admin"
    )
    db.add(new_user)
    db.commit()
    logger.info(f"Admin '{admin_user['username']}' đã tạo tài khoản Admin mới: {username}")
    
    return RedirectResponse(url="/admin/users?success=1", status_code=302)
