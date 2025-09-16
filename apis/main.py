# backend.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os, json, datetime, requests, re
from dotenv import load_dotenv

# LangGraph + DB imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.types import Command
from LangGraphAgent.agent import Agent, State
from database import add_user, get_calibrated_data_from_db, delete_calibrated_data_from_db, deleted_push_data
from config import save_tokens, load_tokens

load_dotenv()

# ---------------- Config ----------------
SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "replace-with-strong-secret")

# Google OAuth config
CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "478641910458-vd7at938uqvfn2mfrhqosuq4r0cokg77.apps.googleusercontent.com"
)
CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
    "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"
)

# Since the frontend is now served by the backend, these are relative paths
FRONTEND_URL = "/static/testpage2.html"
ROLE_FRONTEND_URL = "/static/user_role.html"

# The redirect URI must match what's configured in your Google Cloud Console
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")

SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar", # ✅ ADD THIS LINE
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

TOKEN_DIR = "tokens"
os.makedirs(TOKEN_DIR, exist_ok=True)

# ---------------- FastAPI App ----------------
app = FastAPI()

# Mount the static directory to serve your HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sessions
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    # "lax" is a secure default for same-origin apps
    same_site="lax",
    # https_only=True,
    # domain=".ngrok-free.app"
)

# ---------------- LangGraph Agent ----------------
agent = Agent()
compiled_graph = agent.graph

# ---------------- Helpers ----------------
def sanitize_for_thread_id(s: str) -> str:
    """Make a safe thread id from an email (alphanumeric + underscores)."""
    return re.sub(r"[^0-9a-zA-Z_]", "_", s or "anonymous")


def get_initial_state_for_user(username: str, role: str | None = None) -> State:
    """Return a fresh State for a user's LangGraph invocation."""
    return State(
        username=username,
        certificate_number=None,
        sentiment=False,
        pdf_file_path=None,
        certificate_data=None,
        push_to_db=None,
        push_to_calendar=None,
        curr_node="",
        prev_node="",
        role=role or "",
        pdf_url=""
    )

def get_user_thread_config(username: str) -> dict:
    """Each user gets their own thread_id for LangGraph state."""
    tid = f"certificate-flow-{sanitize_for_thread_id(username)}"
    return {"configurable": {"thread_id": tid}}

# ---------------- Routes to serve HTML ----------------
@app.get("/", response_class=HTMLResponse)
async def serve_login_page():
    """Serves the main login page."""
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/role", response_class=HTMLResponse)
async def serve_role_page():
    """Serves the user role selection page."""
    with open("static/user_role.html", "r") as f:
        return f.read()

# ---------------- OAuth Endpoints ----------------
@app.get("/login")
def login():
    """Redirects the user to Google's OAuth consent screen."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={' '.join(SCOPES)}"
        "&access_type=offline&prompt=consent"
    )
    return RedirectResponse(google_auth_url)
@app.get("/auth/callback")
def auth_callback(request: Request):
    """Exchanges the authorization code for an access token and user info."""
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code"}, status_code=400)

    # Exchange code for tokens
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    })
    tokens = resp.json()

    # ==================== FIX IS HERE ====================
    # Add the client ID and secret to the token dictionary before saving.
    # The Google Auth library needs these to refresh credentials later.
    tokens['client_id'] = CLIENT_ID
    tokens['client_secret'] = CLIENT_SECRET
    # =====================================================

    access_token = tokens.get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo?alt=json", headers=headers).json()
    email = user_info.get("email")
    tokens["account"] = email

    # Store user email in the server session and save the now-complete tokens
    request.session["account_email"] = email
    save_tokens(email, tokens)

    # Redirect to the role selection page
    return RedirectResponse("/role")
@app.get("/me")
def me(request: Request):
    """Returns the logged-in user's email."""
    email = request.session.get("account_email")
    role = request.session.get("role")
    if not email:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    return {"email": email, "role": role}

@app.post("/logout")
def logout(request: Request):
    """Clears the session and logs the user out."""
    request.session.clear()
    return {"status": "logged_out"}

