from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountFlowTests(TestCase):
	def test_login_and_registration_pages_render(self):
		self.assertEqual(self.client.get(reverse("login")).status_code, 200)
		self.assertEqual(self.client.get(reverse("register")).status_code, 200)

	def test_registration_creates_and_authenticates_user(self):
		response = self.client.post(
			reverse("register"),
			{
				"username": "new-renter",
				"password1": "A-rentify-test-password-824!",
				"password2": "A-rentify-test-password-824!",
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertContains(response, "Welcome, new-renter.")

	def test_login_authenticates_user(self):
		user = get_user_model().objects.create_user(
			username="existing-renter",
			password="A-rentify-test-password-824!",
		)

		response = self.client.post(
			reverse("login"),
			{
				"username": user.username,
				"password": "A-rentify-test-password-824!",
			},
		)

		self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
		self.assertTrue(response.wsgi_request.user.is_authenticated)

	def test_profile_requires_authentication(self):
		response = self.client.get(reverse("profile"))

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('profile')}",
			fetch_redirect_response=False,
		)

	def test_logout_is_post_only_and_ends_session(self):
		user = get_user_model().objects.create_user(
			username="signed-in-renter",
			password="A-rentify-test-password-824!",
		)
		self.client.force_login(user)

		get_response = self.client.get(reverse("logout"))
		post_response = self.client.post(reverse("logout"), follow=True)

		self.assertEqual(get_response.status_code, 405)
		self.assertContains(post_response, "You have safely signed out")
		self.assertFalse(post_response.wsgi_request.user.is_authenticated)

	def test_drawer_shows_account_actions_for_current_session(self):
		guest_response = self.client.get(reverse("home"))
		self.assertContains(guest_response, reverse("login"))
		self.assertContains(guest_response, reverse("register"))
		self.assertNotContains(guest_response, "Log out")

		user = get_user_model().objects.create_user(
			username="drawer-renter",
			password="A-rentify-test-password-824!",
		)
		self.client.force_login(user)
		signed_in_response = self.client.get(reverse("home"))

		self.assertContains(signed_in_response, reverse("profile"))
		self.assertContains(signed_in_response, reverse("logout"))
		self.assertContains(signed_in_response, "Log out")
