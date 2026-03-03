from rest_framework import permissions


def is_staff(user):
    return user.is_authenticated and user.groups.filter(name="Staff").exists()


def is_client(user):
    return user.is_authenticated and user.groups.filter(name="Clients").exists()


class MoviePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve"):
            return True
        return is_staff(request.user)

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return is_staff(request.user)


class SessionPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve"):
            return True
        return is_staff(request.user)

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return is_staff(request.user)


class ReviewPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve"):
            return True
        if view.action == "create":
            return is_client(request.user)
        if view.action in ("update", "partial_update", "destroy"):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ("list", "retrieve"):
            return True
        if view.action in ("update", "partial_update"):
            return obj.user_id == request.user.id
        if view.action == "destroy":
            return obj.user_id == request.user.id or is_staff(request.user)
        return False
