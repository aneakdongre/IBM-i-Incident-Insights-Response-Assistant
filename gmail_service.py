# --------------------------------------------------
# GMAIL API SERVICE
# --------------------------------------------------

import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# --------------------------------------------------
# GMAIL API CONFIGURATION
# --------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

CREDENTIALS_FILE = (
    "credentials/credentials.json"
)

TOKEN_FILE = (
    "credentials/token.json"
)


# --------------------------------------------------
# AUTHENTICATE WITH GMAIL
# --------------------------------------------------

def get_gmail_service():

    creds = None

    # Load existing authorization token
    if os.path.exists(TOKEN_FILE):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Refresh or create authorization
    if not creds or not creds.valid:

        if (
            creds
            and creds.expired
            and creds.refresh_token
        ):

            creds.refresh(Request())

        else:

            flow = (
                InstalledAppFlow
                .from_client_secrets_file(
                    CREDENTIALS_FILE,
                    SCOPES
                )
            )

            creds = flow.run_local_server(
                port=0
            )

        # Save authorization token
        with open(
            TOKEN_FILE,
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    # Build Gmail API service
    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


# --------------------------------------------------
# SEND AI INSIGHTS EMAIL
# --------------------------------------------------

def send_ai_insights_email(
    recipient_email,
    insights
):

    service = get_gmail_service()

    subject = (
        "IBM i AI Operational Insights"
    )

    message_body = f"""
IBM i AI Operational Insights

The following operational analysis was generated using
validated incident data and AI-assisted interpretation.

--------------------------------------------------

{insights}

--------------------------------------------------

Important Notice:

AI-generated insights, risks, hypotheses, and recommendations
require operational review and validation. They should not be
treated as confirmed root causes.
"""

    message = MIMEText(
        message_body,
        "plain"
    )

    message["to"] = recipient_email

    message["subject"] = subject

    encoded_message = (
        base64.urlsafe_b64encode(
            message.as_bytes()
        )
        .decode()
    )

    create_message = {
        "raw": encoded_message
    }

    sent_message = (
        service.users()
        .messages()
        .send(
            userId="me",
            body=create_message
        )
        .execute()
    )

    return sent_message