# Stock Investment Tracker API

A FastAPI SaaS skeleton for tracking personal stock investments.
Uses **SQLModel** as the ORM, **SQLite** as the datastore, and **JWT Bearer tokens** for auth.

---

## Project structure

```
stock_tracker/
├── core/
│   ├── config.py        # App settings (pydantic-settings)
│   └── security.py      # Password hashing & JWT helpers
├── models/
│   ├── user.py          # User table + schemas
│   ├── portfolio.py     # Portfolio table + schemas
│   └── investment.py    # Investment table + schemas
├── routers/
│   ├── deps.py          # Shared FastAPI dependencies
│   ├── auth.py          # /auth  — register, login, me
│   ├── portfolios.py    # /portfolios  — CRUD
│   └── investments.py   # /portfolios/{id}/investments  — CRUD + summary
├── database.py          # Engine, session factory
├── main.py              # FastAPI app + lifespan
├── requirements.txt
└── .env.example
```

---

## Quickstart

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — at minimum change SECRET_KEY

# 4. Start the server
uvicorn main:app --reload
```

Then visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Auth flow

| Step | Endpoint | Notes |
|------|----------|-------|
| Register | `POST /auth/register` | JSON body `{email, username, password}` |
| Login | `POST /auth/login` | Form body `username` + `password` → returns JWT |
| Use token | All protected routes | `Authorization: Bearer <token>` header |
| Profile | `GET /auth/me` | Returns current user info |

---

## API overview

### Portfolios
| Method | Path | Description |
|--------|------|-------------|
| GET | `/portfolios/` | List your portfolios |
| POST | `/portfolios/` | Create a portfolio |
| GET | `/portfolios/{id}` | Get one portfolio |
| PATCH | `/portfolios/{id}` | Update a portfolio |
| DELETE | `/portfolios/{id}` | Delete a portfolio |

### Investments
| Method | Path | Description |
|--------|------|-------------|
| GET | `/portfolios/{id}/investments/` | List investments (filterable by ticker & type) |
| POST | `/portfolios/{id}/investments/` | Record a buy/sell |
| GET | `/portfolios/{id}/investments/{inv_id}` | Get one investment |
| PATCH | `/portfolios/{id}/investments/{inv_id}` | Update an investment |
| DELETE | `/portfolios/{id}/investments/{inv_id}` | Delete an investment |
| GET | `/portfolios/{id}/investments/summary/by-ticker` | Net shares + cost basis per ticker |

---

## Next steps / ideas

- Add a price-fetch job (yfinance / Alpha Vantage) to get real-time portfolio value
- Add pagination to list endpoints
- Switch to PostgreSQL for production
- Add rate limiting middleware
- Add email verification on registration
- Write pytest test suite (use `TestClient` from `fastapi.testclient`)
```
