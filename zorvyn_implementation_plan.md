# Finance Data Processing & Access Control Backend
## Implementation Plan & Task Guide

**Zorvyn FinTech — Backend Developer Intern Assessment**
Author: Murali Krishna Pendyala
Stack: Python 3.12 · Django 5.1 · DRF 3.15 · SQLite

---

## 1. What We Are Building

A multi-role financial backend that serves a dashboard frontend. Three layers work in concert: identity (who you are), data (what exists), and aggregation (what you can know about it). Access control threads through all three.

The system is synchronous — CRUD + RBAC + aggregation. No message queues, no background workers, no async delegation. Every request resolves inline.

### Core Capabilities

- User and role management — create users, assign roles, toggle active/inactive status
- Financial records — create, read, update, delete, filter by date/category/type
- Dashboard summaries — aggregated totals, trends, category breakdowns
- Role-based access control enforced at the backend — not assumed from the frontend
- Input validation and structured error responses throughout

### Role Model

| Role    | Access Level            | Permitted Actions                                    |
|---------|-------------------------|------------------------------------------------------|
| Viewer  | Read-only (dashboard)   | Dashboard summaries only                             |
| Analyst | Read + insights         | Dashboard summaries + read financial records         |
| Admin   | Full access             | Everything — users, records, dashboard               |

### Request Gate Pipeline

Every request passes through three gates in order before reaching any business logic. An inactive user never reaches role checking. A wrong role never reaches the operation.

```
Gate 1 — JWT verified?        → 401 if not
Gate 2 — User is_active?      → 403 if not
Gate 3 — Role permitted?      → 403 if not
Gate 4 — Input valid?         → 400 if not
→ Execute operation → Structured JSON response
```

---

## 2. Stack and Versions

| Package                          | Version | Reason                                               |
|----------------------------------|---------|------------------------------------------------------|
| Python                           | 3.12.x  | Current stable, full typing support                  |
| Django                           | 5.1.x   | LTS, ORM aggregation, built-in SQLite                |
| djangorestframework              | 3.15.x  | Compatible with Django 5.1                           |
| djangorestframework-simplejwt    | 5.3.x   | JWT auth, DRF 3.15 compatible                        |
| django-filter                    | 24.3    | FilterSet for record date/category/type queries      |
| drf-spectacular                  | 0.27.x  | OpenAPI/Swagger docs at no extra effort              |
| pytest                           | 8.x     | Test runner                                          |
| pytest-django                    | 4.9.x   | Django fixture and DB access in pytest               |

**Database:** SQLite — built into Python, zero setup, explicitly allowed by the task. The Django ORM handles all queries identically regardless of backend.

> If migrating to Postgres later: change `DATABASE_URL` in `settings.py` and install `psycopg2-binary`. Zero code changes needed.

### SBOM Decision

Skip it. SBOM is a supply chain compliance artifact for production systems. A pinned `requirements.txt` is your dependency manifest for this scope. One line in README suffices:

```bash
# Audit deps: pip-licenses --format=markdown
```

---

## 3. Project Structure

### Architecture Choice

Three options were considered:

- **Option A — Single app:** everything in one app. Fast to start, hard to navigate past ~300 lines.
- **Option B — Multi-app by domain:** `users`, `records`, `dashboard` as separate apps. Clean separation, no redundancy. **Chosen.**
- **Option C — Multi-app with service layer:** adds `services.py` per app. Premature for this scope. Add only if view methods exceed ~25 lines.

> Chosen: Option B. Three domain apps, no service layer. If `dashboard/views.py` aggregation logic grows past ~80 lines, extract to `dashboard/services.py` then.

### File Map

