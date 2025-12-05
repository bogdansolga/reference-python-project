# Reference Python Project

A minimal Flask REST API with SQLite, Pydantic validation, and cookie-based authentication. Python port of the [Next.js reference project](../next-js-reference-project).

## Requirements

- Python 3.11+

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your-openai-api-key-here
```

The `OPENAI_API_KEY` is required for the AI chat feature.

## Running the Development Server

```bash
source venv/bin/activate
python -m src.app
```

The server starts at http://localhost:5000

## Test Credentials

- `user` / `user` (USER role)
- `admin` / `admin` (ADMIN role)

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login (sets session cookie)
- `POST /api/auth/logout` - Logout (clears cookie)

### Sections (requires auth)
- `GET /api/v1/section` - List all sections
- `POST /api/v1/section` - Create section
- `GET /api/v1/section/<id>` - Get section
- `PUT /api/v1/section/<id>` - Update section
- `DELETE /api/v1/section/<id>` - Delete section

### Products (requires auth)
- `GET /api/v1/product` - List all products
- `POST /api/v1/product` - Create product
- `GET /api/v1/product/<id>` - Get product
- `PUT /api/v1/product/<id>` - Update product
- `DELETE /api/v1/product/<id>` - Delete product

### Chat
- `POST /api/chat` - AI chat (requires `OPENAI_API_KEY` env var)

## UI Pages

- `/` - Home page
- `/login` - Login form
- `/sections` - List sections
- `/products` - List products

## Running Tests

```bash
source venv/bin/activate
pytest
```

## Project Structure

```
src/
├── app.py              # Flask app factory
├── lib/
│   ├── auth.py         # Authentication
│   ├── constants.py    # HTTP codes, config
│   ├── db.py           # SQLite + seed data
│   └── errors.py       # Custom exceptions
├── repositories/       # Data access (raw SQL)
├── routes/             # API endpoints + UI views
├── schemas/            # Pydantic models
├── services/           # Business logic
└── templates/          # Jinja2 templates
```

## Sample Data

The database seeds automatically with:
- 3 sections: Electronics, Books, Clothing
- 5 products: Laptop, Smartphone, TypeScript Handbook, Clean Code, T-Shirt
