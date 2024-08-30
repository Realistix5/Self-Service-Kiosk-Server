from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from ..models import RegistrationToken, UserInfo
from unittest.mock import patch


class RegisterViewTest(TestCase):

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

    def test_register_get(self):
        response = self.client.get(reverse('self-service-kiosk:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/register.html')

    @patch('self_service_kiosk.views.member_api.get_user_info')
    @patch('self_service_kiosk.views.send_emails.sendRegistrationEmail')
    def test_register_post_success(self, mock_send_email, mock_get_user_info):
        mock_get_user_info.return_value = ('John Doe', 'john.doe@example.com', 'M', 'Main St', '12345', 'Anytown')

        response = self.client.post(reverse('self-service-kiosk:register'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertTrue(User.objects.filter(username='123456').exists())
        self.assertTrue(UserInfo.objects.filter(user__username='123456').exists())
        self.assertTrue(RegistrationToken.objects.filter(user__username='123456').exists())
        mock_send_email.assert_called_once()

    @patch('self_service_kiosk.views.member_api.get_user_info')
    def test_register_post_user_exists_active(self, mock_get_user_info):
        user = User.objects.create_user(username='123456', email='john.doe@example.com', password='testpassword', is_active=True)
        mock_get_user_info.return_value = ('John Doe', 'john.doe@example.com', 'M', 'Main St', '12345', 'Anytown')

        response = self.client.post(reverse('self-service-kiosk:register'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Nutzer ist bereits registriert und aktiviert.')

    @patch('self_service_kiosk.views.member_api.get_user_info')
    def test_register_post_user_exists_inactive(self, mock_get_user_info):
        user = User.objects.create_user(username='123456', email='john.doe@example.com', password='testpassword', is_active=False)
        mock_get_user_info.return_value = ('John Doe', 'john.doe@example.com', 'M', 'Main St', '12345', 'Anytown')

        response = self.client.post(reverse('self-service-kiosk:register'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Nutzer ist bereits registriert, aber nicht aktiviert.')

    @patch('self_service_kiosk.views.member_api.get_user_info')
    def test_register_post_invalid_member_number(self, mock_get_user_info):
        mock_get_user_info.return_value = (None, None, None, None, None, None)

        response = self.client.post(reverse('self-service-kiosk:register'), {
            'mitgliedsnummer': 'invalid'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'Mitgliedsnummer konnte nicht gefunden werden. Bitte versuche es erneut.')

    @patch('self_service_kiosk.views.member_api.get_user_info')
    def test_register_post_not_authorized(self, mock_get_user_info):
        mock_get_user_info.return_value = ("not authorized", None, None, None, None, None)

        response = self.client.post(reverse('self-service-kiosk:register'), {
            'mitgliedsnummer': '123456'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response,
                            "Abfragen der Mitglieder-API ist fehlgeschlagen. Bitte kontaktiere einen Mitarbeiter.")
