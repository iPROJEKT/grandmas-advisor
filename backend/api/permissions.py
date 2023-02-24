from rest_framework.permissions import (
    SAFE_METHODS, 
    BasePermission,
    IsAuthenticatedOrReadOnly
)

class AdminOrReadOnly(BasePermission):
    def has_permission(self, request, obj):
        return (request.method in SAFE_METHODS or request.user.is_staff)