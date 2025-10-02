from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Trip, Stage, User, Hut, Comment, Photo, Surfboard, SurfSpot


# ===================================================================
# TRIP ADMIN - Enhanced with activity badges, counts, and filters
# ===================================================================
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity_badge', 'start_date', 'end_date', 'creator', 'participant_count', 'stage_count', 'country']
    list_filter = ['activity_type', 'start_date', 'country', 'creator']
    search_fields = ['name', 'description', 'country']  # For autocomplete
    date_hierarchy = 'start_date'
    filter_horizontal = ['participants']
    autocomplete_fields = ['creator']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'activity_type')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location (Surf Trips)', {
            'fields': ('country',),
            'description': 'Country field is used for surf trips to indicate location'
        }),
        ('People', {
            'fields': ('creator', 'participants')
        }),
    )

    actions = ['duplicate_trip']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _participant_count=Count('participants', distinct=True),
            _stage_count=Count('stages', distinct=True)
        )

    def activity_badge(self, obj):
        """Display activity type with emoji badge"""
        if obj.activity_type == 'HIKING':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">🥾 HIKING</span>'
            )
        elif obj.activity_type == 'SURFING':
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">🏄 SURFING</span>'
            )
        return obj.activity_type
    activity_badge.short_description = 'Activity'
    activity_badge.admin_order_field = 'activity_type'

    def participant_count(self, obj):
        """Display number of participants"""
        return obj._participant_count
    participant_count.short_description = 'Participants'
    participant_count.admin_order_field = '_participant_count'

    def stage_count(self, obj):
        """Display number of stages"""
        return obj._stage_count
    stage_count.short_description = 'Stages'
    stage_count.admin_order_field = '_stage_count'

    def duplicate_trip(self, request, queryset):
        """Duplicate selected trips (without photos)"""
        for trip in queryset:
            # Store original stages
            original_stages = list(trip.stages.all())

            # Duplicate trip
            trip.pk = None
            trip.id = None
            trip.name = f"{trip.name} (Copy)"
            trip.save()

            # Re-add participants (M2M relationships aren't auto-copied)
            for participant in queryset.first().participants.all():
                trip.participants.add(participant)

            # Duplicate stages (without photos)
            for stage in original_stages:
                stage.pk = None
                stage.id = None
                stage.trip = trip
                stage.save()

        self.message_user(request, f"{queryset.count()} trip(s) duplicated successfully (without photos).")
    duplicate_trip.short_description = "Duplicate selected trips"


