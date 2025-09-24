from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    is_quick_user = models.BooleanField(default=False, help_text="User created quickly with just a name, without full account setup")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Trip(models.Model):
    ACTIVITY_CHOICES = [
        ('HIKING', 'Hiking'),
        ('SURFING', 'Surfing'),
    ]
    
    # Popular surf destinations for frontend dropdown
    SURF_DESTINATIONS = [
        'AU',  # Australia 🇦🇺
        'BR',  # Brazil 🇧🇷
        'CR',  # Costa Rica 🇨🇷
        'FR',  # France 🇫🇷
        'ID',  # Indonesia 🇮🇩
        'MX',  # Mexico 🇲🇽
        'MA',  # Morocco 🇲🇦
        'NZ',  # New Zealand 🇳🇿
        'PE',  # Peru 🇵🇪
        'PT',  # Portugal 🇵🇹
        'ES',  # Spain 🇪🇸
        'US',  # USA 🇺🇸
        'ZA',  # South Africa 🇿🇦
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_CHOICES, default='HIKING')
    participants = models.ManyToManyField(User, related_name='participated_trips')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    
    # Country field for surf trips (uses django-countries)
    country = CountryField(blank=True, help_text="Country for surf trips")
    
    def __str__(self): return self.name

class Hut(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='huts')
    name = models.CharField(max_length=200)
    link = models.URLField(max_length=500, blank=True)
    def __str__(self): return self.name

class Stage(models.Model):
    ACTIVITY_CHOICES = [
        ('HIKING', 'Hiking'),
        ('SURFING', 'Surfing'),
    ]
    TIDE_STAGE_CHOICES = [
        ('LOW', 'Low'),
        ('MID', 'Mid'),
        ('HIGH', 'High'),
    ]
    TIDE_MOVEMENT_CHOICES = [
        ('RISING', 'Rising'),
        ('FALLING', 'Falling'),
    ]
    DIRECTION_CHOICES = [
        ('N', 'North'),
        ('NE', 'Northeast'), 
        ('E', 'East'),
        ('SE', 'Southeast'),
        ('S', 'South'),
        ('SW', 'Southwest'),
        ('W', 'West'),
        ('NW', 'Northwest'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stages')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # Das fehlerhafte "participants"-Feld ist hier endgültig entfernt.
    name = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)
    
    # Activity type field - defaults to HIKING for backwards compatibility
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_CHOICES, default='HIKING')
    
    # Existing fields for hiking/running
    manual_duration = models.DurationField(null=True, blank=True)
    manual_length_km = models.FloatField(null=True, blank=True)
    manual_elevation_gain = models.IntegerField(null=True, blank=True)
    manual_elevation_loss = models.IntegerField(null=True, blank=True)
    calculated_length_km = models.FloatField(null=True, blank=True)
    calculated_elevation_gain = models.IntegerField(null=True, blank=True)
    calculated_elevation_loss = models.IntegerField(null=True, blank=True)
    calculated_duration = models.DurationField(null=True, blank=True)
    external_link = models.URLField(max_length=500, blank=True)
    
    # Surf-specific fields (all optional for backwards compatibility)
    surf_spot = models.CharField(max_length=200, blank=True, help_text="Name or description of surf spot")
    time_in_water = models.DurationField(null=True, blank=True, help_text="Time spent surfing")
    surfboard_used = models.CharField(max_length=100, blank=True, help_text="Type/description of surfboard")
    wave_height = models.FloatField(null=True, blank=True, help_text="Wave height in meters")
    wave_quality = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Wave quality rating (1-5)"
    )
    water_temperature = models.FloatField(null=True, blank=True, help_text="Water temperature in Celsius")
    waves_caught = models.IntegerField(null=True, blank=True, help_text="Number of waves caught")
    tide_stage = models.CharField(max_length=5, choices=TIDE_STAGE_CHOICES, blank=True)
    tide_movement = models.CharField(max_length=7, choices=TIDE_MOVEMENT_CHOICES, blank=True)
    
    # Additional surf conditions
    swell_direction = models.CharField(max_length=2, choices=DIRECTION_CHOICES, blank=True, help_text="Primary swell direction")
    wind_direction = models.CharField(max_length=2, choices=DIRECTION_CHOICES, blank=True, help_text="Wind direction")
    wave_energy = models.FloatField(null=True, blank=True, help_text="Wave energy/power rating")
    
    def __str__(self): return f"{self.trip.name} - {self.name}"

class TrackPoint(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='track_points')
    location = models.PointField(geography=True, srid=4326)
    elevation = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['timestamp']

class Photo(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='photos')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    caption = models.CharField(max_length=255, blank=True, help_text="Optionale Bildbeschreibung")
    
    # NEU: height_field und width_field für die Dimensionen
    original = models.ImageField(upload_to='photos/originals/', height_field='original_height', width_field='original_width')
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)

    display = models.ImageField(upload_to='photos/display/')
    thumbnail = models.ImageField(upload_to='photos/thumbnails/')
    display_webp = models.ImageField(upload_to='photos/display_webp/')
    thumbnail_webp = models.ImageField(upload_to='photos/thumbnails_webp/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

class Comment(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)