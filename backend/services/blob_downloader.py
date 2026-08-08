import os 
from azure.storage.blob import BlobServiceClient
def download_blob(blobname):
    connection_string = os.getenv("STORAGE_CONNECTION_STRING")
    container_name = os.getenv("BLOB_CONTAINER_NAME")
    blob_service_client=BlobServiceClient.from_connection_string(connection_string)
    blob_client=blob_service_client.get_blob_client(
        container=container_name,blob=blobname)
    download_stream=blob_client.download_blob()
    file_bytes=download_stream.readall()
    type(file_bytes)
    return file_bytes
