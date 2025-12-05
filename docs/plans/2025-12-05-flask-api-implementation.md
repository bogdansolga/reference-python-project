# Flask REST API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replicate the Next.js reference project as a minimal Flask REST API with SQLite, Pydantic validation, and OpenAI chat.

**Architecture:** Layered architecture (Routes → Services → Repositories → Database) with cookie-based auth, raw SQL queries, and Pydantic validation. Each layer has single responsibility.

**Tech Stack:** Flask, SQLite, Pydantic, OpenAI SDK, pytest

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "reference-python-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0",
    "pydantic>=2.0",
    "openai>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Step 2: Create src/__init__.py**

```python
```

**Step 3: Install dependencies**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed flask, pydantic, openai, pytest

**Step 4: Commit**

```bash
git init
git add pyproject.toml src/__init__.py
git commit -m "chore: initial project setup with dependencies"
```

---

## Task 2: Constants Module

**Files:**
- Create: `src/lib/__init__.py`
- Create: `src/lib/constants.py`

**Step 1: Create lib package**

```python
# src/lib/__init__.py
```

**Step 2: Create constants**

```python
# src/lib/constants.py

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Auth
SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE_SECONDS = 86400  # 24 hours

# Database
DATABASE_PATH = "sqlite.db"
```

**Step 3: Commit**

```bash
git add src/lib/
git commit -m "feat: add constants module"
```

---

## Task 3: Custom Errors

**Files:**
- Create: `src/lib/errors.py`
- Create: `tests/__init__.py`
- Create: `tests/lib/__init__.py`
- Create: `tests/lib/test_errors.py`

**Step 1: Write the failing test**

```python
# tests/lib/test_errors.py
from lib.errors import NotFoundError, ValidationError


def test_not_found_error_has_message():
    error = NotFoundError("Product 1 not found")
    assert error.message == "Product 1 not found"


def test_not_found_error_default_message():
    error = NotFoundError()
    assert error.message == "Resource not found"


def test_validation_error_has_message_and_details():
    error = ValidationError("Invalid input", details=["name required"])
    assert error.message == "Invalid input"
    assert error.details == ["name required"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/lib/test_errors.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/lib/errors.py


class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)
```

**Step 4: Create test package files**

```python
# tests/__init__.py
```

```python
# tests/lib/__init__.py
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/lib/test_errors.py -v`
Expected: 3 passed

**Step 6: Commit**

```bash
git add src/lib/errors.py tests/
git commit -m "feat: add custom error classes"
```

---

## Task 4: Database Module

**Files:**
- Create: `src/lib/db.py`
- Create: `tests/lib/test_db.py`

**Step 1: Write the failing test**

```python
# tests/lib/test_db.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/lib/test_db.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/lib/db.py
import os
import sqlite3

_connection: sqlite3.Connection | None = None


def get_db() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = os.environ.get("DATABASE_PATH", "sqlite.db")
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection


def close_db() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def init_db() -> None:
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            section_id INTEGER NOT NULL REFERENCES sections(id)
        );
        """
    )
    conn.commit()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/lib/test_db.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add src/lib/db.py tests/lib/test_db.py
git commit -m "feat: add database module with SQLite"
```

---

## Task 5: Pydantic Types

**Files:**
- Create: `src/types/__init__.py`
- Create: `src/types/section.py`
- Create: `src/types/product.py`
- Create: `tests/types/__init__.py`
- Create: `tests/types/test_section.py`
- Create: `tests/types/test_product.py`

**Step 1: Write failing tests for section types**

```python
# tests/types/test_section.py
import pytest
from pydantic import ValidationError
from types.section import SectionCreate, SectionUpdate, Section


def test_section_create_valid():
    data = SectionCreate(name="Electronics")
    assert data.name == "Electronics"


def test_section_create_missing_name():
    with pytest.raises(ValidationError):
        SectionCreate()


def test_section_update_optional_name():
    data = SectionUpdate()
    assert data.name is None


def test_section_full():
    data = Section(id=1, name="Electronics")
    assert data.id == 1
    assert data.name == "Electronics"
```

**Step 2: Write failing tests for product types**

```python
# tests/types/test_product.py
import pytest
from pydantic import ValidationError
from types.product import ProductCreate, ProductUpdate, Product


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
```

**Step 3: Run tests to verify they fail**

Run: `pytest tests/types/ -v`
Expected: FAIL with ModuleNotFoundError

**Step 4: Write section types**

```python
# src/types/__init__.py
```

