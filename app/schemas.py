# app/schemas.py
# ---------------------------------------------
# Designed template requests (one & many)
# ---------------------------------------------
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class SendDesignedOneRequest(BaseModel):
    to: EmailStr
    subject: str = Field(min_length=1)

    # visual/brand
    logo_url: Optional[str] = None
    title: Optional[str] = "Welcome Aboard! 👋"
    subtitle: Optional[str] = None
    greeting: Optional[str] = None

    # content: choose body_html OR paragraphs/bullets
    body_html: Optional[str] = None
    paragraphs: Optional[List[str]] = None
    bullets: Optional[List[str]] = None

    # optional OTP-like code
    code: Optional[str] = None
    expires_minutes: Optional[int] = 5

    # optional CTA
    cta_label: Optional[str] = None
    cta_url: Optional[str] = None

    # small footer line inside the card
    footer_note: Optional[str] = None

class SendDesignedManyRequest(SendDesignedOneRequest):
    to_list: List[EmailStr] = Field(min_length=1)


# --- FLEX BATCH SEND ---

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Dict, Optional

class FlexBatchItem(BaseModel):
    # accept either "email_adress" (your payload) or "email_addresses"
    email_addresses: List[EmailStr] = Field(alias="email_adress")
    subject: Optional[str] = None

    # you can use ONE of these:
    message: Optional[str] = None          # raw text OR html (see is_html)
    is_html: bool = False                  # if True, treat "message" as HTML
    message_html: Optional[str] = None     # explicit html
    message_text: Optional[str] = None     # explicit plain text

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
