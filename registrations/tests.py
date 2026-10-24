from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from colleges.models import College
from events.models import Event
from .models import Registration


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='CollegeCollab <notifications@example.com>',
)
class RegistrationEmailNotificationTests(TestCase):
    def setUp(self):
        self.college = College.objects.create(
            name='Apex Institute of Technology',
            code='AIT',
            city='Indore',
            email='contact@ait.edu',
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@ait.edu',
            password='TestPassword123!',
            first_name='Taylor',
            role='student',
            college=self.college,
        )
        self.event = Event.objects.create(
            title='Campus Hackathon',
            description='A campus coding event',
            organizer=User.objects.create_user(
                username='organizer',
                email='organizer@ait.edu',
                password='TestPassword123!',
                role='organizer',
                college=self.college,
            ),
            college=self.college,
            venue='Tech Auditorium',
            date='2026-11-15',
            start_time='09:00:00',
            end_time='17:00:00',
            capacity=100,
        )
        self.client = APIClient()
        token = str(RefreshToken.for_user(self.student).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_registration_sends_one_confirmation_and_duplicate_sends_none(self):
        url = reverse('registration-create')
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                url,
                {'event': self.event.id},
                format='json',
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Event registration confirmed: Campus Hackathon',
        )
        self.assertEqual(mail.outbox[0].to, ['student@ait.edu'])
        self.assertIn('Taylor', mail.outbox[0].body)
        self.assertIn('Tech Auditorium', mail.outbox[0].body)

        duplicate_response = self.client.post(
            url,
            {'event': self.event.id},
            format='json',
        )

        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(len(mail.outbox), 1)

    def test_cancellation_sends_confirmation_email(self):
        registration = Registration.objects.create(
            student=self.student,
            event=self.event,
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                reverse('registration-cancel', kwargs={'pk': registration.pk})
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Event registration cancelled: Campus Hackathon',
        )
        self.assertIn('has been cancelled', mail.outbox[0].body)
        self.assertFalse(Registration.objects.filter(pk=registration.pk).exists())

    def test_email_delivery_failure_does_not_fail_registration(self):
        with patch(
            'notifications.services.send_mail',
            side_effect=SMTPException('SMTP credentials must not be logged'),
        ):
            with self.assertLogs('notifications.services', level='WARNING') as logs:
                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        reverse('registration-create'),
                        {'event': self.event.id},
                        format='json',
                    )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Registration.objects.filter(
                student=self.student,
                event=self.event,
            ).exists()
        )
        self.assertNotIn('SMTP credentials', '\n'.join(logs.output))
