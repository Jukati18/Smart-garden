"""Các hàm truy vấn bảng users.
Luôn dùng dấu ? và truyền tham số riêng -> chống SQL Injection."""
from database import get_db


def create_user(username, email, password_hash):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    db.commit()


def get_user_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(username):
    return get_db().execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def get_user_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

#  Ghi 1 lần đo = 1 dòng MỚI (INSERT, không UPDATE) để giữ lịch sử cho biểu đồ.
def add_reading(device_id, sensor_type, value):
    db = get_db()
    db.execute(
        "INSERT INTO readings (device_id, sensor_type, value) VALUES (?, ?, ?)",
        (device_id, sensor_type, value),  #  tham số truyền riêng -> chống SQL Injection
    )
    db.commit()


#  Lấy giá trị MỚI NHẤT của TỪNG sensor_type (mỗi loại đúng 1 dòng).
def get_latest_readings():
    return get_db().execute(
        """
        SELECT r.*
        FROM readings r
        JOIN (SELECT sensor_type, MAX(id) AS max_id
              FROM readings
              GROUP BY sensor_type) m
          ON r.id = m.max_id
        ORDER BY r.sensor_type
        """
    ).fetchall()


#  Lấy tối đa `limit` lần đo gần nhất của 1 loại cảm biến (mới -> cũ).
def get_recent_readings(sensor_type, limit=50):
    limit = max(1, min(int(limit), 1000))  #  Ép về số nguyên 1..1000, tránh truy vấn quá lớn
    return get_db().execute(
        "SELECT * FROM readings WHERE sensor_type = ? "
        "ORDER BY created_at DESC, id DESC LIMIT ?",
        (sensor_type, limit),  #  Cả sensor_type và limit đều truyền bằng dấu ?
    ).fetchall()