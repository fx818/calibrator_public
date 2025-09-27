import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os, sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from gmail_work.gmail import create_service

# --- Your Google API Helper Function ---
def create_service(token_data: dict, api_name: str, api_version: str, scopes: list):
    """Your provided helper function to create a Google API service."""
    creds = Credentials.from_authorized_user_info(token_data, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build(api_name, api_version, credentials=creds)
    return service

# --- The ARQ Task to Send Email via Gmail API ---
async def schedule_gmail_send(ctx, token_data: dict, to: str, subject: str, body: str):
    """
    This is the ARQ task. It uses the provided token to send an email.
    """
    job_id = ctx['job_id']
    print(f"Executing job {job_id}: Sending email to {to}")

    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    try:
        service = create_service(token_data, 'gmail', 'v1', GMAIL_SCOPES)
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = service.users().messages().send(userId='me', body=create_message).execute()
        print(f"Job {job_id} SUCCESS: Message sent with ID: {send_message['id']}")

    except HttpError as error:
        print(f"Job {job_id} FAILED: An API error occurred: {error}")
    except Exception as e:
        print(f"Job {job_id} FAILED: An unexpected error occurred: {e}")

# --- ARQ Worker Configuration ---
class WorkerSettings:
    functions = [schedule_gmail_send] # Register the function for the worker

# arq worker.py