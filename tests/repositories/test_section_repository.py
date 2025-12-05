import os
import pytest
from lib.db import get_db, init_db, close_db
from repositories import section_repository

TEST_DB = "test_sqlite.db"


def setup_function():
    os.environ["DATABASE_PATH"] = TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db()


def teardown_function():
    close_db()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_find_all_empty():
    result = section_repository.find_all()
    assert result == []


def test_create_returns_section():
    result = section_repository.create("Electronics")
    assert result["id"] == 1
    assert result["name"] == "Electronics"


def test_find_by_id_returns_section():
    section_repository.create("Electronics")
    result = section_repository.find_by_id(1)
    assert result["name"] == "Electronics"


def test_find_by_id_not_found():
    result = section_repository.find_by_id(999)
    assert result is None


def test_update_returns_updated():
    section_repository.create("Electronics")
    result = section_repository.update(1, "Tech")
    assert result["name"] == "Tech"


def test_delete_removes_section():
    section_repository.create("Electronics")
    section_repository.delete(1)
    result = section_repository.find_by_id(1)
    assert result is None
