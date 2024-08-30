from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.http import JsonResponse

from ..forms import FeedbackForm
import json


class FeedbackViewTest(TestCase):

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

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_help_page_get(self):
        # Log in the user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to the help page
        response = self.client.get(reverse('self-service-kiosk:help_page'))

        # Check if the response is successful and the form is rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/help_page.html')
        self.assertIsInstance(response.context['form'], FeedbackForm)

    def test_help_page_post_valid(self):
        # Log in the user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a POST request with valid data
        response = self.client.post(reverse('self-service-kiosk:help_page'), {
            'feedback_text': 'This is a feedback message.',
            'feedback_sender': 'John Doe'
        })

        # Check if the feedback email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Neues Feedback vom Self-Service-Kiosk')
        self.assertIn('This is a feedback message.', mail.outbox[0].body)

        # Check if the response is successful and the success message is displayed
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/help_page.html')
        self.assertTrue(response.context['success'])

    def test_help_page_post_invalid(self):
        # Log in the user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a POST request with invalid data
        response = self.client.post(reverse('self-service-kiosk:help_page'), {
            'feedback_text': ''
        })

        # Check if the response is successful and the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/help_page.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertFalse(response.context.get('success', False))

    def test_send_feedback_post_valid(self):
        # Simulate a POST request with valid JSON data
        response = self.client.post(reverse('self-service-kiosk:send_feedback'), json.dumps({
            'feedback_text': 'This is a feedback message.',
            'feedback_sender': 'John Doe'
        }), content_type='application/json')

        # Check if the feedback email is sent
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Neues Feedback vom Self-Service-Kiosk')
        self.assertIn('This is a feedback message.', mail.outbox[0].body)

    def test_send_feedback_post_missing_data(self):
        # Simulate a POST request with missing JSON data
        response = self.client.post(reverse('self-service-kiosk:send_feedback'), json.dumps({
            'feedback_sender': 'John Doe'
        }), content_type='application/json')

        # Check if the response indicates an error
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

