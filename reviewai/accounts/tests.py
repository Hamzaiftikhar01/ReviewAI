from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='testpassword123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            password='adminpassword123'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.full_name, 'Admin User')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
