import os
import sqlite3
from lib.db import get_db, init_db, close_db

TEST_DB = "test_sqlite.db"


def setup_function():
    os.environ["DATABASE_PATH"] = TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def teardown_function():
    close_db()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_get_db_returns_connection():
    conn = get_db()
    assert isinstance(conn, sqlite3.Connection)


def test_init_db_creates_tables():
    init_db()
    conn = get_db()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    assert "sections" in tables
    assert "products" in tables
