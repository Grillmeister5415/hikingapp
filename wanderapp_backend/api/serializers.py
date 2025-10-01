from rest_framework import serializers
from django.contrib.gis.geos import LineString, Point
from .models import Trip, Stage, User, TrackPoint, Comment, Hut, Photo, Surfboard
from datetime import timedelta

# ===================================================================
# HELPER SERIALIZERS (Your existing code, unchanged)
# ===================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_quick_user']

class TrackPointCreateSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    ele = serializers.FloatField(required=False, allow_null=True)
    time = serializers.DateTimeField(required=False, allow_null=True)

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'stage', 'text', 'timestamp', 'author']
        extra_kwargs = {'stage': {'write_only': True}}

class HutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hut
        fields = ['id', 'name', 'link']

class PhotoSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Photo
        fields = [
            'id', 'caption', 'creator', 'uploaded_at',
            'original', 'original_width', 'original_height',
            'display', 'thumbnail',
            'display_webp', 'thumbnail_webp'
        ]
        read_only_fields = ['creator']

class SurfboardSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Surfboard
        fields = ['id', 'name', 'board_type', 'length', 'owner', 'owner_id', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Auto-assign owner to current user if not provided
        if 'owner_id' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        else:
            owner_id = validated_data.pop('owner_id')
            validated_data['owner_id'] = owner_id
        return super().create(validated_data)

class HutCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hut
        fields = ['name', 'link']

class PartnerStatSerializer(serializers.ModelSerializer):
    hike_count = serializers.IntegerField()
    class Meta:
        model = User
        fields = ['id', 'username', 'hike_count']


# ===================================================================
# COMPLEX SERIALIZERS (Your existing StageSerializer is preserved)
# ===================================================================

class StageSerializer(serializers.ModelSerializer):
    track = serializers.SerializerMethodField()
    track_points = TrackPointCreateSerializer(many=True, write_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), source='participants', required=False
    )
    photos = PhotoSerializer(many=True, read_only=True)
    surfboard = SurfboardSerializer(read_only=True)
    surfboard_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Surfboard.objects.all(), source='surfboard', required=False, allow_null=True
    )

    class Meta:
        model = Stage
        fields = [
            'id', 'name', 'date', 'description', 'trip', 'creator', 'participants', 'participants_ids',
            'activity_type',
            'manual_duration', 'manual_length_km', 'manual_elevation_gain', 'manual_elevation_loss',
            'calculated_length_km', 'calculated_elevation_gain', 'calculated_elevation_loss', 'calculated_duration',
            'external_link', 'track', 'track_points', 'comments', 'photos',
            # Surf-specific fields
            'surf_spot', 'time_in_water', 'surfboard_used', 'surfboard', 'surfboard_id', 'wave_height', 'wave_quality',
            'water_temperature', 'waves_caught', 'tide_stage', 'tide_movement',
            'swell_direction', 'wind_direction', 'wave_energy'
        ]
        extra_kwargs = { 'trip': {'required': False} }

    def get_track(self, obj):
        points = obj.track_points.order_by('timestamp').values_list('location', flat=True)
        if not points: return None
        return {'type': 'LineString', 'coordinates': LineString(list(points)).coords}

    def _handle_gpx_data(self, stage, track_points_data):
        stage.track_points.all().delete()
        points_to_create = []
        if track_points_data:
            for point_data in track_points_data:
                points_to_create.append(
                    TrackPoint(
                        stage=stage,
                        location=Point(point_data['lon'], point_data['lat'], srid=4326),
                        elevation=point_data.get('ele'),
                        timestamp=point_data.get('time')
                    )
                )
            if points_to_create:
                TrackPoint.objects.bulk_create(points_to_create)
            try:
                import gpxpy
                gpx = gpxpy.gpx.GPX()
                gpx_track = gpxpy.gpx.GPXTrack()
                gpx.tracks.append(gpx_track)
                gpx_segment = gpxpy.gpx.GPXTrackSegment()
                gpx_track.segments.append(gpx_segment)
                for point_data in track_points_data:
                    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
                        latitude=point_data['lat'], longitude=point_data['lon'], elevation=point_data.get('ele')
                    ))
                stage.calculated_length_km = round(gpx.length_3d() / 1000, 2)
                uphill, downhill = gpx.get_uphill_downhill()
                stage.calculated_elevation_gain = round(uphill)
                stage.calculated_elevation_loss = round(downhill)
                duration_in_seconds = gpx.get_duration()
                if duration_in_seconds:
                    stage.calculated_duration = timedelta(seconds=duration_in_seconds)
            except Exception:
                stage.calculated_length_km, stage.calculated_elevation_gain, stage.calculated_elevation_loss, stage.calculated_duration = None, None, None, None
        else:
            stage.calculated_length_km, stage.calculated_elevation_gain, stage.calculated_elevation_loss, stage.calculated_duration = None, None, None, None
        stage.save()

    def create(self, validated_data):
        track_points_data = validated_data.pop('track_points', [])
        participants_data = validated_data.pop('participants', [])
        stage = Stage.objects.create(**validated_data)
        if participants_data:
            stage.participants.set(participants_data)
        self._handle_gpx_data(stage, track_points_data)
        return stage

    def update(self, instance, validated_data):
        track_points_data = validated_data.pop('track_points', None)
        participants_data = validated_data.pop('participants', None)
        instance = super().update(instance, validated_data)
        if participants_data is not None:
            instance.participants.set(participants_data)
        if track_points_data is not None:
            self._handle_gpx_data(instance, track_points_data)
        return instance

