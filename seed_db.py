import os
import django
from datetime import date

# Domain: project-root | Purpose: Standalone seed script for local development and reviewer setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User
from records.models import FinancialRecord
from common.models import AuditLog
from common.utils import record_audit_log


def seed():
    print("--- Seeding Zorvyn Finance Backend ---")

    admin, created = User.objects.get_or_create(username="admin")
    admin.set_password("admin123")
    admin.role = User.UserRole.ADMIN
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"User: admin (Role: ADMIN) - {'Created' if created else 'Updated'}")

    analyst, created = User.objects.get_or_create(username="analyst")
    analyst.set_password("analyst123")
    analyst.role = User.UserRole.ANALYST
    analyst.save()
    print(f"User: analyst (Role: ANALYST) - {'Created' if created else 'Updated'}")

    viewer, created = User.objects.get_or_create(username="viewer")
    viewer.set_password("viewer123")
    viewer.role = User.UserRole.VIEWER
    viewer.save()
    print(f"User: viewer (Role: VIEWER) - {'Created' if created else 'Updated'}")

    # all_objects avoids stacking soft-deleted records when re-running the script
    FinancialRecord.all_objects.all().delete()

    def create_seeded_record(amount, rec_type, category, date, notes=None):
        record = FinancialRecord.objects.create(
            amount=amount,
            type=rec_type,
            category=category,
            date=date,
            notes=notes if notes else "",
            created_by=admin,
        )
        changes = {
            "amount": str(record.amount),
            "type": record.type,
            "category": record.category,
            "date": str(record.date),
            "notes": record.notes,
        }
        record_audit_log(
            user=admin, instance=record, action=AuditLog.Action.CREATE, changes=changes
        )

    create_seeded_record(
        "5000.00",
        FinancialRecord.RecordType.INCOME,
        "Salary",
        date(2026, 4, 1),
        "Monthly salary deposit",
    )
    create_seeded_record(
        "1200.00",
        FinancialRecord.RecordType.INCOME,
        "Consulting",
        date(2026, 4, 5),
        "Freelance project payoff",
    )
    create_seeded_record(
        "1500.00", FinancialRecord.RecordType.EXPENSE, "Rent", date(2026, 4, 1), "Main office rent"
    )
    create_seeded_record(
        "300.00", FinancialRecord.RecordType.EXPENSE, "Utilities", date(2026, 4, 3)
    )
    create_seeded_record(
        "45.50",
        FinancialRecord.RecordType.EXPENSE,
        "Software",
        date(2026, 4, 4),
        "SaaS subscription",
    )

    print(f"Sample Records: {FinancialRecord.objects.count()} records created.")
    print("--- Seeding Complete ---")
    print("Credentials: [username]123 (e.g. analyst123)")


if __name__ == "__main__":
    seed()
