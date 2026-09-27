"""
Deletes the existing gmail_token.json and walks through a fresh local OAuth
consent flow to regenerate it.

Run this LOCALLY (not on Render/Azure) whenever the deployed token dies with
invalid_grant. It opens a browser window for you to sign in and approve
access, then writes a brand-new token.json to the same path.

After running this, redeploy/upload the new gmail_token.json to wherever
your backend reads it from (e.g. re-upload to Render, or however your
deployment picks up the config folder).

Requirements (install once):
    pip install google-auth-oauthlib google-auth google-api-python-client

You also need gmail_credentials.json (the OAuth client secret you downloaded
from Google Cloud Console -> APIs & Services -> Credentials) sitting in the
same config folder as the token.
"""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# --- adjust these two if your filenames differ ---
CONFIG_DIR = Path(r"C:\Users\dinesh\OneDrive\Documents\Desktop\PODS\backend\config")
TOKEN_PATH = CONFIG_DIR / "gmail_token.json"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"

# Adjust scopes to match what your app actually needs
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def main():
    if TOKEN_PATH.exists():
        os.remove(TOKEN_PATH)
        print(f"Deleted old token: {TOKEN_PATH}")
    else:
        print(f"No existing token found at {TOKEN_PATH}, continuing.")

    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Client secret file not found at {CREDENTIALS_PATH}. "
            "Download it from Cloud Console -> Credentials -> your OAuth "
            "client -> Download JSON, and place it there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH), SCOPES
    )
    # Opens a browser window; sign in and approve access
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json())
    print(f"New token written to: {TOKEN_PATH}")
    print("Now redeploy this token file to your backend.")


if __name__ == "__main__":
    main()