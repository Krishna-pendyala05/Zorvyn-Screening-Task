# Zorvyn Finance Backend

A multi-app Django 5.1 REST API backend for financial data processing, built to demonstrate strict Role-Based Access Control (RBAC), forensic audit logging, and data integrity.

---

## 🔗 Live API

- **Live API Base URL:** `https://zorvyn-screening-task.onrender.com`
- **Interactive Docs (Swagger UI):** `https://zorvyn-screening-task.onrender.com/api/schema/swagger-ui/`
- **Static Schema (Offline):** [`schema.yml`](./schema.yml) (raw OpenAPI 3.0 specification)

> Visiting the root URL (`/`) redirects directly to the Swagger UI.

---

## ⚡ Reviewer Quick-Start

After completing the [local setup](#️-local-setup) below, all entry points are listed here.

| What                | Where                                                                                        | Credentials          |
| :------------------ | :------------------------------------------------------------------------------------------- | :------------------- |
| **Swagger UI**      | [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/) | `admin` / `admin123` |
| **Django Admin**    | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)                                 | `admin` / `admin123` |
| **Audit Forensics** | [http://127.0.0.1:8000/admin/common/auditlog/](http://127.0.0.1:8000/admin/common/auditlog/) | `admin` / `admin123` |
| **Run Test Suite**  | `python -m pytest -v` (20 integration tests, all passing)                                    | -                    |

### Seeded Credentials (Role Cheat-Sheet)

| Role        | Username  | Password     | What they can access                          |
| :---------- | :-------- | :----------- | :-------------------------------------------- |
| **ADMIN**   | `admin`   | `admin123`   | Everything: users, records, dashboard, audit  |
| **ANALYST** | `analyst` | `analyst123` | Read financial records + dashboard only       |
| **VIEWER**  | `viewer`  | `viewer123`  | Dashboard analytics only (no raw records)     |

---

## 🛠️ Technical Stack

| Layer              | Technology                                                           |
| :----------------- | :------------------------------------------------------------------- |
| **Framework**      | Django 5.1 + Django REST Framework 3.15                              |
| **Authentication** | `djangorestframework-simplejwt`: stateless JWT (Bearer tokens)       |
| **API Docs**       | `drf-spectacular`: auto-generated OpenAPI 3.0 & Swagger UI           |
| **Filtering**      | `django-filter`: URL-param based QuerySet filtering                  |
| **Database**       | SQLite (local) / PostgreSQL (cloud, via `dj-database-url`)           |
| **Static Files**   | `whitenoise`: serves Swagger UI assets without a reverse proxy       |
| **Production**     | `gunicorn` WSGI server, deployed on Render                           |
| **Testing**        | `pytest` + `pytest-django`: integration tests via DRF's `APIClient`  |

---

## ✨ Key Features

- **Three-tier RBAC:** Admin, Analyst, and Viewer roles with independently enforced permission gates on every endpoint.
- **Forensic Audit Logging:** Every CREATE, UPDATE, and DELETE (on both users and financial records) is logged with a JSON delta showing only changed fields. Logs are written from the REST API and from Django Admin.
- **Soft Deletion:** Financial records are never hard-deleted via the API. A custom `NonDeletedManager` hides them from all queries; `all_objects` exposes them for admin and audit access.
- **Data Integrity:** A DB-level `CheckConstraint` enforces that `amount > 0`. A serializer-level `validate_amount` gives a descriptive API error before it reaches the DB.
- **Dashboard Analytics:** Aggregation is performed entirely at the database level using `SUM` and `COUNT`, avoiding loading row data into Python memory.

---

## 🏗️ Architecture

This project is a **modular monolith**: a single Django process with a single database, but with business logic strictly partitioned into four independent Django apps. Each app owns its own models, serializers, views, URLs, and tests. Nothing bleeds across boundaries unless explicitly imported.

```
zorvyn-finance/
├── core/         → Global config and root URL dispatcher (no business logic)
├── users/        → Identity, authentication, RBAC permission classes
├── records/      → Core financial domain (CRUD, soft-delete, filtering)
├── dashboard/    → Read-only analytics and aggregation (no write operations)
└── common/       → Cross-cutting infrastructure: AuditLog model + shared utils
```

**Why this structure?**

- **`users/` vs `records/` separation:** Authentication and financial data management are distinct concerns. Keeping them in separate apps means their models, permissions, and tests never share a file, making each easier to reason about independently.
- **`dashboard/` is intentionally write-free:** It owns no models and performs no mutations. All it does is aggregate data from `records/` via DB-level `SUM` and `COUNT`. Keeping it isolated means changes to aggregation logic can never accidentally touch the financial write path.
- **`common/` as shared infrastructure:** The `AuditLog` model and `record_audit_log()` utility are used by `users/`, `records/`, and both admin files. Centralising them in `common/` avoids duplication and ensures every write surface (REST API and Django Admin) uses the exact same logging path.
- **`core/` has no models:** It is purely coordination: settings, root URLs, and WSGI/ASGI entry points. This prevents the anti-pattern of putting business logic in the project package.

---

## 🛡️ Role-Based Access Matrix

| Role        | User Management | Financial Records | Dashboard Analytics |
| :---------- | :-------------- | :---------------- | :------------------ |
| **ADMIN**   | Full CRUD       | Full CRUD         | ✅ Read             |
| **ANALYST** | ❌ No access    | ✅ Read only      | ✅ Read             |
| **VIEWER**  | ❌ No access    | ❌ No access      | ✅ Read             |

> **Note:** There is also an `IsActiveUser` gate that blocks deactivated accounts regardless of their role, checked before role evaluation on every write endpoint.

---

## 🚀 Local Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config (no edits needed for local dev)
cp .env.example .env

# 4. Apply database migrations
python manage.py migrate

# 5. Seed sample users and financial records
python seed_db.py

# 6. Start the development server
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/`.

> **Re-running `seed_db.py`** is safe. Users are upserted with `get_or_create` and all financial records are wiped and recreated, making it fully idempotent.

### Running Tests

```bash
python -m pytest -v
```

All 20 integration tests cover RBAC enforcement, filtering, validation, audit trail integrity, and soft-deletion.

---

## ☁️ Cloud Deployment (Render)

The project is pre-configured for Render (or any similar PaaS).

- **Build Command:** `./render-build.sh`  
  _(installs deps, collects static files, runs migrations, and seeds the DB)_
- **Start Command:** `gunicorn core.wsgi`
- **Required Environment Variables:**

| Variable       | Description                                                          | Example                          |
| :------------- | :------------------------------------------------------------------- | :------------------------------- |
| `SECRET_KEY`   | Django secret key (must be long and random)                          | `your-production-secret-key`     |
| `DEBUG`        | Must be `False` in production                                        | `False`                          |
| `DATABASE_URL` | Full Postgres connection string (Render provides this automatically) | `postgresql://user:pass@host/db` |

---

## 📡 API Reference

All endpoints are prefixed with `/api/`. Authentication uses `Authorization: Bearer <access_token>`.

### Auth

| Method | Endpoint                         | Auth Required      | Description                                                               |
| :----- | :------------------------------- | :----------------- | :------------------------------------------------------------------------ |
| `POST` | `/api/users/auth/login/`         | No                 | Submit `username` + `password`, receive JWT `access` and `refresh` tokens |
| `POST` | `/api/users/auth/token/refresh/` | No (refresh token) | Exchange a valid `refresh` token for a new `access` token                 |

### Users _(ADMIN only)_

| Method   | Endpoint             | Description                                                           |
| :------- | :------------------- | :-------------------------------------------------------------------- |
| `GET`    | `/api/users/`        | Paginated list of all users (20 per page)                             |
| `POST`   | `/api/users/`        | Create a new user account with a specified role                       |
| `GET`    | `/api/users/{uuid}/` | Retrieve a single user by UUID                                        |
| `PATCH`  | `/api/users/{uuid}/` | Update role, email, or active status                                  |
| `DELETE` | `/api/users/{uuid}/` | **Soft-deactivate:** sets `is_active=False`, does not remove the row  |

### Financial Records

| Method   | Endpoint               | Required Role    | Description                                    |
| :------- | :--------------------- | :--------------- | :--------------------------------------------- |
| `GET`    | `/api/records/`        | ANALYST or ADMIN | Paginated list of active records (20 per page) |
| `POST`   | `/api/records/`        | ADMIN only       | Create a new financial record                  |
| `GET`    | `/api/records/{uuid}/` | ANALYST or ADMIN | Retrieve a single record by UUID               |
| `PATCH`  | `/api/records/{uuid}/` | ADMIN only       | Partial update of a record                     |
| `DELETE` | `/api/records/{uuid}/` | ADMIN only       | **Soft-delete** - row is flagged, not removed  |

**Record Filters** (as query params on `GET /api/records/`):

| Param         | Type   | Description                                             |
| :------------ | :----- | :------------------------------------------------------ |
| `date_after`  | date   | Include records on or after this date (`YYYY-MM-DD`)    |
| `date_before` | date   | Include records on or before this date (`YYYY-MM-DD`)   |
| `category`    | string | Case-insensitive exact match (e.g., `?category=salary`) |
| `type`        | string | `INCOME` or `EXPENSE`                                   |

### Dashboard _(Any authenticated user, including VIEWER)_

| Method | Endpoint                     | Description                                                                                                             |
| :----- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/api/dashboard/summary/`    | Returns `total_income`, `total_expenses`, `net_balance` as strings. Supports `date_after` / `date_before` query params. |
| `GET`  | `/api/dashboard/categories/` | Returns a list of `{category, total_amount, record_count}`, ordered by total descending                                 |

---

## 🏛️ Assumptions & Tradeoffs

### Assumptions

1. **Single currency.** All amounts are assumed to be in the same currency. Multi-currency conversion is outside scope.
2. **Admin-managed onboarding.** New user accounts are created by an `ADMIN` via the API. There is no self-registration endpoint by design, this is a controlled internal system.
3. **VIEWER role intent.** Viewers are stakeholders who should see financial summaries (the dashboard) but must never access raw transaction rows. This is why the VIEWER role is explicitly blocked from `/api/records/`.
4. **Soft deletion is final (via API).** There is no API endpoint to "restore" a soft-deleted record. Restoration, if needed, would be done through the Django Admin.

### Tradeoffs

1. **SQLite vs. PostgreSQL.** SQLite is used locally so reviewers can run the project with zero infrastructure setup. `dj-database-url` makes swapping to Postgres purely a config change, no code modifications needed.

2. **Free-text `category` field vs. a `Category` model.** A dedicated model with a foreign key would enforce consistency (preventing "Rent" vs "rent"). A `CharField` was chosen for speed of ingestion and flexibility, with `iexact` filtering partially mitigating the casing inconsistency at read time. In production, a normalized category table would be the right call.

3. **Soft delete on records, not on users.** Financial records are soft-deleted at the model level (`FinancialRecord.delete()` overridden), making it impossible to accidentally hard-delete via the API. Users are deactivated (via `is_active=False` in the `perform_destroy` view) rather than soft-deleted via a separate flag, aligning with Django's built-in `is_active` convention.

4. **Pytest over Django's built-in `TestCase`.** Pytest's fixture system (dependency injection) is cleaner than `unittest` style inheritance and avoids boilerplate. Integration tests (full request/response cycle) were prioritized over unit tests, because in a finance app the entry points between auth, permissions, and serializers are where real bugs surface.

5. **Atomic audit logging.** Every write operation (CREATE, UPDATE, DELETE) on both `records/` and `users/` wraps the database mutation and the audit log INSERT inside `transaction.atomic()`. If either step fails, both roll back. No un-logged mutations, no orphaned log entries.

### Known Limitations

1. **JWT token blacklisting is off.** `BLACKLIST_AFTER_ROTATION` and `ROTATE_REFRESH_TOKENS` are both disabled. This means there is no logout endpoint, a valid access token continues to work for its full 30-minute lifetime even after the account is deactivated. This was a deliberate scope decision: implementing token blacklisting requires an additional database table and a token-invalidation endpoint, which adds infrastructure complexity beyond what was required. The 30-minute access token TTL acts as the natural expiry window. In production, enabling blacklisting or switching to short-lived tokens with a revocation list would be the correct approach.

2. **`seed_db.py` runs on every Render deploy.** The `render-build.sh` build script calls `python seed_db.py` unconditionally. For users, this is safe as `get_or_create` is idempotent. For financial records, all rows are wiped and recreated on each deploy. This is acceptable for the demo environment but would need to be a one-time bootstrap step in any real deployment.

---

_Authored by Murali Krishna Pendyala_
