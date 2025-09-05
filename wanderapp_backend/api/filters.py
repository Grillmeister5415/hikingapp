import django_filters
from django.db import models
from .models import Trip, User

class TripFilter(django_filters.FilterSet):
    # Textsuche bleibt unverändert
    search = django_filters.CharFilter(method='filter_by_search', label="Text Search")
    
    # Datumsbereich-Filter bleibt unverändert
    from_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label='Start Date From')
    to_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label='End Date To')
    
    # NEU: Explizite Definition des Teilnehmer-Filters für Multi-Select
    participants = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        widget=django_filters.widgets.CSVWidget,
        conjoined=True  # Dies sorgt für eine UND-Verknüpfung
    )

    class Meta:
        model = Trip
        fields = ['participants']

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) | models.Q(description__icontains=value)
        ).distinct()