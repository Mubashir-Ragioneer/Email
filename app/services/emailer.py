# app/services/emailer.py
# Gmail API sender with MongoEngine suppression check
from typing import Iterable, Dict, Any
from app.models import SuppressedEmail
from app.core.config import settings
from app.services.gmail_service import get_gmail_service, build_mime, send_mime_message

def _is_suppressed(email: str) -> bool:
    return SuppressedEmail.objects(email=email.lower()).first() is not None

def send_one_email(to_email: str, subject: str, html: str) -> Dict[str, Any]:
    if _is_suppressed(to_email):
        return {"sent": False, "suppressed": True, "to": to_email}

    service = get_gmail_service()
    from_header = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
    msg = build_mime(from_header, to_email, subject, html)
    send_mime_message(service, msg)

    return {"sent": True, "suppressed": False, "to": to_email}

def send_many_individual(to_emails: Iterable[str], subject: str, html: str) -> Dict[str, Any]:
    service = get_gmail_service()
    from_header = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"

    results = []
    for addr in to_emails:
        if _is_suppressed(addr):
            results.append({"sent": False, "suppressed": True, "to": addr})
            continue
        msg = build_mime(from_header, addr, subject, html)
        send_mime_message(service, msg)
        results.append({"sent": True, "suppressed": False, "to": addr})

    return {
        "total": len(results),
        "sent_count": sum(1 for r in results if r["sent"]),
        "suppressed_count": sum(1 for r in results if r["suppressed"]),
        "results": results,
    }
