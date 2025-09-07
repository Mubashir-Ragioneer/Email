# app/services/gmail_service.py
# Gmail API (OAuth2) sender with Azure-friendly credential loading

import os, json, base64
from pathlib import Path
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    """Build a Gmail service using (in order):
    1) GOOGLE_TOKEN_JSON (full token.json content)  [best for Azure]
    2) GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET/GOOGLE_REFRESH_TOKEN
    3) Local dev fallback using client_secret.json + token.json
    """
    creds: Optional[Credentials] = None

    # --- 1) Preferred on Azure: full token JSON in an env var ---
    token_json = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
        except Exception:
            creds = None  # fall through to other methods

    # --- 2) Refresh-token triple in env (also Azure-friendly) ---
    if not creds:
        refresh = os.environ.get("GOOGLE_REFRESH_TOKEN")
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        if refresh and client_id and client_secret:
            creds = Credentials(
                token=None,
                refresh_token=refresh,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES,
            )

    # --- 3) Local dev fallback using files (opens browser once) ---
    if not creds:
        from google_auth_oauthlib.flow import InstalledAppFlow  # imported only if needed

        token_path = Path(settings.GOOGLE_TOKEN_FILE)
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if not creds or not creds.refresh_token:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GOOGLE_CLIENT_SECRET_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def build_mime(
    from_name_email: str,
    to_email: str,
    subject: str,
    html: str,
    *,
    include_footer: bool = True,  # set False for “transactional/plain” sends
) -> MIMEMultipart:
    base_url = getattr(settings, "PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    unsubscribe_url = f"{base_url}/unsubscribe?email={quote(to_email)}"

    footer_html = (
        f'<p style="font-size:12px;color:#6b7280;margin-top:16px;">'
        f'Don’t want these? <a href="{unsubscribe_url}">Unsubscribe</a></p>'
    )
    combined_html = html + footer_html if include_footer else html

    msg = MIMEMultipart("alternative")
    msg["From"] = from_name_email
    msg["To"] = to_email
    msg["Subject"] = subject
    # keep List-Unsubscribe headers (deliverability/compliance)
    msg["List-Unsubscribe"] = (
        f"<mailto:{settings.FROM_EMAIL}?subject=unsubscribe>, <{unsubscribe_url}>"
    )
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    msg.attach(MIMEText("HTML email. Please enable HTML view.", "plain"))
    msg.attach(MIMEText(combined_html, "html"))
    return msg


def send_mime_message(service, mime_msg: MIMEMultipart):
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()
