# wanderapp_backend/api/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, Count, Value, FloatField, DurationField, Q, Case, When, Avg, Min, Max, Subquery, OuterRef
from django.db.models.functions import Coalesce
from datetime import timedelta
from .models import Trip, Stage, Comment, TrackPoint, Hut, User, Photo, Surfboard, SurfSpot
from django_countries import countries

# WICHTIG: Die korrekten Serializer für Liste/Detail importieren
from .serializers import TripListSerializer, TripDetailSerializer, StageSerializer, CommentSerializer, HutSerializer, UserSerializer, PartnerStatSerializer, PhotoSerializer, SurfboardSerializer, SurfSpotSerializer
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
            # Hiking/Running totals - using subqueries to prevent duplication from stage-level filtering
            total_duration=Subquery(
                Stage.objects.filter(trip=OuterRef('pk')).values('trip').annotate(
                    total=Sum(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))))
                ).values('total')[:1]
            ),
            total_distance=Subquery(
                Stage.objects.filter(trip=OuterRef('pk')).values('trip').annotate(
                    total=Sum(Coalesce('calculated_length_km', 'manual_length_km', Value(0.0)))
                ).values('total')[:1]
            ),
            total_gain=Subquery(
                Stage.objects.filter(trip=OuterRef('pk')).values('trip').annotate(
                    total=Sum(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0)))
                ).values('total')[:1]
            ),
            total_loss=Subquery(
                Stage.objects.filter(trip=OuterRef('pk')).values('trip').annotate(
                    total=Sum(Coalesce('calculated_elevation_loss', Value(0)))
                ).values('total')[:1]
            ),

            # Surfing totals - using subqueries to prevent duplication
            total_surf_time=Subquery(
                Stage.objects.filter(trip=OuterRef('pk'), activity_type='SURFING').values('trip').annotate(
                    total=Sum(Coalesce('time_in_water', Value(timedelta(0))))
                ).values('total')[:1]
            ),
            total_wave_count=Subquery(
                Stage.objects.filter(trip=OuterRef('pk'), activity_type='SURFING').values('trip').annotate(
                    total=Sum(Coalesce('waves_caught', Value(0)))
                ).values('total')[:1]
            ),
            unique_surf_spots_count=Subquery(
                Stage.objects.filter(
                    trip=OuterRef('pk'),
                    activity_type='SURFING',
                    surf_spot__isnull=False
                ).exclude(surf_spot='').values('trip').annotate(
                    count=Count('surf_spot', distinct=True)
                ).values('count')[:1]
            )
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

class SurfboardViewSet(viewsets.ModelViewSet):
    serializer_class = SurfboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own surfboards
        return Surfboard.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign owner to current user
        serializer.save(owner=self.request.user)

