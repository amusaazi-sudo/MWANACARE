from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .backends import find_profile_by_phone, normalize_phone
from .models import Child, Note, Referral, ParentProfile


def _widget_attrs(**extra):
    attrs = {"class": "form-control"}
    attrs.update(extra)
    return attrs


class SignUpForm(UserCreationForm):
    """Caregivers sign up with their name and the phone number their clinic registered.

    The phone number becomes their login, so there is no username to remember.
    """

    first_name = forms.CharField(
        max_length=150,
        label="Your name",
        widget=forms.TextInput(attrs=_widget_attrs(autocomplete="name", placeholder="e.g. Jane Nakato")),
    )
    phone_number = forms.CharField(
        max_length=20,
        label="Phone number",
        help_text="Use the number your health facility registered. You'll log in with it.",
        widget=forms.TextInput(attrs=_widget_attrs(autocomplete="tel", inputmode="tel", placeholder="e.g. 0772123456")),
    )
    email = forms.EmailField(
        required=False,
        label="Email (optional)",
        widget=forms.EmailInput(attrs=_widget_attrs(autocomplete="email")),
    )

    field_order = ["first_name", "phone_number", "email", "password1", "password2"]

    class Meta:
        model = User
        fields = ["first_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = None
        for field_name in ("password1", "password2"):
            self.fields[field_name].widget.attrs.update(_widget_attrs(autocomplete="new-password"))
            # Drop Django's default password-rules bullet list; this page only
            # enforces a simple minimum length (see validate_password_for_user).
            self.fields[field_name].help_text = ""
        self.fields["password1"].help_text = "At least 6 characters."

    def clean_phone_number(self):
        phone = normalize_phone(self.cleaned_data["phone_number"])
        profile = find_profile_by_phone(self.cleaned_data["phone_number"])
        if profile is None:
            raise forms.ValidationError(
                "We couldn't find this number. Check it with your health facility, "
                "or ask them to register you and your child first."
            )
        if profile.user_id is not None or User.objects.filter(username=phone).exists():
            raise forms.ValidationError("This number already has an account. Please log in instead.")
        self.profile = profile
        return phone

    def validate_password_for_user(self, user, password_field_name="password2"):
        # Skip the project-wide complexity/common-password/similarity checks for
        # signup specifically; just require a reasonable minimum length.
        password = self.cleaned_data.get(password_field_name)
        if password and len(password) < 6:
            self.add_error(password_field_name, "Password must be at least 6 characters long.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["phone_number"]
        user.first_name = self.cleaned_data["first_name"].strip()
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
        return user


class PhoneLoginForm(AuthenticationForm):
    """Django's login form, relabelled so caregivers log in with their phone number."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "That phone number and password don't match. Check both and try again.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Phone number"
        self.fields["username"].widget.attrs.update(
            _widget_attrs(autocomplete="tel", inputmode="tel", placeholder="e.g. 0772123456")
        )
        self.fields["password"].widget.attrs.update(_widget_attrs(autocomplete="current-password"))


class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ["phone_number", "location"]
        widgets = {
            "phone_number": forms.TextInput(attrs=_widget_attrs()),
            "location": forms.TextInput(attrs=_widget_attrs()),
        }


class FacilitySearchForm(forms.Form):
    location = forms.CharField(
        max_length=200,
        required=False,
        label="Search",
        widget=forms.TextInput(attrs=_widget_attrs(placeholder="Search hospitals, clinics...")),
    )


class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = ["child", "facility"]

    def __init__(self, *args, parent_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_profile is not None:
            self.fields["child"].queryset = Child.objects.filter(parent=parent_profile)
        self.fields["child"].widget.attrs["class"] = "form-select"
        self.fields["facility"].widget.attrs["class"] = "form-select"
        self.fields["child"].label = "Child"
        self.fields["facility"].label = "Clinic"


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["category", "content", "language"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "content": forms.Textarea(attrs=_widget_attrs(rows=4, id="note-content")),
            "language": forms.Select(attrs={"class": "form-select", "id": "note-language"}),
        }


class ReferralCompletionForm(forms.ModelForm):
    # Caregiver-friendly words for the stored statuses (no database change needed).
    STATUS_LABELS = [("Pending", "Planned"), ("Completed", "Visited"), ("Cancelled", "Cancelled")]

    class Meta:
        model = Referral
        fields = ["status", "visit_notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "visit_notes": forms.Textarea(attrs=_widget_attrs(rows=4, placeholder="e.g. Got the measles vaccine. Next visit in 3 months.")),
        }
        labels = {"status": "Did the visit happen?", "visit_notes": "Notes from the visit (optional)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = self.STATUS_LABELS
