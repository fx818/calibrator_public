from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_event(user_date,certificate_number):
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_gmail_v1.json'

    ### Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))
    print("the dir is ..........",(os.path.join(working_dir, token_dir, token_file)))
     ### Check if token file exists, if yes, load the credentials
    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)
        # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
        #   cred = pickle.load(token)


    # if os.path.exists("token.json"):
    #     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     with open("token.json", "w") as token:
    #         token.write(creds.to_json())

    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)

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
    print("Event created: %s" % (event.get("htmlLink")))


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat()
    return dt

# data = convert_to_RFC_datetime(2024, 9, 7, 20, 0)
# print(data)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.date_extraction import extract_date
date = "12 September 2025"
new_date = extract_date(date)
print(new_date)
# create_event(new_date)