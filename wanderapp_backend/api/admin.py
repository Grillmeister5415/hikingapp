from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Trip, Stage, User, Hut, Comment, Photo, Surfboard

@admin.register(Surfboard)
class SurfboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'board_type', 'length', 'owner', 'created_at']
    list_filter = ['board_type', 'owner', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'board_type', 'length', 'owner')
        }),
        ('Additional Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Trip)
admin.site.register(Stage)
admin.site.register(User, UserAdmin)
admin.site.register(Hut)
admin.site.register(Comment)
admin.site.register(Photo)