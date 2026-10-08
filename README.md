# PayFlow — Payment Gateway API

PayFlow is a high-performance, production-ready Payment Gateway RESTful API built with **FastAPI**, **PostgreSQL**, and **Redis**.

The project is intentionally designed with a **layered, zero-ORM architecture** using raw SQL (`psycopg2`) and thread-safe connection pooling. This design offers predictable performance, explicit transaction control, and low latency for financial transaction handling.

---

## Architectural Highlights & Technical Decisions

* **Zero-ORM Database Layer**: Built without SQLAlchemy or Alembic to eliminate ORM abstraction overhead. Data access is implemented via raw parameterized SQL (`%s` placeholders) using a custom `ThreadedConnectionPool` manager with explicit transaction context controls (`commit`/`rollback`).
* **Dual-Tier Authentication**:
  * **User Sessions**: JWT (JSON Web Tokens) with bcrypt password hashing for user signups and merchant management.
  * **Server-to-Server API**: Merchant-facing payment endpoints are authenticated via high-entropy `api_key` (`pk_...`) and hashed `api_secret` (`sk_...`) pairs passed in custom HTTP headers (`x-api-key`, `x-api-secret`).
* **Caching & Low-Latency Lookups**: Hot payment link records are cached in Redis to minimize database read pressure during high-concurrency payment link lookups.
* **Distributed Rate Limiting**: Built-in fixed-window rate limiter powered by Redis (`INCR` + `EXPIRE`), tracking requests per merchant API key or client IP with graceful fallback logic if Redis is unreachable.
* **State Machine & Financial Consistency**: Strict payment link lifecycle management (`active` → `paid`, `expired`, `cancelled`) preventing double-spend attempts, alongside transactional refund validation checking cumulative refund balances.
* **Automated Raw SQL Migration Engine**: Custom lightweight migration runner executing ordered `.sql` schema scripts on container startup with idempotency tracked via a `schema_migrations` table.

---

## Layered Architecture

The codebase strictly isolates responsibilities into thin, single-purpose layers:

```
[ Client / Webhook ]
        │
        ▼
   HTTP Routers (routers/)          <── Middleware (Logging, Rate Limiting)
        │
        ▼
   Business Services (services/)    <── Core (Config, JWT & Hashing)
        │
        ▼
   Repositories (repositories/)     <── Schemas (Pydantic Validation)
        │
        ▼
   Data Layer (db/)                 <── PostgreSQL Pool (psycopg2) & Redis
```

* **`app/routers/`**: HTTP layer only — parses requests, validates schemas, invokes services, and returns responses.
* **`app/services/`**: Core business logic, authorization rules, state transitions, and cache invalidation.
* **`app/repositories/`**: Raw parameterized SQL queries with zero business logic.
* **`app/db/`**: Threaded database connection pool (`psycopg2`), Redis client initialization, and migration scripts.
* **`app/schemas/`**: Strict Pydantic models for request validation and response serialization.
* **`app/core/`**: Environment configurations and security helpers (JWT generation, password hashing).
* **`app/middleware/`**: Cross-cutting concerns including HTTP request logging and Redis rate limiting.

---

## Repository Structure

```
PayFlow/
├── app/
│   ├── core/              # Config & JWT/bcrypt security helpers
│   ├── db/                # Connection pool, Redis client & SQL migrations
│   │   └── migrations/    # Ordered raw SQL migration scripts (001-008)
│   ├── middleware/        # Request logging & Redis rate limiter
│   ├── repositories/      # Raw SQL queries (user, merchant, payment link, tx, refund)
│   ├── routers/           # FastAPI routers (auth, merchants, links, pay, refunds, webhooks)
│   ├── schemas/           # Pydantic request/response validation models
│   ├── services/          # Core domain business logic & state enforcement
│   └── main.py            # FastAPI application entrypoint & health checks
├── tests/                 # Integration test suite (test_flow.py)
├── docker-compose.yml     # Multi-container orchestration (App, Postgres, Redis)
├── Dockerfile             # App container build definition
├── docker-entrypoint.sh   # Entrypoint script running migrations then launching app
└── requirements.txt       # Python dependencies
```

