from django.test import TestCase
from orders.forms import OrderCreateForm

class OrderCreateFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'address': '123 Street'
        }
        form = OrderCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'full_name': 'John Doe',
            'email': 'invalid-email',
            'address': '123 Street'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
