from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product, Brand, Category
from cart.models import Cart, CartItem

User = get_user_model()

class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            brand=self.brand,
            price=100.0,
            available=True
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user)
        self.assertTrue(cart.is_active)

    def test_cart_total_price_and_quantity(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(cart.get_total_quantity(), 2)
        self.assertEqual(cart.get_total_price(), 200.0)

