---
description: Chạy và ghi lại kết quả 4 kịch bản test kiểm định
---

# Kịch bản Test 4 Tình huống sạt lở

Khi bắt đầu Workflow này, cần chạy và ghi lại kết quả 4 kịch bản bắt buộc qua Simulator:

- **Kịch bản 1:** Inject data bình thường → Expect `green`, xác nhận không có Alert sinh ra trong DB.
- **Kịch bản 2:** Inject data vượt ngưỡng vàng → Expect `yellow`, xác nhận Telegram gọi logic gửi tin nhắn cảnh báo sớm.
- **Kịch bản 3:** Inject data vượt ngưỡng đỏ → Expect `red`, Telegram gửi tin nhắn báo động cực kỳ nguy hiểm (khẩn cấp).
- **Kịch bản 4:** Admin thực hiện đổi cấu hình ngưỡng (ThresholdUpdate) → Kiểm tra ngưỡng mới hoạt động đúng trên logic dò xét ở Kịch bản 1,2,3.

**Bộ phận Tracking & Đo lường:**
- Phải đo được thời gian phát hiện từ lúc nhận req (ms) với từng kịch bản.
- Lưu lại logs kết quả kiểm định tự động vào bảng bảng `test_results` sử dụng SQLAlchemy Data Model: `{scenario_name, expected_level, actual_level, passed, detect_time_ms}`.
- Kết thúc Workflow, In ra terminal Console một Bảng tổng kết trạng thái Pass/Fail rõ ràng cho người dùng rà soát.