---

## API Reference

### Auth & Merchant Management

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Public | Create a new user account |
| `POST` | `/auth/login` | Public | Authenticate user and receive a JWT access token |
| `POST` | `/merchants` | Bearer JWT | Provision a new merchant account & return API credentials |
| `GET` | `/merchants/me` | Bearer JWT | Retrieve current merchant profile and API key |

### Payment Links & Processing

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/payment-links` | Merchant Keys | Create a new payment link |
| `GET` | `/payment-links` | Merchant Keys | List payment links created by merchant |
| `GET` | `/payment-links/{id}` | Public | Fetch payment link details (cached in Redis) |
| `POST` | `/payment-links/{id}/pay` | Public | Simulate payment execution against a link |

### Refunds & Webhooks

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/transactions/{id}/refunds` | Merchant Keys | Process a partial or full refund for a transaction |
| `POST` | `/webhooks` | Merchant Keys | Register a webhook endpoint for payment events |
| `GET` | `/webhooks/{id}/logs` | Merchant Keys | Retrieve execution logs for a registered webhook |
| `GET` | `/health` | Public | Health check inspecting PostgreSQL and Redis connectivity |

---

## Usage Workflow Example

### 1. Merchant Setup & Authentication

```bash
# 1. Sign up user
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "merchant@example.com", "password": "securepassword123", "full_name": "Acme Corp"}'

# 2. Login to get JWT Bearer Token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "merchant@example.com", "password": "securepassword123"}'

# 3. Create Merchant Profile (returns x-api-key and x-api-secret)
curl -X POST http://localhost:8000/merchants \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"business_name": "Acme Store"}'
```

### 2. Payment Link Creation & Payment Simulation

```bash
# Create Payment Link using Merchant API credentials
curl -X POST http://localhost:8000/payment-links \
  -H "x-api-key: pk_live_..." \
  -H "x-api-secret: sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 99.99,
    "currency": "USD",
    "description": "Annual Software License"
  }'

# Customer Payment Simulation (Public Endpoint)
curl -X POST http://localhost:8000/payment-links/<LINK_ID>/pay \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "card",
    "simulate_failure": false
  }'
```

### 3. Refund Execution

```bash
# Process Refund
curl -X POST http://localhost:8000/transactions/<TRANSACTION_ID>/refunds \
  -H "x-api-key: pk_live_..." \
  -H "x-api-secret: sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 49.99,
    "reason": "Partial customer refund request"
  }'
```

---

## Database Schema Overview

The database schema consists of 8 raw SQL migration steps managed in `app/db/migrations/`:

* `users`: User credentials (`email`, `password_hash`, `full_name`).
* `merchants`: Merchant accounts linked to users with unique `api_key` and `api_secret_hash`.
* `payment_links`: Payment request records (`amount`, `currency`, `status`, `merchant_id`).
* `transactions`: Recorded payment execution attempts (`payment_link_id`, `status`, `payment_method`).
* `refunds`: Transaction refund records with validation against original transaction totals.
* `webhooks`: Registered merchant webhook target URLs.
* `webhook_logs`: Delivery history and HTTP status tracking for webhooks.
* `webhook_events`: Triggered domain event records.

---

## Local Development & Setup

### Prerequisites

* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### 1. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Ensure environment variables are configured:

```env
PG_USER=postgres
PG_PASSWORD=postgres
PG_DB=payflow
PG_HOST=postgres
PG_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET=supersecretkey
```

### 2. Start Application Stack

Spin up the API, PostgreSQL, and Redis containers:

```bash
docker compose up --build
```

The app automatically executes pending raw SQL migrations on boot and starts listening at `http://localhost:8000`.

### 3. Verify Health

Check system health status:

```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "ok",
  "db": "healthy",
  "redis": "healthy"
}
```

---

## Testing

Run the full end-to-end integration test suite covering signup, merchant provisioning, payment link creation, payment simulation, refund flow, and rate limiting:

```bash
# Inside docker container or virtualenv with requirements installed:
pytest
```
