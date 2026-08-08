import json
import os
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = os.environ["BLOB_CONTAINER_NAME"]
TRACKER_FILE   = "processed_emails.json"


def get_blob_client():
    connection_string = os.environ["STORAGE_CONNECTION_STRING"]
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    return blob_service.get_blob_client(container=CONTAINER_NAME, blob=TRACKER_FILE)


def load_processed_ids():
    try:
        blob_client = get_blob_client()
        data = blob_client.download_blob().readall()
        return json.loads(data)
    except Exception:
        return []


def is_processed(email_id):
    return email_id in load_processed_ids()


def mark_processed(email_id):
    processed = load_processed_ids()
    if email_id not in processed:
        processed.append(email_id)
        blob_client = get_blob_client()
        blob_client.upload_blob(json.dumps(processed), overwrite=True)