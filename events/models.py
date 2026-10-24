
# Create your models here.
from django.db import models
from accounts.models import User
from colleges.models import College


class Event(models.Model):

    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='events'
    )

    venue = models.CharField(max_length=200)

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    capacity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title