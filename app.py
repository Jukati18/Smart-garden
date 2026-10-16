"""Điểm khởi động. Chạy: python app.py"""
from flask import Flask, g, session

import config
import database
import models
from routes import auth, main
from security import get_csrf_token


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    database.init_app(app)

    @app.before_request
    def load_user():
        """Chạy trước MỌI request: đọc user_id trong session rồi nạp user vào g.user.
        Nhờ vậy template và route nào cũng dùng được g.user (None nếu chưa đăng nhập)."""
        user_id = session.get("user_id")
        g.user = models.get_user_by_id(user_id) if user_id else None

    @app.context_processor
    def inject_globals():
        """Biến dùng được trong mọi template mà không cần truyền thủ công."""
        return {"csrf_token": get_csrf_token, "nav_items": main.NAV}

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # debug=True chỉ dùng khi phát triển
