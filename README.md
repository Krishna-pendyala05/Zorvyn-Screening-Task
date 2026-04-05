# Zorvyn Finance Backend

A multi-app Django 5.1 backend for financial data processing. This system is designed to evaluate strict Role-Based Access Control (RBAC), data integrity, and forensic auditability.

---

### Reviewer Command Center (Local)

| Component           | Access Link                                                               | Credentials          |
| :------------------ | :------------------------------------------------------------------------ | :------------------- |
| **API Swagger UI**  | [http://127.0.0.1:8000/...](http://127.0.0.1:8000/api/schema/swagger-ui/) | `admin` / `admin123` |
| **Audit Forensics** | [http://127.0.0.1:8000/...](http://127.0.0.1:8000/admin/common/auditlog/) | `admin` / `admin123` |
| **Automated Tests** | Run `python -m pytest -v` (20 integration tests)                          | **All passing**      |

#### Role Access Cheat-Sheet

- **ADMIN:** `admin` / `admin123` (Full Forensics & Management)
- **ANALYST:** `analyst` / `analyst123` (Read-Only Records & Analytics)
- **VIEWER:** `viewer` / `viewer123` (Dashboard Analytics Only)

---

## Technical Stack

- **Framework:** Django 5.1 & Django Rest Framework (DRF) 3.15
- **Security:** simple-jwt (JWT Authentication)
- **Analytics:** Django ORM Aggregation (Sum/Count)
- **Database:** SQLite (Zero-setup development)
- **Documentation:** drf-spectacular (OpenAPI 3.0 / Swagger UI)
- **Testing:** pytest & pytest-django

---

## Key Features

- **RBAC:** Secure JWT-based pipeline with Admin, Analyst, and Viewer tiers.
- **Forensic Auditing:** Real-time tracking of all modifications via JSON Deltas (Old vs. New).
- **Data Integrity:** Unified soft-deletion system for both transactional and user data.
- **Analytical Engine:** High-performance KPI engine using Django DB-level aggregation.

---

## Setup & Verification

### 1. Local Environment

```bash
# Initialize venv
python -m venv venv
.\venv\Scripts\activate   # Windows

# Install Dependencies
pip install -r requirements.txt
```

### 2. Initialization

```bash
# Apply migrations and seed data
python manage.py migrate
python seed_db.py
```

### 3. Execution

```bash
python manage.py runserver
```

Visit the Swagger UI link in the Command Center to begin interactive testing.

---

## 🛡️ Role-Based Access Matrix

| Role        | User Mgmt   | Financial Records | Dashboard Analytics |
| :---------- | :---------- | :---------------- | :------------------ |
| **ADMIN**   | Full Access | Full Access       | View Only           |
| **ANALYST** | Forbidden   | View Only         | View Only           |
| **VIEWER**  | Forbidden   | Forbidden         | View Only           |

---

## API Reference

API responses are paginated when listing multiple objects. The response format is `{"count": X, "next": URL|null, "previous": URL|null, "results": [...]}` with a default page size of 20.

| Method      | Endpoint                         | Required Role | Returns                                      |
| :---------- | :------------------------------- | :------------ | :------------------------------------------- |
| `POST`      | `/api/users/auth/login/`         | Any           | JWT `access` and `refresh` tokens            |
| `POST`      | `/api/users/auth/token/refresh/` | Any           | New `access` token (using `refresh` token)   |
| `GET`       | `/api/users/`                    | ADMIN         | Paginated list of users                      |
| `POST`      | `/api/users/`                    | ADMIN         | Created user                                 |
| `GET/PATCH/DEL` | `/api/users/{id}/`               | ADMIN         | Retrieved/Updated/Deactivated user           |
| `GET`       | `/api/records/`                  | ANALYST+      | Paginated list of financial records          |
| `POST`      | `/api/records/`                  | ADMIN         | Created financial record                     |
| `GET/PATCH/DEL` | `/api/records/{id}/`             | ANALYST+ (Read), ADMIN (Write) | Retrieved/Updated/Deleted record             |
| `GET`       | `/api/dashboard/summary/`        | VIEWER+       | Aggregated totals (Income, Expense, Balance) |
| `GET`       | `/api/dashboard/categories/`     | VIEWER+       | Aggregated totals grouped by category        |

---

## Engineering Decisions & Tradeoffs

### 1. `IsActiveUser` Security Gate separation

Instead of mixing activation checks into role checks (e.g., `IsActiveAdmin`), `IsActiveUser` is registered as the first gate for every endpoint. Since DRF checks permissions sequentially, this guarantees that deactivated users are blocked instantly, regardless of the role they hold.

### 2. JWT Configuration choice

The token rotation blacklisting (`BLACKLIST_AFTER_ROTATION`) is disabled, and the `rest_framework_simplejwt.token_blacklist` app is not installed. To reduce unnecessary complexity, the DB overhead and configuration required for a token blacklist outweighed the security benefit for this screening task.

### 3. UUID Primary Keys

Sequential IDs in financial systems allow enumeration attacks (e.g., iterating `/api/records/1`, `2`, `3` to scrape data). Switching every model to `id = uuid.uuid4` sacrifices some database locality performance for a massive gain in security against ID scraping.

### 4. Category modeling

The `category` field on `FinancialRecord` is a free-text `CharField(max_length=50)`. While a `Category` relational model or a `TextChoices` enum would prevent duplicates (like "salary" vs "Salary"), it was omitted to keep the scope tight and focused on the core requirements: RBAC, Audit, and Soft-Deletion. We mitigate this slightly with `iexact` filtering for consumers.

### 5. `notes` field consistency

The `notes` field uses `blank=True, default=""` instead of `null=True, blank=True`. Allowing both `NULL` and `""` creates dual-states in the database for the absence of data, complicating application logic and making database constraints harder to write. Enforcing a default `""` ensures consistent string types.

---

## API & System Forensics

### Audit System

All write operations (Admin creations, record updates, row deletions) are captured in a centralized `AuditLog`. Each entry records:

1. `user`: Who did it (via `SET_NULL` to survive user deletion).
2. `action`: CREATE, UPDATE, DELETE.
3. `changes`: A lightweight JSON delta storing only fields that mutated.

### Soft-Deletion

- **Financial Records:** `is_deleted=True` ensures data is never erased from disk. The default manager hides these rows from the API, but they remain available in the Django Admin for forensics.
- **Users:** `is_active=False` ensures a terminated employee can no longer authenticate, but any audit logs tracing back to their past actions will still resolve their name properly.

---

_Authored By Murali Krishna Pendyala_