# ===================================================================
# STAGE ADMIN - Enhanced with activity badges and metrics
# ===================================================================
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity_badge', 'trip', 'date', 'creator', 'distance_display', 'elevation_display', 'photo_count']
    list_filter = ['activity_type', 'date', 'trip__activity_type', 'creator']
    search_fields = ['name', 'description', 'surf_spot']  # For autocomplete
    date_hierarchy = 'date'
    autocomplete_fields = ['creator', 'trip', 'surfboard', 'surf_spot_obj']
    readonly_fields = ['calculated_length_km', 'calculated_elevation_gain', 'calculated_elevation_loss', 'calculated_duration']

    fieldsets = (
        ('Basic Information', {
            'fields': ('trip', 'name', 'date', 'description', 'activity_type', 'creator')
        }),
        ('Hiking Metrics - Manual Entry', {
            'fields': ('manual_duration', 'manual_length_km', 'manual_elevation_gain', 'manual_elevation_loss', 'external_link'),
            'classes': ('collapse',),
            'description': 'Manual metrics take priority over calculated values'
        }),
        ('Hiking Metrics - Calculated (Read-Only)', {
            'fields': ('calculated_duration', 'calculated_length_km', 'calculated_elevation_gain', 'calculated_elevation_loss'),
            'classes': ('collapse',),
        }),
        ('Surf Information', {
            'fields': ('surf_spot', 'surf_spot_obj', 'time_in_water', 'surfboard', 'surfboard_used'),
            'classes': ('collapse',),
        }),
        ('Surf Conditions', {
            'fields': ('wave_height', 'wave_quality', 'wave_energy', 'waves_caught', 'water_temperature', 'tide_stage', 'tide_movement', 'swell_direction', 'wind_direction'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('trip', 'creator', 'surfboard', 'surf_spot_obj').annotate(
            _photo_count=Count('photos', distinct=True)
        )

    def activity_badge(self, obj):
        """Display activity type with emoji badge"""
        if obj.activity_type == 'HIKING':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">🥾</span>'
            )
        elif obj.activity_type == 'SURFING':
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">🏄</span>'
            )
        return obj.activity_type
    activity_badge.short_description = 'Type'
    activity_badge.admin_order_field = 'activity_type'

    def distance_display(self, obj):
        """Display distance (manual or calculated)"""
        if obj.activity_type == 'HIKING':
            distance = obj.manual_length_km or obj.calculated_length_km
            if distance:
                return f"{distance:.1f} km"
        return '-'
    distance_display.short_description = 'Distance'

    def elevation_display(self, obj):
        """Display elevation gain (manual or calculated)"""
        if obj.activity_type == 'HIKING':
            elevation = obj.manual_elevation_gain or obj.calculated_elevation_gain
            if elevation:
                return f"+{elevation} m"
        return '-'
    elevation_display.short_description = 'Elevation'

    def photo_count(self, obj):
        """Display number of photos"""
        return obj._photo_count
    photo_count.short_description = 'Photos'
    photo_count.admin_order_field = '_photo_count'


# ===================================================================
# COMMENT ADMIN - Enhanced with stage and author info
# ===================================================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'author', 'stage', 'timestamp']
    list_filter = ['timestamp', 'author']
    search_fields = ['text']  # For autocomplete
    date_hierarchy = 'timestamp'
    autocomplete_fields = ['author', 'stage']
    readonly_fields = ['timestamp']

    fieldsets = (
        (None, {
            'fields': ('stage', 'author', 'text')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

    def text_preview(self, obj):
        """Show first 80 characters of comment"""
        if len(obj.text) > 80:
            return f"{obj.text[:80]}..."
        return obj.text
    text_preview.short_description = 'Comment'


# ===================================================================
# PHOTO ADMIN - Enhanced with thumbnails and bulk actions
# ===================================================================
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['preview_thumbnail', 'caption_display', 'stage', 'creator', 'dimensions', 'uploaded_at']
    list_filter = ['uploaded_at', 'creator', 'stage__activity_type']
    search_fields = ['caption']  # For autocomplete
    date_hierarchy = 'uploaded_at'
    autocomplete_fields = ['creator', 'stage']
    readonly_fields = ['preview_image', 'original_width', 'original_height', 'uploaded_at', 'original', 'display', 'thumbnail', 'display_webp', 'thumbnail_webp']

    fieldsets = (
        ('Photo Information', {
            'fields': ('stage', 'creator', 'caption', 'preview_image')
        }),
        ('Dimensions', {
            'fields': ('original_width', 'original_height'),
            'classes': ('collapse',)
        }),
        ('File Paths (Read-Only)', {
            'fields': ('original', 'display', 'thumbnail', 'display_webp', 'thumbnail_webp'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['bulk_delete_photos', 'clear_captions']

    def preview_thumbnail(self, obj):
        """Display small thumbnail preview in list"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"/>',
                obj.thumbnail.url
            )
        return '-'
    preview_thumbnail.short_description = 'Preview'

    def preview_image(self, obj):
        """Display larger preview in detail view"""
        if obj.display:
            return format_html(
                '<img src="{}" style="max-width: 600px; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"/>',
                obj.display.url
            )
        return '-'
    preview_image.short_description = 'Image Preview'

    def caption_display(self, obj):
        """Display caption or placeholder"""
        return obj.caption if obj.caption else format_html('<em style="color: #999;">No caption</em>')
    caption_display.short_description = 'Caption'
    caption_display.admin_order_field = 'caption'

    def dimensions(self, obj):
        """Display image dimensions"""
        if obj.original_width and obj.original_height:
            return f"{obj.original_width} × {obj.original_height} px"
        return '-'
    dimensions.short_description = 'Size'

    def bulk_delete_photos(self, request, queryset):
        """Delete selected photos and their files"""
        count = queryset.count()
        for photo in queryset:
            # Delete files
            photo.original.delete(save=False)
            photo.display.delete(save=False)
            photo.thumbnail.delete(save=False)
            photo.display_webp.delete(save=False)
            photo.thumbnail_webp.delete(save=False)
            photo.delete()
        self.message_user(request, f"{count} photo(s) deleted successfully.")
    bulk_delete_photos.short_description = "Delete selected photos (including files)"

    def clear_captions(self, request, queryset):
        """Clear captions from selected photos"""
        count = queryset.update(caption='')
        self.message_user(request, f"Cleared captions from {count} photo(s).")
    clear_captions.short_description = "Clear captions from selected photos"


# ===================================================================
# HUT ADMIN - Enhanced with trip info
# ===================================================================
@admin.register(Hut)
class HutAdmin(admin.ModelAdmin):
    list_display = ['name', 'trip', 'link_display']
    list_filter = ['trip__activity_type', 'trip__start_date']
    search_fields = ['name', 'link']  # For autocomplete
    autocomplete_fields = ['trip']

    fieldsets = (
        (None, {
            'fields': ('trip', 'name', 'link')
        }),
    )

    def link_display(self, obj):
        """Display clickable link if available"""
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff;">🔗 View</a>',
                obj.link
            )
        return '-'
    link_display.short_description = 'Link'


# ===================================================================
# SURFBOARD ADMIN - Enhanced with autocomplete and usage stats
# ===================================================================
@admin.register(Surfboard)
class SurfboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'board_type', 'length', 'owner', 'session_count', 'created_at']
    list_filter = ['board_type', 'owner', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email', 'description']
    autocomplete_fields = ['owner']
    readonly_fields = ['created_at', 'updated_at', 'session_count_display']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'board_type', 'length', 'owner')
        }),
        ('Additional Details', {
            'fields': ('description',)
        }),
        ('Usage Statistics', {
            'fields': ('session_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _session_count=Count('sessions', distinct=True)
        )

    def session_count(self, obj):
        """Display number of surf sessions using this board"""
        return obj._session_count
    session_count.short_description = 'Sessions'
    session_count.admin_order_field = '_session_count'

    def session_count_display(self, obj):
        """Display detailed session count in detail view"""
        count = obj.sessions.count()
        return f"{count} surf session(s) use this board"
    session_count_display.short_description = 'Total Sessions'


# ===================================================================
# SURF SPOT ADMIN - Enhanced with autocomplete and usage stats
# ===================================================================
@admin.register(SurfSpot)
class SurfSpotAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'session_count', 'created_at']
    list_filter = ['owner', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email', 'description']
    autocomplete_fields = ['owner']
    readonly_fields = ['created_at', 'updated_at', 'session_count_display']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner')
        }),
        ('Additional Details', {
            'fields': ('description',)
        }),
        ('Usage Statistics', {
            'fields': ('session_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _session_count=Count('sessions', distinct=True)
        )

    def session_count(self, obj):
        """Display number of surf sessions at this spot"""
        return obj._session_count
    session_count.short_description = 'Sessions'
    session_count.admin_order_field = '_session_count'

    def session_count_display(self, obj):
        """Display detailed session count in detail view"""
        count = obj.sessions.count()
        return f"{count} surf session(s) at this spot"
    session_count_display.short_description = 'Total Sessions'


# ===================================================================
# USER ADMIN - Enhanced with quick user creation
# ===================================================================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_quick_user', 'trip_count', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_quick_user', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    actions = ['create_quick_user']

    # Add is_quick_user to fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('WanderApp Settings', {
            'fields': ('is_quick_user',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _trip_count=Count('created_trips', distinct=True)
        )

    def trip_count(self, obj):
        """Display number of trips created"""
        return obj._trip_count
    trip_count.short_description = 'Trips Created'
    trip_count.admin_order_field = '_trip_count'

    def create_quick_user(self, request, queryset):
        """Helper action to demonstrate quick user creation"""
        self.message_user(
            request,
            "Quick users are created via the API endpoint /api/users/quick_create/. "
            "To create a quick user manually, add a new user and check the 'is_quick_user' field.",
            level='info'
        )
    create_quick_user.short_description = "How to create quick users"
