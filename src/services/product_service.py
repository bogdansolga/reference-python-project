# src/services/product_service.py
from repositories import section_repository, product_repository
from schemas.product import ProductCreate, ProductUpdate
from lib.errors import NotFoundError


def get_all() -> list[dict]:
    return product_repository.find_all()


def get_by_id(id: int) -> dict:
    product = product_repository.find_by_id(id)
    if product is None:
        raise NotFoundError(f"Product {id} not found")
    return product


def create(data: ProductCreate) -> dict:
    section = section_repository.find_by_id(data.section_id)
    if section is None:
        raise NotFoundError(f"Section {data.section_id} not found")
    return product_repository.create(data.name, data.price, data.section_id)


def update(id: int, data: ProductUpdate) -> dict:
    product = product_repository.find_by_id(id)
    if product is None:
        raise NotFoundError(f"Product {id} not found")
    if data.section_id is not None:
        section = section_repository.find_by_id(data.section_id)
        if section is None:
            raise NotFoundError(f"Section {data.section_id} not found")
    return product_repository.update(
        id,
        name=data.name,
        price=data.price,
        section_id=data.section_id,
    )


def delete(id: int) -> None:
    product = product_repository.find_by_id(id)
    if product is None:
        raise NotFoundError(f"Product {id} not found")
    product_repository.delete(id)
