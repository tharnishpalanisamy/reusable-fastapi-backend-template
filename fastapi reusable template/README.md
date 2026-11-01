# FastAPI Starter

An async FastAPI foundation with PostgreSQL, SQLAlchemy 2, Alembic, JWT access tokens, opaque rotating refresh tokens, Argon2 password hashing, RBAC, request logging, and a small test setup.

## Architecture

Request handling follows **Router → Service → Repository → Database**. Routers translate HTTP requests and responses; services own business decisions; repositories contain SQLAlchemy queries; models define persistence; schemas define validated API data. Add a new API version under `app/api/v2` without changing v1.

## Structure

```text
app/                 API, core configuration/security, database, models,
                     schemas, repositories, services, dependencies, middleware
alembic/             Migration environment and revision templates
tests/               Async HTTP tests
.env.example         Local configuration template
```

## Stack

Python 3.12+, FastAPI, PostgreSQL/asyncpg, SQLAlchemy 2 async, Pydantic v2 and Settings, Alembic, PyJWT, pwdlib Argon2, pytest, httpx, Ruff.

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a private random `JWT_SECRET` in `.env`. Production startup requires a 32-character secret, `DEBUG=false`, and explicit CORS origins. Configure `DATABASE_URL` with `postgresql+asyncpg://...`. Create the PostgreSQL database (for example `fastapi_starter`) before migrating.

## Migrations

```powershell
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Model modules are imported by `app.models` for Alembic metadata discovery. The application never creates schema at startup.

## Run

```powershell
uvicorn app.main:app --reload
```

Health is at `GET /health`; Swagger UI is at `/docs`, ReDoc at `/redoc`, and versioned APIs are under `/api/v1`.

## Authentication

`POST /api/v1/auth/signup` and `/login` return a short-lived signed access token and a random opaque refresh token. Send the access token as `Authorization: Bearer ...`. `POST /refresh` rotates the refresh token; a detected reuse revokes active refresh tokens for that user. `POST /logout` revokes the supplied refresh token. `GET /api/v1/auth/me` returns the current user. Refresh tokens are stored only as SHA-256 hashes; access claims contain the user ID and standard token identifiers/timestamps.

## Tests and lint

Tests force `ENVIRONMENT=test` and a separate `fastapi_starter_test` database URL. Before adding database-backed tests, create that database and configure test fixtures to override `get_db` with isolated test sessions. Current health and authentication dependency tests need no database connection.

```powershell
pytest
ruff check .
ruff format --check .
```

## Add a resource

1. Define a SQLAlchemy model in `app/models/widget.py`, then import it in `app/models/__init__.py`.
2. Add request/response schemas in `app/schemas/widget.py`.
3. Put SQL queries in `app/repositories/widget_repository.py`.
4. Put business rules in `app/services/widget_service.py`.
5. Add a router in `app/api/v1/endpoints/widgets.py`; inject a session, call the service, and declare response models.
6. Include that router in `app/api/v1/router.py` and create/apply an Alembic migration.

Example flow: `POST /widgets` validates `WidgetCreate` in the router, calls `WidgetService.create()`, which asks `WidgetRepository.create()` to add and flush a `Widget` model; the router serializes it through `WidgetResponse`.
