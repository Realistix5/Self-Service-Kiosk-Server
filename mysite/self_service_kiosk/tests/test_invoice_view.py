from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

from ..models import Invoice
import os


class InvoiceViewTest(TestCase):

    def setUp(self):
        # Temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create a regular user
        self.user = User.objects.create_user(username='regular_user', password='testpassword')

        # Create a staff user
        self.staff_user = User.objects.create_user(username='staff_user', password='testpassword', is_staff=True)

        # Create a guest user
        self.guest_user = User.objects.create_user(username='guest_user', password='testpassword')

        # Initialize the client
        self.client = Client()

        # Create a test invoice
        self.test_invoice = Invoice.objects.create(
            user=self.staff_user,
            year=2023,
            version=1,
            pdf_path=SimpleUploadedFile('test_invoice.pdf', b'file_content', content_type='application/pdf')
        )

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_invoice_view_authenticated_user(self):
        # Log in the staff user
        self.client.login(username='staff_user', password='testpassword')

        # Simulate a GET request to view the invoice
        response = self.client.get(reverse('self-service-kiosk:invoice_view', args=[self.test_invoice.pdf_path.name]))

        # Check if the response is successful and the file is returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], f'inline; filename="{self.test_invoice.pdf_path.name}"')

    def test_invoice_view_non_staff_user(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to view the invoice
        response = self.client.get(reverse('self-service-kiosk:invoice_view', args=[self.test_invoice.pdf_path.name]))

        # Check if the user is redirected to the admin login page with an error message
        self.assertRedirects(response, reverse('admin:login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Sie haben keine Berechtigung, auf diese Datei zuzugreifen.")

    def test_invoice_view_guest_user(self):
        # Log in the guest user
        self.client.login(username='guest_user', password='testpassword')

        # Simulate a GET request to view the invoice
        response = self.client.get(reverse('self-service-kiosk:invoice_view', args=[self.test_invoice.pdf_path.name]))

        # Check if the user is redirected to the admin login page with an error message
        self.assertRedirects(response, reverse('admin:login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Sie haben keine Berechtigung, auf diese Datei zuzugreifen.")

    def test_invoice_view_file_not_found(self):
        # Log in the staff user
        self.client.login(username='staff_user', password='testpassword')

        # Simulate a GET request to view a non-existent invoice
        response = self.client.get(reverse('self-service-kiosk:invoice_view', args=['non_existent.pdf']))

        # Check if the user is redirected to the admin index page with an error message
        self.assertRedirects(response, reverse('admin:index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Die Datei konnte nicht gefunden werden.")
