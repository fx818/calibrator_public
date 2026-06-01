from langgraph.graph import StateGraph, START, END
from typing import Dict, List, Optional
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dotenv import load_dotenv
load_dotenv()
from apis.database import get_user_activity, increment_attempts, push_data_warranty, reset_attempt

from utils.utility import get_certificate_data, get_text_from_pdf, get_intent
from apis.database import push_data, update_approval
from gmail_work.gmail import fetch_emails_with_attachments
from utils.Sheets import update_approval_in_sheet, update_sheet_with_certificates, update_data_in_sheet, get_data_from_sheet, get_worksheet_from_url
from apis.awsS3.helper import upload_file_to_s3, create_presigned_url_for_viewing

class State(TypedDict):
    username: str
    certificate_number: Optional[list[str]]
    sentiment: bool
    pdf_file_path: Optional[List[str]]
    certificate_data: Optional[List[dict]]
    push_to_db: Optional[bool]
    push_to_calendar: Optional[bool]
    prev_node: str
    curr_node: str
    role: str
    pdf_url: List[str]
    config: Optional[Dict]

import io
import requests
from PyPDF2 import PdfMerger

def merge_pdf_via_pre_signed_url(url1, url2):
    print("inside the function call")
    pdf1 = io.BytesIO(requests.get(url1).content)
    pdf2 = io.BytesIO(requests.get(url2).content)

    merger = PdfMerger()
    merger.append(pdf1)
    merger.append(pdf2)

    with open("merged.pdf", "wb") as f:
        merger.write(f)
    merger.close()

    upload_file_to_s3("merged.pdf", os.getenv("AWS_S3_BUCKET", ""), "merged.pdf")
    presigned_url = create_presigned_url_for_viewing(os.getenv("AWS_S3_BUCKET", ""), "merged.pdf")
    os.remove("merged.pdf")
    print("Function call ends here")
    return presigned_url

