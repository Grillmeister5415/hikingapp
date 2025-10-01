# wanderapp_backend/api/filters.py
import django_filters
from django.db import models
from .models import Trip, User, Stage

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

    # Surf-specific filters
    surf_spot = django_filters.CharFilter(field_name='stages__surf_spot', lookup_expr='icontains', label="Surf Spot")
    surfboard_type = django_filters.CharFilter(field_name='stages__surfboard__name', lookup_expr='icontains', label="Surfboard Type")
    wave_height_min = django_filters.NumberFilter(field_name='stages__wave_height', lookup_expr='gte', label="Min Wave Height (m)")
    wave_height_max = django_filters.NumberFilter(field_name='stages__wave_height', lookup_expr='lte', label="Max Wave Height (m)")
    wave_quality_min = django_filters.NumberFilter(field_name='stages__wave_quality', lookup_expr='gte', label="Min Wave Quality (1-5)")
    wave_quality_max = django_filters.NumberFilter(field_name='stages__wave_quality', lookup_expr='lte', label="Max Wave Quality (1-5)")
    water_temp_min = django_filters.NumberFilter(field_name='stages__water_temperature', lookup_expr='gte', label="Min Water Temp (°C)")
    water_temp_max = django_filters.NumberFilter(field_name='stages__water_temperature', lookup_expr='lte', label="Max Water Temp (°C)")
    tide_stage = django_filters.ChoiceFilter(field_name='stages__tide_stage', choices=Stage.TIDE_STAGE_CHOICES, label="Tide Stage")
    country_code = django_filters.CharFilter(field_name='country', label="Country Code")

    # Hiking-specific filters
    distance_min = django_filters.NumberFilter(method='filter_distance_min', label="Min Distance (km)")
    distance_max = django_filters.NumberFilter(method='filter_distance_max', label="Max Distance (km)")
    elevation_min = django_filters.NumberFilter(method='filter_elevation_min', label="Min Elevation Gain (m)")
    elevation_max = django_filters.NumberFilter(method='filter_elevation_max', label="Max Elevation Gain (m)")
    duration_min = django_filters.NumberFilter(method='filter_duration_min', label="Min Duration (hours)")
    duration_max = django_filters.NumberFilter(method='filter_duration_max', label="Max Duration (hours)")

    class Meta:
        model = Trip
        fields = ['search', 'participants', 'from_date', 'to_date', 'activity_type', 'is_creator',
                 'surf_spot', 'surfboard_type', 'wave_height_min', 'wave_height_max',
                 'wave_quality_min', 'wave_quality_max', 'water_temp_min', 'water_temp_max', 'tide_stage', 'country_code',
                 'distance_min', 'distance_max', 'elevation_min', 'elevation_max', 'duration_min', 'duration_max']

    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(country__icontains=value) |  # Search country field
            models.Q(stages__surf_spot__icontains=value) |  # Search surf spots
            models.Q(stages__surfboard__name__icontains=value) |  # Search surfboard names
            models.Q(stages__name__icontains=value) |  # Search stage names
            models.Q(stages__description__icontains=value) |  # Search stage descriptions
            models.Q(stages__external_link__icontains=value) |  # Search external links
            models.Q(huts__name__icontains=value) |  # Search hut names
            models.Q(participants__username__icontains=value)  # Search participant names
        ).distinct()

    # RENAMED METHOD: This will now only be called when '?is_creator=true' is in the URL.
    def filter_is_creator(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(creator=self.request.user)
        return queryset

    # Hiking filter methods - prioritize manual values, fallback to calculated
    def filter_distance_min(self, queryset, name, value):
        return queryset.filter(
            models.Q(stages__manual_length_km__gte=value) |
            models.Q(stages__manual_length_km__isnull=True, stages__calculated_length_km__gte=value)
        ).distinct()

    def filter_distance_max(self, queryset, name, value):
        return queryset.filter(
            models.Q(stages__manual_length_km__lte=value) |
            models.Q(stages__manual_length_km__isnull=True, stages__calculated_length_km__lte=value)
        ).distinct()

    def filter_elevation_min(self, queryset, name, value):
        return queryset.filter(
            models.Q(stages__manual_elevation_gain__gte=value) |
            models.Q(stages__manual_elevation_gain__isnull=True, stages__calculated_elevation_gain__gte=value)
        ).distinct()

    def filter_elevation_max(self, queryset, name, value):
        return queryset.filter(
            models.Q(stages__manual_elevation_gain__lte=value) |
            models.Q(stages__manual_elevation_gain__isnull=True, stages__calculated_elevation_gain__lte=value)
        ).distinct()

    def filter_duration_min(self, queryset, name, value):
        from datetime import timedelta
        duration_hours = timedelta(hours=value)
        return queryset.filter(
            models.Q(stages__manual_duration__gte=duration_hours) |
            models.Q(stages__manual_duration__isnull=True, stages__calculated_duration__gte=duration_hours)
        ).distinct()

    def filter_duration_max(self, queryset, name, value):
        from datetime import timedelta
        duration_hours = timedelta(hours=value)
        return queryset.filter(
            models.Q(stages__manual_duration__lte=duration_hours) |
            models.Q(stages__manual_duration__isnull=True, stages__calculated_duration__lte=duration_hours)
        ).distinct()