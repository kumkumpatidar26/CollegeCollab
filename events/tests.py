from django.test import TestCase, Client
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.test import override_settings
from colleges.models import College
from accounts.models import User
from events.models import Event
from registrations.models import Registration


class EventManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.college = College.objects.create(
            name="Apex Institute of Technology",
            code="AIT",
            city="Indore",
            email="contact@ait.edu"
        )
        self.other_college = College.objects.create(
            name="Global Engineering College",
            code="GEC",
            city="Bhopal",
            email="contact@gec.edu"
        )
        # Create organizer user
        self.organizer = User.objects.create_user(
            username="event_host",
            email="host@ait.edu",
            password="HostPassword123!",
            role="organizer",
            college=self.college
        )
        # Create student user
        self.student = User.objects.create_user(
            username="tech_student",
            email="student@ait.edu",
            password="StudentPassword123!",
            role="student",
            college=self.college
        )
        # Generate JWT tokens
        self.organizer_token = str(RefreshToken.for_user(self.organizer).access_token)
        self.student_token = str(RefreshToken.for_user(self.student).access_token)

        self.events_url = reverse('event-list-create')

    def test_list_events_unauthenticated(self):
        # Create an event directly in DB
        Event.objects.create(
            title="Campus Hackathon 2026",
            description="24-hour coding challenge",
            organizer=self.organizer,
            college=self.college,
            venue="Tech Auditorium",
            date="2026-11-15",
            start_time="09:00:00",
            end_time="17:00:00",
            capacity=100
        )
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['title'], "Campus Hackathon 2026")
        self.assertEqual(events[0]['college_name'], "Apex Institute of Technology")
        self.assertEqual(events[0]['capacity'], 100)

    def test_create_event_by_organizer(self):
        payload = {
            "title": "Robotics Championship",
            "description": "Annual bot building and racing battle",
            "college": self.college.id,
            "venue": "Innovation Hub Hall A",
            "date": "2026-12-01",
            "start_time": "10:00:00",
            "end_time": "16:00:00",
            "capacity": 80,
            "status": "upcoming"
        }
        response = self.client.post(
            self.events_url,
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.organizer_token}"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Robotics Championship")
        self.assertEqual(data["organizer"], self.organizer.id)
        self.assertEqual(data["college_name"], self.college.name)

        # Verify DB entry
        event = Event.objects.get(title="Robotics Championship")
        self.assertEqual(event.organizer, self.organizer)
        self.assertEqual(event.capacity, 80)
        self.assertEqual(event.venue, "Innovation Hub Hall A")

    def test_create_event_cross_college_validation(self):
        # Organizer cannot create an event for another college
        payload = {
            "title": "Cross College Event",
            "description": "Attempt to create event for other college",
            "college": self.other_college.id,
            "venue": "GEC Auditorium",
            "date": "2026-12-05",
            "start_time": "10:00:00",
            "end_time": "14:00:00",
            "capacity": 50,
            "status": "upcoming"
        }
        response = self.client.post(
            self.events_url,
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.organizer_token}"
        )
        self.assertEqual(response.status_code, 400)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='CollegeCollab <notifications@example.com>',
)
class EventEmailNotificationTests(TestCase):
    def setUp(self):
        self.college = College.objects.create(
            name='Apex Institute of Technology',
            code='AIT',
            city='Indore',
            email='contact@ait.edu',
        )
        self.organizer = User.objects.create_user(
            username='event_host',
            email='host@ait.edu',
            password='TestPassword123!',
            role='organizer',
            college=self.college,
        )
        self.student = User.objects.create_user(
            username='tech_student',
            email='student@ait.edu',
            password='TestPassword123!',
            role='student',
            college=self.college,
        )
        self.event = Event.objects.create(
            title='Campus Hackathon',
            description='A campus coding event',
            organizer=self.organizer,
            college=self.college,
            venue='Tech Auditorium',
            date='2026-11-15',
            start_time='09:00:00',
            end_time='17:00:00',
            capacity=100,
        )
        Registration.objects.create(student=self.student, event=self.event)
        self.client = Client()
        token = str(RefreshToken.for_user(self.organizer).access_token)
        self.auth_header = f'Bearer {token}'
        self.event_url = reverse('event-detail', kwargs={'pk': self.event.pk})
        self.events_url = reverse('event-list-create')
        self.student_token = str(
            RefreshToken.for_user(self.student).access_token
        )

    def test_changed_event_notifies_registrants_but_noop_does_not(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                self.event_url,
                {'venue': 'Student Center'},
                content_type='application/json',
                HTTP_AUTHORIZATION=self.auth_header,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['student@ait.edu'])
        self.assertEqual(
            mail.outbox[0].subject,
            'Event updated: Campus Hackathon',
        )
        self.assertIn('Student Center', mail.outbox[0].body)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                self.event_url,
                {'venue': 'Student Center'},
                content_type='application/json',
                HTTP_AUTHORIZATION=self.auth_header,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_event_status_cancellation_notifies_registrants(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                self.event_url,
                {'status': 'cancelled'},
                content_type='application/json',
                HTTP_AUTHORIZATION=self.auth_header,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Event cancelled: Campus Hackathon',
        )

    def test_event_deletion_notifies_registrants_as_cancellation(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                self.event_url,
                HTTP_AUTHORIZATION=self.auth_header,
            )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Event cancelled: Campus Hackathon',
        )

    def test_create_event_forbidden_for_student(self):
        payload = {
            "title": "Student Unauthorized Event",
            "description": "Student shouldn't be able to create events",
            "college": self.college.id,
            "venue": "Room 101",
            "date": "2026-12-10",
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "capacity": 30
        }
        response = self.client.post(
            self.events_url,
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.student_token}"
        )
        self.assertEqual(response.status_code, 403)
