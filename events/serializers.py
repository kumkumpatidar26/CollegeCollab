from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):

    organizer = serializers.ReadOnlyField(
        source='organizer.id'
    )

    college_name = serializers.CharField(
        source='college.name',
        read_only=True
    )

    def validate(self, data):

        request = self.context.get('request')

        if request and request.user.is_authenticated:

            organizer = request.user
            college = data.get('college')

            if college and organizer.college != college:
                raise serializers.ValidationError(
                    "You can create an event only for your own college."
                )

        return data

    class Meta:

        model = Event

        fields = [
            'id',
            'title',
            'description',
            'organizer',
            'college',
            'college_name',
            'venue',
            'date',
            'start_time',
            'end_time',
            'capacity',
            'status',
            'created_at'
        ]

        read_only_fields = [
            'organizer',
            'college_name',
            'created_at'
        ]