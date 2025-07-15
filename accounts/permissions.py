# accounts/permissions.py

from rest_framework import permissions

class IsOwnerOfProfile(permissions.BasePermission):
    """
    Custom permission so only the owner of a profile
    can update or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
