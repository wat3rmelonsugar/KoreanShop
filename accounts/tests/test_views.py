from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import Favorite
from products.models import Product, Category, Brand

class FavoritesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='user1', email='user1@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Cat1", slug="cat1")
        self.brand = Brand.objects.create(name="Brand1", slug="brand1")
        self.product = Product.objects.create(
            name='Product1',
            slug='product1',
            price=10,
            category=self.category,
            brand=self.brand
        )

    def test_toggle_favorite_add_and_remove(self):
        self.client.login(username='user1', password='testpass')
        response_add = self.client.post('/accounts/toggle-favorite/', {'product_id': self.product.id})
        self.assertJSONEqual(response_add.content, {'status': 'added'})

        response_remove = self.client.post('/accounts/toggle-favorite/', {'product_id': self.product.id})
        self.assertJSONEqual(response_remove.content, {'status': 'removed'})
