from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from ..models import Order, MenuItem, Payment, Category
from unittest.mock import patch


class ConfirmOrderViewTest(TestCase):

    def setUp(self):
        # Temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create user and menu items
        self.user = User.objects.create_user(username='regular_user', password='testpassword')
        self.item = MenuItem.objects.create(name='Test Item',
                                            category=Category.objects.create(category_name='Test Category'), price=10.0)
        self.client = Client()
        self.client.login(username='regular_user', password='testpassword')
        self.session = self.client.session
        self.session['cart'] = {'items': {str(self.item.id): 2}}
        self.session.save()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    @patch('self_service_kiosk.views.sumup_api.confirmSumUpTransactionAndGetAmount')
    def test_confirm_order_paid(self, mock_confirm):
        mock_confirm.return_value = 20.0
        tx_id = 'valid_tx_id'

        response = self.client.get(reverse('self-service-kiosk:confirm_order'), {
            'paid': tx_id
        }, follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:order_success', args=["2"]))
        order = Order.objects.get(user=self.user)
        self.assertTrue(order.paid)
        self.assertTrue(Payment.objects.filter(order=order, transaction_id=tx_id).exists())

    @patch('self_service_kiosk.views.sumup_api.confirmSumUpTransactionAndGetAmount')
    def test_confirm_order_unpaid(self, mock_confirm):
        mock_confirm.return_value = 0

        response = self.client.get(reverse('self-service-kiosk:confirm_order'), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:order_success', args=["1"]))
        order = Order.objects.get(user=self.user)
        self.assertFalse(order.paid)

    def test_confirm_order_empty_cart(self):
        session = self.client.session
        session['cart'] = {'items': {}}
        session.save()

        before = len(Order.objects.all())

        response = self.client.get(reverse('self-service-kiosk:confirm_order'), follow=True)

        after = len(Order.objects.all())

        self.assertEqual(before, after)  # Make sure no order was created
        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, "Du wurdest erfolgreich abgemeldet.")

    @patch('self_service_kiosk.views.Order.objects.create')
    def test_confirm_order_exception(self, mock_create):
        mock_create.side_effect = Exception('Test exception')

        response = self.client.get(reverse('self-service-kiosk:confirm_order'), follow=True)

        self.assertRedirects(response, reverse('self-service-kiosk:login'))
        self.assertContains(response, 'An error occurred while confirming your order. Please try again later.')