```
zorvyn-finance-backend/
│
├── core/
│   ├── settings.py          # All settings — DB, JWT config, installed apps, spectacular
│   ├── urls.py              # Root URL dispatcher — mounts all app routers
│   └── wsgi.py              # Standard WSGI entry point
│
├── users/
│   ├── models.py            # Custom User with role (Viewer/Analyst/Admin) + is_active
│   ├── permissions.py       # Shared DRF BasePermission classes — used by all apps
│   ├── serializers.py       # User create/read/update + password write-only
│   ├── views.py             # User management endpoints (Admin only)
│   ├── urls.py              # /api/users/ + /api/auth/ routes
│   └── tests.py             # Auth, role gate, user management tests
│
├── records/
│   ├── models.py            # FinancialRecord — amount, type, category, date, notes
│   ├── filters.py           # FilterSet: date range, category, record type
│   ├── serializers.py       # Record create/read/update shapes + field validation
│   ├── views.py             # CRUD endpoints with permission_classes wired
│   ├── urls.py              # /api/records/ routes
│   └── tests.py             # CRUD tests per role — create, read, filter, 403 cases
│
├── dashboard/               # No models.py — only queries records.FinancialRecord
│   ├── serializers.py       # Summary response shapes — typed output contracts
│   ├── views.py             # Aggregation queries: Sum, Count, TruncMonth on records
│   ├── urls.py              # /api/dashboard/ routes
│   └── tests.py             # Summary correctness tests, Viewer access tests
│
├── conftest.py              # Shared pytest fixtures — users, tokens, records
├── pytest.ini               # Pytest config — Django settings pointer, test discovery
├── requirements.txt         # Pinned deps — all versions locked
├── .env.example             # SECRET_KEY placeholder — no secrets committed
└── README.md                # Setup steps, endpoint list, role-permission matrix
```

---

## 4. Code Writing Rules

These apply to every file. No exceptions, no drift across phases.

### General

- Imports: stdlib → third-party → internal, one blank line between groups. No wildcard imports.
- Line length: 100 characters max.
- No print statements. No `pass` in except blocks without a comment explaining why.
- No commented-out code in submitted files.
- No TODO comments in submitted files — either do it or leave it out.

### Models

- Always use `TextChoices` for enum fields (role, record type).
- Always add `CheckConstraint` for business-rule constraints — enforce at DB level.
- Always index fields you filter or sort by (`date`, `category`, `type`).
- Use `UUIDField` for primary keys — prevents enumeration.
- Use `DecimalField(max_digits=12, decimal_places=2)` for all money amounts. Never `FloatField`.
- `auto_now_add` on `created_at`, `auto_now` on `updated_at` — always.

### Views

- Use DRF generic class-based views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`, etc.).
- Never put business logic inside a view method. If a method exceeds ~25 lines, extract it.
- Views declare `permission_classes` only — no inline role checks inside methods.

### Permissions

- All access control lives in `users/permissions.py` as `BasePermission` subclasses.
- Never scatter role checks inside view methods.
- `IsActiveUser` always listed first in `permission_classes` — inactive users never reach role checks.

### Serializers

- Validate in `validate_<field>` or `validate()` — never in views.
- Keep `to_representation` overrides minimal and justified.
- Password fields always `write_only=True`.

### Error Responses

- Always return structured JSON. Never let Django HTML error pages leak through.
- Use DRF `ValidationError`, `PermissionDenied`, `NotFound` — never raise raw `Exception`.
- `400` bad input · `401` unauthenticated · `403` wrong role or inactive · `404` not found · `409` conflict

---

## 5. Comment Style

One rule: **comment why, not what.** The code says what. The comment says why it is done this way.

**Module-level — one line at the top of every file:**
```python
# Domain: users | Purpose: DRF permission classes enforcing role-based access
# Domain: records | Purpose: FilterSet for date range, category, and type filtering
```

**Inline — only for non-obvious decisions:**
```python
class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        # Inactive users are blocked before role checking reaches them
        return bool(request.user and request.user.is_active)
