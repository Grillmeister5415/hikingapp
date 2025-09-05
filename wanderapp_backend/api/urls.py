from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, StageViewSet, UserStatsView, CommentViewSet, HutViewSet, UserViewSet, DashboardDataView, PhotoViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'huts', HutViewSet, basename='hut')
router.register(r'users', UserViewSet, basename='user')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', UserStatsView.as_view(), name='my-stats'),
    path('stats/<int:pk>/', UserStatsView.as_view(), name='user-stats'),
    # NEU: Zwei Routen für die Dashboard-Daten
    path('dashboard-data/', DashboardDataView.as_view(), name='my-dashboard-data'),
    path('dashboard-data/<int:pk>/', DashboardDataView.as_view(), name='user-dashboard-data'),
]