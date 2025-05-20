from django.test import TestCase
from orders.models import Order, OrderItem
from products.models import Product, Brand, Category

class OrderModelTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Test Category', slug='test-cat')
        brand = Brand.objects.create(name='Test Brand', slug='test-brand')
        self.product = Product.objects.create(
            name='Product 1',
            slug='product-1',
            category=category,
            brand=brand,
            price=100
        )

    def test_order_total_cost(self):
        order = Order.objects.create(full_name='Test', email='test@example.com', address='123 Main St')
        OrderItem.objects.create(order=order, product=self.product, price=100, quantity=2)
        OrderItem.objects.create(order=order, product=self.product, price=150, quantity=1)
        self.assertEqual(order.get_total_cost(), 350)
