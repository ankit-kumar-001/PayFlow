# PayFlow Architecture and Flow: Day 1 Scaffolding

This document provides a deep dive into the initial scaffolding of the **PayFlow** project, explaining the structure, the tools chosen, and how the different components interact with each other.

## 1. Project Overview and Philosophy

The project is built on **FastAPI** using **Python 3.11+**, adhering strictly to a set of core principles:
- **No ORMs:** We interact with PostgreSQL exclusively via raw, parameterized SQL using `psycopg2`. No SQLAlchemy or Alembic.
- **Layered Architecture:** The codebase is split into distinct layers (Routers, Services, Repositories) to enforce separation of concerns. Each layer must remain thin and focused.
- **Minimal Dependencies:** We favor small, hand-written helpers (e.g., for JWT, rate limiting) over heavy third-party frameworks.

## 2. Directory Structure

The `app/` directory forms the core of our application. Here is a breakdown of what each folder does:

```text
app/
├── main.py          # The FastAPI application entry point.
├── core/            # App-wide settings and security (config, JWT helpers, hashing).
├── db/              # Database connection pools, Redis clients, and cursor context managers.
├── routers/         # The HTTP layer. Defines API endpoints, parses requests, and returns responses.
├── services/        # The Business Logic layer. Orchestrates data from repositories and applies rules.
├── repositories/    # The Data Access layer. Contains pure SQL queries interacting with the database.
├── schemas/         # Pydantic models used strictly for request validation and response formatting.
└── middleware/      # Cross-cutting HTTP concerns like rate limiting, logging, and CORS.
```

### The Request Flow
When a user makes a request to the API, it follows a strict path:
1. **Router:** Receives the HTTP request, validates the payload using a `Schema`, and calls a `Service`.
2. **Service:** Contains the core business logic. It determines *what* needs to be done and calls one or more `Repositories`.
3. **Repository:** Executes a raw parameterized SQL query using the connection pool from `db/`, then returns the raw data back to the `Service`.
4. **Service -> Router:** The Service processes the data and returns it to the Router, which then formats it into a response `Schema` and sends it to the client.

## 3. Deep Dive into the Code Components

### 3.1 Configuration (`app/core/config.py`)
Instead of using complex libraries like `pydantic-settings`, we use a simple `Settings` class combined with `python-dotenv`. It reads environment variables from `.env` (like database credentials, Redis host, and JWT secrets) and exposes them as Python attributes. This keeps configuration extremely fast and simple.

### 3.2 Database Connection Pool (`app/db/pool.py`)
Since we aren't using an ORM, we need an efficient way to manage database connections. 
- We use `psycopg2.pool.ThreadedConnectionPool` to maintain a pool of reusable connections (min 1, max 10) to PostgreSQL.
- We implemented a `@contextmanager` called `get_cursor()`. 
  - **Why?** It ensures that every time we need to execute a query, we safely check out a connection, yield a cursor, automatically `commit()` the transaction if successful, `rollback()` if an error occurs, and safely release the connection back to the pool.

### 3.3 The FastAPI Entry Point (`app/main.py`)
This is where the FastAPI application is initialized. Currently, it hosts a single `/health` endpoint.
- When you call `/health`, it attempts to execute a basic `SELECT 1` query using our `get_cursor()` function to verify the PostgreSQL connection.
- It also sends a `ping()` to Redis to ensure the caching layer is responsive.
- It returns an aggregated health status, which is crucial for Docker to know if the application is ready to serve traffic.

## 4. Docker and Infrastructure

The project runs inside isolated Docker containers using `docker-compose.yml`.

- **postgres:** Runs the official PostgreSQL 16 image. It exposes port 5432 and uses a named volume (`postgres_data`) to ensure data persists even if the container is destroyed.
- **redis:** Runs the official Redis 7 image, exposing port 6379 for caching.
- **app:** Builds the Python 3.11-slim `Dockerfile`. 
  - **Dependency Management:** It uses the `depends_on` block with `condition: service_healthy`. This means the FastAPI app container *will not start* until both PostgreSQL and Redis are fully initialized and report as healthy. 
  - **Port Mapping:** Mapped to host port **8002** as per your recent request.

## Summary
You now have a robust, highly scalable, and dependency-light foundation. The database pool handles connections safely, the configuration is strictly typed and centralized, and the Docker environment ensures that the application behaves identically on any machine.
