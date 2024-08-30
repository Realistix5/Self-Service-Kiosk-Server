from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from self_service_kiosk.models import Payment, Order
from unittest.mock import patch


class ProcessPaymentViewTest(TestCase):

    def setUp(self):
        # Temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create user and initialize the client
        self.user = User.objects.create_user(username='regular_user', password='testpassword')
        self.client = Client()
        self.client.login(username='regular_user', password='testpassword')

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    @patch('self_service_kiosk.views.sumup_api.confirmSumUpTransactionAndGetAmount')
    def test_process_payment_order_success(self, mock_confirm):
        mock_confirm.return_value = 100.0
        tx_id = 'valid_tx_id'

        response = self.client.get(reverse('self-service-kiosk:process_payment'), {
            'paid': tx_id,
            'type': 'order'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:confirm_order') + '?paid=' + tx_id, target_status_code=302)

    @patch('self_service_kiosk.views.sumup_api.confirmSumUpTransactionAndGetAmount')
    def test_process_payment_credit_success(self, mock_confirm):
        mock_confirm.return_value = 50.0
        tx_id = 'valid_tx_id'

        response = self.client.get(reverse('self-service-kiosk:process_payment'), {
            'paid': tx_id,
            'type': 'credit'
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:account_details'))
        self.assertTrue(Payment.objects.filter(transaction_id=tx_id, user=self.user, amount=50.0).exists())

    def test_process_payment_duplicate_transaction_id(self):
        Payment.objects.create(transaction_id='duplicate_tx_id', user=self.user, amount=100.0)

        response = self.client.get(reverse('self-service-kiosk:process_payment'), {
            'paid': 'duplicate_tx_id',
            'type': 'order'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:payment_problem') + '?code=11')

    def test_process_payment_invalid_type(self):
        tx_id = 'valid_tx_id'

        response = self.client.get(reverse('self-service-kiosk:process_payment'), {
            'paid': tx_id,
            'type': 'invalid_type'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:payment_problem') + '?code=12')

    @patch('self_service_kiosk.views.sumup_api.confirmSumUpTransactionAndGetAmount')
    def test_process_payment_credit_failure(self, mock_confirm):
        mock_confirm.return_value = 0
        tx_id = 'valid_tx_id'

        response = self.client.get(reverse('self-service-kiosk:process_payment'), {
            'paid': tx_id,
            'type': 'credit'
        })

        self.assertRedirects(response, reverse('self-service-kiosk:payment_problem') + '?code=13')
