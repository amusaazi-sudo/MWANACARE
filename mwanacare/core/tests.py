"""Tests for signup, login, home, records and navigation. Run with:  python manage.py test core"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Child, Facility, GrowthMeasurement, ImmunizationRecord, ParentProfile, Referral

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


class NavigationTests(TestCase):
    def setUp(self):
        self.profile = ParentProfile.objects.create(phone_number="0772123456")
        self.client.post(reverse("signup"), signup_data())

    def test_current_page_is_marked_in_the_menu(self):
        response = self.client.get(reverse("facility_finder"))
        self.assertContains(response, f'href="{reverse("facility_finder")}" class="active" aria-current="page"')

    def test_old_children_page_redirects_to_records(self):
        self.assertRedirects(self.client.get(reverse("children")), reverse("records"))

    def test_visits_use_caregiver_friendly_words(self):
        child = Child.objects.create(parent=self.profile, name="Amani", date_of_birth=date(2025, 1, 1), gender="F")
        clinic = Facility.objects.create(name="Mulago", address="Kampala", location="Kampala")
        Referral.objects.create(child=child, facility=clinic)
        response = self.client.get(reverse("referrals"))
        self.assertContains(response, "Planned")
        self.assertContains(response, "Record visit")
        self.assertNotContains(response, "Referral Flow")


class HomeTests(TestCase):
    def setUp(self):
        self.profile = ParentProfile.objects.create(phone_number="0772123456")
        self.client.post(reverse("signup"), signup_data())
        self.child = self.add_child("Amani")

    def add_child(self, name):
        return Child.objects.create(parent=self.profile, name=name, date_of_birth=date(2025, 6, 1), gender="F")

    def add_record(self, child, vaccine, due_in_days=None, given=False):
        today = date.today()
        return ImmunizationRecord.objects.create(
            child=child,
            vaccine_name=vaccine,
            date_given=today - timedelta(days=60) if given else None,
            next_due_date=today + timedelta(days=due_in_days) if due_in_days is not None else None,
        )

    def test_shows_the_next_vaccines_and_a_countdown(self):
        self.add_record(self.child, "BCG", given=True)
        self.add_record(self.child, "Polio 3", due_in_days=6)
        self.add_record(self.child, "PCV 3", due_in_days=6)
        self.add_record(self.child, "Measles-Rubella 1", due_in_days=40)

        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "In 6 days")
        self.assertContains(response, "Polio 3")
        self.assertContains(response, "PCV 3")
        self.assertContains(response, "1 of 4")
        self.assertContains(response, "Coming up")

    def test_overdue_vaccine_says_how_late_it_is(self):
        self.add_record(self.child, "Polio 3", due_in_days=-3)
        self.assertContains(self.client.get(reverse("dashboard")), "3 days late")

    def test_all_caught_up_when_nothing_is_scheduled(self):
        self.add_record(self.child, "BCG", given=True)
        self.assertContains(self.client.get(reverse("dashboard")), "All caught up")

    def test_switching_between_children(self):
        nia = self.add_child("Nia")
        response = self.client.get(reverse("dashboard"), {"child": nia.pk})
        self.assertContains(response, "Next for Nia")

    def test_plan_a_visit_preselects_the_child(self):
        response = self.client.get(reverse("referrals"), {"child": self.child.pk})
        self.assertContains(response, f'value="{self.child.pk}" selected')
