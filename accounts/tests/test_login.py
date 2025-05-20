from django.test import TestCase
from django.contrib.auth import get_user_model

class LoginTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="alant",
            email="alant@example.com",
            password="alan123"
        )

    def test_login_with_valid_credentials(self):
        login = self.client.login(username="alant", password="alan123")
        self.assertTrue(login)

    def test_login_view_response(self):
        response = self.client.post('/login/', {
            'username': 'alant',
            'password': 'alan123',
        })
        self.assertEqual(response.status_code, 302)
