from flask import Blueprint, request, jsonify
from lib.auth import require_auth
from lib.constants import HTTP_CREATED, HTTP_NO_CONTENT
from services import product_service
from schemas.product import ProductCreate, ProductUpdate

bp = Blueprint("product", __name__, url_prefix="/api/v1/product")


@bp.route("", methods=["GET"])
@require_auth
def get_all():
    return jsonify(product_service.get_all())


@bp.route("", methods=["POST"])
@require_auth
def create():
    data = ProductCreate.model_validate(request.json)
    product = product_service.create(data)
    return jsonify(product), HTTP_CREATED


@bp.route("/<int:id>", methods=["GET"])
@require_auth
def get_by_id(id: int):
    return jsonify(product_service.get_by_id(id))


@bp.route("/<int:id>", methods=["PUT"])
@require_auth
def update(id: int):
    data = ProductUpdate.model_validate(request.json)
    return jsonify(product_service.update(id, data))


@bp.route("/<int:id>", methods=["DELETE"])
@require_auth
def delete(id: int):
    product_service.delete(id)
    return "", HTTP_NO_CONTENT
