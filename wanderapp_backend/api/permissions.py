from rest_framework import permissions

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Bei einer Stage prüfen wir den Stage-Ersteller
        if hasattr(obj, 'creator'):
            return obj.creator == request.user
        # Bei einem Trip prüfen wir den Trip-Ersteller
        if hasattr(obj, 'trip') and hasattr(obj.trip, 'creator'):
             return obj.trip.creator == request.user
        return False

# NEU: Berechtigungs-Klasse für Kommentare
class IsAuthorOrStageCreatorOrAdmin(permissions.BasePermission):
    """
    Permission to only allow author of a comment, creator of the stage,
    or an admin to delete it. Everyone can read.
    """
    def has_object_permission(self, request, view, obj):
        # Leseberechtigung für alle
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Löschberechtigung nur für den Autor, den Etappen-Ersteller oder Admins/Staff
        return obj.author == request.user or obj.stage.creator == request.user or request.user.is_staff