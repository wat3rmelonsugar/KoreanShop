from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Brand, Category
from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem

User = get_user_model()

class OrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='TestCat', slug='test-cat')
        self.brand = Brand.objects.create(name='TestBrand', slug='test-brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            brand=self.brand,
            price=500,
            available=True
        )

    def test_order_create_authenticated(self):
        self.client.login(username='testuser', password='12345')


        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        response = self.client.post(
            reverse('orders:order_create'),
            data={
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'address': '456 Elm St'
            }
        )

        self.assertRedirects(response, reverse('orders:order_confirmation', args=[Order.objects.first().id]))
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().items.count(), 1)

    def test_order_create_empty_cart(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('orders:order_create'),
            data={
                'full_name': 'Empty Cart',
                'email': 'no@cart.com',
                'address': 'No Address'
            },
            follow=True
        )
        self.assertContains(response, "Your cart is empty")

    def test_order_confirmation_view(self):
        order = Order.objects.create(
            full_name="Test",
            email="test@example.com",
            address="123 test st"
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )

        response = self.client.get(reverse('orders:order_confirmation', args=[order.id]))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, f'Номер заказа: {order.id}')
        self.assertContains(response, f'{2} x {self.product.name}')
        self.assertContains(response, f'{self.product.price}')
