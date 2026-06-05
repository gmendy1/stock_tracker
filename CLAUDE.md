# CLAUDE.md — Stock Investment Tracker

## Project Overview

A FastAPI-based REST API for tracking personal stock investments. Users can register, manage multiple portfolios, and record buy/sell transactions with per-ticker analytics.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Uvicorn |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | SQLite (dev) |
| Auth | JWT via python-jose, bcrypt via passlib |
| Config | pydantic-settings |

## Project Structure

```
stock_tracker/
├── core/
│   ├── config.py          # Pydantic settings, loaded from .env
│   └── security.py        # Password hashing & JWT helpers
├── models/
│   ├── user.py            # User table + UserCreate/UserRead/UserUpdate schemas
│   ├── portfolio.py       # Portfolio table + schemas
│   └── investment.py      # Investment table + TransactionType enum + schemas
├── routers/
│   ├── deps.py            # CurrentUser & DBSession Annotated dependencies
│   ├── auth.py            # /auth/* endpoints
│   ├── portfolios.py      # /portfolios/* endpoints
│   └── investments.py     # /portfolios/{id}/investments/* endpoints
├── schemas/               # Currently unused; schemas live in models/
├── database.py            # SQLite engine + get_session() dependency
├── main.py                # App init, lifespan, CORS, router registration
├── requirements.txt
└── .env.example
```

## Running Locally

```bash
# 1. Create and activate virtualenv
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — generate a SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

# 4. Start dev server
uvicorn main:app --reload

# 5. Open API docs
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
# Health:     http://localhost:8000/health
```

## Environment Variables

Defined in `.env.example`, loaded by `core/config.py` via pydantic-settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `"Stock Investment Tracker"` | Application display name |
| `DEBUG` | `false` | Enables SQL echo logging |
| `SECRET_KEY` | *(required)* | 64-char hex string for JWT signing |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime (24 hours) |
| `DATABASE_URL` | `sqlite:///./stock_tracker.db` | SQLite file path |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/auth/me` | Yes | Get own profile |
| PUT | `/auth/me` | Yes | Update own profile |
| GET | `/portfolios/` | Yes | List user's portfolios |
| POST | `/portfolios/` | Yes | Create portfolio |
| GET | `/portfolios/{id}` | Yes | Get portfolio |
| PATCH | `/portfolios/{id}` | Yes | Update portfolio |
| DELETE | `/portfolios/{id}` | Yes | Delete portfolio + investments |
| GET | `/portfolios/{id}/investments/` | Yes | List investments (filter by ticker/type) |
| POST | `/portfolios/{id}/investments/` | Yes | Record buy/sell transaction |
| GET | `/portfolios/{id}/investments/{inv_id}` | Yes | Get investment |
| PATCH | `/portfolios/{id}/investments/{inv_id}` | Yes | Update investment |
| DELETE | `/portfolios/{id}/investments/{inv_id}` | Yes | Delete investment |
| GET | `/portfolios/{id}/investments/summary/by-ticker` | Yes | Aggregate net shares & cost basis per ticker |
| GET | `/health` | No | Health check |

## Code Conventions

### Naming
- **Router files**: plural nouns (`portfolios.py`, `investments.py`)
- **Private helpers**: underscore-prefixed (`_get_owned_portfolio`, `_assert_portfolio_ownership`)
- **Models/Schemas**: PascalCase (`UserCreate`, `InvestmentRead`, `TransactionType`)
- **DB tables**: lowercase plural (`users`, `portfolios`, `investments`)

### Patterns
- **Dual-purpose models**: SQLModel classes serve as both ORM tables and Pydantic schemas
- **Dependencies**: Use `CurrentUser` and `DBSession` type aliases from `routers/deps.py`
- **Partial updates**: Use `.model_dump(exclude_unset=True)` for PATCH endpoints
- **Ownership checks**: All portfolio/investment mutations go through `_get_owned_portfolio()` or `_assert_portfolio_ownership()` — return 404 if not found or not owned
- **Circular imports**: Use `TYPE_CHECKING` blocks and string forward references in relationships
- **Tickers**: Always uppercase on write (enforced in `investments.py`)

### HTTP Status Codes
- `201` — resource created
- `204` — deleted (no body)
- `400` — validation / uniqueness failure
- `401` — invalid or missing token
- `404` — not found or not owned (intentionally ambiguous for security)

## Data Model

```
User (1) ──< Portfolio (1) ──< Investment
```

- A user owns many portfolios.
- A portfolio contains many investments (transactions).
- Deleting a portfolio cascades to its investments.
- `Investment.total_value` is a computed property: `shares × price_per_share`.
- `TransactionType`: `BUY` or `SELL` — used in summary aggregation.

## Testing

No tests exist yet. Recommended setup:

```bash
pip install pytest httpx

# Suggested structure:
tests/
├── conftest.py           # In-memory SQLite engine, TestClient fixture
├── test_auth.py
├── test_portfolios.py
└── test_investments.py
```

Use `fastapi.testclient.TestClient` and override `get_session` dependency to point at an in-memory test DB.

## Known Gaps / Planned Work

- No real-time price fetching (yfinance / Alpha Vantage integration planned)
- No pagination on list endpoints
- CORS is open (`allow_origins=["*"]`) — restrict in production
- No email verification on registration
- No test suite
- SQLite only — switch to PostgreSQL for production
