# Register your models here.
from django.contrib import admin
from .models import ParentProfile, Child, Facility, ImmunizationRecord, Referral, Reminder

admin.site.register([ParentProfile, Child, Facility, ImmunizationRecord, Referral, Reminder])
