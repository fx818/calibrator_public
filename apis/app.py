from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import json
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import requests, json, os, datetime

import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.types import Command
from LangGraphAgent.agent import Agent, State
from database import add_user, increment_attempts
load_dotenv()

import requests
import datetime

# Create agent
agent = Agent()
compiled_graph = agent.graph

# Thread config → keeps state persistent across calls
THREAD_ID = "certificate-flow-001"
thread_config = {"configurable": {"thread_id": THREAD_ID}}

# Initial state
initial_state = State(
    username="",
    vendor_email="",
    certificate_number=None,
    sentiment=False,
    pdf_file_path=None,
    certificate_data=None,
    push_to_db=None,
    push_to_calendar=None,
)

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


from starlette.middleware.sessions import SessionMiddleware


SECRET_KEY = "hewjfnerkgnoekrgklwnrjgwrjingjklwnfjkwnjk98734832728rifj2iojf93fh3"  # should be strong and secret
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="none",
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
TOKEN_DIR = "token files"
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
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?alt=json", headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch user info", "details": response.json()}

    user_info = response.json()
    tokens["account"] = user_info.get("email")
    print("Storing tokens:", tokens)  # debug
    # with open(tokens["account"]+TOKEN_FILE, "w") as f:
    #     json.dump(tokens, f, indent=2)

    account_email = tokens.get("account", "default_account")
    request.session["account_email"] = account_email
    filename = f"{account_email}_token.json"  # e.g., testingbyme818@gmail.com_token.json
    filepath = os.path.join(TOKEN_DIR, filename)
    
    # Write token JSON
    with open(filepath, "w") as f:
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

    # with open(saved_tokens["account"]+TOKEN_FILE, "w") as f:
    #     json.dump(saved_tokens, f, indent=2)

    account_email = saved_tokens.get("account", "default_account")
    filename = f"{account_email}_token.json"  # e.g., testingbyme818@gmail.com_token.json
    filepath = os.path.join(TOKEN_DIR, filename)
    
    # Write token JSON
    with open(filepath, "w") as f:
        json.dump(saved_tokens, f, indent=2)

    return saved_tokens

TOKEN_DIR = "token files"

# Ensure the directory exists
os.makedirs(TOKEN_DIR, exist_ok=True)

# Construct path dynamically based on account
def get_token_path(account_email):
    filename = f"{account_email}_token.json"
    return os.path.join(TOKEN_DIR, filename)

@app.get("/me")
def get_user_info(request: Request):
    email = request.session.get("account_email")
    print("email is ", email)
    if not email:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    return {"email": email}


# @app.get("/me")
# def get_user_info(request: Request):

#     # Use a default account email if needed
#     account_email = request.session.get("account_email", "") # or read from session/cookie
#     if not account_email:
#         # No session, redirect to login
#         return RedirectResponse(url="/login")
    
#     filepath = get_token_path(account_email)
    
#     if not os.path.exists(filepath):
#         # Token file missing, redirect to login
#         return RedirectResponse(url="/login")


#     with open(filepath, "r") as f:
#         tokens = json.load(f)

#     access_token = tokens.get("token")
#     refresh_token = tokens.get("refresh_token")

#     expiry = datetime.datetime.fromisoformat(tokens["expiry"].replace("Z", "+00:00"))
#     now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

#     # Refresh token if expired
#     if now >= expiry and refresh_token:
#         token_url = "https://oauth2.googleapis.com/token"
#         data = {
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "refresh_token": refresh_token,
#             "grant_type": "refresh_token",
#         }
#         r = requests.post(token_url, data=data).json()
#         access_token = r.get("access_token")
#         expiry = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=r.get("expires_in", 3600))
#         tokens["token"] = access_token
#         tokens["expiry"] = expiry.isoformat() + "Z"

#         with open(filepath, "w") as f:
#             json.dump(tokens, f, indent=2)

#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?alt=json", headers=headers)

#     if response.status_code != 200:
#         return {"error": "Failed to fetch user info", "details": response.json()}

#     user_info = response.json()
#     tokens["account"] = user_info.get("email")

#     # Save again to ensure consistency
#     with open(filepath, "w") as f:
#         json.dump(tokens, f, indent=2)

#     return {"email": user_info.get("email"), "name": user_info.get("name")}




from pydantic import BaseModel


