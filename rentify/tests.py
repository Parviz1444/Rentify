from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Listing


class ListingManagementTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="listing-owner",
            password="A-rentify-test-password-824!",
        )
        self.other_user = user_model.objects.create_user(
            username="other-user",
            password="A-rentify-test-password-824!",
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            purpose=Listing.Purpose.RENT,
            property_type=Listing.PropertyType.APARTMENT,
            title="Sunny apartment",
            description="A comfortable apartment.",
            city="Bukhara",
            address="1 Main Street",
            price="500.00",
            bedrooms=2,
            bathrooms=1,
            area_sqm=75,
        )

    def test_owner_can_edit_listing(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("listing_edit", args=[self.listing.pk]),
            {
                "purpose": Listing.Purpose.RENT,
                "property_type": Listing.PropertyType.APARTMENT,
                "title": "Updated apartment",
                "description": "An updated description.",
                "city": "Bukhara",
                "address": "1 Main Street",
                "price": "600.00",
                "bedrooms": "2",
                "bathrooms": "1",
                "area_sqm": "75",
            },
        )

        self.assertRedirects(
            response,
            reverse("listing_detail", args=[self.listing.pk]),
            fetch_redirect_response=False,
        )
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Updated apartment")

    def test_only_owner_can_edit_or_delete_listing(self):
        self.client.force_login(self.other_user)

        edit_response = self.client.get(reverse("listing_edit", args=[self.listing.pk]))
        delete_response = self.client.post(
            reverse("listing_delete", args=[self.listing.pk])
        )

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.listing.refresh_from_db()
        self.assertTrue(self.listing.is_active)

    def test_owner_can_delete_listing_with_post(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("listing_delete", args=[self.listing.pk]))

        self.assertRedirects(
            response,
            reverse("profile"),
            fetch_redirect_response=False,
        )
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_active)

    def test_delete_requires_post(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("listing_delete", args=[self.listing.pk]))

        self.assertEqual(response.status_code, 405)

    def test_management_buttons_are_only_shown_to_owner(self):
        guest_response = self.client.get(
            reverse("listing_detail", args=[self.listing.pk])
        )
        self.assertNotContains(guest_response, ">Edit</span>", status_code=200)
        self.assertNotContains(guest_response, ">Delete</span>", status_code=200)

        self.client.force_login(self.owner)
        owner_response = self.client.get(
            reverse("listing_detail", args=[self.listing.pk])
        )
        self.assertContains(owner_response, ">Edit</span>")
        self.assertContains(owner_response, ">Delete</span>")