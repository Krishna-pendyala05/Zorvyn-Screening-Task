import os
import django
from datetime import date

# Domain: project-root | Purpose: Standalone seed script for local development and reviewer setup

# Initialize Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User
from records.models import FinancialRecord

def seed():
    print("--- Seeding Zorvyn Finance Backend ---")

    # 1. Create Role-Based Users
    # ---------------------------------------------------------
    
    # Admin: Full CRUD + User Management
    admin, created = User.objects.get_or_create(username="admin")
    admin.set_password("admin123")
    admin.role = User.UserRole.ADMIN
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"User: admin (Role: ADMIN) - {'Created' if created else 'Updated'}")

    # Analyst: Read-only access to records and dashboard
    analyst, created = User.objects.get_or_create(username="analyst")
    analyst.set_password("analyst123")
    analyst.role = User.UserRole.ANALYST
    analyst.save()
    print(f"User: analyst (Role: ANALYST) - {'Created' if created else 'Updated'}")

    # Viewer: Dashboard access only
    viewer, created = User.objects.get_or_create(username="viewer")
    viewer.set_password("viewer123")
    viewer.role = User.UserRole.VIEWER
    viewer.save()
    print(f"User: viewer (Role: VIEWER) - {'Created' if created else 'Updated'}")

    # 2. Create Sample Financial Records
    # ---------------------------------------------------------
    
    # Clear existing records to ensure idempotent seeding
    FinancialRecord.objects.all().delete()

    FinancialRecord.objects.create(
        amount="5000.00", 
        type=FinancialRecord.RecordType.INCOME, 
        category="Salary", 
        date=date(2026, 4, 1),
        notes="Monthly salary deposit"
    )
    FinancialRecord.objects.create(
        amount="1200.00", 
        type=FinancialRecord.RecordType.INCOME, 
        category="Consulting", 
        date=date(2026, 4, 5),
        notes="Freelance project payoff"
    )
    FinancialRecord.objects.create(
        amount="1500.00", 
        type=FinancialRecord.RecordType.EXPENSE, 
        category="Rent", 
        date=date(2026, 4, 1),
        notes="Main office rent"
    )
    FinancialRecord.objects.create(
        amount="300.00", 
        type=FinancialRecord.RecordType.EXPENSE, 
        category="Utilities", 
        date=date(2026, 4, 3)
    )
    FinancialRecord.objects.create(
        amount="45.50", 
        type=FinancialRecord.RecordType.EXPENSE, 
        category="Software", 
        date=date(2026, 4, 4),
        notes="SaaS subscription"
    )

    print(f"Sample Records: {FinancialRecord.objects.count()} records created.")
    print("--- Seeding Complete ---")
    print("Credentials: [username]123 (e.g. analyst123)")

if __name__ == "__main__":
    seed()
