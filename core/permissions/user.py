from users.models import User
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role_management == 'ADMIN'

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id