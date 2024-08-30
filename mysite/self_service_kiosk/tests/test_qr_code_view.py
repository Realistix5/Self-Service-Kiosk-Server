from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
import uuid


class QRCodeViewTest(TestCase):

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

    def test_qr_code_login(self):
        token = str(uuid.uuid4())
        response = self.client.post(reverse('self-service-kiosk:qr_code'), {
            'qr_code': f'login:{token}'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:login_with_token', args=[token]), target_status_code=302)

    def test_qr_code_reset_password(self):
        token = str(uuid.uuid4())
        response = self.client.post(reverse('self-service-kiosk:qr_code'), {
            'qr_code': f'reset_password:{token}'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:set_password', args=[token]), target_status_code=302)

    def test_qr_code_register(self):
        token = str(uuid.uuid4())
        response = self.client.post(reverse('self-service-kiosk:qr_code'), {
            'qr_code': f'register:{token}'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:set_password', args=[token]), target_status_code=302)

    def test_qr_code_invalid_action(self):
        response = self.client.post(reverse('self-service-kiosk:qr_code'), {
            'qr_code': 'invalid_action'
        })

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Ungültige Aktion im QR-Code'})

    def test_qr_code_no_code(self):
        response = self.client.post(reverse('self-service-kiosk:qr_code'))

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'QR-Code nicht gefunden'})

    def test_qr_code_get_request(self):
        # Send a GET request to the view
        response = self.client.get(reverse('self-service-kiosk:qr_code'))

        self.assertEqual(response.status_code, 403)  # HttpResponseForbidden