class SurfSpotViewSet(viewsets.ModelViewSet):
    serializer_class = SurfSpotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own surf spots
        return SurfSpot.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign owner to current user
        serializer.save(owner=self.request.user)

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

    @action(detail=False, methods=['post'])
    def quick_create(self, request):
        """Create a lightweight user with just a username"""
        username = request.data.get('username', '').strip()

        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user with auto-generated email
        email = f"{username}@temp.wanderapp.local"

        # Ensure unique email
        counter = 1
        while User.objects.filter(email=email).exists():
            email = f"{username}{counter}@temp.wanderapp.local"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            is_quick_user=True,
            password=None  # No password for quick users
        )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by username"""
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return Response({'users': []})

        users = User.objects.filter(
            username__icontains=query
        ).order_by('username')[:10]  # Limit to 10 results

        serializer = self.get_serializer(users, many=True)
        return Response({'users': serializer.data})

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try: user = User.objects.get(pk=pk)
            except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)
        else: user = request.user

        # Get filters from query parameters
        activity_type = request.GET.get('activity_type')
        year = request.GET.get('year')

        user_stages = Stage.objects.filter(trip__participants=user).distinct()

        # Apply activity type filter if provided
        if activity_type:
            user_stages = user_stages.filter(activity_type=activity_type)

        # Apply year filter if provided
        if year:
            try:
                year_int = int(year)
                user_stages = user_stages.filter(date__year=year_int)
            except ValueError:
                pass  # Invalid year, ignore filter

        # Filter trips by activity type and year if provided
        user_trips = Trip.objects.filter(participants=user).distinct()
        if activity_type:
            user_trips = user_trips.filter(activity_type=activity_type)
        if year:
            try:
                year_int = int(year)
                # Include trips if start OR end date is in the year
                user_trips = user_trips.filter(
                    Q(start_date__year=year_int) | Q(end_date__year=year_int)
                )
            except ValueError:
                pass  # Invalid year, ignore filter
        trip_count = user_trips.count()
        stage_count = user_stages.count()
        
        # Overall stats
        stats = user_stages.aggregate(
            total_km=Sum(Coalesce('calculated_length_km', 'manual_length_km', Value(0.0))),
            total_elevation=Sum(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0))),
            total_loss=Sum(Coalesce('calculated_elevation_loss', Value(0))),
            total_duration=Sum(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))))
        )
        
        # Activity-specific stats
        hiking_stages = user_stages.filter(activity_type='HIKING')
        surfing_stages = user_stages.filter(activity_type='SURFING')
        hiking_trips = user_trips.filter(activity_type='HIKING')
        surfing_trips = user_trips.filter(activity_type='SURFING')

        hiking_stats = hiking_stages.aggregate(
            count=Count('id'),
            total_km=Sum(Coalesce('calculated_length_km', 'manual_length_km', Value(0.0))),
            total_elevation=Sum(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0))),
            total_loss=Sum(Coalesce('calculated_elevation_loss', Value(0))),
            total_duration=Sum(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))))
        )

        surfing_stats = surfing_stages.aggregate(
            count=Count('id'),
            total_time_in_water=Sum(Coalesce('time_in_water', Value(timedelta(0)))),
            total_waves_caught=Sum(Coalesce('waves_caught', Value(0))),
            avg_water_temp=Avg(Coalesce('water_temperature', Value(0.0))),
            min_water_temp=Min(Coalesce('water_temperature', Value(999.0))),
            max_water_temp=Max(Coalesce('water_temperature', Value(-999.0)))
        )
        
        # Calculate most used surfboard
        most_used_board = None
        if surfing_stages.exists():
            board_counts = surfing_stages.exclude(surfboard__isnull=True).values('surfboard__name').annotate(count=Count('surfboard')).order_by('-count').first()
            if board_counts:
                most_used_board = board_counts['surfboard__name']
        
        stats_data = {
            'username': user.username,
            'trip_count': trip_count,
            'stage_count': stage_count,
            'total_km': round(stats.get('total_km') or 0, 2),
            'total_elevation': stats.get('total_elevation') or 0,
            'total_loss': stats.get('total_loss') or 0,
            'total_duration': (stats.get('total_duration') or timedelta(0)).total_seconds(),
            
            # Activity-specific stats
            'hiking': {
                'trip_count': hiking_trips.count(),
                'stage_count': hiking_stats['count'] or 0,
                'count': hiking_stats['count'] or 0,  # Keep for backward compatibility
                'total_km': round(hiking_stats.get('total_km') or 0, 2),
                'total_elevation': hiking_stats.get('total_elevation') or 0,
                'total_loss': hiking_stats.get('total_loss') or 0,
                'total_duration': (hiking_stats.get('total_duration') or timedelta(0)).total_seconds(),
            },
            'surfing': {
                'trip_count': surfing_trips.count(),
                'stage_count': surfing_stats['count'] or 0,
                'count': surfing_stats['count'] or 0,  # Keep for backward compatibility
                'total_time_in_water': (surfing_stats.get('total_time_in_water') or timedelta(0)).total_seconds(),
                'total_waves_caught': surfing_stats.get('total_waves_caught') or 0,
                'most_used_surfboard': most_used_board,
                'avg_water_temperature': round(surfing_stats.get('avg_water_temp') or 0, 1) if surfing_stats.get('avg_water_temp') else None,
                'min_water_temperature': surfing_stats.get('min_water_temp') if surfing_stats.get('min_water_temp', 999) != 999 else None,
                'max_water_temperature': surfing_stats.get('max_water_temp') if surfing_stats.get('max_water_temp', -999) != -999 else None,
            }
        }
        return Response(stats_data)
        
class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try: user = User.objects.get(pk=pk)
            except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)
        else: user = request.user

        # Get filters from query parameters
        activity_type = request.GET.get('activity_type')
        year = request.GET.get('year')

        user_stages = Stage.objects.filter(trip__participants=user).distinct()

        # Apply activity type filter if provided
        if activity_type:
            user_stages = user_stages.filter(activity_type=activity_type)

        # Apply year filter if provided
        if year:
            try:
                year_int = int(year)
                user_stages = user_stages.filter(date__year=year_int)
            except ValueError:
                pass  # Invalid year, ignore filter
        
        # Overall records
        longest_stage_km = user_stages.order_by(Coalesce('calculated_length_km', 'manual_length_km', Value(0)).desc()).first()
        highest_stage_gain = user_stages.order_by(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0)).desc()).first()
        longest_stage_duration = user_stages.order_by(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))).desc()).first()
        
        # Activity-specific records
        hiking_stages = user_stages.filter(activity_type='HIKING')
        surfing_stages = user_stages.filter(activity_type='SURFING')
        
        # Hiking records
        longest_hike_km = hiking_stages.order_by(Coalesce('calculated_length_km', 'manual_length_km', Value(0)).desc()).first()
        highest_hike_gain = hiking_stages.order_by(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0)).desc()).first()
        longest_hike_duration = hiking_stages.order_by(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))).desc()).first()
        
        # Surfing records
        longest_surf_session = surfing_stages.order_by(Coalesce('time_in_water', Value(timedelta(0))).desc()).first()
        most_waves_caught = surfing_stages.order_by(Coalesce('waves_caught', Value(0)).desc()).first()
        best_wave_quality = surfing_stages.order_by(Coalesce('wave_quality', Value(0)).desc()).first()
        
        # Filter trips by activity type and year if provided
        user_trips = Trip.objects.filter(participants=user)
        if activity_type:
            user_trips = user_trips.filter(activity_type=activity_type)
        if year:
            try:
                year_int = int(year)
                # Include trips if start OR end date is in the year
                user_trips = user_trips.filter(
                    Q(start_date__year=year_int) | Q(end_date__year=year_int)
                )
            except ValueError:
                pass  # Invalid year, ignore filter
        
        top_partners_data = User.objects.filter(
            participated_trips__in=user_trips
        ).exclude(pk=user.pk).annotate(
            total_trips=Count('participated_trips', filter=Q(participated_trips__in=user_trips), distinct=True),
            hiking_count=Count('participated_trips', filter=Q(participated_trips__in=user_trips, participated_trips__activity_type='HIKING'), distinct=True),
            surfing_count=Count('participated_trips', filter=Q(participated_trips__in=user_trips, participated_trips__activity_type='SURFING'), distinct=True)
        ).order_by('-total_trips')[:3]

        # Build partner data with last_together info
        top_partners = []
        for partner in top_partners_data:
            # Find most recent trip together
            last_trip_together = user_trips.filter(participants=partner).order_by('-start_date').first()
            top_partners.append({
                'id': partner.id,
                'username': partner.username,
                'hiking_count': partner.hiking_count,
                'surfing_count': partner.surfing_count,
                'hike_count': partner.total_trips,  # Keep for backward compatibility
                'last_together': {
                    'date': last_trip_together.start_date.isoformat() if last_trip_together else None,
                    'trip_name': last_trip_together.name if last_trip_together else None,
                    'trip_id': last_trip_together.id if last_trip_together else None
                } if last_trip_together else None
            })

        data = {
            'top_partners': top_partners,
        }
        
        # Only include records for hiking or when no filter is applied (surfing should not have records)
        if activity_type != 'SURFING':
            data.update({
                # Overall records
                'longest_stage_by_km': StageSerializer(longest_stage_km, context={'request': request}).data if longest_stage_km else None,
                'highest_stage_by_gain': StageSerializer(highest_stage_gain, context={'request': request}).data if highest_stage_gain else None,
                'longest_stage_by_duration': StageSerializer(longest_stage_duration, context={'request': request}).data if longest_stage_duration else None,
                
                # Activity-specific records
                'hiking_records': {
                    'longest_by_km': StageSerializer(longest_hike_km, context={'request': request}).data if longest_hike_km else None,
                    'highest_by_gain': StageSerializer(highest_hike_gain, context={'request': request}).data if highest_hike_gain else None,
                    'longest_by_duration': StageSerializer(longest_hike_duration, context={'request': request}).data if longest_hike_duration else None,
                },
                'surfing_records': {
                    'longest_session': StageSerializer(longest_surf_session, context={'request': request}).data if longest_surf_session else None,
                    'most_waves_caught': StageSerializer(most_waves_caught, context={'request': request}).data if most_waves_caught else None,
                    'best_wave_quality': StageSerializer(best_wave_quality, context={'request': request}).data if best_wave_quality else None,
                }
            })
        return Response(data)

class DashboardOverviewView(APIView):
    """
    Aggregated dashboard endpoint that combines stats, records, and partners in one call.
    Supports year filtering via ?year=2025 query parameter.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try: user = User.objects.get(pk=pk)
            except User.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)
        else: user = request.user

        # Get year filter from query parameters
        year = request.GET.get('year')

        # Base querysets
        user_stages = Stage.objects.filter(trip__participants=user).distinct()
        user_trips = Trip.objects.filter(participants=user).distinct()

        # Apply year filtering if provided
        if year:
            try:
                year_int = int(year)
                user_stages = user_stages.filter(date__year=year_int)
                # Include trips if start OR end date is in the year (handles year-spanning trips)
                user_trips = user_trips.filter(
                    Q(start_date__year=year_int) | Q(end_date__year=year_int)
                )
            except ValueError:
                pass  # Invalid year, ignore filter

        # Calculate available years from all stages (unfiltered)
        all_user_stages = Stage.objects.filter(trip__participants=user).distinct()
        available_years = list(
            all_user_stages.dates('date', 'year', order='DESC').values_list('date__year', flat=True)
        )

        # Split by activity type
        hiking_stages = user_stages.filter(activity_type='HIKING')
        surfing_stages = user_stages.filter(activity_type='SURFING')
        hiking_trips = user_trips.filter(activity_type='HIKING')
        surfing_trips = user_trips.filter(activity_type='SURFING')

        # Hiking stats
        hiking_stats = hiking_stages.aggregate(
            stage_count=Count('id'),
            total_km=Sum(Coalesce('calculated_length_km', 'manual_length_km', Value(0.0))),
            total_elevation=Sum(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0))),
            total_loss=Sum(Coalesce('calculated_elevation_loss', Value(0))),
            total_duration=Sum(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))))
        )

        # Surfing stats
        surfing_stats = surfing_stages.aggregate(
            stage_count=Count('id'),
            total_time_in_water=Sum(Coalesce('time_in_water', Value(timedelta(0)))),
            total_waves_caught=Sum(Coalesce('waves_caught', Value(0))),
            avg_water_temp=Avg(Coalesce('water_temperature', Value(0.0))),
            min_water_temp=Min(Coalesce('water_temperature', Value(999.0))),
            max_water_temp=Max(Coalesce('water_temperature', Value(-999.0)))
        )

        # Most used surfboard
        most_used_board = None
        if surfing_stages.exists():
            board_counts = surfing_stages.exclude(surfboard__isnull=True).values('surfboard__name').annotate(count=Count('surfboard')).order_by('-count').first()
            if board_counts:
                most_used_board = board_counts['surfboard__name']

        # Hiking records
        longest_hike_km = hiking_stages.order_by(Coalesce('calculated_length_km', 'manual_length_km', Value(0)).desc()).first()
        highest_hike_gain = hiking_stages.order_by(Coalesce('calculated_elevation_gain', 'manual_elevation_gain', Value(0)).desc()).first()
        longest_hike_duration = hiking_stages.order_by(Coalesce('calculated_duration', 'manual_duration', Value(timedelta(0))).desc()).first()

        # Surfing records
        longest_surf_session = surfing_stages.order_by(Coalesce('time_in_water', Value(timedelta(0))).desc()).first()
        most_waves_caught = surfing_stages.order_by(Coalesce('waves_caught', Value(0)).desc()).first()
        best_wave_quality = surfing_stages.order_by(Coalesce('wave_quality', Value(0)).desc()).first()

        # Recent activity
        last_hike = hiking_stages.order_by('-date').first()
        last_surf = surfing_stages.order_by('-date').first()

        # Top partners with last together info
        top_partners_data = User.objects.filter(
            participated_trips__in=user_trips
        ).exclude(pk=user.pk).annotate(
            total_trips=Count('participated_trips', filter=Q(participated_trips__in=user_trips), distinct=True),
            hiking_count=Count('participated_trips', filter=Q(participated_trips__in=user_trips, participated_trips__activity_type='HIKING'), distinct=True),
            surfing_count=Count('participated_trips', filter=Q(participated_trips__in=user_trips, participated_trips__activity_type='SURFING'), distinct=True)
        ).order_by('-total_trips')[:3]

        # Build partner data with last_together info
        top_partners = []
        for partner in top_partners_data:
            # Find most recent trip together
            last_trip_together = user_trips.filter(participants=partner).order_by('-start_date').first()
            top_partners.append({
                'id': partner.id,
                'username': partner.username,
                'hiking_count': partner.hiking_count,
                'surfing_count': partner.surfing_count,
                'last_together': {
                    'date': last_trip_together.start_date.isoformat() if last_trip_together else None,
                    'trip_name': last_trip_together.name if last_trip_together else None,
                    'trip_id': last_trip_together.id if last_trip_together else None
                } if last_trip_together else None
            })

        # Helper function to serialize stage record
        def serialize_record(stage):
            if not stage:
                return None
            return {
                'id': stage.id,
                'name': stage.name,
                'trip_id': stage.trip.id,
                'date': stage.date.isoformat(),
                'calculated_length_km': stage.calculated_length_km,
                'manual_length_km': stage.manual_length_km,
                'calculated_elevation_gain': stage.calculated_elevation_gain,
                'manual_elevation_gain': stage.manual_elevation_gain,
                'calculated_elevation_loss': stage.calculated_elevation_loss,
                'calculated_duration': str(stage.calculated_duration) if stage.calculated_duration else None,
                'manual_duration': str(stage.manual_duration) if stage.manual_duration else None,
                'time_in_water': str(stage.time_in_water) if stage.time_in_water else None,
                'waves_caught': stage.waves_caught,
                'wave_quality': stage.wave_quality
            }

        # Build response
        data = {
            'user': {
                'id': user.id,
                'username': user.username
            },
            'selected_year': int(year) if year else None,
            'available_years': available_years,
            'totals': {
                'trip_count': user_trips.count(),
                'hiking': {
                    'trip_count': hiking_trips.count(),
                    'stage_count': hiking_stats['stage_count'] or 0,
                    'count': hiking_stats['stage_count'] or 0,  # Keep for backward compatibility
                    'total_km': round(hiking_stats.get('total_km') or 0, 2),
                    'total_elevation': hiking_stats.get('total_elevation') or 0,
                    'total_loss': hiking_stats.get('total_loss') or 0,
                    'total_duration': (hiking_stats.get('total_duration') or timedelta(0)).total_seconds()
                },
                'surfing': {
                    'trip_count': surfing_trips.count(),
                    'stage_count': surfing_stats['stage_count'] or 0,
                    'count': surfing_stats['stage_count'] or 0,  # Keep for backward compatibility
                    'total_time_in_water': (surfing_stats.get('total_time_in_water') or timedelta(0)).total_seconds(),
                    'total_waves_caught': surfing_stats.get('total_waves_caught') or 0,
                    'most_used_surfboard': most_used_board,
                    'avg_water_temperature': round(surfing_stats.get('avg_water_temp') or 0, 1) if surfing_stats.get('avg_water_temp') else None,
                    'min_water_temperature': surfing_stats.get('min_water_temp') if surfing_stats.get('min_water_temp', 999) != 999 else None,
                    'max_water_temperature': surfing_stats.get('max_water_temp') if surfing_stats.get('max_water_temp', -999) != -999 else None
                }
            },
            'records': {
                'hiking': {
                    'longest_km': serialize_record(longest_hike_km),
                    'highest_gain': serialize_record(highest_hike_gain),
                    'longest_duration': serialize_record(longest_hike_duration)
                },
                'surfing': {
                    'longest_session': serialize_record(longest_surf_session),
                    'most_waves': serialize_record(most_waves_caught),
                    'best_quality': serialize_record(best_wave_quality)
                }
            },
            'recent_activity': {
                'last_hike': serialize_record(last_hike),
                'last_surf': serialize_record(last_surf)
            },
            'top_partners': top_partners
        }

        return Response(data)

