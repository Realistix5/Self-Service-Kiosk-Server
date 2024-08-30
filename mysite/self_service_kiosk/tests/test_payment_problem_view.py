from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

class PaymentProblemViewTest(TestCase):

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

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_payment_problem(self):
        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 1})
        self.assertContains(response, 'Es hat geklappt, wieso sind wir hier?')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 2})
        self.assertTemplateUsed(response, 'self_service_kiosk/payment_failed.html')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 3})
        self.assertContains(response, 'Bitte Ortungsdienste aktivieren.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 4})
        self.assertContains(response, 'Fehlerhafte Eingabeparameter.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 5})
        self.assertContains(response, 'Fehlerhafter Token.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 6})
        self.assertContains(response, 'Verbingung fehlgeschlagen.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 7})
        self.assertContains(response, 'Keine Berechtigung.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 8})
        self.assertContains(response, 'Kein Händler eingeloggt.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 9})
        self.assertContains(response, 'Fehler: Foreign Transaction ID bereits vergeben.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 10})
        self.assertContains(response, 'Fehler: Falscher Affiliate Key.')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 11})
        self.assertContains(response, 'Die Zahlung konnte nicht bestätigt werden. (Fehler 11)')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 12})
        self.assertContains(response, 'Die Zahlung konnte nicht bestätigt werden. (Fehler 12)')

        response = self.client.get(reverse('self-service-kiosk:payment_problem'), {'code': 13})
        self.assertContains(response, 'Die Zahlung konnte nicht bestätigt werden. (Fehler 13)')
