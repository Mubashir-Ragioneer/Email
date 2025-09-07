# app/routers/email.py
# ---------------------------------------------------
# Designed email routes (fixed layout, flexible content)
# ---------------------------------------------------
from fastapi import APIRouter, HTTPException
from app.schemas import (
    # SendOneRequest, SendManyRequest,
    SendDesignedOneRequest, SendDesignedManyRequest,
)
from app.services.emailer import send_one_email, send_many_individual
from app.services.templater import render_template
from app.core.config import settings

router = APIRouter(prefix="/email", tags=["email"])

# ...existing /send-one and /send-many...

@router.post("/send-designed-one")
def send_designed_one(payload: SendDesignedOneRequest):
    html = render_template(
        "fixed_card.html",
        subject=payload.subject,
        brand=settings.FROM_NAME or "MyCofoundr.AI",
        logo_url=payload.logo_url,
        title=payload.title,
        subtitle=payload.subtitle,
        greeting=payload.greeting,
        body_html=payload.body_html,
        paragraphs=payload.paragraphs,
        bullets=payload.bullets,
        code=payload.code,
        expires_minutes=payload.expires_minutes,
        cta_label=payload.cta_label,
        cta_url=payload.cta_url,
        footer_note=payload.footer_note,
    )
    res = send_one_email(payload.to, payload.subject, html)
    if not res["sent"] and not res["suppressed"]:
        raise HTTPException(status_code=500, detail="Failed to send")
    return res

@router.post("/send-designed-many")
def send_designed_many(payload: SendDesignedManyRequest):
    html = render_template(
        "fixed_card.html",
        subject=payload.subject,
        brand=settings.FROM_NAME or "MyCofoundr.AI",
        logo_url=payload.logo_url,
        title=payload.title,
        subtitle=payload.subtitle,
        greeting=payload.greeting,
        body_html=payload.body_html,
        paragraphs=payload.paragraphs,
        bullets=payload.bullets,
        code=payload.code,
        expires_minutes=payload.expires_minutes,
        cta_label=payload.cta_label,
        cta_url=payload.cta_url,
        footer_note=payload.footer_note,
    )
    # same HTML for all recipients (no CC/BCC leak)
    return send_many_individual(payload.to_list, payload.subject, html)


from fastapi import APIRouter, HTTPException, Body
from pydantic import ValidationError
from html import escape

from app.schemas import FlexBatchItem
from app.services.emailer import send_many_individual

router = APIRouter(prefix="/email", tags=["email"])

def _text_to_html(txt: str) -> str:
    # simple, email-safe conversion of plain text to HTML
    return "<p>" + "</p><p>".join(escape(txt).splitlines()) + "</p>"

def _coerce_to_html(item: FlexBatchItem) -> str:
    if item.message_html:
        return item.message_html
    if item.message_text:
        return _text_to_html(item.message_text)
    if item.message is not None:
        return item.message if item.is_html else _text_to_html(item.message)
    raise ValueError("No message provided")

@router.post("/send-flex-batch")
def send_flex_batch(payload: dict = Body(..., description="Either {'batches': {...}} or a top-level dict of items")):
    """
    Accepts a map of arbitrary keys -> { message/html/text, email_adress[...] }
    Example minimal body (top-level dict):
    {
      "1": {"message": "hi", "email_adress": ["a@example.com"]},
      "2": {"message": "<b>hello</b>", "is_html": true, "email_adress": ["b@example.com","c@example.com"]}
    }
    """
    # Support both wrapper {"batches": {...}} and direct map {...}
    batches_raw = payload.get("batches", payload)

    results = {}
    total = sent = suppressed = 0

    for key, raw in batches_raw.items():
        try:
            item = FlexBatchItem.model_validate(raw)
            html = _coerce_to_html(item)
            subject = item.subject or "No subject"
        except ValidationError as ve:
            results[key] = {"error": "validation_error", "details": ve.errors()}
            continue
        except ValueError as ve:
            results[key] = {"error": str(ve)}
            continue

        group_res = send_many_individual(item.email_addresses, subject, html)
        results[key] = group_res
        total += group_res["total"]
        sent += group_res["sent_count"]
        suppressed += group_res["suppressed_count"]

    return {
        "summary": {
            "groups": len(batches_raw),
            "total_recipients": total,
            "sent_count": sent,
            "suppressed_count": suppressed
        },
        "results": results
    }
    