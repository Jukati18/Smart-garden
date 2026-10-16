# Smart Garden - Web

Website quản lý vườn thông minh (đồ án Vật lý cho CNTT). Hiện có: layout chung, đăng ký/đăng nhập, dashboard, các trang chừa chỗ.

## Chạy thử
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py                # mở http://127.0.0.1:5000
```
Database SQLite tự tạo ở `instance/garden.db` lần chạy đầu. Khi deploy, đặt biến môi trường `SECRET_KEY`.

## Cấu trúc
- `app.py`: khởi động, nạp user cho mỗi request
- `config.py`, `database.py`, `models.py`, `security.py`: cấu hình, DB, truy vấn user, đăng nhập + CSRF
- `routes/auth.py`: đăng ký, đăng nhập, đăng xuất
- `routes/main.py`: dashboard, menu (`NAV`), trang chừa chỗ (`PLACEHOLDERS`)
- `templates/`: `base.html` (khung HTML) -> `layout.html` (sidebar sau đăng nhập) -> từng trang
- `static/css/style.css`: giao diện

## Thêm tính năng mới
1. Tạo route trong `routes/` và template kế thừa `layout.html`.
2. Xoá mục tương ứng khỏi `PLACEHOLDERS`, đổi `ready` thành `True` trong `NAV`.
3. Route cần đăng nhập thì gắn `@login_required`.
