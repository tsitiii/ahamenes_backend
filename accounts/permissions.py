from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'super_admin')

class IsTeamAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and 
            request.user.role in ['team_admin', 'super_admin']
        )

class IsTeamManager(permissions.BasePermission):
    """
    Allows super_admin full access, and team_admin access only to their own team.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['team_admin', 'super_admin'])

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        # For Team object
        if hasattr(obj, 'id') and request.user.team_id == obj.id:
            return True
        return False
