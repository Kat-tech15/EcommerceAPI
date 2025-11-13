from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def create_obj_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHOD:
            return True
        return obj.owner == request.user