```

**Constraint comments — why a constraint exists:**
```python
constraints = [
    # Prevents zero-value entries that corrupt balance calculations
    CheckConstraint(check=Q(amount__gt=0), name='record_amount_positive')
]
```

**Rules:**
- No docstrings — DRF + drf-spectacular generates API docs from serializers automatically.
- No block comments — if a section needs a block comment, the section is too complex.
- No inline comments on obvious lines.
- Never end a comment with a period.

---

## 6. Endpoint Surface

| Method | Endpoint                       | Auth          | Who                    |
|--------|-------------------------------|---------------|------------------------|
| POST   | `/api/auth/login/`            | None          | Anyone                 |
| POST   | `/api/auth/refresh/`          | Refresh token | Anyone                 |
| GET    | `/api/users/`                 | JWT           | Admin                  |
| POST   | `/api/users/`                 | JWT           | Admin                  |
| PATCH  | `/api/users/{id}/`            | JWT           | Admin                  |
| DELETE | `/api/users/{id}/`            | JWT           | Admin                  |
| GET    | `/api/records/`               | JWT           | Analyst, Admin         |
| POST   | `/api/records/`               | JWT           | Admin                  |
| PATCH  | `/api/records/{id}/`          | JWT           | Admin                  |
| DELETE | `/api/records/{id}/`          | JWT           | Admin                  |
| GET    | `/api/dashboard/summary/`     | JWT           | Viewer, Analyst, Admin |
| GET    | `/api/dashboard/trends/`      | JWT           | Viewer, Analyst, Admin |
| GET    | `/api/dashboard/categories/`  | JWT           | Viewer, Analyst, Admin |
| GET    | `/api/schema/swagger-ui/`     | None          | Anyone (dev)           |

---

## 7. Implementation Phases

Work in this exact order. Each phase produces working, testable code before the next begins. Do not start Phase 3 before Phase 2 is passing tests.

---

### Phase 1 — Project Scaffold

**Goal:** `runserver` works, `pytest` discovers the project, all dependencies installed.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Create project: `django-admin startproject core .` | `core/` |
| ☐ | Create apps: `python manage.py startapp users` / `records` / `dashboard` | `users/ records/ dashboard/` |
| ☐ | Write `requirements.txt` with all pinned versions | `requirements.txt` |
| ☐ | Configure `settings.py` — DB (SQLite), `INSTALLED_APPS`, REST_FRAMEWORK defaults, JWT config, SPECTACULAR settings | `core/settings.py` |
| ☐ | Set up root `urls.py` — mount `api/` prefix and schema routes | `core/urls.py` |
| ☐ | Create `.env.example` with `SECRET_KEY` placeholder | `.env.example` |
| ☐ | Write `pytest.ini` — `DJANGO_SETTINGS_MODULE` pointer, `testpaths` | `pytest.ini` |
| ☐ | Confirm: `python manage.py runserver` starts, `pytest` collects 0 tests (passes) | all |

---

### Phase 2 — User Model, Roles, JWT, Permissions

**Goal:** users can register, login, get a JWT token, and role gates work correctly.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Define `AbstractUser` subclass with `role` (`TextChoices`: VIEWER/ANALYST/ADMIN) and `is_active` | `users/models.py` |
| ☐ | Set `AUTH_USER_MODEL = "users.User"` in `settings.py` | `core/settings.py` |
| ☐ | Run and commit initial migration | `migrations/` |
| ☐ | Write `UserSerializer` — password `write_only`, role field, validate role choices | `users/serializers.py` |
| ☐ | Write `IsActiveUser` permission class — blocks inactive users with 403 | `users/permissions.py` |
| ☐ | Write `IsAdminRole` permission class — checks `role == ADMIN` | `users/permissions.py` |
| ☐ | Write `IsAnalystOrAbove` permission class — checks `role in [ANALYST, ADMIN]` | `users/permissions.py` |
| ☐ | Write `UserListCreateView` (Admin only) and `UserDetailView` (Admin only) | `users/views.py` |
| ☐ | Mount simplejwt `TokenObtainPairView` and `TokenRefreshView`, mount user routes | `users/urls.py` |
| ☐ | Wire `users/urls.py` into `core/urls.py` | `core/urls.py` |
| ☐ | Write `conftest.py` fixtures: `admin_user`, `analyst_user`, `viewer_user`, `inactive_user`, auth tokens for each | `conftest.py` |
| ☐ | Test: Viewer `POST /api/users/` returns 403 | `users/tests.py` |
| ☐ | Test: Inactive user with valid JWT returns 403 | `users/tests.py` |
| ☐ | Test: Admin can create a user, list users | `users/tests.py` |
| ☐ | Test: Login returns access + refresh tokens | `users/tests.py` |

---

### Phase 3 — Financial Records CRUD + Filtering

**Goal:** financial records can be created, read, updated, deleted, and filtered. Role gates enforced.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Define `FinancialRecord` model — UUID pk, `amount` (DecimalField), `type` (TextChoices: INCOME/EXPENSE), `category` (CharField), `date` (DateField), `notes` (optional) | `records/models.py` |
| ☐ | Add `CheckConstraint` for `amount > 0` | `records/models.py` |
| ☐ | Add `db_index=True` on `date` and `category` fields | `records/models.py` |
| ☐ | Run and commit migration | `migrations/` |
| ☐ | Write `RecordSerializer` — validate amount > 0, validate type choices, date format | `records/serializers.py` |
| ☐ | Write `RecordFilter` (FilterSet) — `date_after`, `date_before`, `category`, `record_type` | `records/filters.py` |
| ☐ | Write `RecordListCreateView` — GET (Analyst+), POST (Admin only) | `records/views.py` |
| ☐ | Write `RecordDetailView` — GET (Analyst+), PATCH/DELETE (Admin only) | `records/views.py` |
| ☐ | Wire `filter_backends = [DjangoFilterBackend]` on list view, set `filterset_class` | `records/views.py` |
| ☐ | Mount record routes and wire into `core/urls.py` | `records/urls.py` |
| ☐ | Add fixtures: sample records (mixed income/expense, multiple categories) to `conftest.py` | `conftest.py` |
| ☐ | Test: Admin creates a record — 201 returned | `records/tests.py` |
| ☐ | Test: Analyst reads records — 200 returned | `records/tests.py` |
| ☐ | Test: Viewer `GET /api/records/` returns 403 | `records/tests.py` |
| ☐ | Test: Analyst `POST /api/records/` returns 403 | `records/tests.py` |
| ☐ | Test: Filter by category returns correct subset | `records/tests.py` |
| ☐ | Test: Filter by `date_after` / `date_before` returns correct subset | `records/tests.py` |
| ☐ | Test: Invalid amount (negative) returns 400 with useful message | `records/tests.py` |
| ☐ | Test: Missing required field returns 400 with field-level error | `records/tests.py` |

---

### Phase 4 — Dashboard Aggregation Endpoints

**Goal:** three summary endpoints return correct aggregated data. Viewer, Analyst, Admin can all reach them.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Write `/api/dashboard/summary/` — `total_income` (Sum), `total_expenses` (Sum), `net_balance`, `record_count` | `dashboard/views.py` |
| ☐ | Write `/api/dashboard/categories/` — group by category, sum per category, annotate with total | `dashboard/views.py` |
| ☐ | Write `/api/dashboard/trends/` — `TruncMonth` on date, Sum per month, return last 12 months ordered | `dashboard/views.py` |
| ☐ | Write serializers for each summary response shape | `dashboard/serializers.py` |
| ☐ | Apply `permission_classes = [IsActiveUser]` on all dashboard views (all roles permitted) | `dashboard/views.py` |
| ☐ | Mount dashboard routes and wire into `core/urls.py` | `dashboard/urls.py` |
| ☐ | Test: Summary returns correct totals against known fixture data | `dashboard/tests.py` |
| ☐ | Test: Category breakdown sums correctly | `dashboard/tests.py` |
| ☐ | Test: Viewer can access `/api/dashboard/summary/` — 200 returned | `dashboard/tests.py` |
| ☐ | Test: Unauthenticated request to dashboard returns 401 | `dashboard/tests.py` |
| ☐ | Test: Empty database returns zeros not errors | `dashboard/tests.py` |

---

### Phase 5 — Validation Hardening + Error Responses

**Goal:** every bad input produces a structured, useful JSON error. No raw exceptions leak.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Confirm `REST_FRAMEWORK` default renderer is `JSONRenderer` (disable `BrowsableAPIRenderer` in prod) | `core/settings.py` |
| ☐ | Add `EXCEPTION_HANDLER` = custom handler if default DRF exceptions need reshaping | `core/settings.py` |
| ☐ | Test: `POST /api/records/` with missing `amount` field — 400 with `{amount: ["This field is required."]}` | `records/tests.py` |
| ☐ | Test: `POST /api/records/` with invalid `type` value — 400 with choices error message | `records/tests.py` |
| ☐ | Test: `GET /api/records/{bad-uuid}/` — 404 with structured message | `records/tests.py` |
| ☐ | Test: `POST /api/auth/login/` with wrong password — 401 | `users/tests.py` |
| ☐ | Test: Request with expired JWT — 401 | `users/tests.py` |
| ☐ | Test: Admin `PATCH /api/users/{id}/` assigning invalid role — 400 | `users/tests.py` |
| ☐ | Test: Admin cannot delete themselves — confirm behavior (403 or 400, document choice) | `users/tests.py` |

---

### Phase 6 — Documentation + README

**Goal:** a reviewer can clone, run, and understand the project in under 5 minutes.

| ☐ | Task | File(s) |
|---|------|---------|
| ☐ | Confirm drf-spectacular generates schema at `/api/schema/` and Swagger UI at `/api/schema/swagger-ui/` | `core/urls.py` |
| ☐ | Write README: one-command setup (pip install + migrate + runserver) | `README.md` |
| ☐ | Write README: role-permission matrix table | `README.md` |
| ☐ | Write README: all endpoint list with method, path, who can access | `README.md` |
| ☐ | Write README: how to run tests (`pytest`) | `README.md` |
| ☐ | Write README: note on SQLite (deliberately chosen, zero setup) | `README.md` |
| ☐ | Create a superuser / seed script or management command with sample data for reviewers | `users/management/` |
| ☐ | Final check: `pytest` passes with 0 failures, `runserver` starts cleanly | all |

---

## 8. What to Carry Over from the Payment Service

Build fresh — but these patterns port directly from `django-payment-notification-service`:

| Pattern | From | Why It Applies |
|---------|------|----------------|
| `UUIDField` as primary key | `payments/models.py` | Safe IDs, prevents enumeration |
| `DecimalField(12, 2)` for amounts | `payments/models.py` | Correct type for money — always |
| `CheckConstraint` for `amount > 0` | `payments/models.py` Meta | Enforce at DB level again |
| `db_index=True` on date fields | `payments/models.py` | Dashboard trend queries hit dates hard |
| `TextChoices` enums for status | `payments/models.py` | Use for `role` and record `type` |
| `auto_now_add` / `auto_now` timestamps | `payments/models.py` | Same pattern, same fields |
| `transaction.atomic()` on creates | `payments/views.py` | Protect record creation |
| DRF `generics.*` class-based views | `payments/views.py` | Same structure, same convention |
| `djangorestframework-simplejwt` setup | `requirements.txt` / settings | Bring JWT config over exactly |
| `drf-spectacular` for Swagger docs | `requirements.txt` | Zorvyn will appreciate clean API docs |
| `pytest` + `conftest.py` discipline | `conftest.py`, `pytest.ini` | Same testing structure |

**Leave behind entirely:** Celery, SQS, LocalStack, Terraform, idempotency via client-supplied `payment_id`, notification logging, Docker (optional here).

### The Key Gap to Build Fresh

The existing project has zero RBAC logic — `permission_classes = [IsAuthenticated]` is the only gate. The entire `users/permissions.py` layer is new work.

```python
# What you have
permission_classes = [permissions.IsAuthenticated]

