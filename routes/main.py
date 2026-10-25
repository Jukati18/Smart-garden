"""Các trang sau đăng nhập: Dashboard + các trang chừa chỗ cho chức năng sau."""
from datetime import datetime, timedelta  # Đổi giờ UTC -> giờ Việt Nam

from flask import Blueprint, g, jsonify, redirect, render_template, url_for  # Thêm jsonify

import models  # Để gọi models.get_latest_readings()
from security import login_required

bp = Blueprint("main", __name__)

# Menu bên trái. Thêm/sửa trang chỉ cần sửa danh sách này (sidebar tự cập nhật).
# ready=False -> hiện nhãn "Sắp có". Khi làm xong 1 trang, đổi thành True.
NAV = [
    {"endpoint": "main.dashboard", "label": "Tổng quan", "ready": True},
    {"endpoint": "main.sensors", "label": "Cảm biến", "ready": True},           # False -> True (YCNC 2)
    {"endpoint": "main.notifications", "label": "Thông báo", "ready": False},   # YCNC 6
    {"endpoint": "main.history", "label": "Lịch sử", "ready": False},           # YCNC 4, 5 (thành viên khác)
    {"endpoint": "main.control", "label": "Điều khiển", "ready": False},        # YCNC 3 (thành viên khác)
    {"endpoint": "main.chatbot", "label": "Chatbot", "ready": False},           # YCNC 8 (thành viên khác)
    {"endpoint": "main.predict", "label": "Dự đoán", "ready": False},           # YCNC 11 (thành viên khác)
]

# Tên hiển thị + đơn vị (TÙY CHỌN). Loại cảm biến không có trong dict vẫn hiện bình thường
# bằng chính sensor_type, nên thêm cảm biến mới KHÔNG bắt buộc sửa chỗ này.
SENSOR_META = {
    "soil_moisture": {"label": "Độ ẩm đất", "unit": "%"},
    "temperature": {"label": "Nhiệt độ", "unit": "°C"},
    "light": {"label": "Ánh sáng", "unit": "lux"},
}


# Created_at trong DB là giờ UTC, cộng 7 tiếng để hiển thị giờ Việt Nam.
def _to_local(created_at):
    utc = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    return (utc + timedelta(hours=7)).strftime("%H:%M:%S %d/%m/%Y")


# Đổi các dòng sqlite3.Row thành list dict thuần.
# Dùng chung cho trang HTML và API JSON, vì sqlite3.Row không tự chuyển thành JSON được.
def _latest_for_view():
    result = []
    for row in models.get_latest_readings():
        meta = SENSOR_META.get(row["sensor_type"], {})
        result.append({
            "sensor_type": row["sensor_type"],
            "label": meta.get("label", row["sensor_type"]),  # không có tên đẹp thì dùng sensor_type
            "value": round(row["value"], 1),
            "unit": meta.get("unit", ""),
            "device_id": row["device_id"],
            "created_at": _to_local(row["created_at"]),
        })
    return result


@bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if g.user else "auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# Trang Cảm biến thật (YCNC 2: input -> web frontend). Endpoint tự đặt tên là "main.sensors".
@bp.route("/sensors")
@login_required
def sensors():
    # Server render sẵn lần đầu để trang có nội dung ngay, JS chỉ lo cập nhật sau đó
    return render_template("sensors.html", readings=_latest_for_view())


# API JSON cho JavaScript gọi mỗi 5 giây.
@bp.route("/api/sensors/latest")
@login_required
def api_sensors_latest():
    return jsonify(_latest_for_view())


# Trang chừa chỗ: slug -> (tiêu đề, mô tả). Ai làm tính năng nào thì thay view tương ứng
# bằng một hàm riêng + template riêng, rồi xoá mục đó khỏi dict này.
PLACEHOLDERS = {
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