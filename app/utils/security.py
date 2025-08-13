import os
import hmac
import secrets
from hashlib import sha256
from flask import request, session, abort


def get_admin_password_hash() -> bytes:
    password = os.getenv('ADMIN_PASSWORD', '')
    return sha256(password.encode('utf-8')).digest()


def check_admin_password(password: str) -> bool:
    expected = get_admin_password_hash()
    attempt = sha256(password.encode('utf-8')).digest()
    return hmac.compare_digest(expected, attempt)


def ensure_csrf_token() -> str:
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token


def validate_csrf() -> None:
    token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    if not token or token != session.get('csrf_token'):
        abort(400, description='Invalid CSRF token')
