from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied 

class IsCustomerOwnership(BasePermission):
    message = 'You are not allowed to access this address'
    def has_object_permission(self, request, view, obj):
        return request.user.customer_profile == obj.customer
          