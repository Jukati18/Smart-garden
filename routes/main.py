"""Các trang sau đăng nhập: Dashboard + các trang chừa chỗ cho chức năng sau."""
from flask import Blueprint, g, redirect, render_template, url_for

from security import login_required

bp = Blueprint("main", __name__)

# Menu bên trái. Thêm/sửa trang chỉ cần sửa danh sách này (sidebar tự cập nhật).
# ready=False -> hiện nhãn "Sắp có". Khi làm xong 1 trang, đổi thành True.
NAV = [
    {"endpoint": "main.dashboard", "label": "Tổng quan", "ready": True},
    {"endpoint": "main.sensors", "label": "Cảm biến", "ready": False},          # YCNC 2
    {"endpoint": "main.notifications", "label": "Thông báo", "ready": False},   # YCNC 6
    {"endpoint": "main.history", "label": "Lịch sử", "ready": False},           # YCNC 4, 5 (thành viên khác)
    {"endpoint": "main.control", "label": "Điều khiển", "ready": False},        # YCNC 3 (thành viên khác)
    {"endpoint": "main.chatbot", "label": "Chatbot", "ready": False},           # YCNC 8 (thành viên khác)
    {"endpoint": "main.predict", "label": "Dự đoán", "ready": False},           # YCNC 11 (thành viên khác)
]


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if g.user else "auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# Trang chừa chỗ: slug -> (tiêu đề, mô tả). Ai làm tính năng nào thì thay view tương ứng
# bằng một hàm riêng + template riêng, rồi xoá mục đó khỏi dict này.
PLACEHOLDERS = {
    "sensors": ("Cảm biến", "Dữ liệu cảm biến sẽ hiện ở đây khi thiết bị gửi lên."),
    "notifications": ("Thông báo", "Cài đặt ngưỡng và xem lịch sử thông báo gửi về điện thoại."),
    "history": ("Lịch sử", "Biểu đồ dữ liệu theo thời gian."),
    "control": ("Điều khiển", "Bật tắt thiết bị từ web."),
    "chatbot": ("Chatbot", "Hỏi đáp thông tin hệ thống."),
    "predict": ("Dự đoán", "Phân tích và dự đoán từ dữ liệu cảm biến."),
}


def _register_placeholder(slug, title, desc):
    @login_required
    def view():
        return render_template("placeholder.html", title=title, desc=desc)

    # endpoint=slug nên url_for("main.sensors") hoạt động như route viết tay.
    bp.add_url_rule(f"/{slug}", endpoint=slug, view_func=view)


for _slug, (_title, _desc) in PLACEHOLDERS.items():
    _register_placeholder(_slug, _title, _desc)
