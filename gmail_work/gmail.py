import base64
from random import random, randint
import string
import os, time
from typing import List
# from google_apis import create_service
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build







import os
import datetime
from collections import namedtuple
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def create_service(client_secret_file, api_name, api_version, scopes, username):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = scopes
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'{username}_token.json'

    ### Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)
        # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
        #   cred = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        services = []
        for i in range(len(API_SERVICE_NAME)):
            service = build(API_SERVICE_NAME[i], API_VERSION[i], credentials=creds, static_discovery=False)
            services.append(service)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return services + [os.path.join(working_dir, token_dir, token_file)]
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None, None, None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

# generate 10 digit random number
def id_generator(size=10):
    return ''.join(str(randint(0, 9)) for _ in range(size))

# SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/calendar"]
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

class GmailException(Exception):
    """Custom exception for Gmail-related errors."""
class NoEmailFound(GmailException):
    """Raised when no email is found."""


def search_emails(service, query: str, label_ids: List=None):
    """Search for emails matching the query."""
    try:
        message_list_response = service.users().messages().list(
            userId='me', 
            q=query, 
            labelIds=label_ids
            ).execute()
        message_items = message_list_response.get('messages', [])
        next_page_token = message_list_response.get('nextPageToken', None)
        while next_page_token:
            message_list_response = service.users().messages().list(
            userId='me', 
            q=query, 
            labelIds=label_ids,
            nextPageToken=next_page_token
            ).execute()
            message_items.extend(message_list_response.get('messages', []))
            next_page_token = message_list_response.get('nextPageToken', None)
        return message_items

    except Exception as e:
        raise GmailException(f"Error searching emails: {e}")
    
def get_file_data(service, message_id, attachment_id, file_name, save_location):
    response = service.users().messages().attachments().get(
        userId='me', 
        messageId=message_id, 
        id=attachment_id
        ).execute()
    filedata = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
    return filedata

def get_message_details(service, message_id, msg_format='metadata', metadata_headers:List=None):
    try:
        message_detail = service.users().messages().get(
            userId='me', 
            id=message_id,
            format=msg_format,
            metadataHeaders=metadata_headers
        ).execute()
        return message_detail
    except Exception as e:
        raise GmailException(f"Error fetching message details: {e}")

def fetch_emails_with_attachments(username, vendor_email, num_email):
    gmail_service, ig1 , ig2 = create_service("client.json", ["gmail", "calendar"], ["v1", "v3"], SCOPES, username)
    # gmail_service, _= create_service(client_file, api_name, api_version, scopes)
    query_string = f"from:({vendor_email}) has:attachment"
    save_location = "downloaded_attachments"
    email_messages = search_emails(gmail_service,query_string)
    all_paths = []
    i = 0
    for email_message in email_messages:
        if i==num_email: break
        i += 1
        msg_id = email_message['id']
        message_detail = get_message_details(gmail_service, msg_id, msg_format='full', metadata_headers=['parts'])
        message_detailPayload = message_detail.get('payload', {})
        if 'parts' in message_detailPayload:
            for msgPayload in message_detailPayload['parts']:
                filename = msgPayload.get('filename')
                # ext = filename.split('.')[-1]
                body = msgPayload.get('body', {})
                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']
                    attachment_content = get_file_data(gmail_service, msg_id, attachment_id, filename, save_location)
                    print(f"Attachment content type: {type(attachment_content)}")
                    if not os.path.exists(save_location):
                        os.makedirs(save_location)
                    
                    with open(os.path.join(save_location, filename), 'wb') as _f:
                        _f.write(attachment_content)
                    print(f"Saved attachment: {filename} at {save_location}")
                    all_paths.append(os.path.join(save_location, filename))
        time.sleep(1)
    return all_paths

def create_event(username, user_date, certificate_number):
    _ig1, service, ig2 = create_service("client.json", ["gmail", "calendar"], ["v1", "v3"], SCOPES, username)
    event = {
        "summary": f"Calibration Due for {certificate_number}",
        "location": "Design Room",
        "description": "Calibration check for DUC GTM-13",
        "start": {
            "dateTime": f"{user_date}T10:00:00",
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": f"{user_date}T11:00:00",
            "timeZone": "Asia/Kolkata",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},  # 1 day before
                {"method": "popup", "minutes": 10},      # 10 minutes before
            ],
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    # if ig2 and os.path.exists(ig2):
    #     os.remove(ig2)
    print("Event created: %s" % (event.get("htmlLink")))
    return {"path":ig2}
