import os
import base64
import io
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image


SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg":  "jpg",
    "image/png":  "png",
    "image/webp": "webp",
}


def _safe_decode_base64(data: str) -> bytes:
    """Decode base64, handling both standard and URL-safe variants with missing padding."""
    # Gmail uses URL-safe base64
    data = data.replace("-", "+").replace("_", "/")
    # Fix padding
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.b64decode(data)


def get_attachment_bytes(attachment):
    """
    Returns (file_bytes, extension) for supported attachment types.
    - PDF  → returned as-is, extension = 'pdf'
    - Image → returned as-is, extension = 'jpg'/'png'/'webp'
    - Anything else → (None, None)
    """
    content_type = (attachment.get("contentType") or "").lower().strip()
    raw = attachment.get("contentBytes", "")

    if not raw:
        return None, None

    try:
        file_bytes = _safe_decode_base64(raw)
    except Exception:
        return None, None

    if not file_bytes:
        return None, None

    # PDF — pass through unchanged
    if content_type == "application/pdf":
        # Validate it's actually a PDF (check magic bytes)
        if file_bytes[:4] != b"%PDF":
            return None, None
        return file_bytes, "pdf"

    # Image — pass through unchanged
    if content_type in SUPPORTED_IMAGE_TYPES:
        return file_bytes, SUPPORTED_IMAGE_TYPES[content_type]

    return None, None


# ── kept for backwards-compat if anything still imports this name ──
def convert_attachment_to_pdf(attachment):
    return get_attachment_bytes(attachment)


def convert_email_to_pdf(email):
    """Convert email metadata + body to a PDF (used if you ever re-enable body upload)."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()
    content = []

    subject = email.get("subject", "No Subject")
    sender  = email.get("sender",  "Unknown")
    received = email.get("received", "")
    body    = email.get("body", "")

    if isinstance(body, dict):
        body = body.get("content", "")
    if isinstance(sender, dict):
        sender = sender.get("emailAddress", {}).get("address", "Unknown")

    content.append(Paragraph(f"Subject: {subject}", styles["Heading1"]))
    content.append(Spacer(1, 0.2 * inch))
    content.append(Paragraph(f"From: {sender}", styles["Normal"]))
    content.append(Spacer(1, 0.1 * inch))
    content.append(Paragraph(f"Received: {received}", styles["Normal"]))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph("Email Body:", styles["Heading2"]))
    content.append(Spacer(1, 0.2 * inch))

    clean_body = re.sub(r"<[^>]+>", "", body)
    clean_body = clean_body.encode("ascii", "ignore").decode("ascii").strip()
    if not clean_body:
        clean_body = "(No body content)"

    content.append(Paragraph(clean_body, styles["Normal"]))
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()