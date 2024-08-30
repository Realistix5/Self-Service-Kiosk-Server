from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings


class StandardAuthenticationTest(TestCase):

    def setUp(self):
        # temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create a regular user
        self.user = User.objects.create_user(username='regular_user', password='testpassword')

        # Create a guest user
        self.guest_user = User.objects.create_user(username='guest_user', password='testpassword')

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_user_login_success(self):
        # Simulate a POST request to login the regular user
        response = self.client.post(reverse('self-service-kiosk:login'), {
            'username': 'regular_user',
            'password': 'testpassword'
        }, follow=True)

        # Check if the user is redirected to the all products page after successful login
        self.assertRedirects(response, reverse('self-service-kiosk:all_products'), status_code=301)

        # Check if the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_login_failure(self):
        # Simulate a POST request with incorrect credentials
        response = self.client.post(reverse('self-service-kiosk:login'), {
            'username': 'regular_user',
            'password': 'wrongpassword'
        })

        # Check if the user is redirected back to the login page with an error message
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/login.html')
        self.assertContains(response, 'Fehlerhafter Nutzername oder Passwort. Bitte erneut versuchen.')

        # Check if the user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_guest_login_success(self):
        # Simulate a GET request to login the guest user
        response = self.client.get(reverse('self-service-kiosk:guest_login'), secure=True, follow=True)

        # Check if the user is redirected to the all products page after successful login
        self.assertRedirects(response, reverse('self-service-kiosk:all_products'), status_code=301)

        # Check if the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'guest_user')

    def test_guest_login_failure(self):
        # Temporarily rename the guest user to simulate login failure
        self.guest_user.username = 'guest_user_renamed'
        self.guest_user.save()

        # Simulate a GET request to login the guest user
        response = self.client.get(reverse('self-service-kiosk:guest_login'), secure=True)

        # Check if the user is redirected back to the login page with an error message
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/login.html')
        self.assertContains(response, 'Fehler beim Gast-Login. Bitte versuchen Sie es erneut.')

        # Check if the user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_logout(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to logout the user
        response = self.client.get(reverse('self-service-kiosk:logout'), follow=True)

        # Check if the user is redirected to the login page after logout
        self.assertRedirects(response, reverse('self-service-kiosk:login'), status_code=301)

        # Check if the user is not authenticated
        response = self.client.get(reverse('self-service-kiosk:all_products'))
        self.assertRedirects(response, f'{reverse("self-service-kiosk:login")}?next={reverse("self-service-kiosk:all_products")}')
