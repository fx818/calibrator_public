from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import requests, json, os, datetime

app = FastAPI()



from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://fx818.github.io",   # your frontend URL
    "http://localhost:5500",     # optional local testing
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # allow these origins
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, etc.
    allow_headers=["*"],
)



# Google OAuth config
CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "478641910458-vd7at938uqvfn2mfrhqosuq4r0cokg77.apps.googleusercontent.com"
)
CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
    "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"
)
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"
FRONTEND_URL = "https://fx818.github.io/frontend_calibrator/page.html" # Separate frontend
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

TOKEN_FILE = "token.json"

# ---------------------------
# Step 1: Login redirect
# ---------------------------
@app.get("/login")
def login():
    print("Initiating login...")  # debug
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={' '.join(SCOPES)}"
        "&access_type=offline&prompt=consent"
    )
    print("Redirecting to:", google_auth_url)  # debug
    return RedirectResponse(google_auth_url)


# ---------------------------
# Step 2: OAuth callback
# ---------------------------
@app.get("/auth/callback")
def auth_callback(request: Request):
    print("Received callback with query params:", request.query_params)
    code = request.query_params.get("code")
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    print("Exchanging code for tokens...")  # debug
    response = requests.post(token_url, data=data)
    token_data = response.json()
    print("Google token response:", token_data)  # debug

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=token_data.get("expires_in", 3600))

    tokens = {
        "token": access_token,
        "refresh_token": refresh_token,
        "token_uri": token_url,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scopes": SCOPES,
        "universe_domain": "googleapis.com",
        "account": "",
        "expiry": expiry.isoformat() + "Z"
    }
    print("Storing tokens:", tokens)  # debug
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    # ---------------------------
    # Step 3: Intermediate redirect to frontend
    # ---------------------------
    print("Redirecting to frontend...")  # debug
    return RedirectResponse("/auth/redirect")


# ---------------------------
# Step 3: Intermediate redirect page
# ---------------------------
@app.get("/auth/redirect")
def redirect_to_frontend():
    print("Serving redirect page to frontend...")  # debug
    return HTMLResponse(f"""
    <html>
      <head>
        <script>
          window.location.href = "{FRONTEND_URL}";
        </script>
      </head>
      <body>
        Redirecting to frontend...
      </body>
    </html>
    """)


# ---------------------------
# Step 4: API to get saved tokens
# ---------------------------
@app.get("/tokens")
def get_tokens():
    print("Fetching stored tokens...")  # debug
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return {"error": "No tokens found"}


# ---------------------------
# Step 5: Refresh access token
# ---------------------------
@app.post("/refresh")
def refresh_tokens():
    print("Refreshing access token...")  # debug
    if not os.path.exists(TOKEN_FILE):
        return {"error": "No tokens to refresh"}

    with open(TOKEN_FILE, "r") as f:
        saved_tokens = json.load(f)

    refresh_token = saved_tokens.get("refresh_token")
    if not refresh_token:
        return {"error": "No refresh_token available"}

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()
    new_token = token_data.get("access_token")

    expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=token_data.get("expires_in", 3600))
    saved_tokens["token"] = new_token
    saved_tokens["expiry"] = expiry.isoformat() + "Z"

    with open(TOKEN_FILE, "w") as f:
        json.dump(saved_tokens, f, indent=2)

    return saved_tokens


@app.get("/me")
def get_user_info():
    if not os.path.exists(TOKEN_FILE):
        return {"error": "No tokens found"}

    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)

    access_token = tokens.get("token")
    refresh_token = tokens.get("refresh_token")

    expiry = datetime.datetime.fromisoformat(tokens["expiry"].replace("Z", "+00:00"))
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    # Refresh if expired
    if now >= expiry and refresh_token:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        r = requests.post(token_url, data=data).json()
        access_token = r.get("access_token")
        expiry = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=r.get("expires_in", 3600))
        tokens["token"] = access_token
        tokens["expiry"] = expiry.isoformat()
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?alt=json", headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch user info", "details": response.json()}

    user_info = response.json()
    tokens["account"] = user_info.get("email")
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return {"email": user_info.get("email"), "name": user_info.get("name")}
