import django_filters
from .models import FinancialRecord

# Domain: records | Purpose: FilterSet for date range, category, and type filtering


class RecordFilter(django_filters.FilterSet):
    # Maps URL parameters to ORM lookups enabling robust front-end slice-and-dice functionality
    date_after = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        help_text="Records on or after this date (YYYY-MM-DD).",
    )
    date_before = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        help_text="Records on or before this date (YYYY-MM-DD).",
    )

    # iexact makes category filtering case-insensitive for end users
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")

    type = django_filters.ChoiceFilter(
        choices=FinancialRecord.RecordType.choices,
        help_text="Filter by transaction type (INCOME or EXPENSE).",
    )

    class Meta:
        model = FinancialRecord
        fields = []
