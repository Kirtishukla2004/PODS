import os
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from datetime import datetime

def get_servicebus_client():
    connection_string = os.environ["SERVICE_BUS_CONNECTION_STRING"]
    return ServiceBusClient.from_connection_string(connection_string)

def send_to_queue(email_id, subject, sender, blob_names):
    queue_name = os.environ["SERVICE_BUS_QUEUE_NAME"]
    
    # Build the message payload
    message_payload = {
        "email_id": email_id,
        "subject": subject,
        "sender": sender,
        "blob_names": blob_names,
        "processed_at": datetime.utcnow().isoformat()
    }
    
    with get_servicebus_client() as client:
        with client.get_queue_sender(queue_name) as sender_client:
            message = ServiceBusMessage(
                json.dumps(message_payload)
            )
            sender_client.send_messages(message)
    
    return message_payload