# ---------------- Token Endpoints ----------------
@app.get("/tokens")
def get_tokens(request: Request):
    """Retrieves the stored tokens for the logged-in user."""
    email = request.session.get("account_email")
    if not email:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    tokens = load_tokens(email)
    return tokens or {"error": "No tokens"}

@app.post("/refresh")
def refresh_tokens(request: Request):
    """Refreshes the access token using the refresh token."""
    email = request.session.get("account_email")
    if not email:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    tokens = load_tokens(email)
    if not tokens or not tokens.get("refresh_token"):
        return JSONResponse({"error": "No refresh_token"}, status_code=400)

    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    })
    new_tokens = r.json()
    tokens["token"] = new_tokens.get("access_token")
    expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=new_tokens.get("expires_in", 3600))
    tokens["expiry"] = expiry.isoformat() + "Z"
    save_tokens(email, tokens)
    return tokens

# ---------------- Roles Endpoint ----------------
@app.post("/define_role")
def define_role(request: Request, role: str):
    """Defines the user's role and stores it in the session and database."""
    email = request.session.get("account_email")
    if not email:
        return JSONResponse({"error": "Login required"}, status_code=401)
    add_user(email, role)
    request.session["role"] = role
    return {"success": True, "redirect_url": FRONTEND_URL}

# ---------------- Certificate Workflow ----------------
class ExtractRequest(BaseModel):
    username: str
    vendor_email: str
    number_of_email_to_fetch: int

@app.post("/extract_certificates")
def extract_certificates(request: Request):
    """Initiates the certificate extraction workflow."""
    email = request.session.get("account_email")
    role = request.session.get("role")
    if not email or not role:
        return JSONResponse({"status": "Error", "message": "Login & set role"}, status_code=401)

    state = get_initial_state_for_user(email, role)
    thread_config = get_user_thread_config(email)

    result = compiled_graph.invoke(state, config=thread_config)
    raw_certs = result.get("certificate_data", []) or []
    certificates = [{"certificate_number": c if isinstance(c, str) else c.get("certificate_number", ""), "status": "pending"} for c in raw_certs]

    if "__interrupt__" in result:
        raw_msg = result["__interrupt__"][0].value
        msg = raw_msg.get("message") if isinstance(raw_msg, dict) else str(raw_msg)
        print("The pdf path url is ", result.get("pdf_url"))
        return {"status": "Waiting", "message": msg or "Waiting approval...", "certificates": certificates, "raw_certs": raw_certs, "pdf_url_path": result.get("pdf_url")}

    return {"status": "Completed", "message": "Certificates extracted", "certificates": certificates, "result": result}

@app.post("/approval")
def approval(request: Request, user_input: str):
    """Resumes the workflow after user approval."""
    email = request.session.get("account_email")
    if not email:
        return JSONResponse({"status": "Error", "message": "Not logged in"}, status_code=401)
    thread_config = get_user_thread_config(email)
    result = compiled_graph.invoke(Command(resume=user_input.strip().lower()), config=thread_config)
    if not result.get("sentiment", False):
        return {"status": "Rejected", "message": "User did not approve"}
    return {"status": "Approved", "result": result}

# ---------------- Data Endpoints ----------------
@app.post("/get_calibrated_data")
def get_calibrated_data(request: Request):
    """Retrieves calibrated data for the user."""
    email = request.session.get("account_email")
    role = request.session.get("role")
    if not email or not role:
        return JSONResponse({"error": "Login & set role"}, status_code=401)
    data = get_calibrated_data_from_db(email, role)
    return {"data": data}

@app.delete("/delete_records")
def delete_records(request: Request, pk: str):
    """Deletes a record from the database."""
    email = request.session.get("account_email")
    if not email:
        return JSONResponse({"error": "Login required"}, status_code=401)
    role = request.session.get("role")
    if not role:
        print("Role is not defined")
        return {"status": "No role found during deletion"}
    data, _ = delete_calibrated_data_from_db(pk, email, role)
    if role == "calibration_manager":
        deleted_push_data(data, email)
    return {"data": data}