class CountriesAPIView(APIView):
    """
    API endpoint to get country options for surf trips.
    Returns popular surf destinations first, then all other countries.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get popular surf destinations from the Trip model
        surf_destinations = Trip.SURF_DESTINATIONS
        
        # Generate flag emoji for country code
        def get_country_flag(country_code):
            if not country_code or len(country_code) != 2:
                return '🌍'
            return ''.join(chr(ord(char) + 127397) for char in country_code.upper())
        
        # Popular surf destinations with flags
        popular_destinations = []
        for code in surf_destinations:
            country_name = dict(countries)[code] if code in dict(countries) else code
            popular_destinations.append({
                'code': code,
                'name': country_name,
                'flag': get_country_flag(code),
                'display': f"{country_name} {get_country_flag(code)}"
            })
        
        # All other countries (excluding popular destinations)
        all_countries = []
        for code, name in countries:
            if code not in surf_destinations:
                all_countries.append({
                    'code': code,
                    'name': name,
                    'flag': get_country_flag(code),
                    'display': f"{name} {get_country_flag(code)}"
                })
        
        # Sort all countries alphabetically
        all_countries = sorted(all_countries, key=lambda x: x['name'])
        
        return Response({
            'popular_surf_destinations': popular_destinations,
            'all_countries': all_countries
        })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import gpxpy
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_suggestions(request):
    """
    Return search suggestions for autocomplete functionality
    """
    query = request.GET.get('q', '').lower().strip()

    if len(query) < 2:
        return Response({'suggestions': []})

    suggestions = []

    # Search surf spots from SurfSpot model
    surf_spots = SurfSpot.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:5]

    for spot in surf_spots:
        suggestions.append({
            'type': 'surf_spot',
            'label': spot,
            'value': spot,
            'category': 'Surf Spots'
        })

    # Search countries
    countries_with_surf = Trip.objects.filter(
        country__icontains=query,
        activity_type='SURFING'
    ).values_list('country', flat=True).distinct()[:5]

    for country in countries_with_surf:
        if country:
            suggestions.append({
                'type': 'country',
                'label': f'🌍 {country}',
                'value': country,
                'category': 'Countries'
            })

    # Search surfboards from Surfboard model
    surfboards = Surfboard.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:5]

    for board in surfboards:
        suggestions.append({
            'type': 'surfboard',
            'label': board,
            'value': board,
            'category': 'Surfboards'
        })

    # Search participant usernames
    participants = User.objects.filter(
        username__icontains=query,
        participated_trips__activity_type='SURFING'
    ).values_list('username', flat=True).distinct()[:3]

    for participant in participants:
        suggestions.append({
            'type': 'participant',
            'label': f'👤 {participant}',
            'value': participant,
            'category': 'Surfers'
        })

    return Response({'suggestions': suggestions[:15]})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_gpx_metrics(request):
    """
    Calculate metrics from GPX file content using the same logic as the backend serializer
    """
    try:
        gpx_content = request.data.get('gpx_content', '')
        if not gpx_content:
            return Response({'error': 'No GPX content provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Parse GPX content using gpxpy (same as in serializer)
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Convert track points data to GPX points
        track_points_data = request.data.get('track_points', [])
        if not track_points_data:
            return Response({'error': 'No track points provided'}, status=status.HTTP_400_BAD_REQUEST)

        for point_data in track_points_data:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
                latitude=point_data['lat'],
                longitude=point_data['lon'],
                elevation=point_data.get('ele')
            ))

        # Calculate metrics using gpxpy (same as serializer)
        calculated_length_km = round(gpx.length_3d() / 1000, 2)
        uphill, downhill = gpx.get_uphill_downhill()
        calculated_elevation_gain = round(uphill)
        calculated_elevation_loss = round(downhill)

        duration_in_seconds = gpx.get_duration()
        calculated_duration = timedelta(seconds=duration_in_seconds) if duration_in_seconds else None

        # Format duration for display
        duration_formatted = ''
        if calculated_duration:
            total_seconds = int(calculated_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            duration_formatted = f"{hours:02d}:{minutes:02d}"

        return Response({
            'length': calculated_length_km,
            'elevationGain': calculated_elevation_gain,
            'elevationLoss': calculated_elevation_loss,
            'duration': total_seconds if calculated_duration else None,
            'durationFormatted': duration_formatted
        })

    except Exception as e:
        return Response({'error': f'GPX calculation failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)