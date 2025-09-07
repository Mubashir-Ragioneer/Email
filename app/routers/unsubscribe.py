from fastapi import APIRouter, Query
from app.models import SuppressedEmail

router = APIRouter(prefix="/unsubscribe", tags=["unsubscribe"])

@router.get("")
def unsubscribe_get(email: str = Query(..., description="Email to unsubscribe")):
    email_l = email.lower()
    existing = SuppressedEmail.objects(email=email_l).first()
    if not existing:
        SuppressedEmail(email=email_l).save()
    return {"ok": True, "email": email_l, "message": "You have been unsubscribed."}
