from importlib import import_module

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from accounts.models import User
from colleges.models import College
from events.models import Event
from registrations.models import Registration


class GmailSMTPSettingsTests(SimpleTestCase):
    def test_smtp_configuration_uses_gmail_with_tls(self):
        project_settings = import_module('config.settings')
        self.assertEqual(
            project_settings.EMAIL_BACKEND,
            'django.core.mail.backends.smtp.EmailBackend',
        )
        self.assertEqual(project_settings.EMAIL_HOST, 'smtp.gmail.com')
        self.assertEqual(project_settings.EMAIL_PORT, 587)
        self.assertTrue(project_settings.EMAIL_USE_TLS)


class OrganizerRegistrationNotificationTests(TestCase):
    def setUp(self):
        self.college = College.objects.create(
            name='Apex Institute of Technology',
            code='AIT',
            city='Indore',
            email='contact@ait.edu',
        )
        self.organizer = User.objects.create_user(
            username='event_organizer',
            email='organizer@ait.edu',
            password='TestPassword123!',
            first_name='Shivam',
            role='organizer',
            college=self.college,
        )
        self.other_organizer = User.objects.create_user(
            username='other_organizer',
            email='other@ait.edu',
            password='TestPassword123!',
            role='organizer',
            college=self.college,
        )
        self.student = User.objects.create_user(
            username='registered_student',
            email='student@ait.edu',
            password='TestPassword123!',
            first_name='Asha',
            last_name='Patel',
            role='student',
            college=self.college,
        )
        self.event = self.create_event('Shivam Hackathon', self.organizer)
        self.other_event = self.create_event('Other Organizer Event', self.other_organizer)
        self.client = APIClient()

    def create_event(self, title, organizer):
        return Event.objects.create(
            title=title,
            description='Event for notification testing',
            organizer=organizer,
            college=self.college,
            venue='Tech Auditorium',
            date='2026-11-15',
            start_time='09:00:00',
            end_time='17:00:00',
            capacity=100,
        )

    def test_student_registration_appears_only_for_event_organizer_newest_first(self):
        registration_url = reverse('registration-create')
        self.client.force_authenticate(user=self.student)
        first_response = self.client.post(
            registration_url,
            {'event': self.event.pk},
            format='json',
        )
        second_response = self.client.post(
            registration_url,
            {'event': self.other_event.pk},
            format='json',
        )
        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 201)

        first_registration = Registration.objects.get(
            student=self.student,
            event=self.event,
        )
        second_registration = Registration.objects.get(
            student=self.student,
            event=self.other_event,
        )
        current_time = timezone.now()
        Registration.objects.filter(pk=first_registration.pk).update(
            registered_at=current_time - timedelta(minutes=2),
        )
        Registration.objects.filter(pk=second_registration.pk).update(
            registered_at=current_time - timedelta(minutes=1),
        )

        self.client.force_authenticate(user=self.organizer)
        response = self.client.get(reverse('organizer-registration-notifications'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_title'], 'Shivam Hackathon')
        self.assertEqual(response.data[0]['student_name'], 'Asha Patel')
        self.assertEqual(response.data[0]['id'], first_registration.pk)
        self.assertIn('registered_at', response.data[0])

    def test_students_cannot_access_organizer_notifications(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(reverse('organizer-registration-notifications'))

        self.assertEqual(response.status_code, 403)
