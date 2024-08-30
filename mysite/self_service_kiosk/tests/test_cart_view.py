from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Category, MenuItem


class CartViewTest(TestCase):

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

        # Create a guest user
        self.guest_user = User.objects.create_user(username='guest_user', password='testpassword')

        # Create a category and menu items
        self.category = Category.objects.create(category_name='Test Category')
        self.menu_item1 = MenuItem.objects.create(name='Test Item 1', category=self.category, price=10.00)
        self.menu_item2 = MenuItem.objects.create(name='Test Item 2', category=self.category, price=15.00)

        # Initialize the client
        self.client = Client()

    def tearDown(self):
        # Restore SSL settings
        settings.SECURE_SSL_REDIRECT = self._original_secure_ssl_redirect
        settings.SESSION_COOKIE_SECURE = self._original_session_cookie_secure
        settings.CSRF_COOKIE_SECURE = self._original_csrf_cookie_secure

    def test_cart_view_with_items(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Add items to the session cart
        session = self.client.session
        session['cart'] = {
            'items': {
                str(self.menu_item1.id): 99,
                str(self.menu_item2.id): 11
            }
        }
        session.save()

        # Simulate a GET request to view the cart
        response = self.client.get(reverse('self-service-kiosk:cart'))

        # Check if the cart page is rendered successfully with items
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/cart.html')
        self.assertContains(response, self.menu_item1.name)
        self.assertContains(response, self.menu_item2.name)
        self.assertContains(response, '99')
        self.assertContains(response, '11')

    def test_cart_view_empty(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate a GET request to view the cart with an empty session
        response = self.client.get(reverse('self-service-kiosk:cart'))

        # Check if the cart page is rendered successfully without items
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'self_service_kiosk/cart.html')
        self.assertContains(response, 'Ihr Warenkorb ist leer.')

    def test_update_quantity_add_item(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Simulate an AJAX POST request to add an item to the cart
        response = self.client.post(reverse('self-service-kiosk:update_quantity', args=[self.menu_item1.id, 3]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Quantity updated successfully'})

        # Check if the item is added to the session cart
        session = self.client.session
        self.assertIn('cart', session)
        self.assertEqual(session['cart']['items'][str(self.menu_item1.id)], 3)

    def test_update_quantity_remove_item(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Add an item to the session cart
        session = self.client.session
        session['cart'] = {
            'items': {
                str(self.menu_item1.id): 2
            }
        }
        session.save()

        # Simulate an AJAX POST request to remove the item from the cart
        response = self.client.post(reverse('self-service-kiosk:update_quantity', args=[self.menu_item1.id, 0]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Quantity updated successfully'})

        # Check if the item is removed from the session cart
        session = self.client.session
        self.assertNotIn(str(self.menu_item1.id), session['cart']['items'])

    def test_update_quantity_update_item(self):
        # Log in the regular user
        self.client.login(username='regular_user', password='testpassword')

        # Add an item to the session cart
        session = self.client.session
        session['cart'] = {
            'items': {
                str(self.menu_item1.id): 2
            }
        }
        session.save()

        # Simulate an AJAX POST request to update the item quantity in the cart
        response = self.client.post(reverse('self-service-kiosk:update_quantity', args=[self.menu_item1.id, 5]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Quantity updated successfully'})

        # Check if the item quantity is updated in the session cart
        session = self.client.session
        self.assertEqual(session['cart']['items'][str(self.menu_item1.id)], 5)
