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
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

The AI chat feature runs on Claude. Use a direct `ANTHROPIC_API_KEY` for local
demos, or route through **Claude on Vertex AI** (set `ANTHROPIC_VERTEX_PROJECT_ID`
+ `CLOUD_ML_REGION`, authenticate with `gcloud auth application-default login` —
no API key needed). Override the model with `CHAT_MODEL`. See `.env.example`.

## Running the Development Server

```bash
source venv/bin/activate
python -m src.app
```

The server starts at http://localhost:8000

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
- `POST /api/chat` - AI chat, powered by Claude (direct `ANTHROPIC_API_KEY`, or Claude on Vertex AI)

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

## Deploy to Kubernetes

A minimal manifest set lives in [`k8s/`](k8s/) — Namespace, ConfigMap, Secret
(template), Deployment, Service, and a Traefik Ingress. The container runs
**gunicorn** binding `0.0.0.0:8000` (Flask's `app.run()` binds localhost, which is
unreachable in a pod).

```bash
# build + push (multi-arch)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t <registry>/reference-python-project:1.0 --push .

# namespace + non-secret objects
kubectl apply -f k8s/

# the API key is NOT committed — create the Secret out-of-band:
kubectl -n reference-python create secret generic app-secrets \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-...

kubectl -n reference-python rollout status deployment/reference-python
```

The Ingress uses `ingressClassName: traefik` (k3s default). SQLite is ephemeral
(auto-seeds on boot); add a PVC + `DATABASE_PATH` to persist. See
`k8s/11-secret.example.yaml`.

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
