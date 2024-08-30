from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from self_service_kiosk.models import LoginToken
from django.conf import settings
import uuid
from django.utils import timezone

class LoginWithTokenViewTest(TestCase):

    def setUp(self):
        # Temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create user and token
        self.user = User.objects.create_user(username='regular_user', password='testpassword')
        self.token = LoginToken.objects.create(user=self.user, token=uuid.uuid4(), valid_until=timezone.now() + timezone.timedelta(days=1))

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_login_with_valid_token(self):
        response = self.client.get(reverse('self-service-kiosk:login_with_token', args=[self.token.token]), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_expired_token(self):
        self.token.valid_until = timezone.now() - timezone.timedelta(days=1)
        self.token.save()

        response = self.client.get(reverse('self-service-kiosk:login_with_token', args=[self.token.token]), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Dieser Token ist abgelaufen. Bitte Passwort zurücksetzen um neuen zu generieren.')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_token(self):
        invalid_token = uuid.uuid4()

        response = self.client.get(reverse('self-service-kiosk:login_with_token', args=[invalid_token]), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Ungültiger Token.')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
