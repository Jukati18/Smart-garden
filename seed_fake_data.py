# THÊM MỚI: script chạy riêng để chèn dữ liệu GIẢ vào bảng readings (chỉ dùng để test giao diện).
# Chạy:  python seed_fake_data.py          -> chèn 30 dòng
#        python seed_fake_data.py clear    -> xóa toàn bộ dữ liệu giả
import random
import sys
from datetime import datetime, timedelta, timezone

from app import app            # THÊM MỚI: lấy đối tượng Flask app để tạo app context
from database import get_db    # THÊM MỚI: dùng lại hàm kết nối DB của dự án

FAKE_DEVICE = "fake-esp32"     # THÊM MỚI: đặt tên thiết bị giả riêng để xóa dễ, không lẫn dữ liệu thật

# THÊM MỚI: loại cảm biến -> (giá trị nhỏ nhất, lớn nhất) hợp lý để random
SENSORS = {
    "soil_moisture": (20, 80),   # độ ẩm đất (%)
    "temperature": (24, 35),     # nhiệt độ (°C)
    "light": (200, 900),         # ánh sáng (lux)
}
ROUNDS = 10                      # THÊM MỚI: 10 lượt x 3 cảm biến = 30 dòng


def seed():
    now = datetime.now(timezone.utc)
    # THÊM MỚI: get_db() cần app context (nó dùng g và current_app) nên phải bọc trong with
    with app.app_context():
        db = get_db()
        for i in range(ROUNDS):
            # THÊM MỚI: lượt cũ nhất chèn trước, mỗi lượt cách nhau 5 phút -> id tăng theo thời gian
            minutes_ago = (ROUNDS - 1 - i) * 5
            # THÊM MỚI: cùng định dạng với CURRENT_TIMESTAMP của SQLite (giờ UTC)
            ts = (now - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
            for sensor_type, (low, high) in SENSORS.items():
                value = round(random.uniform(low, high), 1)
                db.execute(
                    "INSERT INTO readings (device_id, sensor_type, value, created_at) "
                    "VALUES (?, ?, ?, ?)",          # THÊM MỚI: vẫn dùng ? như các hàm khác
                    (FAKE_DEVICE, sensor_type, value, ts),
                )
        db.commit()
    print(f"Đã chèn {ROUNDS * len(SENSORS)} dòng dữ liệu giả.")


def clear():
    # THÊM MỚI: chỉ xóa dòng của thiết bị giả, dữ liệu thật (nếu có) được giữ nguyên
    with app.app_context():
        db = get_db()
        cur = db.execute("DELETE FROM readings WHERE device_id = ?", (FAKE_DEVICE,))
        db.commit()
    print(f"Đã xóa {cur.rowcount} dòng dữ liệu giả.")


if __name__ == "__main__":
    # THÊM MỚI: có tham số "clear" thì xóa, không thì chèn
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear()
    else:
        seed()