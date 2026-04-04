from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.conf import settings
import uuid

# Domain: records | Purpose: Financial transaction data model with accountability and integrity

# Custom manager to exclude deleted records by default
class NonDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class FinancialRecord(models.Model):
    class RecordType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    # UUID primary key to prevent enumeration
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Financial data - always DecimalField for money
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Enum-based classification
    type = models.CharField(
        max_length=10, 
        choices=RecordType.choices,
        help_text="Whether this is income or expense."
    )
    
    # Category and date are indexed as they are primary filter targets
    category = models.CharField(max_length=50, db_index=True)
    date = models.DateField(db_index=True)
    
    # Contextual data
    notes = models.TextField(blank=True, null=True)
    
    # Ownership: Who created this record?
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="financial_records",
        help_text="The user who originally created this transaction."
    )
    
    # Soft deletion fields
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Managers
    objects = NonDeletedManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]
        constraints = [
            # Enforce positive values at the database level
            CheckConstraint(
                check=Q(amount__gt=0), 
                name="record_amount_positive"
            )
        ]

    def delete(self, *args, **kwargs):
        """
        Soft-delete: Mark as deleted instead of removing from DB.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        """
        Actually remove the record from the database.
        """
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.category})"
