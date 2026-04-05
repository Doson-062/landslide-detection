from fastapi import APIRouter

router = APIRouter(prefix="/api/thresholds", tags=["Thresholds"])

@router.get("/")
def get_thresholds():
    """
    API lấy các giới hạn cấu hình hiện tại (nghieng_warn, nghieng_danger...) từ Database.
    """
    return {"message": "Giới hạn Thresholds"}
