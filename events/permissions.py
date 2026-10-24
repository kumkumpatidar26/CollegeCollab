from rest_framework.permissions import BasePermission


class IsOrganizer(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'organizer'
        )


class IsEventOwnerOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        return (
            request.user.is_authenticated
            and request.user.role == 'organizer'
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        return obj.organizer == request.user