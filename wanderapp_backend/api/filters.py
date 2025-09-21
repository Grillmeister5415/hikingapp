# wanderapp_backend/api/filters.py
import django_filters
from django.db import models
from .models import Trip, User

class TripFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_search', label="Text Search")
    from_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label='Start Date From')
    to_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label='End Date To')
    
    # Activity type filter for category-based separation
    activity_type = django_filters.ChoiceFilter(choices=Trip.ACTIVITY_CHOICES, label="Activity Type")
    
    # This now correctly corresponds to the method below
    is_creator = django_filters.BooleanFilter(method='filter_is_creator')

    # The participants filter from your original file
    participants = django_filters.ModelMultipleChoiceFilter(
        field_name='participants__id',
        to_field_name='id',
        queryset=User.objects.all(),
        widget=django_filters.widgets.CSVWidget,
        conjoined=True
    )

    class Meta:
        model = Trip
        fields = ['search', 'participants', 'from_date', 'to_date', 'activity_type', 'is_creator']

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) | models.Q(description__icontains=value)
        ).distinct()

    # RENAMED METHOD: This will now only be called when '?is_creator=true' is in the URL.
    def filter_is_creator(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(creator=self.request.user)
        return queryset