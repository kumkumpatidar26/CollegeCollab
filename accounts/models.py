

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from colleges.models import College


class User(AbstractUser):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    college = models.ForeignKey(
    College,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='users'
)

    def __str__(self):
        return self.username



class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    mobile = models.CharField(max_length=15)
    course = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username

class OrganizerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='organizer_profile'
    )
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
