from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category, Brand

class TemplateRenderingTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=500,
            available=True,
            category=self.category,
            brand=self.brand,  # ← добавь это
        )

    def test_list_template_used(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertTemplateUsed(response, "products/product/list.html")

    def test_detail_template_used(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.id, self.product.slug])
        )
        self.assertTemplateUsed(response, "products/product/detail.html")
