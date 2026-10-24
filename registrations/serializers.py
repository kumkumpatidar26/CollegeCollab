from rest_framework import serializers
from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):

    event_title = serializers.CharField(
        source='event.title',
        read_only=True
    )

    event_date = serializers.DateField(
        source='event.date',
        read_only=True
    )

    event_venue = serializers.CharField(
        source='event.venue',
        read_only=True
    )

    event_college = serializers.CharField(
        source='event.college.name',
        read_only=True
    )

    class Meta:
        model = Registration
        fields = [
            'id',
            'student',
            'event',
            'event_title',
            'event_date',
            'event_venue',
            'event_college',
            'registered_at'
        ]

        read_only_fields = [
            'student',
            'registered_at',
            'event_title',
            'event_date',
            'event_venue',
            'event_college'
        ]

    def validate(self, data):

        student = self.context['request'].user
        event = data.get('event')

        if Registration.objects.filter(
            student=student,
            event=event
        ).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )

        if event.registrations.count() >= event.capacity:
            raise serializers.ValidationError(
                "This event is full."
            )

        return data