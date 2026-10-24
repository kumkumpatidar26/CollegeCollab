from django.test import TestCase, Client
from django.urls import reverse


class FrontendRouteTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_and_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_events_page_status_and_template(self):
        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_dashboard_page_status_and_template(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/dashboard.html')

    def test_dashboard_uses_django_static_url_for_event_script(self):
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '<script src="/static/event.js"></script>')

    def test_signup_form_elements_present_in_template(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode('utf-8')
        # Check login card and switch link
        self.assertIn('id="loginCard"', content)
        self.assertIn('id="showSignupLink"', content)
        self.assertIn('id="loginAlert"', content)

        # Check signup card and form
        self.assertIn('id="signupCard"', content)
        self.assertIn('id="signupForm"', content)
        self.assertIn('id="showLoginLink"', content)

        # Check role selection
        self.assertIn('id="btnRoleStudent"', content)
        self.assertIn('id="btnRoleOrganizer"', content)
        self.assertIn('id="signupRole"', content)

        # Check common fields
        self.assertIn('id="signupUsername"', content)
        self.assertIn('id="signupEmail"', content)
        self.assertIn('id="signupPassword"', content)
        self.assertIn('id="signupCollege"', content)

        # Check student and organizer specific fields
        self.assertIn('id="studentFields"', content)
        self.assertIn('id="signupMobile"', content)
        self.assertIn('id="signupCourse"', content)
        self.assertIn('id="signupYear"', content)
        self.assertIn('id="organizerFields"', content)
        self.assertIn('id="signupDesignation"', content)

        # Check alert and submit
        self.assertIn('id="signupAlert"', content)
        self.assertIn('id="signupSubmitBtn"', content)

    def test_create_event_form_elements_present_in_template(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode('utf-8')

        # Check create event container and form
        self.assertIn('id="createEvent"', content)
        self.assertIn('id="createEventForm"', content)
        self.assertIn('class="create-event-card"', content)
        self.assertIn('btn-create-event', content)

        # Check all form input IDs
        self.assertIn('id="eventTitle"', content)
        self.assertIn('id="eventDescription"', content)
        self.assertIn('id="eventVenue"', content)
        self.assertIn('id="eventDate"', content)
        self.assertIn('id="eventStartTime"', content)
        self.assertIn('id="eventEndTime"', content)
        self.assertIn('id="eventCapacity"', content)

        # Check events container and filters
        self.assertIn('id="eventContainer"', content)
        self.assertIn('id="search"', content)
        self.assertIn('id="category"', content)
