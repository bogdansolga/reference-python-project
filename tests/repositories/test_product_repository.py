import os
import pytest
from lib.db import get_db, init_db, close_db
from repositories import section_repository, product_repository

TEST_DB = "test_sqlite.db"


def setup_function():
    os.environ["DATABASE_PATH"] = TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db()
    section_repository.create("Electronics")


def teardown_function():
    close_db()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_find_all_empty():
    result = product_repository.find_all()
    assert result == []


def test_create_returns_product():
    result = product_repository.create("Laptop", 999.99, 1)
    assert result["id"] == 1
    assert result["name"] == "Laptop"
    assert result["price"] == 999.99
    assert result["section_id"] == 1


def test_find_by_id_returns_product():
    product_repository.create("Laptop", 999.99, 1)
    result = product_repository.find_by_id(1)
    assert result["name"] == "Laptop"


def test_find_by_id_not_found():
    result = product_repository.find_by_id(999)
    assert result is None


def test_update_returns_updated():
    product_repository.create("Laptop", 999.99, 1)
    result = product_repository.update(1, name="MacBook", price=1299.99)
    assert result["name"] == "MacBook"
    assert result["price"] == 1299.99


def test_delete_removes_product():
    product_repository.create("Laptop", 999.99, 1)
    product_repository.delete(1)
    result = product_repository.find_by_id(1)
    assert result is None