```python
# src/types/section.py
from pydantic import BaseModel


class SectionCreate(BaseModel):
    name: str


class SectionUpdate(BaseModel):
    name: str | None = None


class Section(BaseModel):
    id: int
    name: str
```

**Step 5: Write product types**

```python
# src/types/product.py
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    section_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    section_id: int | None = None


class Product(BaseModel):
    id: int
    name: str
    price: float
    section_id: int
```

**Step 6: Create test package file**

```python
# tests/types/__init__.py
```

**Step 7: Run tests to verify they pass**

Run: `pytest tests/types/ -v`
Expected: 8 passed

**Step 8: Commit**

```bash
git add src/types/ tests/types/
git commit -m "feat: add Pydantic schemas for section and product"
```

---

## Task 6: Section Repository

**Files:**
- Create: `src/repositories/__init__.py`
- Create: `src/repositories/section_repository.py`
- Create: `tests/repositories/__init__.py`
- Create: `tests/repositories/test_section_repository.py`

**Step 1: Write failing tests**

```python
# tests/repositories/test_section_repository.py
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
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/repositories/test_section_repository.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/repositories/__init__.py
```

```python
# src/repositories/section_repository.py
from lib.db import get_db


def _row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return dict(row)


def find_all() -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT * FROM sections").fetchall()
    return [dict(row) for row in rows]


def find_by_id(id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM sections WHERE id = ?", (id,)).fetchone()
    return _row_to_dict(row)


def create(name: str) -> dict:
    db = get_db()
    cursor = db.execute("INSERT INTO sections (name) VALUES (?)", (name,))
    db.commit()
    return find_by_id(cursor.lastrowid)


def update(id: int, name: str) -> dict | None:
    db = get_db()
    db.execute("UPDATE sections SET name = ? WHERE id = ?", (name, id))
    db.commit()
    return find_by_id(id)


def delete(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM sections WHERE id = ?", (id,))
    db.commit()
```

**Step 4: Create test package file**

```python
# tests/repositories/__init__.py
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/repositories/test_section_repository.py -v`
Expected: 6 passed

**Step 6: Commit**

```bash
git add src/repositories/ tests/repositories/
git commit -m "feat: add section repository with CRUD operations"
```

---

## Task 7: Product Repository

**Files:**
- Create: `src/repositories/product_repository.py`
- Create: `tests/repositories/test_product_repository.py`

**Step 1: Write failing tests**

```python
# tests/repositories/test_product_repository.py
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
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/repositories/test_product_repository.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/repositories/product_repository.py
from lib.db import get_db


def _row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return dict(row)


def find_all() -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT * FROM products").fetchall()
    return [dict(row) for row in rows]


def find_by_id(id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    return _row_to_dict(row)


def create(name: str, price: float, section_id: int) -> dict:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name, price, section_id) VALUES (?, ?, ?)",
        (name, price, section_id),
    )
    db.commit()
    return find_by_id(cursor.lastrowid)


def update(
    id: int,
    name: str | None = None,
    price: float | None = None,
    section_id: int | None = None,
) -> dict | None:
    db = get_db()
    current = find_by_id(id)
    if current is None:
        return None
    new_name = name if name is not None else current["name"]
    new_price = price if price is not None else current["price"]
    new_section_id = section_id if section_id is not None else current["section_id"]
    db.execute(
        "UPDATE products SET name = ?, price = ?, section_id = ? WHERE id = ?",
        (new_name, new_price, new_section_id, id),
    )
    db.commit()
    return find_by_id(id)


def delete(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (id,))
    db.commit()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/repositories/test_product_repository.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add src/repositories/product_repository.py tests/repositories/test_product_repository.py
git commit -m "feat: add product repository with CRUD operations"
```

---

## Task 8: Section Service

**Files:**
- Create: `src/services/__init__.py`
- Create: `src/services/section_service.py`
- Create: `tests/services/__init__.py`
- Create: `tests/services/test_section_service.py`

**Step 1: Write failing tests**

