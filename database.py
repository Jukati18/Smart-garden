"""Kết nối SQLite và tạo bảng"""
import os
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- 'Admin' và 'admin' coi là một
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,                        -- Không lưu mật khẩu thô
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng readings lưu MỌI lần đo của MỌI cảm biến (thiết kế tổng quát).
CREATE TABLE IF NOT EXISTS readings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,      --  Mỗi lần đo là 1 dòng riêng, id luôn tăng
    device_id   TEXT NOT NULL,                          --  Thiết bị gửi (vd "esp32-01")
    sensor_type TEXT NOT NULL,                          --  Loại cảm biến, KHÔNG hard-code (vd "soil_moisture")
    value       REAL NOT NULL,                          --  Giá trị đo (số thực)
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP --  Thời điểm ghi (giờ UTC)
);

-- index giúp tìm "mới nhất" / "N dòng gần đây" của 1 loại cảm biến mà không quét cả bảng.
CREATE INDEX IF NOT EXISTS idx_readings_type_time
    ON readings (sensor_type, created_at);
"""


def get_db():
    """Mỗi request mở 1 kết nối, lưu trong g (đối tượng sống trong 1 request)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # truy cập cột theo tên: user["username"]
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Gọi 1 lần lúc khởi động: đăng ký đóng kết nối + tạo bảng nếu chưa có."""
    app.teardown_appcontext(close_db)
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    with app.app_context():
        get_db().executescript(SCHEMA)
