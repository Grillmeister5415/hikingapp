# wanderapp_backend/api/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, Count, Value, FloatField, DurationField, Q
from django.db.models.functions import Coalesce
from datetime import timedelta
from .models import Trip, Stage, Comment, TrackPoint, Hut, User, Photo

# WICHTIG: Die korrekten Serializer für Liste/Detail importieren
from .serializers import TripListSerializer, TripDetailSerializer, StageSerializer, CommentSerializer, HutSerializer, UserSerializer, PartnerStatSerializer, PhotoSerializer
from .pagination import StandardResultsSetPagination # Unser Paginierungs-Modul
from .permissions import IsCreatorOrReadOnly, IsAuthorOrStageCreatorOrAdmin
from .filters import TripFilter
from .image_processing import process_and_save_photo


class TripViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCreatorOrReadOnly]
    filterset_class = TripFilter
    pagination_class = StandardResultsSetPagination

    # We use your original get_queryset to ensure all annotations are present
    def get_queryset(self):
        queryset = Trip.objects.all().annotate(
            total_duration=Sum(Coalesce('stages__calculated_duration', 'stages__manual_duration', Value(timedelta(0)))),
            total_distance=Sum(Coalesce('stages__calculated_length_km', 'stages__manual_length_km', Value(0.0))),
            total_gain=Sum(Coalesce('stages__calculated_elevation_gain', 'stages__manual_elevation_gain', Value(0))),
            total_loss=Sum(Coalesce('stages__calculated_elevation_loss', Value(0)))
        ).prefetch_related('participants', 'creator', 'huts')
        return queryset.order_by('-start_date')

    # This method correctly chooses the serializer for the view
    def get_serializer_class(self):
        if self.action == 'list':
            return TripListSerializer # Use the updated lightweight serializer for the list
        return TripDetailSerializer # Use the full serializer for everything else

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photos(self, request, pk=None):
        stage = self.get_object()
        if stage.creator != request.user and not request.user.is_staff:
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        
        uploaded_photos_data = []
        for file in request.FILES.getlist('photos'):
            photo = process_and_save_photo(file, stage, request.user)
            uploaded_photos_data.append(PhotoSerializer(photo, context={'request': request}).data)
        
        return Response(uploaded_photos_data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrStageCreatorOrAdmin]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class HutViewSet(viewsets.ModelViewSet):
    queryset = Hut.objects.all()
    serializer_class = HutSerializer
    permission_classes = [IsAuthenticated]

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsCreatorOrReadOnly]

    def perform_destroy(self, instance):
        instance.original.delete(save=False)
        instance.display.delete(save=False)
        instance.thumbnail.delete(save=False)
        instance.display_webp.delete(save=False)
        instance.thumbnail_webp.delete(save=False)
        instance.delete()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try: user = User.objects.get(pk=pk)
            except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)
        else: user = request.user
        user_stages = Stage.objects.filter(trip__participants=user).distinct()
        trip_count = Trip.objects.filter(participants=user).distinct().count()
        stage_count = user_stages.count()
        stats = user_stages.aggregate(
            total_km=Sum(Coalesce('calculated_length_km', 'manual_length_km', Value(0.0))),
            total_elevation=Sum(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0))),
            total_loss=Sum(Coalesce('calculated_elevation_loss', Value(0))),
            total_duration=Sum(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))))
        )
        stats_data = {
            'username': user.username,
            'trip_count': trip_count,
            'stage_count': stage_count,
            'total_km': round(stats.get('total_km') or 0, 2),
            'total_elevation': stats.get('total_elevation') or 0,
            'total_loss': stats.get('total_loss') or 0,
            'total_duration': (stats.get('total_duration') or timedelta(0)).total_seconds(),
        }
        return Response(stats_data)
        
class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try: user = User.objects.get(pk=pk)
            except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)
        else: user = request.user
        user_stages = Stage.objects.filter(trip__participants=user).distinct()
        longest_stage_km = user_stages.order_by(Coalesce('calculated_length_km', 'manual_length_km', Value(0)).desc()).first()
        highest_stage_gain = user_stages.order_by(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0)).desc()).first()
        longest_stage_duration = user_stages.order_by(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))).desc()).first()
        user_trips = Trip.objects.filter(participants=user)
        top_partners = User.objects.filter(
            participated_trips__in=user_trips
        ).exclude(pk=user.pk).annotate(
            hike_count=Count('participated_trips', filter=Q(participated_trips__in=user_trips))
        ).order_by('-hike_count')[:3]
        data = {
            'longest_stage_by_km': StageSerializer(longest_stage_km, context={'request': request}).data if longest_stage_km else None,
            'highest_stage_by_gain': StageSerializer(highest_stage_gain, context={'request': request}).data if highest_stage_gain else None,
            'longest_stage_by_duration': StageSerializer(longest_stage_duration, context={'request': request}).data if longest_stage_duration else None,
            'top_partners': PartnerStatSerializer(top_partners, many=True).data
        }
        return Response(data)