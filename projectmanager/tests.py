from django.test import TestCase

from django.contrib.auth.models import User

# Create your tests here.

class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'dashboard/home.html')


class LogInTest(TestCase):
    def test_can_log_in(self):
        user = User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()

        response = self.client.login(username='testuser', password='user')
        self.assertEqual(response, False)
