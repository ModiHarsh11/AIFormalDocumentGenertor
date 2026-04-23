from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
	EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
	DEFAULT_FROM_EMAIL="no-reply@test.local",
)
class AuthFlowTests(TestCase):
	def setUp(self):
		self.password = "StrongPass123!"
		self.user = User.objects.create_user(
			username="alice",
			email="alice@example.com",
			password=self.password,
		)

	def test_home_redirects_anonymous_users_to_login(self):
		response = self.client.get(reverse("home"))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

	def test_home_renders_for_authenticated_users(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse("home"))
		self.assertEqual(response.status_code, 200)

	def test_login_page_contains_forgot_password_link(self):
		response = self.client.get(reverse("login"))
		self.assertContains(response, reverse("password_reset"))

	def test_password_reset_request_sends_email(self):
		response = self.client.post(reverse("password_reset"), {"email": self.user.email})
		self.assertRedirects(response, reverse("password_reset_done"))
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn("password reset", mail.outbox[0].subject.lower())

	def test_password_reset_link_opens_confirm_page(self):
		self.client.post(reverse("password_reset"), {"email": self.user.email})
		self.assertEqual(len(mail.outbox), 1)

		reset_url = None
		for line in mail.outbox[0].body.splitlines():
			line = line.strip()
			if "/reset/" in line:
				reset_url = line
				break

		self.assertIsNotNone(reset_url, "Password reset URL not found in email body.")
		response = self.client.get(reset_url, follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Set a New Password")
