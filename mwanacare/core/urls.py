from django.urls import path

from . import views


urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("children/", views.child_list, name="children"),
    path("children/new/", views.child_create, name="child_create"),
    path("children/<int:pk>/edit/", views.child_update, name="child_update"),
    path("records/", views.records, name="records"),
    path("reminders/", views.reminders, name="reminders"),
    path("facilities/", views.facility_finder, name="facility_finder"),
    path("facilities/new/", views.facility_create, name="facility_create"),
    path("referrals/", views.referrals, name="referrals"),
    path("referrals/<int:pk>/update/", views.referral_update, name="referral_update"),
    path("aftercare/", views.aftercare, name="aftercare"),
]
