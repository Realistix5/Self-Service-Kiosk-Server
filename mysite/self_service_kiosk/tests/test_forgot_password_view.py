from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from ..models import PasswordResetToken
from unittest.mock import patch


class ForgotPasswordViewTest(TestCase):

    def setUp(self):
        # Temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_forgot_password_get(self):
        response = self.client.get(reverse('self-service-kiosk:forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/forgot_password.html')

    @patch('self_service_kiosk.views.send_emails.sendForgotPasswordEmail')
    def test_forgot_password_post_success(self, mock_send_email):
        user = User.objects.create_user(username='123456', email='john.doe@example.com', password='testpassword', is_active=True)

        response = self.client.post(reverse('self-service-kiosk:forgot_password'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Email, um dein Passwort zurückzusetzen wurde an john.doe@example.com gesendet.')
        self.assertTrue(PasswordResetToken.objects.filter(user=user).exists())
        mock_send_email.assert_called_once()

    def test_forgot_password_post_user_not_found(self):
        response = self.client.post(reverse('self-service-kiosk:forgot_password'), {
            'mitgliedsnummer': 'nonexistent'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Kein Nutzer mit dieser Mitgliedsnummer registriert.')

    def test_forgot_password_post_user_inactive(self):
        user = User.objects.create_user(username='123456', password='testpassword', is_active=False)

        response = self.client.post(reverse('self-service-kiosk:forgot_password'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, "Nutzer ist noch nicht aktiviert. Bitte nutze &gt;&gt; Noch kein Konto? &lt;&lt;"
                                      " um dein Konto zu aktivieren.")
