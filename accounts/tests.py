from django.test import TestCase, Client
from django.urls import reverse
from colleges.models import College
from accounts.models import User, StudentProfile, OrganizerProfile


class LoginAPITests(TestCase):
    def test_valid_credentials_return_jwt_tokens(self):
        User.objects.create_user(
            username="login_student",
            email="login@example.edu",
            password="SecurePassword123!",
        )

        response = self.client.post(
            reverse('token_obtain_pair'),
            {
                "username": "login_student",
                "password": "SecurePassword123!",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())


class SignupAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.college = College.objects.create(
            name="Apex Institute of Technology",
            code="AIT",
            city="Indore",
            email="contact@ait.edu"
        )
        self.register_url = reverse('register')
        self.colleges_url = reverse('college-list-create')

    def test_colleges_list_endpoint_for_signup(self):
        response = self.client.get(self.colleges_url)
        self.assertEqual(response.status_code, 200)
        colleges = response.json()
        self.assertTrue(len(colleges) >= 1)
        self.assertEqual(colleges[0]['id'], self.college.id)
        self.assertEqual(colleges[0]['name'], "Apex Institute of Technology")

    def test_student_signup_success(self):
        payload = {
            "username": "alice_student",
            "email": "alice@ait.edu",
            "password": "SecurePassword123!",
            "role": "student",
            "college": self.college.id,
            "mobile": "9876543210",
            "course": "Computer Science",
            "year": 3
        }
        response = self.client.post(
            self.register_url,
            payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], "alice_student")
        self.assertEqual(data["role"], "student")
        self.assertEqual(data["college"], self.college.id)

        # Check DB
        user = User.objects.get(username="alice_student")
        self.assertEqual(user.email, "alice@ait.edu")
        self.assertEqual(user.role, "student")
        self.assertEqual(user.college, self.college)
        self.assertTrue(hasattr(user, "student_profile"))
        self.assertEqual(user.student_profile.mobile, "9876543210")
        self.assertEqual(user.student_profile.course, "Computer Science")
        self.assertEqual(user.student_profile.year, 3)

    def test_organizer_signup_success(self):
        payload = {
            "username": "bob_organizer",
            "email": "bob@ait.edu",
            "password": "SecurePassword123!",
            "role": "organizer",
            "college": self.college.id,
            "designation": "Tech Club President"
        }
        response = self.client.post(
            self.register_url,
            payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], "bob_organizer")
        self.assertEqual(data["role"], "organizer")

        # Check DB
        user = User.objects.get(username="bob_organizer")
        self.assertEqual(user.role, "organizer")
        self.assertTrue(hasattr(user, "organizer_profile"))
        self.assertEqual(user.organizer_profile.designation, "Tech Club President")

    def test_signup_validation_errors(self):
        # Missing required fields
        response = self.client.post(
            self.register_url,
            {},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertIn("username", errors)
        self.assertIn("email", errors)
        self.assertIn("password", errors)

    def test_signup_duplicate_username_error(self):
        User.objects.create_user(
            username="existing_user",
            email="existing@ait.edu",
            password="Password123!"
        )
        payload = {
            "username": "existing_user",
            "email": "different@ait.edu",
            "password": "Password123!",
            "role": "student",
            "college": self.college.id
        }
        response = self.client.post(
            self.register_url,
            payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertIn("username", errors)
