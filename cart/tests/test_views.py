from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from products.models import Product, Brand, Category
from cart.models import Cart
from django.urls import reverse

User = get_user_model()

class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            brand=self.brand,
            price=300,
            available=True
        )

    def test_cart_add_authenticated_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 2},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart_total', response.json())

    def test_cart_detail_view(self):
        self.client.login(username='testuser', password='12345')
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 1},
            content_type='application/json'
        )
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_cart_remove_view(self):
        self.client.login(username='testuser', password='12345')
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 1},
            content_type='application/json'
        )
        cart = Cart.objects.get(user=self.user, is_active=True)
        item = cart.items.first()
        response = self.client.get(reverse('cart:remove_item', args=[item.id]))
        self.assertEqual(response.status_code, 302)

    def test_cart_clear_view(self):
        self.client.login(username='testuser', password='12345')
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 1},
            content_type='application/json'
        )
        response = self.client.get(reverse('cart:cart_clear'))
        self.assertEqual(response.status_code, 302)