from langgraph.types import interrupt
class Agent:
    def __init__(self):
        self.graph = self.build_graph()

    def gmail_file_node(self, state: State):
        print()
        print()
        print("Previous urls is ", state.get("pdf_url", []))
        print()
        print()
        username = state.get("username", "")
        state.update({"curr_node": "gmail_file_node", "prev_node": "Starting point"})
        if not username:
            raise ValueError("Bro, You need to login.")
        print("username is ", username)
        # increment_attempts(username)
        role = state.get("role", "")
        if not role:
            raise ValueError("Bro, role is not set.")
        print("the role is ", role)
        if role == "calibration_manager":
            all_paths = fetch_emails_with_attachments(username, "Calibration")
        elif role == "warranty_claim_manager":
            all_paths = fetch_emails_with_attachments(username, "Warranty")
        else:
            all_paths = []
        if not all_paths:
            print("No new emails with attachments found for given role ", role)
            # return {"status": "No new emails with attachments found."}
            return state
        state.update({"pdf_file_path": all_paths})
        all_file_path_url = []
        try:
            for path in all_paths:
                print("Uploading file to S3: ", os.path.basename(path))
                upload_file_to_s3(path, os.getenv("AWS_S3_BUCKET", ""), os.path.basename(path))
                path_url = create_presigned_url_for_viewing(os.getenv("AWS_S3_BUCKET", ""), os.path.basename(path))
                print("the path url is", path_url)
                all_file_path_url.append(path_url)
        except Exception as e:
            print("Some error occurred while uploading to S3: ", e)
        prev_pdf_url = state.get("pdf_url", [])
        if prev_pdf_url and all_file_path_url:
            # Lets merge both pdfs
            try:
                new_url = merge_pdf_via_pre_signed_url(prev_pdf_url[0], all_file_path_url[0])
                print("new url is ", new_url)
                all_file_path_url = [new_url]
            except Exception as e:
                print("Error while fucntion call for merging pdfs: ", e)
        state.update({"pdf_url": all_file_path_url})
        print("the final pdf url is ", state.get("pdf_url", []))
        print("################ Gmail node is called #######################")
        return state

    def certificate_data(self, state: State):
        print()
        print("Entering into the certificate node")
        print()
        all_data = []
        all_paths = state.get("pdf_file_path", [])
        if not all_paths:
            print("No path found")
            return state
        for path in all_paths:
            text = get_text_from_pdf(path)
            print("the text is ", text)
            data = get_certificate_data(text)
            print("the data extracted from the certificate is ", data)
            all_data.extend(data)
            # os.remove(path)  # Clean up file after processing
        print()
        print("all data extracted from all certificates is ", all_data)
        state.update({"certificate_data": all_data})
        try:
            state.update({"certificate_number": [certi["certificate_number"] for certi in all_data]})
            state.update({"curr_node": "certificate_data", "prev_node": "gmail_file_node"})
        except:
            print("Error updating state with certificate data")
            state.update({"certificate_number": []})
            state.update({"curr_node": "certificate_data", "prev_node": "gmail_file_node"})
        print("################ certificate_data node is called #######################")
        return state
    
    def push_data_to_db(self, state:State):
        print()
        print("Entering into push db node")
        print()
        alldata = state.get("certificate_data", [])
        print("Data to be pushed to DB: ", alldata)
        if not alldata:
            print("No certificate data found to push to DB.")
            return {"status": "No data to be pushed"}
        for record in alldata:
            print()
            print()
            print("each record is ", record)
            print()
            print()
            print("The intent of record is ", record.get("intent"))
            if record.get("intent") == "calibration_certificate":
                # No prob here due to intent key
                push_data(record, state.get("username", ""))
                print("record successfully pushed to DB")
                state.update({"push_to_db": True})
            elif record.get("intent") == "Warranty_claim":
                # Have to do here due to intent key
                push_data_warranty(record, state.get("username", ""))
                print("warranty record successfully pushed to DB")
                state.update({"push_to_db": True})
            
        # Pushing to the sheet
        state.update({"curr_node": "push_data_to_db", "prev_node": "certificate_data"})
        # Also push to sheet
        # url = os.getenv("SHEET_URL", "")
        # warranty_url = os.getenv("WARRANTY_SHEET_URL", "")
        url = state.get("config").get("sheet")
        warranty_url = state.get("config").get("sheet")
        print("Both the url is ", url)
        print("Both the url is ", warranty_url)
        for row in alldata:
            if row["intent"] == "calibration_certificate":
                if not url:
                    print("No sheet url found")
                    print("################ push_data_to_db node is called #######################")
                    return state
                _, header = get_data_from_sheet(url)
                worksheet = get_worksheet_from_url(url)
                print("all data is ", alldata)
                if not header:
                    header_val = list(row.keys())
                    header_val.remove("intent")
                    header_val.append("Approval")
                    header_val.append("Email")
                    worksheet.append_row(header_val)
                    print("Added header")
                row.pop("intent", None)
                valtopush = list(row.values())
                valtopush.append("Pending")
                valtopush.append(state.get("username", ""))
                status = update_data_in_sheet(url, valtopush, pk_idx=4)
                row["intent"] = "calibration_certificate"
                print("the status after update_data_in_sheet is ", status)
            elif row["intent"] == "Warranty_claim":
                # add the code logic here to push warranty data to sheet
                if not warranty_url:
                    print("No sheet url found")
                    print("################ push_data_to_db node is called #######################")
                    return state
                _, header = get_data_from_sheet(warranty_url)
                worksheet = get_worksheet_from_url(warranty_url)
                print("all data is ", alldata)
                if not header:
                    header_val = list(row.keys())
                    header_val.remove("intent")
                    header_val.append("Approval")
                    header_val.append("Email")
                    worksheet.append_row(header_val)
                    print("Added header in warranty claim sheet")
                row.pop("intent", None)
                valtopush = list(row.values())
                valtopush.append("Pending")
                valtopush.append(state.get("username", ""))
                status = update_data_in_sheet(warranty_url, valtopush, pk_idx=0)
                row["intent"] = "Warranty_claim"
                print("the status after update_data_in_sheet is ", status)
        print("################ push_data_to_db node is called #######################")
        return state

    def user_approval(self, state: State):
        # pushdb = state.get("push_to_db", False)
        # if not pushdb:
        #     raise Exception("Data not pushed to DB yet.")
        # # Take approval from user in realtime
        # state.update({"sentiment": True})
        pushdb = state.get("push_to_db", False)
        if not pushdb:
            print("Data not pushed to DB yet.")
            return {"status": "Data not pushed to DB yet."}
        
        # Pause until API provides user approval
        approval = interrupt({"message": "Waiting for user approval..."})
        state.update({"sentiment": approval in ["yes", "y", "approve", "approved"]})
        state.update({"curr_node": "user_approval", "prev_node": "push_data_to_db"})
        print("################ user_approval node is called #######################")
        return state
    
    def push_to_calendar(self, state: State):
        if not state.get("sentiment", False):
            print("User approval not received.")
            return {"status": "User approval not received."}
        # Logic to push to calendar can be added here
        all_data = state.get("certificate_data", [])
        data = {}
        if not all_data:
            print("No certificate data found")
            print("################ push_to_calendar node is called #######################")
            return state
        for record in all_data:
            intent = record.get("intent", "")
            if not intent:
                print("No intent found in the record")
                return {"status": "No intent found in the record"}
            if intent == "calibration_certificate":
                pk = record["duc_id"]
                data = update_approval(pk, state.get("username", ""), intent)
                print("response from the update_approval func is ", data)
            elif intent == "Warranty_claim":
                pk = record["warranty_claim_no"]
                data = update_approval(pk, state.get("username", ""), intent)
                print("response from the update_approval func is ", data)
        state.update({"push_to_calendar": True})
        url = os.getenv("SHEET_URL", "")
        warranty_url = state.get("config")
        
        for cert in all_data:
            if cert["intent"] == "calibration_certificate":
                cert.pop("intent", None)
                if not url:
                    print("No sheet url found")
                    print("################ push_to_calendar node is called #######################")
                    return state
                cert["intent"] = "calibration_certificate"
                status = update_approval_in_sheet(url, cert.get("duc_id", ""), pk_idx = 4)
                print("the status after update_approval_in_sheet is ", status)
            elif cert["intent"] == "Warranty_claim":
                cert.pop("intent", None)
                if not warranty_url:
                    print("No warranty sheet url found")
                    print("################ push_to_calendar node is called #######################")
                    return state
                cert["intent"] = "Warranty_claim"
                status = update_approval_in_sheet(warranty_url, cert.get("warranty_claim_no", ""), pk_idx = 0)
                print("the status after update_approval_in_sheet is ", status)

        # attempts = get_user_activity(state.get("username"))
        # print(attempts)
        # if not attempts.get("data", []):
        #     return state
        # if data and attempts.get("data", []) and attempts.get("data", [])[0][2] > 2:
        #     path = data.get("path", "")
        #     if path:
        #         print("removing file: ", path.get("path", ""))
        #         # os.remove(path.get("path", ""))
        #         resp = reset_attempt(username=state.get("username"))
        #         print("res after reset attempt is ", resp)
        state.update({"curr_node": "push_to_calendar", "prev_node": "user_approval"})
        print("################ push_to_calendar node is called #######################")
        return state

    def build_graph(self):
        graph = StateGraph(State)
        graph.add_node("gmail_file_node", self.gmail_file_node)
        graph.add_node("certificate_data", self.certificate_data)
        graph.add_node("push_data_to_db", self.push_data_to_db)
        graph.add_node("user_approval", self.user_approval)
        graph.add_node("push_to_calendar", self.push_to_calendar)

        # Adding Edge
        graph.add_edge(START, "gmail_file_node")
        graph.add_edge("gmail_file_node", "certificate_data")
        graph.add_edge("certificate_data", "push_data_to_db")
        graph.add_edge("push_data_to_db", "user_approval")
        graph.add_edge("user_approval", "push_to_calendar")
        graph.add_edge("push_to_calendar", END)
        # Add MemorySaver checkpointer for resuming
        checkpointer = MemorySaver()
        return graph.compile(checkpointer=checkpointer)