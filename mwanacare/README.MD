# 🌍 MwanaCare

**One companion, from home to clinic and back.**

MwanaCare is an **AI-powered child-health navigation platform** built with **Django, Python, Bootstrap, and modern APIs**.  
It transforms the fragmented immunization journey into a connected experience: reminders, records, referrals, facility search, and safe aftercare guidance — all in one system.

---

## 🚀 Core Features
- 👶 **Child Registration** — One-time caregiver sign-up creates portable child profiles.
- 📊 **Dashboard** — Unified view of all children, upcoming vaccines, reminders, and visit history.
- 💉 **Digital Health Records** — Vaccinations, growth, diagnoses, and visit notes stored in a timeline.
- 🔔 **Smart Notifications** — In-app alerts + WhatsApp message dispatch for reminders and referrals.
- 📍 **Hospital Search** — Integrated maps and geolocation to find nearby verified facilities.
- 📋 **Digital Referrals** — Track referral status from pending → completed.
- 🤖 **AI Aftercare Assistant** — Post-immunization guidance via chatbot interface.
- 📱 **WhatsApp Integration** — Families receive reminders where they already are, no new app habit needed.

---

## 🧩 System Flow
```text
👩🏾 Parent
      │
      ▼
👶 Add Child Profile
      │
      ▼
💉 Vaccination Record
      │
      ▼
🔔 Vaccination Due
      │
      ▼
📍 Find Care
      │
      ▼
🏥 Select Facility
      │
      ▼
📋 Digital Referral
      │
      ▼
💉 Receive Care
      │
      ▼
📱 Record Updated
      │
      ▼
🤖 AI Aftercare
      │
      ▼
🔔 Next Reminder
🛠️ Tech Stack
Backend: Django 5, Python 3.14

Frontend: HTML, CSS, Bootstrap

Database: SQLite (dev), PostgreSQL (prod)

Notifications: Django signals + Celery tasks

Messaging: WhatsApp Cloud API integration

AI Assistant: Django app + external AI API adapter

Maps/Location: Leaflet.js or Google Maps API integration

📂 Project Structure
Code
mwanacare/
│── core/                # Main app (models, views, templates)
│   ├── models.py        # Child, Facility, ImmunizationRecord, Referral, Reminder
│   ├── views.py         # Business logic
│   ├── templates/       # HTML templates (Bootstrap UI)
│   └── static/          # CSS, JS, images
│── mwanacare/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│── requirements.txt     # Dependencies
│── manage.py
⚙️ Setup Instructions
Clone the repository:

bash
git clone https://github.com/amusaazi-sudo/MWANACARE.git
cd MWANACARE
Create and activate virtual environment:

bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
Install dependencies:

bash
pip install -r requirements.txt
Run migrations:

bash
python manage.py makemigrations
python manage.py migrate
Start development server:

bash
python manage.py runserver
👥 Team Workflow
Branches:

aliah-branch → Models + backend logic

hearty-branch → Bootstrap UI + templates

maggy-branch → Facility finder + referral + AI assistant

Use Pull Requests for merging into main.

Keep main stable and production-ready.

📌 Roadmap
Phase 1 (MVP): Child profiles, vaccination records, reminders, facility finder, AI aftercare.

Phase 2: Facility dashboards, referral analytics, subscription model.

Phase 3: USSD/SMS inclusion for non-smartphone caregivers.

Phase 4: Full ecosystem integration (clinics, labs, pharmacies, insurers).

💡 Business Model
Facility subscriptions for verified listings + analytics.

Referral coordination fees per completed referral.

Premium caregiver tier for multi-child households.

Verified partner listings (pharmacies, labs, insurers).

✨ Closing Note
MwanaCare is not a replacement for doctors.
It is a bridge: helping caregivers remember, reach, record, understand, and return — ensuring no child is left behind in the immunization journey.

Code

---

This README is **technical, visionary, and investor-ready**: it shows