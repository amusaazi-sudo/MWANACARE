"""Tests for signing up and logging in. Run with:  python manage.py test core"""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Child, GrowthMeasurement, ParentProfile

PASSWORD = "safe-pass-123"


def signup_data(**overrides):
    data = {
        "first_name": "Jane Nakato",
        "phone_number": "0772123456",
        "email": "",
        "password1": PASSWORD,
        "password2": PASSWORD,
    }
    data.update(overrides)
    return data


class SignUpTests(TestCase):
    def setUp(self):
        self.profile = ParentProfile.objects.create(phone_number="0772123456", location="Kampala")

    def test_name_with_spaces_and_no_email_is_accepted(self):
        response = self.client.post(reverse("signup"), signup_data())
        self.assertRedirects(response, reverse("dashboard"))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.user.first_name, "Jane Nakato")

    def test_spaces_in_the_phone_number_still_match(self):
        self.client.post(reverse("signup"), signup_data(phone_number="0772 123 456"))
        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.user)

    def test_unknown_phone_number_is_rejected(self):
        response = self.client.post(reverse("signup"), signup_data(phone_number="0700000000"))
        self.assertContains(response, "couldn&#x27;t find this number")
        self.assertFalse(User.objects.exists())

    def test_number_that_already_has_an_account_is_rejected(self):
        self.client.post(reverse("signup"), signup_data())
        self.client.logout()
        response = self.client.post(reverse("signup"), signup_data(first_name="Someone Else"))
        self.assertContains(response, "already has an account")
        self.assertEqual(User.objects.count(), 1)

    def test_short_password_is_rejected(self):
        response = self.client.post(reverse("signup"), signup_data(password1="abc", password2="abc"))
        self.assertContains(response, "at least 6 characters")


class LoginTests(TestCase):
    def setUp(self):
        ParentProfile.objects.create(phone_number="0772123456")
        self.client.post(reverse("signup"), signup_data())
        self.client.logout()

    def test_caregiver_logs_in_with_phone_number(self):
        response = self.client.post(reverse("login"), {"username": "0772 123 456", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboard"))

    def test_wrong_password_shows_a_clear_message(self):
        response = self.client.post(reverse("login"), {"username": "0772123456", "password": "wrong"})
        self.assertContains(response, "don&#x27;t match")

    def test_staff_can_still_log_in_with_username(self):
        User.objects.create_user(username="nurse", password=PASSWORD)
        self.assertTrue(self.client.login(username="nurse", password=PASSWORD))


class HealthRecordTests(TestCase):
    def test_percentiles_use_proper_ordinals(self):
        profile = ParentProfile.objects.create(phone_number="0772123456")
        self.client.post(reverse("signup"), signup_data())
        child = Child.objects.create(parent=profile, name="Amani", date_of_birth=date(2025, 1, 1), gender="F")
        GrowthMeasurement.objects.create(child=child, height_cm=70, height_percentile=2, weight_percentile=23)

        response = self.client.get(reverse("child_health_record", args=[child.pk]))
        self.assertContains(response, "2nd percentile")
        self.assertContains(response, "23rd percentile")
