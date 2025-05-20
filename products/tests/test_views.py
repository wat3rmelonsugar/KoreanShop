from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Brand, Product, Review

User = get_user_model()

class ProductViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')  # поправлен пароль

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            brand=self.brand,
            price=100,
            available=True
        )

    def test_product_list_view(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_list_by_category(self):
        response = self.client.get(reverse('products:product_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_list_by_brand(self):
        response = self.client.get(reverse('products:product_list_by_brand', args=[self.brand.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_view(self):
        response = self.client.get(reverse('products:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_review_submission(self):
        self.client.login(username='testuser', password='testpass')  # убедись, что пароль совпадает с setUp

        url = reverse('products:product_detail', args=[self.product.id, self.product.slug])

        data = {
            'action': 'add',
            'rating': '5',
            'comment': 'Отличный продукт!'
        }

        response = self.client.post(url, data=data)


        self.assertEqual(response.status_code, 302)

        self.assertTrue(Review.objects.filter(
            user=self.user,
            product=self.product,
            rating=5,
            comment='Отличный продукт!'
        ).exists())
