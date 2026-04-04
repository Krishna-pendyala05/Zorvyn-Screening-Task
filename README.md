# Zorvyn Finance Backend

A multi-app Django 5.1 backend for financial data processing. This system is designed to evaluate strict Role-Based Access Control (RBAC), data integrity, and forensic auditability.

---

### Reviewer Command Center (Local)

| Component           | Access Link                                                               | Credentials              |
| :------------------ | :------------------------------------------------------------------------ | :----------------------- |
| **API Swagger UI**  | [http://127.0.0.1:8000/...](http://127.0.0.1:8000/api/schema/swagger-ui/) | `admin` / `admin123`     |
| **Audit Forensics** | [http://127.0.0.1:8000/...](http://127.0.0.1:8000/admin/common/auditlog/) | `admin` / `admin123`     |
| **Automated Tests** | `python -m pytest`                                                        | **20/20 Passing** (100%) |

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

- **Advanced RBAC:** Secure JWT-based pipeline with Admin, Analyst, and Viewer tiers.
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

### 2. Initialization (Clean 0001 Schema)

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
| **ADMIN**   | Full Access | Full Access       | View Analytics      |
| **ANALYST** | Forbidden   | View Only         | View Analytics      |
| **VIEWER**  | Forbidden   | Forbidden         | View Analytics      |

**Access Logic:**

- **Full Access:** Create, Read, Update, Delete (Audit Logs automatically generated).
- **View Only:** GET Access to protected endpoints (No modification allowed).
- **Forbidden:** 403 Forbidden (Strict RBAC enforcement).

---

## Design Philosophy & Engineering Notes

### Architectural Assumptions

- **Single-Tenant Model:** Assumed a unified financial domain where Analysts handle transaction review and Admins manage data entry.
- **Creator Accountability:** Assumed that every financial record must be linked back to the specific individual (Admin) who added it for forensic accountability.
- **JWT Lifetimes:** Assumed a 30-minute access token window is optimal for high-security financial dashboards to balance security and UX.

### Technical Tradeoffs

- **Soft-Deletion:** Chose storage overhead over data loss to ensure permanent audit compliance for financial reviews.
- **JSON Deltas:** Chose targeted field-tracking over full object snapshots to maintain human-readable, performant forensic trails.
- **DB-Level Aggregation:** Optimized performance by performing group-by operations at the database level via Django ORM.

---

## API & System Forensics

### Audit System

All financial and user modifications are captured in a centralized AuditLog model. Each entry records the user, action type, and a JSON object containing the exact field changes.

### Security Gate Pipeline

A multi-gate pipeline ensures that even a valid JWT won't grant access if the user account has been deactivated (soft-deleted).

---

_Authored By Murali Krishna Pendyala_
