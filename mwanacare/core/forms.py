from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Child, Facility, ImmunizationRecord, ParentProfile, Referral, Reminder


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)
    location = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "phone_number", "location"]


class ParentProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ["phone_number", "location"]


class ChildForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Child
        fields = ["name", "date_of_birth", "gender"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class ImmunizationRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ImmunizationRecord
        fields = ["child", "vaccine_name", "date_given", "next_due_date", "facility"]
        widgets = {
            "date_given": forms.DateInput(attrs={"type": "date"}),
            "next_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, parent_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_profile:
            self.fields["child"].queryset = Child.objects.filter(parent=parent_profile)


class ReminderForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["child", "message", "due_date", "sent"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, parent_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_profile:
            self.fields["child"].queryset = Child.objects.filter(parent=parent_profile)


class ReferralForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Referral
        fields = ["child", "facility"]

    def __init__(self, *args, parent_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_profile:
            self.fields["child"].queryset = Child.objects.filter(parent=parent_profile)


class ReferralCompletionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Referral
        fields = ["status", "visit_notes"]


class FacilitySearchForm(BootstrapFormMixin, forms.Form):
    location = forms.CharField(max_length=200, required=False)
    radius_km = forms.IntegerField(min_value=1, max_value=100, initial=10)


class FacilityForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Facility
        fields = ["name", "address", "phone", "email", "location", "latitude", "longitude"]