```python
# tests/services/test_section_service.py
import pytest
from unittest.mock import patch, MagicMock
from services import section_service
from types.section import SectionCreate, SectionUpdate
from lib.errors import NotFoundError


@patch("services.section_service.section_repository")
def test_get_all_returns_sections(mock_repo):
    mock_repo.find_all.return_value = [{"id": 1, "name": "Electronics"}]
    result = section_service.get_all()
    assert len(result) == 1
    assert result[0]["name"] == "Electronics"


@patch("services.section_service.section_repository")
def test_get_by_id_returns_section(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    result = section_service.get_by_id(1)
    assert result["name"] == "Electronics"


@patch("services.section_service.section_repository")
def test_get_by_id_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.get_by_id(999)


@patch("services.section_service.section_repository")
def test_create_returns_new_section(mock_repo):
    mock_repo.create.return_value = {"id": 1, "name": "Books"}
    result = section_service.create(SectionCreate(name="Books"))
    assert result["name"] == "Books"
    mock_repo.create.assert_called_once_with("Books")


@patch("services.section_service.section_repository")
def test_update_returns_updated_section(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    mock_repo.update.return_value = {"id": 1, "name": "Tech"}
    result = section_service.update(1, SectionUpdate(name="Tech"))
    assert result["name"] == "Tech"


@patch("services.section_service.section_repository")
def test_update_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.update(999, SectionUpdate(name="Tech"))


@patch("services.section_service.section_repository")
def test_delete_calls_repository(mock_repo):
    mock_repo.find_by_id.return_value = {"id": 1, "name": "Electronics"}
    section_service.delete(1)
    mock_repo.delete.assert_called_once_with(1)


@patch("services.section_service.section_repository")
def test_delete_not_found_raises(mock_repo):
    mock_repo.find_by_id.return_value = None
    with pytest.raises(NotFoundError):
        section_service.delete(999)
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/services/test_section_service.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/services/__init__.py
```

```python
# src/services/section_service.py
from repositories import section_repository
from types.section import SectionCreate, SectionUpdate
from lib.errors import NotFoundError


def get_all() -> list[dict]:
    return section_repository.find_all()


def get_by_id(id: int) -> dict:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    return section


def create(data: SectionCreate) -> dict:
    return section_repository.create(data.name)


def update(id: int, data: SectionUpdate) -> dict:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    if data.name is not None:
        return section_repository.update(id, data.name)
    return section


def delete(id: int) -> None:
    section = section_repository.find_by_id(id)
    if section is None:
        raise NotFoundError(f"Section {id} not found")
    section_repository.delete(id)
```

**Step 4: Create test package file**

```python
# tests/services/__init__.py
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/services/test_section_service.py -v`
Expected: 8 passed

**Step 6: Commit**

```bash
git add src/services/ tests/services/
git commit -m "feat: add section service with business logic"
```

---

## Task 9: Product Service

**Files:**
- Create: `src/services/product_service.py`
- Create: `tests/services/test_product_service.py`

**Step 1: Write failing tests**

```python
# tests/services/test_product_service.py
import pytest
from unittest.mock import patch
from services import product_service
from types.product import ProductCreate, ProductUpdate
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
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/services/test_product_service.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/services/product_service.py
from repositories import section_repository, product_repository
from types.product import ProductCreate, ProductUpdate
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
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/services/test_product_service.py -v`
Expected: 9 passed

**Step 5: Commit**

```bash
git add src/services/product_service.py tests/services/test_product_service.py
git commit -m "feat: add product service with business logic"
```

---

## Task 10: Auth Module

**Files:**
- Create: `src/lib/auth.py`
- Create: `tests/lib/test_auth.py`

**Step 1: Write failing tests**

```python
# tests/lib/test_auth.py
from lib.auth import login, USERS


def test_login_valid_user():
    result = login("user", "user")
    assert result is not None
    assert result["username"] == "user"
    assert result["role"] == "USER"
    assert "password" not in result


def test_login_valid_admin():
    result = login("admin", "admin")
    assert result is not None
    assert result["username"] == "admin"
    assert result["role"] == "ADMIN"


def test_login_invalid_password():
    result = login("user", "wrong")
    assert result is None


def test_login_invalid_username():
    result = login("unknown", "password")
    assert result is None
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_auth.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write implementation**

```python
# src/lib/auth.py
import json
from functools import wraps
from flask import request, jsonify, make_response
from lib.constants import SESSION_COOKIE_NAME, HTTP_UNAUTHORIZED

USERS = {
    "user": {"id": 1, "username": "user", "password": "user", "role": "USER"},
    "admin": {"id": 2, "username": "admin", "password": "admin", "role": "ADMIN"},
}


def login(username: str, password: str) -> dict | None:
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def get_session() -> dict | None:
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie:
        try:
            return json.loads(cookie)
        except json.JSONDecodeError:
            return None
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_session():
            return jsonify({"error": "Unauthorized"}), HTTP_UNAUTHORIZED
        return f(*args, **kwargs)
    return decorated
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/lib/test_auth.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add src/lib/auth.py tests/lib/test_auth.py
git commit -m "feat: add authentication module"
```

---

## Task 11: Flask App with Error Handlers

**Files:**
- Create: `src/app.py`

**Step 1: Write Flask app**

```python
# src/app.py
from flask import Flask, jsonify
from pydantic import ValidationError as PydanticValidationError
from lib.db import init_db, close_db
from lib.errors import NotFoundError
from lib.constants import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR


