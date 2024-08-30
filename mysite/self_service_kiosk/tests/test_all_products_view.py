from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Category, MenuItem
from django.conf import settings


class AllProductsViewTest(TestCase):

    def setUp(self):
        # temporary settings
        self._original_secure_ssl_redirect = settings.SECURE_SSL_REDIRECT
        settings.SECURE_SSL_REDIRECT = False
        self._original_session_cookie_secure = settings.SESSION_COOKIE_SECURE
        settings.SESSION_COOKIE_SECURE = False
        self._original_csrf_cookie_secure = settings.CSRF_COOKIE_SECURE
        settings.CSRF_COOKIE_SECURE = False

        # Create a regular user
        self.user = User.objects.create_user(username='regular_user', password='testpassword')

        # Create an event user
        self.event_user = User.objects.create_user(username='event_user', password='testpassword')

        # Create categories
        self.regular_category = Category.objects.create(category_name='Regular Category', event_category=False, order_number=1)
        self.event_category = Category.objects.create(category_name='Event Category', event_category=True, order_number=2)

        # Create menu items
        self.regular_item = MenuItem.objects.create(name='Regular Item', category=self.regular_category, hidden=False,
                                                    order_number=1, price=1)
        self.hidden_item = MenuItem.objects.create(name='Hidden Item', category=self.regular_category, hidden=True,
                                                   order_number=2, price=1)
        self.event_item = MenuItem.objects.create(name='Event Item', category=self.event_category, hidden=False,
                                                  order_number=1, price=1)

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_all_products_view_regular_user(self):
        self.client.login(username='regular_user', password='testpassword')
        response = self.client.get(reverse('self-service-kiosk:all_products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/all_products.html')

        # Check that only regular categories and visible items are displayed
        self.assertContains(response, 'Regular Category')
        self.assertContains(response, 'Regular Item')
        self.assertNotContains(response, 'Event Category')
        self.assertNotContains(response, 'Hidden Item')
        self.assertNotContains(response, 'Event Item')

    def test_all_products_view_event_user(self):
        self.client.login(username='event_user', password='testpassword')
        response = self.client.get(reverse('self-service-kiosk:all_products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/all_products.html')

        # Check that all categories and visible items are displayed
        self.assertNotContains(response, 'Regular Category')
        self.assertNotContains(response, 'Regular Item')
        self.assertContains(response, 'Event Category')
        self.assertContains(response, 'Event Item')
        self.assertNotContains(response, 'Hidden Item')

    def test_all_products_view_no_login(self):
        response = self.client.get("/", follow=True)
        self.assertRedirects(response, f'{reverse("self-service-kiosk:login")}?next={reverse("self-service-kiosk:index")}')

    def test_cart_items_display(self):
        self.client.login(username='regular_user', password='testpassword')

        # Add items to cart session
        session = self.client.session
        session['cart'] = {'items': {str(self.regular_item.id): 2}}
        session.save()

        response = self.client.get(reverse('self-service-kiosk:all_products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Regular Item')
        self.assertContains(response, '2')  # Check that the quantity is displayed correctly


