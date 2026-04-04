import django_filters
from .models import FinancialRecord

# Domain: records | Purpose: FilterSet for dynamic querying of financial transactions via DRF and django-filter

class RecordFilter(django_filters.FilterSet):
    """
    Advanced filtering for financial records.
    Supports date range queries, category filtering, and record type classification.
    """
    date_after = django_filters.DateFilter(
        field_name="date", 
        lookup_expr="gte",
        help_text="Records starting from this date (YYYY-MM-DD)."
    )
    date_before = django_filters.DateFilter(
        field_name="date", 
        lookup_expr="lte",
        help_text="Records up to this date (YYYY-MM-DD)."
    )
    
    # Case-insensitive exact category filtering
    category = django_filters.CharFilter(
        field_name="category", 
        lookup_expr="iexact"
    )
    
    # Enum-based type filtering (INCOME/EXPENSE)
    type = django_filters.ChoiceFilter(
        choices=FinancialRecord.RecordType.choices,
        help_text="Filter by transaction type (Income or Expense)."
    )

    class Meta:
        model = FinancialRecord
        fields = ["category", "type"]
