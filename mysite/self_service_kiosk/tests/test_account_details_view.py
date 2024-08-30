from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Order, OrderItem, MenuItem, Payment, Category


class AccountDetailsViewTest(TestCase):

    def setUp(self):
        # Temporarily disable SSL settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create a regular users
        self.user = User.objects.create_user(username='regular_user', password='testpassword')
        self.user2 = User.objects.create_user(username='regular_user2', password='testpassword')

        # Create a guest user
        self.guest_user = User.objects.create_user(username='guest_user', password='testpassword')

        # Create a category and menu items
        self.category = Category.objects.create(category_name='Test Category')
        self.menu_item1 = MenuItem.objects.create(name='Test Item 1', category=self.category, price=10.00)
        self.menu_item2 = MenuItem.objects.create(name='Test Item 2', category=self.category, price=15.00)

        # Create orders and payments for the regular user
        self.order1 = Order.objects.create(user=self.user, paid=False)
        self.order_item1 = OrderItem.objects.create(order=self.order1, menu_item=self.menu_item1, quantity=10)
        self.order2 = Order.objects.create(user=self.user, paid=True)
        self.order_item2 = OrderItem.objects.create(order=self.order2, menu_item=self.menu_item2, quantity=1)
        self.order3 = Order.objects.create(user=self.user2, paid=False)
        self.order_item3 = OrderItem.objects.create(order=self.order3, menu_item=self.menu_item1, quantity=1)

        self.payment1 = Payment.objects.create(user=self.user, amount=10.00, transaction_id="XYZ")
        self.payment2 = Payment.objects.create(user=self.user2, amount=100.00, transaction_id="XYZ2")

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        # Restore SSL settings
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_account_details_view_for_regular_user_open_amount(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to view account details
        response = self.client.get(reverse('self-service-kiosk:account_details'))

        # Check if the account details page is rendered successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/account_details.html')

        # Check if the total price is calculated correctly
        self.assertContains(response, 'Offener Betrag:')
        self.assertContains(response, '90,00')

    def test_account_details_view_for_regular_user_balance(self):
        # Log in the regular user
        self.client.login(username='regular_user2', password='testpassword')

        # Simulate a GET request to view account details
        response = self.client.get(reverse('self-service-kiosk:account_details'))

        # Check if the account details page is rendered successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/account_details.html')

        # Check if the total price is calculated correctly
        self.assertContains(response, 'Restliches Guthaben:')
        self.assertContains(response, '90,00')

    def test_account_details_view_for_guest_user(self):
        # Log in the guest user
        self.client.login(username='guest_user', password='testpassword')

        # Simulate a GET request to view account details
        response = self.client.get(reverse('self-service-kiosk:account_details'))

        # Check if access is denied for guest user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'not allowed for guest user')
