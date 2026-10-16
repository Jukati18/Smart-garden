"""Công cụ bảo mật dùng chung: bắt buộc đăng nhập + chống CSRF."""
import secrets
from functools import wraps

from flask import abort, g, redirect, request, session, url_for


def login_required(view):
    """Decorator: gắn vào route nào thì route đó yêu cầu đăng nhập.
    Chưa đăng nhập -> chuyển về /login và nhớ trang định vào (tham số next)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def get_csrf_token():
    """Mỗi session có 1 token ngẫu nhiên, nhúng vào mọi form POST."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


def check_csrf():
    """Gọi đầu mỗi route POST. Web lạ không biết token nên không giả mạo được form."""
    sent = request.form.get("csrf_token", "").encode()
    expected = session.get("csrf_token", "").encode()
    if not sent or not secrets.compare_digest(sent, expected):
        abort(400)
