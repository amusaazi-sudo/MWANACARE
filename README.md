# MwanaCare

*One companion, from home to clinic and back.*

MwanaCare is a Django web app that helps parents and caregivers stay on top of their children's immunizations: it reminds them when vaccinations are due, keeps a digital health record, helps them find nearby partner health facilities, and gives safe after-vaccination guidance in English, Kiswahili and Luganda.

First built for the **Absa Girl Code Hackathon**, and still being improved.

**My role:** founder and lead developer. I came up with MwanaCare and designed and built the Django application: the data models, phone-number account linking, the admin workflow for clinics, reminders, the clinic finder, MwanaAI and Mwana Notes. I also redesigned the navigation for phones, with a bottom tab bar.

## The problem

Immunization journeys are fragmented and stressful for families. Parents forget vaccination dates, paper records get lost, and health facilities are hard to find. The result: children miss vaccines they need, leading to preventable illness.

MwanaCare follows the whole journey in one place: **remember → find → visit → record → understand → return**.

## Screenshots

| Home | Health record | Clinics |
|---|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Health record](docs/screenshots/health-record.png) | ![Clinics](docs/screenshots/facility-finder.png) |

## Features

| Page | What it does |
|---|---|
| **Dashboard** | Children, upcoming vaccinations, active reminders and recent completed referral visits |
| **Records** | Blood type, allergies, latest growth measurement with percentiles, and a vaccination timeline with status labels (Completed / Due soon / Overdue / Upcoming) |
| **Reminders** | Generated automatically from the vaccination schedule. A banner follows the caregiver across the site, turning red once a vaccination is overdue, until the reminder is resolved |
| **Clinics** | Search and filter partner clinics, see them on a live map, and sort by distance using the phone's location |
| **Visits** | Plan a clinic visit for a child, then record how it went |
| **MwanaAI** | Answers common after-vaccination and child-health questions in English, Kiswahili or Luganda, typed or spoken |
| **Mwana Notes** | Caregivers record health notes, bills paid or debts, by typing or voice, and send a copy to WhatsApp |

## Key design decisions

- **Caregivers never type in medical data.** Partner clinics enter records through the Django admin. At signup, a caregiver's account is linked to their facility's records by matching their phone number. This keeps medical data accurate and trustworthy.
- **MwanaAI is deliberately not a language model.** In a health setting, predictable answers matter more than clever ones, so MwanaAI uses keyword matching with fixed, pre-written answers. It gives general guidance and tells caregivers when to seek care, and never tries to diagnose.
- **No paid APIs needed.** Maps use Leaflet and OpenStreetMap, and voice input uses the browser's built-in speech recognition, so the app runs without API keys.

## Tech stack

- **Backend:** Python 3, Django 6.1, SQLite for development
- **Frontend:** Django templates with a shared `base.html`, Bootstrap 5
- **Maps:** Leaflet + OpenStreetMap
- **Voice input:** the browser's `SpeechRecognition` API (Chrome and Edge)
- **Collaboration:** Git and GitHub with feature branches and pull requests

## Since the hackathon

At the hackathon I focused on a clickable prototype of the core journey and documented the bigger integrations as a roadmap. Since then the app has gained real data models, phone-number account linking, automatic reminders with the site-wide banner, the live facility map with distance sorting, MwanaAI in three languages, voice input, and Mwana Notes.

## Challenges

1. **Turning screen-by-screen mockups into reusable templates.** I identified what repeated across screens (navigation, cards, badges) and moved it into `base.html` and shared styles instead of copying it into every page.
2. **Designing screens that didn't exist in the mockups.** The user journey needed both a vaccination schedule and a full health record, so I designed the missing screen myself and kept it consistent with the rest.
3. **Keeping health guidance safe.** MwanaAI had to help without ever sounding like a doctor: general guidance with clear advice on when to visit a clinic.
4. **Three people, one repository.** Early on we overwrote each other's work by all committing to `main`. We switched to feature branches and pull requests, with each person owning specific files.

## Status and roadmap

MwanaCare is a working prototype. My next focus is **polishing the user experience**: making each feature simpler and clearer to use.

| Phase | Goal |
|---|---|
| 1. MVP | Child profiles, vaccination records, automatic reminders, facility finder and aftercare guidance (in progress) |
| 2. Facility dashboards | Analytics and dashboards for health facilities |
| 3. USSD and SMS | Access for caregivers with feature phones |
| 4. Full ecosystem | Connections with pharmacies, labs, insurers and other partners |

Also planned: sending real WhatsApp messages through the WhatsApp Cloud API, automated tests, a public demo deployment, and having the Kiswahili and Luganda answers reviewed by native speakers and a clinician.

## Getting started

```bash
cd mwanacare
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash. macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

### Add data through the admin first

Caregivers can only link to records that already exist, so a facility (you, during setup) adds them first:

1. Log in at `http://127.0.0.1:8000/admin/` with your superuser account.
2. Under **Core → Parent profiles**, add a profile with a `phone_number` and `location`. Leave `user` blank; it fills in when the caregiver signs up.
3. Add the children in the inline **Children** section.
4. Open a child to add **Immunization records** and **Growth measurements**. These drive the health record page and the reminders.
5. Under **Core → Facilities**, add partner facilities. Add `latitude` and `longitude` to show them on the map.

### Sign up and log in as a caregiver

Go to `/signup/` and enter your name, the phone number entered in step 2, and a password. Spaces in the phone number are fine.

- No matching number: signup is refused with a message to contact the facility.
- Number already linked to an account: the caregiver is asked to log in instead.
- Matching and unclaimed: the account is created and linked to that profile and its children.

Caregivers then **log in with their phone number** and password. Staff and superusers log in with their username as usual.

## Running the tests

```bash
python manage.py test core
```

## Technical notes

- **Reminder banner:** a context processor (`core/context_processors.py`) adds active reminders to every page.
- **MwanaAI:** `core/services.py::post_immunization_answer`. The Kiswahili and Luganda answers are prototype translations and should be reviewed before real use.
- **WhatsApp:** `core/services.py::dispatch_whatsapp_message` prints messages to the server console by default. Set `WHATSAPP_PROVIDER` in `settings.py` and extend that function to connect a real provider.
- **Before deploying:** replace the development `SECRET_KEY` and set `DEBUG = False`. Signup passwords need at least 6 characters.

## Team

- **Aliyer Bakers Musaazi** — founder and lead developer
- **Taliwako Margaret** — helped shape the idea and pitch,mockups
- **Mangeni Hearty** — helped shape the idea and pitch