from rest_framework import serializers
from .models import User, StudentProfile, OrganizerProfile


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    # Student details
    mobile = serializers.CharField(
        write_only=True,
        required=False
    )

    course = serializers.CharField(
        write_only=True,
        required=False
    )

    year = serializers.IntegerField(
        write_only=True,
        required=False
    )

    # Organizer details
    designation = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'college',
            'mobile',
            'course',
            'year',
            'designation'
        ]

    def create(self, validated_data):

        mobile = validated_data.pop('mobile', '')
        course = validated_data.pop('course', '')
        year = validated_data.pop('year', 1)
        designation = validated_data.pop('designation', '')

        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        if user.role == 'student':

            StudentProfile.objects.create(
                user=user,
                mobile=mobile,
                course=course,
                year=year
            )

        elif user.role == 'organizer':

            OrganizerProfile.objects.create(
                user=user,
                designation=designation
            )

        return user