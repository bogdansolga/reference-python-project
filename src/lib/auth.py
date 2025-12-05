import json
from functools import wraps
from flask import request, jsonify, make_response
from lib.constants import SESSION_COOKIE_NAME, HTTP_UNAUTHORIZED

USERS = {
    "user": {"id": 1, "username": "user", "password": "user", "role": "USER"},
    "admin": {"id": 2, "username": "admin", "password": "admin", "role": "ADMIN"},
}


def login(username: str, password: str) -> dict | None:
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def get_session() -> dict | None:
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie:
        try:
            return json.loads(cookie)
        except json.JSONDecodeError:
            return None
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_session():
            return jsonify({"error": "Unauthorized"}), HTTP_UNAUTHORIZED
        return f(*args, **kwargs)
    return decorated
