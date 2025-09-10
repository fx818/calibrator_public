from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import json
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.types import Command
from LangGraphAgent.agent import Agent, State
from database import add_user, increment_attempts
load_dotenv()


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

class ExtractRequest(BaseModel):
    username: str
    vendor_email: str
    number_of_email_to_fetch: int

@app.get("/")
def read_root():
    return {"status": "API is running"}

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
