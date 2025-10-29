from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Разрешение, позволяющее работать только со своими привычками
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ только если пользователь является владельцем привычки
        return obj.user == request.user
