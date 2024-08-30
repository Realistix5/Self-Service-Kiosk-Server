from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from ..models import RegistrationToken, PasswordResetToken, LoginToken
from django.utils import timezone
from unittest.mock import patch


class SetPasswordViewTest(TestCase):

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

        # Create user
        self.user = User.objects.create_user(username='123456', email='john.doe@example.com', password='oldpassword')

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_set_password_get_registration_token(self):
        token = RegistrationToken.objects.create(user=self.user)

        response = self.client.get(reverse('self-service-kiosk:set_password', args=[token.token]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/set_password.html')

    def test_set_password_get_password_reset_token(self):
        token = PasswordResetToken.objects.create(user=self.user)

        response = self.client.get(reverse('self-service-kiosk:set_password', args=[token.token]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/set_password.html')

    def test_set_password_post_success(self):
        token = PasswordResetToken.objects.create(user=self.user)
        new_password = 'newpassword123'

        response = self.client.post(reverse('self-service-kiosk:set_password', args=[token.token]), {
            'new_password1': new_password,
            'new_password2': new_password
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(PasswordResetToken.objects.filter(user=self.user).exists())

    @patch('self_service_kiosk.views.send_emails.sendNewPasswordSetEmail')
    def test_set_password_post_activate_user(self, mock_send_email):
        token = RegistrationToken.objects.create(user=self.user)
        new_password = 'newpassword123'

        response = self.client.post(reverse('self-service-kiosk:set_password', args=[token.token]), {
            'new_password1': new_password,
            'new_password2': new_password
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertTrue(self.user.is_active)
        self.assertFalse(RegistrationToken.objects.filter(user=self.user).exists())
        self.assertContains(response, 'Dein Account wurde erfolgreich aktiviert und dein Passwort gesetzt.')
        mock_send_email.assert_called_once()

    def test_set_password_post_invalid_token(self):
        dummy_uuid4 = "116bfec3-e903-4f4a-a811-c5178cac7f29"
        response = self.client.post(reverse('self-service-kiosk:set_password', args=[dummy_uuid4]), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Der aufgerufene Token wurde nicht gefunden.')

    def test_set_password_post_expired_token(self):
        token = PasswordResetToken.objects.create(user=self.user)
        token.valid_until = timezone.now() - timezone.timedelta(days=1)
        token.save()

        response = self.client.post(reverse('self-service-kiosk:set_password', args=[token.token]), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Der aufgerufene Token wurde bereits verwendet.')
