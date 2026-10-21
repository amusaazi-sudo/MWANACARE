from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    FacilitySearchForm,
    NoteForm,
    ParentProfileForm,
    ReferralCompletionForm,
    ReferralForm,
    SignUpForm,
)
from .models import Child, Facility, ImmunizationRecord, LANGUAGE_CHOICES, Note, ParentProfile, Referral, Reminder
from .overview import child_overview
from .services import (
    dispatch_whatsapp_message,
    forward_note_to_whatsapp,
    post_immunization_answer,
    sync_due_reminders,
)


def get_parent_profile(user):
    profile = ParentProfile.objects.filter(user=user).first()
    if profile is not None:
        return profile
    # Safety net for accounts (e.g. staff/superusers) that were never linked to a
    # facility-provided record. Ordinary caregivers get linked at signup instead.
    profile, _ = ParentProfile.objects.get_or_create(user=user, phone_number=f"unset-{user.pk}")
    return profile


def welcome(request):
    return render(request, "welcome.html")


def signup(request):
    """Create a login and link it to the records the caregiver's facility already entered.

    SignUpForm checks the phone number matches an unclaimed profile.
    """
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        form.profile.user = user
        form.profile.save(update_fields=["user"])
        # Two login backends are configured, so Django needs to be told which one to use here.
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Welcome, {user.first_name}! Your account is linked to your child's records.")
        return redirect("dashboard")
    return render(request, "signup.html", {"form": form})


@login_required
def dashboard(request):
    """Home: what the chosen child needs next, then what's coming up."""
    profile = get_parent_profile(request.user)
    children = list(Child.objects.filter(parent=profile).order_by("date_of_birth"))
    chosen = request.GET.get("child")
    child = next((c for c in children if str(c.pk) == chosen), children[0] if children else None)

    planned_visit = None
    if child:
        planned_visit = (
            Referral.objects.filter(child=child, status="Pending")
            .select_related("facility")
            .order_by("-referral_date")
            .first()
        )

    return render(
        request,
        "dashboard.html",
        {
            "children": children,
            "child": child,
            "overview": child_overview(child) if child else None,
            "planned_visit": planned_visit,
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
    """Old "Children" page, now part of Records. Kept so existing links still work."""
    return redirect("records")


@login_required
def records(request):
    """Overview: pick which child's health record to view. No data entry here --
    vaccination history comes entirely from the facility via the admin."""
    profile_obj = get_parent_profile(request.user)
    children = Child.objects.filter(parent=profile_obj)
    if children.count() == 1:
        return redirect("child_health_record", pk=children.first().pk)
    return render(request, "records.html", {"children": children})


@login_required
def child_health_record(request, pk):
    profile_obj = get_parent_profile(request.user)
    child = get_object_or_404(Child, pk=pk, parent=profile_obj)
    immunizations = ImmunizationRecord.objects.filter(child=child).order_by("next_due_date", "date_given")
    return render(
        request,
        "health-record.html",
        {
            "child": child,
            "immunizations": immunizations,
            "growth": child.latest_growth_measurement(),
        },
    )


@login_required
def reminders(request):
    """Reminders are derived automatically from each child's due/overdue
    vaccinations -- there is nothing for a caregiver to type in here."""
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        reminder = get_object_or_404(Reminder, pk=request.POST.get("reminder_id"), child__parent=profile_obj)
        result = dispatch_whatsapp_message(profile_obj.phone_number, reminder.message)
        reminder.sent = result.sent
        reminder.save(update_fields=["sent"])
        messages.success(request, result.detail)
        return redirect("reminders")

    reminder_list = sync_due_reminders(profile_obj)
    return render(request, "reminder.html", {"reminders": reminder_list})


@login_required
def facility_finder(request):
    form = FacilitySearchForm(request.GET or None)
    facilities = Facility.objects.all().order_by("name")
    query = ""
    if form.is_valid():
        query = form.cleaned_data.get("location") or ""
        if query:
            facilities = facilities.filter(
                Q(name__icontains=query) | Q(location__icontains=query) | Q(address__icontains=query)
            )

    active_tag = request.GET.get("tag", "")
    if active_tag:
        facilities = facilities.filter(services__icontains=active_tag)

    return render(
        request,
        "hospital-finder.html",
        {
            "form": form,
            "facilities": facilities,
            "query_location": query,
            "active_tag": active_tag,
            "filter_tags": ["Vaccination", "Paediatrics", "Emergency"],
        },
    )


@login_required
def referrals(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = ReferralForm(request.POST, parent_profile=profile_obj)
        if form.is_valid():
            referral = form.save()
            message = f"Visit planned for {referral.child.name} at {referral.facility.name}."
            result = dispatch_whatsapp_message(referral.child.parent.phone_number, message)
            messages.success(request, f"{message} {result.detail}")
            return redirect("referrals")
    else:
        # "Plan a visit" on Home links here with ?child=<id> to preselect the child.
        form = ReferralForm(parent_profile=profile_obj, initial={"child": request.GET.get("child")})

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
            messages.success(request, "Visit updated.")
            return redirect("referrals")
    else:
        form = ReferralCompletionForm(instance=referral)
    return render(request, "referral-update.html", {"form": form, "referral": referral})


@login_required
def mwanaai(request):
    answer = None
    question = ""
    language = request.POST.get("language") or "en"
    if request.method == "POST":
        question = request.POST.get("question", "")
        answer = post_immunization_answer(question, language)
    return render(
        request,
        "mwanaai.html",
        {
            "answer": answer,
            "question": question,
            "language": language,
            "language_choices": LANGUAGE_CHOICES,
        },
    )


@login_required
def notes(request):
    profile_obj = get_parent_profile(request.user)
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.parent = profile_obj
            note.save()
            messages.success(request, "Note saved.")
            return redirect("notes")
    else:
        form = NoteForm()

    note_list = Note.objects.filter(parent=profile_obj)
    return render(request, "notes.html", {"form": form, "notes": note_list})


@login_required
def note_forward(request, pk):
    profile_obj = get_parent_profile(request.user)
    note = get_object_or_404(Note, pk=pk, parent=profile_obj)
    if request.method == "POST":
        result = forward_note_to_whatsapp(note)
        note.forwarded_to_whatsapp = result.sent
        note.save(update_fields=["forwarded_to_whatsapp"])
        messages.success(request, result.detail)
    return redirect("notes")
