from rest_framework import serializers

from registrations.models import Registration


class OrganizerRegistrationNotificationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ['id', 'event_title', 'student_name', 'registered_at']

    def get_student_name(self, registration):
        return registration.student.get_full_name() or registration.student.username
