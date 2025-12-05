import pytest
from pydantic import ValidationError
from schemas.product import ProductCreate, ProductUpdate, Product


def test_product_create_valid():
    data = ProductCreate(name="Laptop", price=999.99, section_id=1)
    assert data.name == "Laptop"
    assert data.price == 999.99
    assert data.section_id == 1


def test_product_create_missing_fields():
    with pytest.raises(ValidationError):
        ProductCreate(name="Laptop")


def test_product_update_all_optional():
    data = ProductUpdate()
    assert data.name is None
    assert data.price is None
    assert data.section_id is None


def test_product_full():
    data = Product(id=1, name="Laptop", price=999.99, section_id=1)
    assert data.id == 1
