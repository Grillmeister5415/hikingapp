from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, StageViewSet, UserStatsView, CommentViewSet, HutViewSet, UserViewSet, DashboardDataView, DashboardOverviewView, PhotoViewSet, SurfboardViewSet, SurfSpotViewSet, CountriesAPIView, search_suggestions, calculate_gpx_metrics

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'huts', HutViewSet, basename='hut')
router.register(r'surfboards', SurfboardViewSet, basename='surfboard')
router.register(r'surfspots', SurfSpotViewSet, basename='surfspot')
router.register(r'users', UserViewSet, basename='user')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', UserStatsView.as_view(), name='my-stats'),
    path('stats/<int:pk>/', UserStatsView.as_view(), name='user-stats'),
    # Dashboard endpoints
    path('dashboard-data/', DashboardDataView.as_view(), name='my-dashboard-data'),
    path('dashboard-data/<int:pk>/', DashboardDataView.as_view(), name='user-dashboard-data'),
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='my-dashboard-overview'),
    path('dashboard/overview/<int:pk>/', DashboardOverviewView.as_view(), name='user-dashboard-overview'),
    # Countries API for surf trips
    path('countries/', CountriesAPIView.as_view(), name='countries'),
    # Search suggestions for autocomplete
    path('search-suggestions/', search_suggestions, name='search-suggestions'),
    # GPX calculations API
    path('calculate-gpx/', calculate_gpx_metrics, name='calculate-gpx'),
]