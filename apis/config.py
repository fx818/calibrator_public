import json
import os, sys
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
TOKEN_DIR = os.getenv("TOKEN_DIR","tokens")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # apis/
DB_PATH = os.path.join("", "calibration.db")


def get_token_path(account_email: str):
    """Return the file path for a user's token file."""
    return os.path.join(TOKEN_DIR, f"{account_email}_token.json")

def save_tokens(account_email: str, tokens: dict):
    """Save Google tokens to a file for a specific user."""
    with open(get_token_path(account_email), "w") as f:
        json.dump(tokens, f, indent=2)

def load_tokens(account_email: str):
    """Load Google tokens from a file for a specific user."""
    path = get_token_path(account_email)
    print("the token path is: ", path)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def load_settings(username):
    """Get from db"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT calibration_sheet, warranty_sheet, store_dept_email, vendor_email, calibration_dept_email FROM config WHERE email = ?", (username,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "calibration_sheet": row[0],
                "warranty_sheet": row[1],
                "store_dept_email": row[2],
                "vendor_email": row[3],
                "calibration_dept_email": row[4],
                "error": False
            }
    except Exception as e:
        print(f"Error loading configs for {username}: {e}")
        conn.close()
        return {"error": str(e)}

def load_new_settings(email):
    """Get from db"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email, sheet, scheduled_emails FROM configs WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "email": row[0],
                "sheet": row[1],
                "scheduled_emails": json.loads(row[2]),
                "error": False
            }
    except Exception as e:
        print(f"Error loading configs for {email}: {e}")
        conn.close()
        return {
                "email": email,
                "sheet": "",
                "scheduled_emails": {},
                "error": True
            }

