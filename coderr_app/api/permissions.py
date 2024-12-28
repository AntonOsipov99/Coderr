from rest_framework.permissions import BasePermission, SAFE_METHODS
from user_auth_app.models import BusinessPartner, Customer

class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            business_profile = BusinessPartner.objects.get(user=request.user)
            return business_profile.type == 'business'
        except BusinessPartner.DoesNotExist:
            return False

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
            
        if not request.user.is_authenticated:
            return False
            
        try:
            Customer.objects.get(user=request.user)
            return True
        except Customer.DoesNotExist:
            return False

class IsCustomerOrAdminModification(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Wenn es sich um einen Create-Request handelt, nur Customer erlauben
        if view.action == 'create':
            try:
                Customer.objects.get(user=request.user)
                return True
            except Customer.DoesNotExist:
                return False
                
        # Für Update und Delete: Customer oder Admin erlauben
        if request.user.is_staff:
            return True
            
        try:
            Customer.objects.get(user=request.user)
            return True
        except Customer.DoesNotExist:
            return False