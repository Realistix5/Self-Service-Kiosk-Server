from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings


class OrderSuccessViewTest(TestCase):

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
        self.client.login(username='regular_user', password='testpassword')
        session = self.client.session
        session['checkout_amount'] = "50.00"
        session.save()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_order_success_case_1(self):
        response = self.client.get(reverse('self-service-kiosk:order_success', args={"1"}))
        self.assertContains(response, 'Bestellung über 50.00€ erfolgreich auf Rechnung bestellt.')

    def test_order_success_case_2(self):
        response = self.client.get(reverse('self-service-kiosk:order_success', args={"2"}))
        self.assertContains(response, 'Bestellung über 50.00€ erfolgreich platziert und bezahlt.')

    def test_order_success_unknown_case(self):
        response = self.client.get(reverse('self-service-kiosk:order_success', args={"99"}))
        self.assertContains(response, 'Unbekannter Fall.')