class TripListSerializer(serializers.ModelSerializer):
    """
    Based on your original TripSerializer but with the heavy 'stages' field removed.
    This guarantees all other fields and annotations are handled correctly.
    """
    participants = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    huts = HutSerializer(many=True, read_only=True)
    country = serializers.SerializerMethodField()
    country_display = serializers.CharField(source='get_country_display', read_only=True)
    
    # All your annotated fields, correctly defined as read-only
    total_distance = serializers.FloatField(read_only=True)
    total_gain = serializers.IntegerField(read_only=True)
    total_loss = serializers.IntegerField(read_only=True)
    total_duration = serializers.DurationField(read_only=True)
    
    # Surf-specific totals
    total_surf_time = serializers.DurationField(read_only=True)
    total_wave_count = serializers.IntegerField(read_only=True)
    unique_surf_spots_count = serializers.IntegerField(read_only=True)
    
    # Stage count for different activity types
    stage_count = serializers.SerializerMethodField()
    surf_session_count = serializers.SerializerMethodField()
    
    def get_country(self, obj):
        return str(obj.country) if obj.country else ''
    
    def get_stage_count(self, obj):
        return obj.stages.count()
    
    def get_surf_session_count(self, obj):
        return obj.stages.filter(activity_type='SURFING').count()

    class Meta:
        model = Trip
        # These are the fields from your original serializer, minus 'stages' and write-only fields
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'activity_type', 'creator', 
            'participants', 'huts', 'country', 'country_display', 'total_distance', 'total_gain', 'total_loss', 'total_duration',
            'total_surf_time', 'total_wave_count', 'unique_surf_spots_count', 'stage_count', 'surf_session_count'
        ]

class TripDetailSerializer(serializers.ModelSerializer):
    """ This is your full, original TripSerializer used for creating, updating, and viewing a single trip. """
    participants = UserSerializer(many=True, read_only=True)
    stages = StageSerializer(many=True, read_only=True) # Includes the heavy stages data
    creator = UserSerializer(read_only=True)
    huts = HutSerializer(many=True, read_only=True)
    country = serializers.SerializerMethodField()
    country_display = serializers.CharField(source='get_country_display', read_only=True)
    
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), source='participants', required=False
    )
    huts_data = HutCreateSerializer(many=True, write_only=True, required=False)
    country_code = serializers.CharField(write_only=True, required=False, source='country')

    total_distance = serializers.FloatField(read_only=True)
    total_gain = serializers.IntegerField(read_only=True)
    total_loss = serializers.IntegerField(read_only=True)
    total_duration = serializers.DurationField(read_only=True)
    
    # Surf-specific totals
    total_surf_time = serializers.DurationField(read_only=True)
    total_wave_count = serializers.IntegerField(read_only=True)
    unique_surf_spots_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'activity_type', 'creator', 
            'participants', 'stages', 'huts', 'country', 'country_display', 'total_distance', 'total_gain', 'total_loss', 'total_duration',
            'total_surf_time', 'total_wave_count', 'unique_surf_spots_count', 'participants_ids', 'huts_data', 'country_code'
        ]
    
    def get_country(self, obj):
        return str(obj.country) if obj.country else ''
    
    def validate(self, data):
        if data.get('activity_type') == 'SURFING' and not data.get('country'):
            raise serializers.ValidationError("Country is required for surf trips")
        return data
    
    def create(self, validated_data):
        huts_data = validated_data.pop('huts_data', [])
        participants = validated_data.pop('participants', [])
        trip = Trip.objects.create(**validated_data)
        if participants:
            trip.participants.set(participants)
        for hut_data in huts_data:
            Hut.objects.create(trip=trip, **hut_data)
        return trip
    
    def update(self, instance, validated_data):
        huts_data = validated_data.pop('huts_data', [])
        participants = validated_data.pop('participants', None)
        instance = super().update(instance, validated_data)
        if participants is not None:
            instance.participants.set(participants)
        instance.huts.all().delete()
        for hut_data in huts_data:
            Hut.objects.create(trip=instance, **hut_data)
        return instance