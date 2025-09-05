from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Trip(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(User, related_name='participated_trips')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    def __str__(self): return self.name

class Hut(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='huts')
    name = models.CharField(max_length=200)
    link = models.URLField(max_length=500, blank=True)
    def __str__(self): return self.name

class Stage(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stages')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # Das fehlerhafte "participants"-Feld ist hier endgültig entfernt.
    name = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)
    manual_duration = models.DurationField(null=True, blank=True)
    manual_length_km = models.FloatField(null=True, blank=True)
    manual_elevation_gain = models.IntegerField(null=True, blank=True)
    calculated_length_km = models.FloatField(null=True, blank=True)
    calculated_elevation_gain = models.IntegerField(null=True, blank=True)
    calculated_elevation_loss = models.IntegerField(null=True, blank=True)
    calculated_duration = models.DurationField(null=True, blank=True)
    external_link = models.URLField(max_length=500, blank=True)
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