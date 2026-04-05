from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.conf import settings
import uuid

# Domain: records | Purpose: Financial transaction model with soft-deletion and audit trail


class NonDeletedManager(models.Manager):
    # Enforces soft-deletion policy by filtering out flagged records at the ORM base level

    def get_queryset(self):
        # Default queryset hides soft-deleted records from all API consumers
        return super().get_queryset().filter(is_deleted=False)


class FinancialRecord(models.Model):
    # Core transactional entity providing financial auditability and soft-deletion tracking

    class RecordType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    # UUIDs prevent sequential ID enumeration on financial records
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # DecimalField is required for money; FloatField introduces rounding errors
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    type = models.CharField(max_length=10, choices=RecordType.choices)

    # Indexed because category and date are the primary filter targets
    category = models.CharField(max_length=50, db_index=True)
    date = models.DateField(db_index=True)

    # Empty string default avoids the null/blank dual-state inconsistency
    notes = models.TextField(blank=True, default="")

    # SET_NULL preserves records when the creating user is later deactivated
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="financial_records",
    )

    # is_deleted is indexed to keep soft-delete filtering fast on large datasets
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NonDeletedManager()
    # all_objects exposes soft-deleted rows for admin and audit access
    all_objects = models.Manager()

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]
        constraints = [
            # Prevents zero-value entries that corrupt balance calculations
            CheckConstraint(
                condition=Q(amount__gt=0),
                name="record_amount_positive",
            )
        ]

    def delete(self, *args, **kwargs):
        # Soft-delete: sets a flag instead of removing the row
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.category})"
