from django.db import models
from django.db.models import CheckConstraint, Q
import uuid

# Domain: records | Purpose: Financial transaction data model with integrity constraints

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
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.category})"
