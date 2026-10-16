"""Cấu hình chung. Flask đọc các biến VIẾT HOA qua app.config.from_object(config)."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Khoá dùng để ký cookie session. Khi deploy PHẢI đặt biến môi trường SECRET_KEY.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

# File SQLite nằm trong thư mục instance/ (đã bị .gitignore, không push lên GitHub).
DATABASE = os.path.join(BASE_DIR, "instance", "garden.db")

# Cookie chỉ gửi kèm request cùng site và JavaScript không đọc được.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
