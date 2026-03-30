"""
Module Logic Phát Hiện Bất Thường (Detection Engine).
So sánh dữ liệu đầu vào với cấu hình Ngưỡng (Threshold) từ Database.
Trả về các cấp độ: green (an toàn), yellow (nguy hiểm loại 2), red (báo động khẩn).
"""

import logging

logger = logging.getLogger("DetectionEngine")

def check_alert_level(data: dict, threshold: dict) -> tuple[str, str]:
    """
    Hàm kiểm tra rule-based trạng thái sạt lở của 1 bản ghi thời gian thực.
    
    Args:
        data (dict): Dữ liệu truyền từ cảm biến (do_nghieng, do_rung, luong_mua).
        threshold (dict): Bảng thông số Threshold lưu ở DB. (warn/danger).
    
    Returns:
        tuple (level, message): 
            - level: 'green', 'yellow', 'red'
            - message: Chuỗi giải thích lý do (hoặc rỗng nếu green).
    """
    
    # Lấy dữ liệu
    nghieng = data.get('do_nghieng')
    rung = data.get('do_rung')
    mua = data.get('luong_mua')
    
    # Điều kiện Red (Cực kỳ khẩn cấp - Bất kỳ chỉ số nào chạm danger)
    red_reasons = []
    if nghieng is not None and nghieng >= threshold.get('nghieng_danger', 20):
        red_reasons.append(f"Góc nghiêng ({nghieng}°) ≥ Nguy hiểm ({threshold.get('nghieng_danger')}°)")
    if rung is not None and rung >= threshold.get('rung_danger', 6):
        red_reasons.append(f"Độ rung ({rung} m/s²) ≥ Nguy hiểm ({threshold.get('rung_danger')} m/s²)")
    if mua is not None and mua >= threshold.get('mua_danger', 60):
        red_reasons.append(f"Lượng mưa ({mua}mm) ≥ Nguy hiểm ({threshold.get('mua_danger')}mm)")
        
    if red_reasons:
        msg = " | ".join(red_reasons)
        logger.warning(f"PHÁT HIỆN SẠT LỞ LEVEL RED: {msg}")
        return 'red', msg
        
    # Điều kiện Yellow (Cảnh báo sớm - Bất kỳ thông số nào chạm Warn)
    yellow_reasons = []
    if nghieng is not None and nghieng >= threshold.get('nghieng_warn', 10):
        yellow_reasons.append(f"Góc nghiêng ({nghieng}°) ≥ Cảnh báo ({threshold.get('nghieng_warn')}°)")
    if rung is not None and rung >= threshold.get('rung_warn', 3):
        yellow_reasons.append(f"Độ rung ({rung} m/s²) ≥ Cảnh báo ({threshold.get('rung_warn')} m/s²)")
    if mua is not None and mua >= threshold.get('mua_warn', 30):
        yellow_reasons.append(f"Lượng mưa ({mua}mm) ≥ Cảnh báo ({threshold.get('mua_warn')}mm)")
        
    if yellow_reasons:
        msg = " | ".join(yellow_reasons)
        logger.info(f"CẢNH BÁO SỚM LEVEL YELLOW: {msg}")
        return 'yellow', msg

    # Mặc định an toàn
    return 'green', "Chỉ số an toàn"
