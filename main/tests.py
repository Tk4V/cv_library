"""
Main tests module - imports all test modules for easy discovery.
"""
from django.test import TestCase
from django.urls import reverse
from .models import CV


class BasicCVTests(TestCase):
    """Basic CV tests for backward compatibility."""
    
    @classmethod
    def setUpTestData(cls) -> None:
        CV.objects.create(
            firstname="Ada",
            lastname="Lovelace",
            skills="Math",
            projects="Engine",
            bio="Pioneer",
            contacts="ada@example.com",
        )

    def test_list_page_redirects_to_login(self):
        """Test that CV list redirects to login when not authenticated."""
        response = self.client.get(reverse("cv_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('cv_list')}")

    def test_detail_page_redirects_to_login(self):
        """Test that CV detail redirects to login when not authenticated."""
        cv = CV.objects.first()
        response = self.client.get(reverse("cv_detail", args=[cv.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('cv_detail', args=[cv.pk])}")

    def test_home_page_accessible(self):
        """Test that home page is accessible without authentication."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CV Project")
