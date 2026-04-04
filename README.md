# Zorvyn Finance Backend

A multi-app Django 5.1 backend for processing and visualizing financial transaction data with strict Role-Based Access Control (RBAC).

## 🚀 Key Features
- **Identity & RBAC:** Secure JWT-based authentication with three distinct roles (**ADMIN**, **ANALYST**, **VIEWER**).
- **Financial Persistence:** High-precision monetary data storage using `DecimalField` and primary key security with `UUID`.
- **Advanced Filtering:** Query transactions by date range, category, and type using `django-filter`.
- **Analytical Dashboard:** Real-time KPI aggregation (Income, Expenses, Net Balance) and categorical breakdowns.
- **Automated Documentation:** Industry-standard OpenAPI 3.0 schema with interactive Swagger UI.

---

## 🛠️ Tech Stack
- **Framework:** Django 5.1 & Django Rest Framework (DRF) 3.15
- **Security:** `djangorestframework-simplejwt`
- **Analytics:** Django Aggregation (SUM/COUNT)
- **Database:** SQLite (Zero-setup development)
- **Documentation:** `drf-spectacular` (Swagger UI)

---

## ⚙️ Local Setup

### 1. Clone & Environment
```bash
# Initialize Virtual Environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
# Apply Migrations
python manage.py migrate

# Seed Test Accounts & Sample Data
python seed_db.py
```

### 4. Run Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** to access the interactive API Documentation.

---

## 🛡️ Access Control Matrix (RBAC)

| Role | User Management | Financial CRUD | Analytics Dashboard |
| :--- | :---: | :---: | :---: |
| **ADMIN** | ✅ Full Access | ✅ Full Access | ✅ Read-Only |
| **ANALYST** | ❌ Forbidden | ❌ Read-Only | ✅ Read-Only |
| **VIEWER** | ❌ Forbidden | ❌ Forbidden | ✅ Read-Only |

### **Test Credentials (via `seed_db.py`)**
- **Admin:** `admin` / `admin123`
- **Analyst:** `analyst` / `analyst123`
- **Viewer:** `viewer` / `viewer123`

---

## 🧪 Testing
Run the full automated test suite to verify data integrity and permission gates:
```bash
pytest
```
*Successfully 16/16 test cases passing.*

---

## 📖 API Documentation
The API is self-documented via Swagger at `/api/schema/swagger-ui/`.
- **JWT Lifetimes:** 30-minute Access Tokens, 7-day Refresh Tokens.
- **Header:** Use `Authorization: Bearer <your_access_token>`.
