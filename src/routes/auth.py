import json
from flask import Blueprint, request, jsonify, make_response
from lib.auth import login, get_session
from lib.constants import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/login", methods=["POST"])
def login_route():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required"}), HTTP_BAD_REQUEST

    user = login(data["username"], data["password"])
    if not user:
        return jsonify({"error": "Invalid credentials"}), HTTP_UNAUTHORIZED

    response = make_response(jsonify({"user": user}))
    response.set_cookie(
        SESSION_COOKIE_NAME,
        json.dumps(user),
        httponly=True,
        max_age=SESSION_MAX_AGE_SECONDS,
    )
    return response


@bp.route("/logout", methods=["POST"])
def logout_route():
    response = make_response(jsonify({"success": True}))
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
