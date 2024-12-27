from rest_framework import permissions
from user_auth_app.models import BusinessPartner

class IsBusinessUser(permissions.BasePermission):
    """
    Custom permission to only allow business users to create offers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            business_profile = BusinessPartner.objects.get(user=request.user)
            return business_profile.type == 'business'
        except BusinessPartner.DoesNotExist:
            return False

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit/delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user