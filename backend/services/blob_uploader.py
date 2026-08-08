import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime, timezone

_container_client = None

def get_container_client():
    global _container_client
    if _container_client is None:
        connection_string = os.environ["STORAGE_CONNECTION_STRING"]
        container_name = os.environ["BLOB_CONTAINER_NAME"]
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        _container_client = blob_service.get_container_client(container_name)
    return _container_client


EXTENSION_CONTENT_TYPE_MAP = {
    "pdf":  "application/pdf",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "png":  "image/png",
    "webp": "image/webp",
}


def upload_file(file_bytes, email_id, filename, extension):
    container_client = get_container_client()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_filename = filename.rsplit(".", 1)[0] if "." in filename else filename
    blob_name = f"{timestamp}_{email_id}_{base_filename}.{extension}"

    blob_client = container_client.get_blob_client(blob_name)

    content_type = EXTENSION_CONTENT_TYPE_MAP.get(extension.lower(), "application/octet-stream")

    blob_client.upload_blob(
        file_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )

    return blob_name