@app.get("/")
def read_root():
    return {"status": "API is running"}
class ExtractRequest(BaseModel):
    username: str
    vendor_email: str
    number_of_email_to_fetch: int

@app.post("/extract_certificates")
def extract_certificates(req: ExtractRequest):
    """Start workflow: fetch → extract → push DB → wait for approval"""
    try:
        vendor_email = req.vendor_email
        num_email = req.number_of_email_to_fetch
        username = req.username
        if not vendor_email:
            raise ValueError("Vendor email is required.")
        initial_state["vendor_email"] = vendor_email
        initial_state["number_of_email_to_fetch"] = num_email
        initial_state["username"] = username
        status = add_user(username)
        # if status.get("exist"):
        # increment_attempts(username)
        print("user added in the db")
        print("res.username is ", req.username)
        result = {}
        print("######################################################################################################")
        result = compiled_graph.invoke(initial_state, config=thread_config)
        # Normalize certificates
        raw_certs = result.get("certificate_data", []) or []
        certificates = [
            {
                "certificate_number": cert if isinstance(cert, str) else cert.get("certificate_number"),
                "status": "pending",
            }
            for cert in raw_certs
        ]
        print("######################################################################################################")
        print("the extracted certificates are: ", certificates)
        print("######################################################################################################")
        # Case 1: Workflow paused for approval
        if "__interrupt__" in result:
            raw_msg = result["__interrupt__"][0].value
            # ✅ Normalize message to string
            msg = raw_msg.get("message") if isinstance(raw_msg, dict) else str(raw_msg)
            return {
                "status": "Waiting",
                "message": msg or "Waiting for user approval...",
                "certificates": certificates,
                "raw_certs": raw_certs,  # optional for debugging
            }

        # Case 2: Workflow finished successfully
        return {
            "status": "Completed",
            "message": "Certificates extracted successfully",
            "certificates": certificates,
            "result": result,  # optional for debugging
        }

    except Exception as e:
        print("########################################################################################################")
        print("Error during certificate extraction:", str(e))
        return {
            "status": "Error",
            "message": str(e),
            "certificates": [],
        }

@app.post("/approval")
def take_approval(user_input: str):
    """Resume graph after approval/rejection"""
    user_input = user_input.strip().lower()
    result = compiled_graph.invoke(Command(resume=user_input), config=thread_config)

    if not result.get("sentiment", False):
        return {"status": "Rejected", "message": "User did not approve"}

    return {"status": "Approved", "result": result}
    


# @app.post("/extract_certificates")
# def extract_certificates():
#     global current_state
#     try:
#         print("########### Agent invoke in process ###########")
#         result = agent_instance.invoke(initial_state)

#         # Check if paused
#         if isinstance(result, Interrupted):
#             current_state = result
#             print("########### Agent paused for approval ###########")
#             return {
#                 "status": "Waiting for approval",
#                 "message": "Please call /approval with yes/no"
#             }

#         print("########### Agent completed successfully ###########")
#         return {"status": "Completed", "result": result}

#     except Exception as e:
#         return {"status": "Error", "message": str(e)}

#     # text = get_text_from_pdf(temp_path)
#     # os.remove(temp_path)
#     # data = get_certificate_data(text)
#     # print(data)
#     # """Push to db with approval as pending"""
#     # response = push_data(data)
#     # return {
#     #     "response": response,
#     #     "data":data
#     # }

# @app.post("/approval")
# def take_approval(user_input: str):
#     global current_state
#     if not current_state:
#         return {"status": "Error", "message": "No agent run is waiting for approval"}

#     user_input = user_input.strip().lower()

#     # Resume Agent from the paused state
#     resumed = agent_instance.resume(current_state, user_input)

#     if not resumed.get("sentiment", False):
#         return {"status": "Rejected", "message": "User did not approve"}

#     return {"status": "Approved", "message": "Proceeding to calendar update"}
#     # user_input = user_input.strip().lower()
#     # if user_input in ['yes', 'y', 'approve', 'approved']:
#     #     return JSONResponse({"approval": "True"})
#     # return JSONResponse({"approval": "False"})

# @app.post("/after_approval")
# def after_approval(certificate_number: str):
#     """Change the approval in the db as approved"""
#     # call the function
#     response = update_approval(certificate_number)
#     return response
