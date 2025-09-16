import json
import os
TOKEN_DIR = os.getenv("TOKEN_DIR","")

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
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)