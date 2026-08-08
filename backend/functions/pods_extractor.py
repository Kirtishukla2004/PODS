import azure.functions as func
import logging
import json

from function_app import app
from services.blob_downloader import download_blob
from services.dataextractergeminiAi import extract_document


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="%SERVICE_BUS_QUEUE_NAME%",
    connection="SERVICE_BUS_CONNECTION_STRING"
)
def PodsMessageExtract(msg: func.ServiceBusMessage):

    logging.info("Received message from Service Bus")

    body = msg.get_body().decode("utf-8")
    data = json.loads(body)

    blob_name = data["blob_names"][0]

    file_bytes = download_blob(blob_name)

    result = extract_document(file_bytes, blob_name)

    logging.info(result)