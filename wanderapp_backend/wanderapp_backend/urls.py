"""
URL configuration for wanderapp_backend project.
"""
from django.contrib import admin
from django.urls import path, include

# NEUE, WICHTIGE IMPORTE
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# DIESER NEUE BLOCK IST DIE ENDGÜLTIGE LÖSUNG
# Er weist den Django-Entwicklungsserver an, die Dateien aus Ihrem MEDIA_ROOT-Verzeichnis
# unter der MEDIA_URL bereitzustellen, aber nur, wenn DEBUG=True ist.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)