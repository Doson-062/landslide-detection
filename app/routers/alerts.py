from fastapi import APIRouter

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts():
    """
    API lấy danh sách lịch sử cảnh báo sạt lở (Mức vàng/đỏ).
    (Chuẩn bị logic lấy từ Database sau này)
    """
    return {"message": "Dach sách Alerts sẽ được hiển thị tại đây"}
