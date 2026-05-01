# PODS - Purchase Order Detection System

## Stage 1: Email Ingestion
Fetches PO emails from Outlook, converts to PDF, 
stores in Blob Storage and queues in Service Bus.

## Setup
1. Clone the repo
2. cd backend
3. python -m venv venv
4. venv\Scripts\activate
5. pip install -r requirements.txt
6. Add your local.settings.json with credentials