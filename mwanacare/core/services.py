from dataclasses import dataclass

from django.conf import settings


@dataclass
class WhatsAppDispatchResult:
    sent: bool
    detail: str


def dispatch_whatsapp_message(phone_number, message):
    """Placeholder integration point for Twilio or Meta WhatsApp Cloud API."""
    if not phone_number:
        return WhatsAppDispatchResult(False, "No phone number on caregiver profile.")

    provider = getattr(settings, "WHATSAPP_PROVIDER", "console")
    if provider == "console":
        print(f"[MwanaCare WhatsApp] To {phone_number}: {message}")
        return WhatsAppDispatchResult(True, "WhatsApp reminder queued in console mode.")

    return WhatsAppDispatchResult(False, "WhatsApp provider is not configured yet.")


def post_immunization_answer(question):
    normalized = question.lower()
    guidance = [
        (
            ("fever", "temperature", "hot"),
            "A mild fever after vaccination is common. Keep the child hydrated, dress them lightly, and seek clinical help if the fever is high, persistent, or the child is unusually sleepy.",
        ),
        (
            ("swelling", "pain", "red", "sore"),
            "A sore or slightly swollen injection site can happen. A clean cool cloth may help. Do not rub the injection site.",
        ),
        (
            ("breastfeed", "feeding", "eat"),
            "Continue normal feeding or breastfeeding. Small frequent feeds are helpful if the child is fussy.",
        ),
        (
            ("emergency", "danger", "rash", "breathing", "convulsion"),
            "Seek urgent care immediately for difficulty breathing, swelling of the face, convulsions, a widespread rash, or if the child becomes very weak.",
        ),
    ]

    for keywords, answer in guidance:
        if any(keyword in normalized for keyword in keywords):
            return answer

    return (
        "Most children have only mild symptoms after immunization. Watch for fever, swelling, feeding changes, or unusual sleepiness. "
        "For worrying symptoms, contact a health worker or visit the nearest facility."
    )
