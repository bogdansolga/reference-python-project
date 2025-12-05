# tests/services/test_product_service.py
import pytest
from unittest.mock import patch
from services import product_service
from schemas.product import ProductCreate, ProductUpdate
from lib.errors import NotFoundError


@patch("services.product_service.product_repository")
def test_get_all_returns_products(mock_repo):
    mock_repo.find_all.return_value = [{"id": 1, "name": "Laptop", "price": 999.99, "section_id": 1}]
    result = product_service.get_all()
    assert len(result) == 1
    assert result[0]["name"] == "Laptop"


@patch("services.product_service.product_repository")
def test_get_by_id_returns_product(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Laptop", "price": 999.99, "section_id": 1}
    result = product_service.get_by_id(1)
    assert result["name"] == "Laptop"


@patch("services.product_service.product_repository")
def test_get_by_id_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        product_service.get_by_id(999)


@patch("services.product_service.product_repository")
@patch("services.product_service.section_repository")
def test_create_returns_new_product(mock_section_repo, mock_product_repo):
    mock_section_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    mock_product_repo.create.return_value = {"id": 1, "name": "Laptop", "price": 999.99, "section_id": 1}
    result = product_service.create(ProductCreate(name="Laptop", price=999.99, section_id=1))
    assert result["name"] == "Laptop"


@patch("services.product_service.product_repository")
@patch("services.product_service.section_repository")
def test_create_invalid_section_raises(mock_section_repo, mock_product_repo):
    mock_section_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        product_service.create(ProductCreate(name="Laptop", price=999.99, section_id=999))


@patch("services.product_service.product_repository")
@patch("services.product_service.section_repository")
def test_update_returns_updated_product(mock_section_repo, mock_product_repo):
    mock_product_repo.find_by_id.return_value = {"id": 1, "name": "Laptop", "price": 999.99, "section_id": 1}
    mock_product_repo.update.return_value = {"id": 1, "name": "MacBook", "price": 1299.99, "section_id": 1}
    result = product_service.update(1, ProductUpdate(name="MacBook", price=1299.99))
    assert result["name"] == "MacBook"


@patch("services.product_service.product_repository")
def test_update_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        product_service.update(999, ProductUpdate(name="MacBook"))


@patch("services.product_service.product_repository")
def test_delete_calls_repository(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Laptop", "price": 999.99, "section_id": 1}
    product_service.delete(1)
    mock_repo.delete.assert_called_once_with(1)


@patch("services.product_service.product_repository")
def test_delete_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        product_service.delete(999)
