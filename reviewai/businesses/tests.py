from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Business

User = get_user_model()

class BusinessesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            full_name='Business Owner',
            password='password123'
        )

    def test_create_business(self):
        business = Business.objects.create(
            owner=self.user,
            name='Test Restaurant',
            category='Restaurant',
            location='London, UK',
            tone='Friendly'
        )
        self.assertEqual(business.name, 'Test Restaurant')
        self.assertEqual(business.owner, self.user)
        self.assertEqual(business.category, 'Restaurant')
        self.assertEqual(business.tone, 'Friendly')
