from flask import Blueprint, request, jsonify
from lib.auth import require_auth
from lib.constants import HTTP_CREATED, HTTP_NO_CONTENT
from services import section_service
from schemas.section import SectionCreate, SectionUpdate

bp = Blueprint("section", __name__, url_prefix="/api/v1/section")


@bp.route("", methods=["GET"])
@require_auth
def get_all():
    return jsonify(section_service.get_all())


@bp.route("", methods=["POST"])
@require_auth
def create():
    data = SectionCreate.model_validate(request.json)
    section = section_service.create(data)
    return jsonify(section), HTTP_CREATED


@bp.route("/<int:id>", methods=["GET"])
@require_auth
def get_by_id(id: int):
    return jsonify(section_service.get_by_id(id))


@bp.route("/<int:id>", methods=["PUT"])
@require_auth
def update(id: int):
    data = SectionUpdate.model_validate(request.json)
    return jsonify(section_service.update(id, data))


@bp.route("/<int:id>", methods=["DELETE"])
@require_auth
def delete(id: int):
    section_service.delete(id)
    return "", HTTP_NO_CONTENT
