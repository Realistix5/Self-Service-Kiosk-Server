from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Order, OrderItem, MenuItem, Category


class OrderDetailViewTest(TestCase):

    def setUp(self):
        # Temporarily disable SSL settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create a regular user
        self.user = User.objects.create_user(username='regular_user', password='testpassword')

        # Create another user
        self.other_user = User.objects.create_user(username='other_user', password='testpassword')

        # Create a category and menu items
        self.category = Category.objects.create(category_name='Test Category')
        self.menu_item1 = MenuItem.objects.create(name='Test Item 1', category=self.category, price=10.00)
        self.menu_item2 = MenuItem.objects.create(name='Test Item 2', category=self.category, price=15.00)

        # Create an order for the regular user
        self.order = Order.objects.create(user=self.user, paid=False)
        self.order_item1 = OrderItem.objects.create(order=self.order, menu_item=self.menu_item1, quantity=2)
        self.order_item2 = OrderItem.objects.create(order=self.order, menu_item=self.menu_item2, quantity=1)

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        # Restore SSL settings
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_order_detail_view_for_own_order(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to view order detail
        response = self.client.get(reverse('self-service-kiosk:order_detail', args=[self.order.id]))

        # Check if the order detail page is rendered successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/order.html')

        # Check if the order items are displayed correctly
        self.assertContains(response, self.menu_item1.name)
        self.assertContains(response, self.menu_item2.name)

    def test_order_detail_view_for_other_user_order(self):
        # Log in another user
        self.client.login(username='other_user', password='testpassword')

        # Simulate a GET request to view order detail
        response = self.client.get(reverse('self-service-kiosk:order_detail', args=[self.order.id]))

        # Check if access is denied for another user's order
        self.assertEqual(response.status_code, 404)

    def test_order_detail_view_for_anonymous_user(self):
        # Simulate a GET request to view order detail without logging in
        response = self.client.get(reverse('self-service-kiosk:order_detail', args=[self.order.id]))

        # Check if the user is redirected to the login page
        self.assertRedirects(response, f'{reverse("self-service-kiosk:login")}?next={reverse("self-service-kiosk:order_detail", args=[self.order.id])}')
