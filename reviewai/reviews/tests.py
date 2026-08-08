from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from businesses.models import Business
from .models import Review

User = get_user_model()

class ReviewsTest(TestCase):
    def setUp(self):
        # Create User A
        self.user_a = User.objects.create_user(
            email='user_a@example.com',
            full_name='User A',
            password='password123'
        )
        self.business_a = Business.objects.create(
            owner=self.user_a,
            name='Business A',
            category='Restaurant'
        )
        self.review_a = Review.objects.create(
            business=self.business_a,
            customer_name='Customer A',
            rating=5,
            review_text='Food was good'
        )

        # Create User B
        self.user_b = User.objects.create_user(
            email='user_b@example.com',
            full_name='User B',
            password='password123'
        )
        self.business_b = Business.objects.create(
            owner=self.user_b,
            name='Business B',
            category='Hotel'
        )
        self.review_b = Review.objects.create(
            business=self.business_b,
            customer_name='Customer B',
            rating=2,
            review_text='Room was dirty'
        )

        self.client = Client()

    def test_review_isolation(self):
        # Log in User A
        self.client.login(email='user_a@example.com', password='password123')

        # Try to view User A's review details (should succeed)
        response_a = self.client.get(reverse('review_detail', args=[self.review_a.id]))
        self.assertEqual(response_a.status_code, 200)

        # Try to view User B's review details (should fail with 404)
        response_b = self.client.get(reverse('review_detail', args=[self.review_b.id]))
        self.assertEqual(response_b.status_code, 404)

        # Try to delete User B's review (should fail with 404)
        response_delete = self.client.post(reverse('review_delete', args=[self.review_b.id]))
        self.assertEqual(response_delete.status_code, 404)
