from django.test import SimpleTestCase
from django.urls import reverse, resolve
from products.views import product_list, product_detail

class TestUrls(SimpleTestCase):
    def test_list_url_resolves(self):
        url = reverse("products:product_list")
        self.assertEqual(resolve(url).func, product_list)

    def test_detail_url_resolves(self):
        url = reverse("products:product_detail", args=[1, "slug"])
        self.assertEqual(resolve(url).func, product_detail)
