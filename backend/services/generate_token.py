# generate_token.py — run this manually, once, from your own machine
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

credentials_file = os.environ["GMAIL_CREDENTIALS_FILE"]
token_file = os.environ["GMAIL_TOKEN_FILE"]

flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

with open(token_file, "w") as f:
    f.write(creds.to_json())

print(f"New token written to {token_file}")