# What you need to build
permission_classes = [IsActiveUser, IsAdminRole]        # user management
permission_classes = [IsActiveUser, IsAnalystOrAbove]   # record reads
permission_classes = [IsActiveUser]                     # dashboard (all roles)
```

---

## 9. Quick Reference

### Setup Commands

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
pytest
```

### Django ORM Aggregation Functions Used in Dashboard

| Function | Import | Used For |
|----------|--------|----------|
| `Sum()` | `django.db.models` | Total income, total expenses |
| `Count()` | `django.db.models` | Record count, category counts |
| `TruncMonth()` | `django.db.models.functions` | Monthly trend bucketing |
| `TruncWeek()` | `django.db.models.functions` | Weekly trend bucketing (optional) |
| `annotate() + values()` | QuerySet methods | Group-by category totals |

### HTTP Status Code Reference

| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | Successful GET, PATCH |
| 201 | Created | Successful POST creating a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, missing required fields, failed validation |
| 401 | Unauthorized | No token, invalid token, expired token |
| 403 | Forbidden | Valid token but wrong role, or user is inactive |
| 404 | Not Found | Resource does not exist |
| 405 | Method Not Allowed | DRF handles this automatically |

### Permission Class Matrix

| `permission_classes` used on | Viewer | Analyst | Admin |
|------------------------------|--------|---------|-------|
| `[IsActiveUser, IsAdminRole]` | ✗ | ✗ | ✓ |
| `[IsActiveUser, IsAnalystOrAbove]` | ✗ | ✓ | ✓ |
| `[IsActiveUser]` | ✓ | ✓ | ✓ |

---

*Zorvyn Finance Backend — Implementation Plan · Murali Krishna Pendyala*
