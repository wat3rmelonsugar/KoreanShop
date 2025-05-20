from accounts.forms import UserRegisterForm
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'WrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(username='existing', email='existing@example.com', password='pass123')
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_missing_email(self):
        form_data = {
            'username': 'testuser',
            'email': '',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
