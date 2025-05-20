from django.test import TestCase
from accounts.models import Favorite
from django.contrib.auth import get_user_model
from products.models import Product, Category, Brand

class FavoriteModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', password='pass')
        self.category = Category.objects.create(name="C", slug="c")
        self.brand = Brand.objects.create(name="B", slug="b")
        self.product = Product.objects.create(
            name='Prod', slug='prod', category=self.category, brand=self.brand, price=1
        )

    def test_str_method(self):
        fav = Favorite.objects.create(user=self.user, product=self.product)
        self.assertEqual(str(fav), f"{self.user.username} -> {self.product}")
