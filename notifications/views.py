from rest_framework import generics

from events.permissions import IsOrganizer
from registrations.models import Registration
from .serializers import OrganizerRegistrationNotificationSerializer


class OrganizerRegistrationNotificationsView(generics.ListAPIView):
    serializer_class = OrganizerRegistrationNotificationSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return (
            Registration.objects
            .filter(event__organizer=self.request.user)
            .select_related('event', 'student')
            .order_by('-registered_at', '-pk')
        )
