import requests
import json
from datetime import datetime, timedelta, timezone
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from apis.config import load_tokens

def schedule_email_via_api(token_data: dict, receiver: str, subject: str, body: str, send_at: datetime):
    """
    Calls the FastAPI endpoint to schedule an email using the Gmail API.

    Args:
        token_data: The user's OAuth2 token data as a dictionary.
        receiver: The recipient's email address.
        subject: The subject of the email.
        body: The content of the email.
        send_at: A datetime object for when to send the email.
    """
    # The URL of your running FastAPI application's endpoint
    api_url = "http://127.0.0.1:8000/schedule-gmail-redis"
    # Construct the JSON payload required by the API
    payload = {
        "token_data": token_data,
        "receiver_email": receiver,
        "subject": subject,
        "body": body,
        # Convert the datetime object to an ISO 8601 string format with 'Z' for UTC
        "send_at": send_at.isoformat()
    }

    print(f"Sending request to {api_url} with payload:")
    print(json.dumps(payload, indent=2))

    try:
        # Make the POST request
        response = requests.post(api_url, json=payload)

        # Check the response from the server
        if response.status_code == 200:
            print("\n✅ Success! Server responded:")
            print(response.json())
        else:
            print(f"\n❌ Error! Server returned status code {response.status_code}:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ A network error occurred: {e}")

