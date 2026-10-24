# Create your models here.
from django.db import models
from accounts.models import User
from events.models import Event


class Registration(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'event'],
                name='unique_student_event'
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.event.title}"

