# Flask REST API Design

Replication of the Next.js reference project in Python using minimal dependencies.

## Stack

- **Framework**: Flask
- **Database**: SQLite (raw SQL, no ORM)
- **Validation**: Pydantic
- **AI**: OpenAI SDK
- **Testing**: pytest

## Project Structure

```
src/
├── app.py                    # Flask app initialization
├── routes/
│   ├── auth.py              # Login/logout endpoints
│   ├── section.py           # Section CRUD
│   ├── product.py           # Product CRUD
│   └── chat.py              # AI chat endpoint
├── services/
│   ├── section_service.py
│   └── product_service.py
├── repositories/
│   ├── section_repository.py
│   └── product_repository.py
├── lib/
│   ├── db.py                # SQLite connection
│   ├── auth.py              # Cookie-based auth
│   ├── errors.py            # Custom exceptions
│   └── constants.py         # HTTP codes, config values
└── types/
    ├── section.py           # Pydantic schemas
    └── product.py           # Pydantic schemas

tests/
└── services/
    ├── test_section_service.py
    └── test_product_service.py
```

## Database Schema

```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    section_id INTEGER NOT NULL REFERENCES sections(id)
);
```

## Constants

```python
# lib/constants.py

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
```

## API Endpoints

### Authentication (Public)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Login, sets session cookie |
| POST | `/api/auth/logout` | Logout, clears cookie |

### Sections (Protected)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/section` | List all sections |
| POST | `/api/v1/section` | Create section |
| GET | `/api/v1/section/<id>` | Get section by ID |
| PUT | `/api/v1/section/<id>` | Update section |
| DELETE | `/api/v1/section/<id>` | Delete section |

### Products (Protected)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/product` | List all products |
| POST | `/api/v1/product` | Create product |
| GET | `/api/v1/product/<id>` | Get product by ID |
| PUT | `/api/v1/product/<id>` | Update product |
| DELETE | `/api/v1/product/<id>` | Delete product |

### Chat (Public)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Streaming AI chat |

## Authentication

- Cookie-based sessions (httpOnly, 24-hour expiry)
- Hardcoded test users:
  - `user/user` (USER role)
  - `admin/admin` (ADMIN role)
- `@require_auth` decorator for protected routes

## Validation

Pydantic schemas for all input:

```python
# Section
class SectionCreate(BaseModel):
    name: str

class SectionUpdate(BaseModel):
    name: str | None = None

# Product
class ProductCreate(BaseModel):
    name: str
    price: float
    section_id: int

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    section_id: int | None = None
```

## Error Handling

Custom exceptions mapped to HTTP status codes:

| Exception | HTTP Status |
|-----------|-------------|
| `NotFoundError` | 404 |
| `PydanticValidationError` | 400 |
| `Exception` (generic) | 500 |

## Testing

- pytest with `unittest.mock.patch`
- Services tested with mocked repositories
- Same pattern as source project's Vitest tests

## Dependencies

```
flask
pydantic
openai
pytest
```
