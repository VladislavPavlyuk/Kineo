from rest_framework import permissions


def is_staff(user):
    # Перевіряємо і авторизацію, і наявність групи Staff
    return user.is_authenticated and user.groups.filter(name="Staff").exists()


def is_client(user):
    # Клієнт - це користувач у групі Clients
    return user.is_authenticated and user.groups.filter(name="Clients").exists()


class MoviePermissions(permissions.BasePermission):
    # Права на рівні endpoint (до завантаження конкретного об'єкта)
    def has_permission(self, request, view):
        # Перегляд фільмів відкритий всім
        if view.action in ("list", "retrieve"):
            return True
        # Створення/редагування/видалення тільки для Staff
        return is_staff(request.user)

    # Права на рівні конкретного об'єкта
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
        # Відгуки читати може будь-хто
        if view.action in ("list", "retrieve"):
            return True
        # Створювати можуть тільки клієнти
        if view.action == "create":
            return is_client(request.user)
        # На update/delete йдемо далі до object-level перевірки
        if view.action in ("update", "partial_update", "destroy"):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ("list", "retrieve"):
            return True
        # Редагувати можна лише свій відгук
        if view.action in ("update", "partial_update"):
            return obj.user_id == request.user.id
        # Видаляти можна свій або (як виняток) Staff
        if view.action == "destroy":
            return obj.user_id == request.user.id or is_staff(request.user)
        return False


class BookingPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create", "update", "partial_update", "destroy"):
            return request.user.is_authenticated and is_client(request.user)
        return False

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class FavoriteMoviePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve", "create", "destroy"):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
