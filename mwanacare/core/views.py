from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ChildForm,
    FacilityForm,
    FacilitySearchForm,
    ImmunizationRecordForm,
    ParentProfileForm,
    ReferralCompletionForm,
    ReferralForm,
    ReminderForm,
    SignUpForm,
)
from .models import Child, Facility, ImmunizationRecord, ParentProfile, Referral, Reminder
from .services import dispatch_whatsapp_message, post_immunization_answer


def get_parent_profile(user):
    profile, _ = ParentProfile.objects.get_or_create(user=user)
    return profile


def welcome(request):
    return render(request, "welcome.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            ParentProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data.get("phone_number", ""),
                location=form.cleaned_data.get("location", ""),
            )
            login(request, user)
            messages.success(request, "Your MwanaCare account is ready.")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


@login_required
def dashboard(request):
    profile = get_parent_profile(request.user)
    today = timezone.localdate()
    children = Child.objects.filter(parent=profile)
    upcoming_records = ImmunizationRecord.objects.filter(
        child__parent=profile,
        next_due_date__gte=today,
    ).order_by("next_due_date")[:6]
    reminders = Reminder.objects.filter(
        child__parent=profile,
        due_date__gte=today,
        sent=False,
    ).order_by("due_date")[:6]
    recent_visits = Referral.objects.filter(
        child__parent=profile,
        status="Completed",
    ).order_by("-completed_at", "-referral_date")[:6]

    return render(
        request,
        "dashboard.html",
        {
            "children": children,
            "upcoming_records": upcoming_records,
            "reminders": reminders,
            "recent_visits": recent_visits,
            "pending_referrals": Referral.objects.filter(child__parent=profile, status="Pending").count(),
        },
    )


@login_required
def profile(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ParentProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ParentProfileForm(instance=profile_obj)
    return render(request, "profile.html", {"form": form})


@login_required
def child_list(request):
    profile_obj = get_parent_profile(request.user)
    children = Child.objects.filter(parent=profile_obj)
    return render(request, "child-tracker.html", {"children": children})


@login_required
def child_create(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = profile_obj
            child.save()
            messages.success(request, f"{child.name}'s profile was added.")
            return redirect("children")
    else:
        form = ChildForm()
    return render(request, "child-form.html", {"form": form, "title": "Register Child"})


@login_required
def child_update(request, pk):
    profile_obj = get_parent_profile(request.user)
    child = get_object_or_404(Child, pk=pk, parent=profile_obj)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, "Child profile updated.")
            return redirect("children")
    else:
        form = ChildForm(instance=child)
    return render(request, "child-form.html", {"form": form, "title": "Edit Child Profile"})


@login_required
def records(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ImmunizationRecordForm(request.POST, parent_profile=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Vaccination record saved.")
            return redirect("records")
    else:
        form = ImmunizationRecordForm(parent_profile=profile_obj)

    records_qs = ImmunizationRecord.objects.filter(child__parent=profile_obj).order_by("next_due_date", "child__name")
    return render(request, "records.html", {"form": form, "records": records_qs})


@login_required
def reminders(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ReminderForm(request.POST, parent_profile=profile_obj)
        if form.is_valid():
            reminder = form.save()
            result = dispatch_whatsapp_message(reminder.child.parent.phone_number, reminder.message)
            messages.success(request, result.detail)
            return redirect("reminders")
    else:
        form = ReminderForm(parent_profile=profile_obj)

    reminder_list = Reminder.objects.filter(child__parent=profile_obj).order_by("due_date")
    return render(request, "reminder.html", {"form": form, "reminders": reminder_list})


@login_required
def facility_finder(request):
    form = FacilitySearchForm(request.GET or None)
    facilities = Facility.objects.all().order_by("name")
    query_location = ""
    if form.is_valid():
        query_location = form.cleaned_data.get("location") or ""
        if query_location:
            facilities = facilities.filter(location__icontains=query_location)
    return render(
        request,
        "hospital-finder.html",
        {"form": form, "facilities": facilities, "query_location": query_location},
    )


@login_required
def facility_create(request):
    if request.method == "POST":
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Facility added.")
            return redirect("facility_finder")
    else:
        form = FacilityForm()
    return render(request, "facility-form.html", {"form": form})


@login_required
def referrals(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ReferralForm(request.POST, parent_profile=profile_obj)
        if form.is_valid():
            referral = form.save()
            message = f"Referral created for {referral.child.name} to {referral.facility.name}."
            result = dispatch_whatsapp_message(referral.child.parent.phone_number, message)
            messages.success(request, f"{message} {result.detail}")
            return redirect("referrals")
    else:
        form = ReferralForm(parent_profile=profile_obj)

    referral_list = Referral.objects.filter(child__parent=profile_obj).order_by("-referral_date")
    return render(request, "referral.html", {"form": form, "referrals": referral_list})


@login_required
def referral_update(request, pk):
    profile_obj = get_parent_profile(request.user)
    referral = get_object_or_404(Referral, pk=pk, child__parent=profile_obj)
    if request.method == "POST":
        form = ReferralCompletionForm(request.POST, instance=referral)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.status == "Completed" and not updated.completed_at:
                updated.completed_at = timezone.now()
            updated.save()
            messages.success(request, "Referral record updated.")
            return redirect("referrals")
    else:
        form = ReferralCompletionForm(instance=referral)
    return render(request, "referral-update.html", {"form": form, "referral": referral})


@login_required
def aftercare(request):
    answer = None
    question = ""
    if request.method == "POST":
        question = request.POST.get("question", "")
        answer = post_immunization_answer(question)
    return render(request, "aftercare.html", {"answer": answer, "question": question})
