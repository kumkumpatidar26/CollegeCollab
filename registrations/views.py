from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Registration
from .serializers import RegistrationSerializer

from notifications.services import (
    queue_registration_cancellation,
    queue_registration_confirmation,
)


class RegistrationCreateView(generics.CreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        registration = serializer.save(student=self.request.user)
        queue_registration_confirmation(registration)



class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(
            student=self.request.user
        )
class EventRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs['event_id']

        return Registration.objects.filter(
            event_id=event_id,
            event__organizer=self.request.user
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "event_id": int(kwargs['event_id']),
            "registered_count": queryset.count(),
            "registrations": serializer.data
        })

    
class RegistrationDeleteView(generics.DestroyAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(
            student=self.request.user
        )

    def perform_destroy(self, instance):
        queue_registration_cancellation(instance)
        super().perform_destroy(instance)