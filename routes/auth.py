"""Đăng ký / đăng nhập / đăng xuất (YCNC 9: tài khoản lưu trong database)."""
import re
import sqlite3

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import models
from security import check_csrf

bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def safe_next(target):
    """Chỉ cho chuyển hướng tới đường dẫn nội bộ, chặn kiểu /login?next=http://web-xau.com
    (lỗi 'open redirect')."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return url_for("main.dashboard")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if g.user:
        return redirect(url_for("main.dashboard"))

    errors = []
    form = {"username": "", "email": ""}  # giữ lại để điền sẵn khi có lỗi (không giữ mật khẩu)

    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        form = {"username": username, "email": email}

        # Luôn kiểm tra ở server, dù HTML đã có required (người dùng có thể bỏ qua HTML).
        if not USERNAME_RE.match(username):
            errors.append("Tên đăng nhập gồm 3–32 ký tự: chữ, số hoặc dấu gạch dưới.")
        if not EMAIL_RE.match(email):
            errors.append("Email không hợp lệ.")
        if len(password) < 8:
            errors.append("Mật khẩu cần ít nhất 8 ký tự.")
        if password != confirm:
            errors.append("Mật khẩu nhập lại không khớp.")

        if not errors:
            if models.get_user_by_username(username):
                errors.append("Tên đăng nhập đã được dùng.")
            if models.get_user_by_email(email):
                errors.append("Email đã được dùng.")

        if not errors:
            try:
                # Chỉ lưu bản băm (hash) của mật khẩu, kèm salt ngẫu nhiên do werkzeug tạo.
                models.create_user(username, email, generate_password_hash(password))
            except sqlite3.IntegrityError:  # 2 người đăng ký cùng lúc -> UNIQUE chặn lại
                errors.append("Tên đăng nhập hoặc email đã được dùng.")
            else:
                flash("Đăng ký thành công. Hãy đăng nhập.", "success")
                return redirect(url_for("auth.login"))

    return render_template("register.html", errors=errors, form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
    if g.user:
        return redirect(url_for("main.dashboard"))

    error = None
    username = ""

    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = models.get_user_by_username(username)

        # Báo lỗi chung chung, không cho biết sai tên hay sai mật khẩu (tránh dò tài khoản).
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Sai tên đăng nhập hoặc mật khẩu."
        else:
            session.clear()  # xoá session cũ rồi mới ghi mới (chống session fixation)
            session["user_id"] = user["id"]
            return redirect(safe_next(request.args.get("next")))

    return render_template("login.html", error=error, username=username)


@bp.route("/logout", methods=("POST",))  # POST để web lạ không tự đăng xuất người dùng bằng link
def logout():
    check_csrf()
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("auth.login"))
