import json
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from lib.auth import login, get_session
from lib.constants import SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS
from services import section_service, product_service

bp = Blueprint("views", __name__)


@bp.route("/")
def index():
    user = get_session()
    return render_template("index.html", user=user)


@bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = login(username, password)
        if user:
            response = make_response(redirect(url_for("views.index")))
            response.set_cookie(
                SESSION_COOKIE_NAME,
                json.dumps(user),
                httponly=True,
                max_age=SESSION_MAX_AGE_SECONDS,
            )
            return response
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout_page():
    response = make_response(redirect(url_for("views.index")))
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@bp.route("/sections")
def sections_page():
    user = get_session()
    if not user:
        return redirect(url_for("views.login_page"))
    sections = section_service.get_all()
    return render_template("sections.html", sections=sections)


@bp.route("/products")
def products_page():
    user = get_session()
    if not user:
        return redirect(url_for("views.login_page"))
    products = product_service.get_all()
    return render_template("products.html", products=products)
