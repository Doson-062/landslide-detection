from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Threshold
from fastapi.responses import RedirectResponse
import logging

logger = logging.getLogger("Router.Thresholds")
router = APIRouter(prefix="/api/thresholds", tags=["Thresholds"])

@router.get("/")
def get_thresholds(db: Session = Depends(get_db)):
    """
    API lấy các giới hạn cấu hình hiện tại từ Database.
    """
    thres = db.query(Threshold).first()
    if not thres:
        # Tạo mặc định nếu chưa có
        thres = Threshold()
        db.add(thres)
        db.commit()
        db.refresh(thres)
    return thres

@router.post("/")
async def update_thresholds(
    request: Request,
    nghieng_warn: float = Form(...),
    nghieng_danger: float = Form(...),
    rung_warn: float = Form(...),
    rung_danger: float = Form(...),
    mua_warn: float = Form(...),
    mua_danger: float = Form(...),
    db: Session = Depends(get_db)
):
    """
    API cập nhật cấu hình ngưỡng mới từ Form.
    """
    thres = db.query(Threshold).first()
    if not thres:
        thres = Threshold()
        db.add(thres)
    
    thres.nghieng_warn = nghieng_warn
    thres.nghieng_danger = nghieng_danger
    thres.rung_warn = rung_warn
    thres.rung_danger = rung_danger
    thres.mua_warn = mua_warn
    thres.mua_danger = mua_danger
    
    db.commit()
    logger.info("Admin đã cập nhật cấu hình Ngưỡng mới.")
    
    return RedirectResponse(url="/admin/thresholds?success=1", status_code=302)
