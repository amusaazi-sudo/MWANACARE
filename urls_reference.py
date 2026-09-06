# core/urls.py
# Reference wiring for the {% url '...' %} tags used across the templates.
# Merge this into your existing urls.py (adjust view imports to match views.py).

from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tracker/", views.child_tracker, name="child_tracker"),
    path("records/", views.records, name="records"),
    path("hospitals/", views.hospital_finder, name="hospital_finder"),
    path("reminders/", views.reminder, name="reminder"),
    path("referrals/", views.referral, name="referral"),
    path("aftercare/", views.aftercare, name="aftercare"),
]

# Matching views.py stubs (swap render() context for real querysets later):
#
# from django.shortcuts import render
#
# def welcome(request):        return render(request, "welcome.html")
# def signup(request):         return render(request, "signup.html")
# def dashboard(request):      return render(request, "dashboard.html")
# def child_tracker(request):  return render(request, "child-tracker.html")
# def records(request):        return render(request, "records.html")
# def hospital_finder(request):return render(request, "hospital-finder.html")
# def reminder(request):       return render(request, "reminder.html")
# def referral(request):       return render(request, "referral.html")
# def aftercare(request):      return render(request, "aftercare.html")
