# Zorvyn Finance Backend — Project Guide

## Build & Setup Commands
- **Environment:** `python -m venv venv`
- **Activation:** `.\venv\Scripts\activate` (PowerShell) or `venv\Scripts\activate.bat` (CMD)
- **Install:** `pip install -r requirements.txt`
- **Migrations:** `python manage.py migrate`
- **Seed Data:** `python seed_db.py` (Creates admin, analyst, and viewer users)
- **Run Server:** `python manage.py runserver`

## Standard Credentials (from `seed_db.py`)
| Role | Username | Password |
| :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin123` |
| **ANALYST** | `analyst` | `analyst123` |
| **VIEWER** | `viewer` | `viewer123` |

## Test Commands
- **Run All Tests:** `pytest`
- **User/Auth Tests:** `pytest users/tests.py`
- **Record Tests:** `pytest records/tests.py`
- **Dashboard Tests:** `pytest dashboard/tests.py`

## Project Structure
- `core/`: Settings and root URL dispatcher.
- `users/`: Identity management and custom RBAC permissions.
- `records/`: Financial transaction CRUD and filtering.
- `dashboard/`: KPI aggregations and categorical summaries.

## Coding Standards
- **Primary Keys:** Always use `UUIDField`.
- **Financials:** Always use `DecimalField(max_digits=12, decimal_places=2)`.
- **RBAC:** Multi-gate permissions (`IsActiveUser` -> Role Gate).
- **Documentation:** OpenAPI/Swagger available at `/api/schema/swagger-ui/`.
