# Zorvyn Finance Backend

A multi-app Django 5.1 backend for processing and visualizing financial transaction data with a focus on strict Role-Based Access Control (RBAC), data integrity, and forensic auditability.

---

## 🚀 Key Features

- **🛡️ Advanced RBAC:** Secure JWT-based authentication with three distinct roles (**ADMIN**, **ANALYST**, **VIEWER**) and a multi-gate permission pipeline.
- **📋 High-Precision Audit logging:** Centralized tracking of all financial modifications via **JSON Deltas**, capturing exactly what changed, when, and by whom.
- **♻️ Data Integrity (Soft-Deletion):** Transaction and user deactivation system that preserves historical context while maintaining a clean active UI.
- **📈 Analytical aggregation:** Real-time KPI engine for calculating Net Balance and categorical breakdowns with `Decimal` precision.
- **📖 Self-Documenting API:** Professional OpenAPI 3.0 schema with rich placeholders and Swagger UI integration.

---

## 🧪 Testing & Quality

Run the full automated test suite to verify 20/20 critical path validations (RBAC, Audit, Aggregation).
```bash
python -m pytest
```
> [!NOTE]
> **Verified Status:** ✅ **20/20 tests passing** with zero warnings and 100% logic integrity.

---

## ⚙️ Local Setup

### 1. Initialize & Install
```bash
# Set up venv
python -m venv venv
.\venv\Scripts\activate   # Windows

# Install libraries
pip install -r requirements.txt
```

### 2. Database & Seeds
```bash
# Migrate & Populate
python manage.py migrate
python seed_db.py
```

### 3. Run & Explore
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** for interactive Swagger documentation.

---

## 🧠 Design Philosophy

This project was built using a **monorepo-style domain separation** strategy.

### **Architectural Assumptions**
- **Single-Tenant Model:** Assumed a unified financial domain where Analysts handle transaction review and Admins manage entry.
- **Creator Accountability:** Assumed that every financial record must be linked back to the specific individual (Admin) who added it for tracking.
- **JWT Lifetimes:** Assumed a 30-minute access token window is optimal for high-security financial dashboards.

### **Technical Tradeoffs**
- **Soft-Deletion vs Hard-Deletion:** 
  - *Tradeoff:* Chose soft-deletion to ensure permanent audit compliance.
  - *Result:* Preserves data history at the cost of slight database storage overhead.
- **JSON Delta Auditing:**
  - *Tradeoff:* logging specific changed fields instead of the full object state.
  - *Result:* Maintains a clear, human-readable forensic trail while reducing log storage size.
- **Django Aggregation:** 
  - *Tradeoff:* Performing group-by operations at the DB level via Django ORM.
  - *Result:* Optimized retrieval of financial analytics compared to in-memory Python calculations.

---

## 🛡️ Role-Based Access Matrix

| Role | User Mgmt | Financial Records | Dashboard Analytics |
| :--- | :--- | :--- | :--- |
| **ADMIN** | ✅ Full Access | ✅ Full Access | 👁️ View Analytics |
| **ANALYST** | ❌ Forbidden | 👁️ View Only | 👁️ View Analytics |
| **VIEWER** | ❌ Forbidden | ❌ Forbidden | 👁️ View Analytics |

**Access Key:**
- ✅ **Full Access:** Create, Read, Update, Delete (Audit Logs generated).
- 👁️ **View Only:** GET Access to relevant endpoints only.
- ❌ **Blocked:** 403 Forbidden.

---

## 🛠️ API & System Notes

### **Audit Forensics**
All financial modifications are captured in the **AuditLog** model. You can view the JSON deltas in the [Django Admin](http://127.0.0.1:8000/admin/common/auditlog/) to see pre-and-post change values.

### **Security Gates**
A custom pipeline ensures that even a valid JWT won't grant access if the user account has been deactivated (soft-deleted).

### **Test Credentials**
- **Admin:** `admin` / `admin123`
- **Analyst:** `analyst` / `analyst123`
- **Viewer:** `viewer` / `viewer123`
