# gspread_client.py

import gspread
from google.oauth2.service_account import Credentials
import os

# This variable will hold our single client instance
_gspread_client = None

def get_gspread_client():
    """
    Creates and returns a single, authorized gspread client instance.
    The client is created only on the first call and reused on subsequent calls.
    """
    global _gspread_client

    # Only authorize a new client if one doesn't already exist
    if _gspread_client is None:
        print("------- Authorizing Gspread Client for the first time... -------")
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        
        # Best practice: Load credentials path from an environment variable
        creds_file_path = "../utils/prossimawork.json" 
        if not creds_file_path:
            raise ValueError("GOOGLE_CREDS_FILE environment variable not set.")

        creds = Credentials.from_service_account_file(creds_file_path, scopes=scopes)
        _gspread_client = gspread.authorize(creds)
        print("------- Gspread Client Authorized Successfully. -------")
        
    return _gspread_client