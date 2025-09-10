from langgraph.graph import StateGraph, START, END
from typing import List, Optional
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from dotenv import load_dotenv
load_dotenv()
from apis.database import get_user_activity, increment_attempts, reset_attempt

from utils.utility import get_certificate_data, get_text_from_pdf
from utils.utility import update_approval
from utils.utility import push_data
from gmail_work.gmail import fetch_emails_with_attachments

class State(TypedDict):
    username: str
    vendor_email: str
    number_of_email_to_fetch: int
    certificate_number: Optional[list[str]]
    sentiment: bool
    pdf_file_path: Optional[List[str]]
    certificate_data: Optional[List[dict]]
    push_to_db: Optional[bool]
    push_to_calendar: Optional[bool]
    
from langgraph.types import interrupt
class Agent:
    def __init__(self):
        self.graph = self.build_graph()

    def gmail_file_node(self, state: State):
        vendor_email = state.get("vendor_email", "")
        username = state.get("username", "")
        num_email = state.get("number_of_email_to_fetch", 1)
        if not vendor_email or not username:
            raise ValueError("Vendor email and your username is required.")
        print("username is ", username)
        # increment_attempts(username)
        all_paths = fetch_emails_with_attachments(username, vendor_email, num_email)
        state.update({"pdf_file_path": all_paths})
        
        print("################ Gmail node is called #######################")
        return state

    def certificate_data(self, state: State):
        all_data = []
        for path in state.get("pdf_file_path", []):
            text = get_text_from_pdf(path)
            data = get_certificate_data(text)
            all_data.extend(data)
            os.remove(path)  # Clean up file after processing
        state.update({"certificate_data": all_data})
        state.update({"certificate_number": [certi["certificate_number"] for certi in all_data]})
        return state
    
    def push_data_to_db(self, state:State):
        alldata = state.get("certificate_data", [])
        if alldata:
            push_data(alldata)
        state.update({"push_to_db": True})
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
            raise Exception("Data not pushed to DB yet.")
        
        # Pause until API provides user approval
        approval = interrupt({"message": "Waiting for user approval..."})
        state.update({"sentiment": approval in ["yes", "y", "approve", "approved"]})
        print("################ user_approval node is called #######################")
        return state

        # return state
    
    def push_to_calendar(self, state: State):
        if not state.get("sentiment", False):
            raise Exception("User approval not received.")
        # Logic to push to calendar can be added here
        certificate_numbers = state.get("certificate_number", [])
        if not certificate_numbers: raise Exception("no certificate extracted")
        data = {}
        for certificate_number in certificate_numbers:
            data = update_approval(state.get("username", ""), certificate_number)
        state.update({"push_to_calendar": True})
        attempts = get_user_activity(state.get("username"))
        print(attempts)
        # if not attempts.get("data", []):
        #     return state
        # if data and attempts.get("data", []) and attempts.get("data", [])[0][2] > 2:
        #     path = data.get("path", "")
        #     if path:
        #         print("removing file: ", path.get("path", ""))
        #         # os.remove(path.get("path", ""))
        #         resp = reset_attempt(username=state.get("username"))
        #         print("res after reset attempt is ", resp)
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