import pytest
from detection.engine import check_alert_level

def test_engine_normal_behavior():
    """Kiểm tra xem hệ thống có trả về thẻ Green khi số đo bình thường (dưới Threshold) không."""
    pass

def test_engine_danger_tilt():
    """Kiểm tra có trả về thẻ Red khi độ nghiêng vọt lên 20 độ hay không."""
    pass
