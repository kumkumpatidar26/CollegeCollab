

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Event
from .serializers import EventSerializer
from .permissions import IsOrganizer , IsEventOwnerOrReadOnly
from notifications.services import queue_event_notification


class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOrganizer()]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventOwnerOrReadOnly]

    def perform_update(self, serializer):
        event = serializer.instance
        tracked_fields = (
            'title',
            'description',
            'college_id',
            'venue',
            'date',
            'start_time',
            'end_time',
            'capacity',
            'status',
        )
        previous_values = {
            field: getattr(event, field)
            for field in tracked_fields
        }
        recipients = list(
            event.registrations.values_list(
                'student__email',
                flat=True,
            ).distinct()
        )

        event = serializer.save()
        changed = any(
            previous_values[field] != getattr(event, field)
            for field in tracked_fields
        )
        if changed:
            queue_event_notification(
                event,
                recipients,
                cancelled=(
                    previous_values['status'] != 'cancelled'
                    and event.status == 'cancelled'
                ),
            )

    def perform_destroy(self, instance):
        recipients = list(
            instance.registrations.values_list(
                'student__email',
                flat=True,
            ).distinct()
        )
        super().perform_destroy(instance)
        queue_event_notification(instance, recipients, cancelled=True)