def create_app() -> Flask:
    app = Flask(__name__)

    # Initialize database
    with app.app_context():
        init_db()

    # Register error handlers
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": e.message}), HTTP_NOT_FOUND

    @app.errorhandler(PydanticValidationError)
    def handle_validation(e):
        return jsonify({"error": "Validation failed", "details": e.errors()}), HTTP_BAD_REQUEST

    @app.errorhandler(Exception)
    def handle_generic(e):
        return jsonify({"error": "Internal server error"}), HTTP_INTERNAL_ERROR

    # Register blueprints (will add in next tasks)
    from routes.auth import bp as auth_bp
    from routes.section import bp as section_bp
    from routes.product import bp as product_bp
    from routes.chat import bp as chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(section_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chat_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

**Step 2: Commit (will complete after routes)**

Note: This file depends on routes we'll create in the next tasks.

---

## Task 12: Auth Routes

**Files:**
- Create: `src/routes/__init__.py`
- Create: `src/routes/auth.py`

**Step 1: Write auth routes**

```python
# src/routes/__init__.py
```

```python
# src/routes/auth.py
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
```

**Step 2: Commit**

```bash
git add src/routes/
git commit -m "feat: add auth routes for login/logout"
```

---

## Task 13: Section Routes

**Files:**
- Create: `src/routes/section.py`

**Step 1: Write section routes**

```python
# src/routes/section.py
from flask import Blueprint, request, jsonify
from lib.auth import require_auth
from lib.constants import HTTP_CREATED, HTTP_NO_CONTENT
from services import section_service
from types.section import SectionCreate, SectionUpdate

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
```

**Step 2: Commit**

```bash
git add src/routes/section.py
git commit -m "feat: add section CRUD routes"
```

---

## Task 14: Product Routes

**Files:**
- Create: `src/routes/product.py`

**Step 1: Write product routes**

```python
# src/routes/product.py
from flask import Blueprint, request, jsonify
from lib.auth import require_auth
from lib.constants import HTTP_CREATED, HTTP_NO_CONTENT
from services import product_service
from types.product import ProductCreate, ProductUpdate

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
```

**Step 2: Commit**

```bash
git add src/routes/product.py
git commit -m "feat: add product CRUD routes"
```

---

## Task 15: Chat Route

**Files:**
- Create: `src/routes/chat.py`

**Step 1: Write chat route**

```python
# src/routes/chat.py
import os
from flask import Blueprint, request, Response, jsonify
from openai import OpenAI
from lib.constants import HTTP_BAD_REQUEST

bp = Blueprint("chat", __name__, url_prefix="/api/chat")

SYSTEM_PROMPT = """You are a helpful assistant for a product management system.
You can help users understand and manage their products and sections."""


@bp.route("", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", []) if data else []

    if not messages:
        return jsonify({"error": "Messages required"}), HTTP_BAD_REQUEST

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "OpenAI API key not configured"}), HTTP_BAD_REQUEST

    client = OpenAI(api_key=api_key)

    def generate():
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(generate(), mimetype="text/plain")
```

**Step 2: Commit**

```bash
git add src/routes/chat.py
git commit -m "feat: add AI chat route with OpenAI streaming"
```

---

## Task 16: Final Integration and App Commit

**Step 1: Commit app.py**

```bash
git add src/app.py
git commit -m "feat: add Flask app with error handlers and blueprint registration"
```

**Step 2: Run all tests**

Run: `pytest -v`
Expected: All tests pass (30+ tests)

**Step 3: Test manually**

Run: `python -m src.app`

Test login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user"}' \
  -c cookies.txt
```

Test create section:
```bash
curl -X POST http://localhost:5000/api/v1/section \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics"}' \
  -b cookies.txt
```

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: complete Flask REST API implementation"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Project setup | - |
| 2 | Constants module | - |
| 3 | Custom errors | 3 |
| 4 | Database module | 2 |
| 5 | Pydantic types | 8 |
| 6 | Section repository | 6 |
| 7 | Product repository | 6 |
| 8 | Section service | 8 |
| 9 | Product service | 9 |
| 10 | Auth module | 4 |
| 11-16 | Routes & App | - |

**Total: ~46 tests**
