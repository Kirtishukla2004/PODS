import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = None
    token_file       = os.environ["GMAIL_TOKEN_FILE"]
    credentials_file = os.environ["GMAIL_CREDENTIALS_FILE"]

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, "w") as f:
                f.write(creds.to_json())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
            with open(token_file, "w") as f:
                f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


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

    subject  = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender   = next((h["value"] for h in headers if h["name"] == "From"),    "Unknown")
    received = next((h["value"] for h in headers if h["name"] == "Date"),    "")

    body = ""
    if "parts" in email_data["payload"]:
        for part in email_data["payload"]["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
    elif "data" in email_data["payload"].get("body", {}):
        body = base64.urlsafe_b64decode(email_data["payload"]["body"]["data"]).decode("utf-8")

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
        filename     = part.get("filename", "")
        body         = part.get("body", {})
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
                "contentBytes": attachment["data"],   # URL-safe base64 from Gmail API
            })
    return attachments


def mark_email_as_read(email_id):
    service = get_gmail_service()
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()