"""Let caregivers log in with the phone number their health facility registered.

Caregivers remember their phone number far more easily than a username they
chose once. Staff and superusers still log in with their username, through
Django's normal ModelBackend, which stays enabled in settings.
"""

import re

from django.contrib.auth.backends import ModelBackend

from .models import ParentProfile


def normalize_phone(value):
    """Remove spaces, dashes, dots and brackets: '0772 123-456' -> '0772123456'."""
    return re.sub(r"[\s\-.()]", "", value or "")


def find_profile_by_phone(value):
    """Match the phone number as typed, or with spacing removed."""
    candidates = {value.strip(), normalize_phone(value)}
    return ParentProfile.objects.filter(phone_number__in=candidates).select_related("user").first()


class PhoneNumberBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        profile = find_profile_by_phone(username)
        user = profile.user if profile else None
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
