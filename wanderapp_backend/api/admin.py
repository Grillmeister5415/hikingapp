from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Trip, Stage, User, Hut, Comment, Photo

admin.site.register(Trip)
admin.site.register(Stage)
admin.site.register(User, UserAdmin)
admin.site.register(Hut)
admin.site.register(Comment)
admin.site.register(Photo)