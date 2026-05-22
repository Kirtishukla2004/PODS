import azure.functions as func
import logging

from pdf_converter   import get_attachment_bytes
from blob_uploader   import upload_file
from service_bus_sender import send_to_queue
from email_tracker   import is_processed, mark_processed
from email_fetcher   import (
    fetch_emails, fetch_attachments,
    mark_email_as_read, get_email_details, get_gmail_service,
)

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */5 * * * *",
    arg_name="myTimer",
    run_on_startup=False,
)
def EmailIngestion(myTimer: func.TimerRequest) -> None:
    logging.info("Email ingestion function started")

    emails = fetch_emails()
    logging.info(f"Found {len(emails)} unread emails")

    for email_data in emails:
        email    = get_email_details(email_data)
        email_id = email["id"]
        subject  = email.get("subject", "No Subject")
        sender   = email.get("sender",  "")

        if is_processed(email_id):
            logging.info(f"Skipping already processed email: {subject}")
            continue

        logging.info(f"Processing email: {subject}")
        blob_names = []

        try:
            if not email.get("hasAttachments"):
                logging.info(f"No attachments in email: {subject} — skipping")
                mark_email_as_read(email_id)
                mark_processed(email_id)
                continue

            service     = get_gmail_service()
            attachments = fetch_attachments(service, email_id, email_data["payload"])

            if not attachments:
                logging.info(f"No valid attachments found for: {subject}")
                mark_email_as_read(email_id)
                mark_processed(email_id)
                continue

            for i, attachment in enumerate(attachments):
                file_bytes, extension = get_attachment_bytes(attachment)

                if file_bytes and extension:
                    attachment_name = attachment.get("filename", f"attachment_{i}")
                    blob_name = upload_file(file_bytes, email_id, attachment_name, extension)
                    blob_names.append(blob_name)
                    logging.info(f"Uploaded {extension.upper()}: {blob_name}")
                else:
                    logging.info(
                        f"Skipping unsupported attachment: "
                        f"{attachment.get('filename', 'unknown')} "
                        f"({attachment.get('contentType', 'unknown type')})"
                    )

            if blob_names:
                send_to_queue(email_id, subject, sender, blob_names)
                logging.info(f"Sent to Service Bus: {subject}")
            else:
                logging.info(f"No supported files to queue for: {subject}")

            mark_processed(email_id)
            mark_email_as_read(email_id)
            logging.info(f"Marked as processed: {subject}")

        except Exception as e:
            logging.error(f"Failed to process email '{subject}': {str(e)}", exc_info=True)
            continue

    logging.info("Email ingestion function completed")