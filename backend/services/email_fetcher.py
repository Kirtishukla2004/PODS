import os
import base64
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailAuthError(Exception):
    """Raised when Gmail credentials are missing/invalid and need manual re-authorization."""
    pass


def get_gmail_service():
    token_file = os.environ["GMAIL_TOKEN_FILE"]

    if not os.path.exists(token_file):
        raise GmailAuthError(
            f"No token file at {token_file}. Run the one-time local "
            "auth script to generate it before deploying."
        )

    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if creds.valid:
        return build("gmail", "v1", credentials=creds)

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(token_file, "w") as f:
                f.write(creds.to_json())
            return build("gmail", "v1", credentials=creds)
        except RefreshError as e:
            # invalid_grant lands here — token is dead, not just expired.
            # No interactive flow inside a timer trigger. Fail loudly
            # and distinctly so it's easy to alert on.
            logging.error(f"Gmail refresh token invalid, needs re-auth: {e}")
            raise GmailAuthError(
                "Gmail refresh token was revoked/expired (invalid_grant). "
                "Re-run the local OAuth consent flow manually and redeploy "
                "the token file."
            ) from e

    raise GmailAuthError(
        "Gmail credentials invalid and no refresh token present.")


def fetch_emails():
    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=50,
    ).execute()

    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        email_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full",
        ).execute()
        emails.append(email_data)
    return emails


def get_email_details(email_data):
    headers = email_data["payload"]["headers"]

    subject = next((h["value"]
                   for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"]
                  for h in headers if h["name"] == "From"),    "Unknown")
    received = next((h["value"]
                    for h in headers if h["name"] == "Date"),    "")

    body = ""
    if "parts" in email_data["payload"]:
        for part in email_data["payload"]["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                body = base64.urlsafe_b64decode(
                    part["body"]["data"]).decode("utf-8")
                break
    elif "data" in email_data["payload"].get("body", {}):
        body = base64.urlsafe_b64decode(
            email_data["payload"]["body"]["data"]).decode("utf-8")

    return {
        "id":             email_data["id"],
        "subject":        subject,
        "sender":         sender,
        "received":       received,
        "body":           body,
        "hasAttachments": any(
            part.get("filename")
            for part in email_data["payload"].get("parts", [])
        ),
    }


def fetch_attachments(service, email_id, payload):
    attachments = []
    for part in payload.get("parts", []):
        filename = part.get("filename", "")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        if filename and attachment_id:
            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=email_id,
                id=attachment_id,
            ).execute()

            attachments.append({
                "filename":     filename,
                "contentType":  part["mimeType"],
                # URL-safe base64 from Gmail API
                "contentBytes": attachment["data"],
            })
    return attachments


def mark_email_as_read(email_id):
    service = get_gmail_service()
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
