import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from openai import OpenAI
from dotenv import load_dotenv
import gspread #type: ignore
from google.oauth2.service_account import Credentials # type: ignore
# from date_extraction import extract_date
from gmail_work.gmail import create_event
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

import re
from datetime import datetime

date_patterns = [
    # 12/05/2025 or 12-05-2025
    r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",

    # 12 May 2025, 12May2025, 12May2025 (with/without space)
    r"(\d{1,2})\s*([A-Za-z]+)\s*(\d{4})"
]
def extract_date(text: str) -> str | None:
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()

                    # If month is number
                    if month.isdigit():
                        date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                    else:
                        date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%B-%Y")
            except ValueError:
                try:
                    # Try abbreviated month (e.g. May, Jan)
                    date_obj = datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%Y")
                except:
                    continue
            return date_obj.strftime("%Y-%m-%d")
    return None



from agentic_doc.parse import parse #type: ignore
def get_text_from_pdf(file_path):
    result = parse(file_path)
    return result[0].markdown

# JSON schema (from previous example)
certificate_schema = {
  "type": "object",
  "properties": {
    "certificate_number": {"type": "string"},
    "issue_date": {"type": "string"},
    "customer_name": {"type": "string"},
    "customer_address": {"type": "string"},
    "duc_id": {"type": "string"},
    "duc_serial_number": {"type": "string"},
    "duc_make_model": {"type": "string"},
    "duc_range": {"type": "string"},
    "duc_least_count": {"type": "number"},
    "duc_condition_at_receipt": {"type": "string"},
    "duc_location": {"type": "string"},
    "calibration_done_at": {"type": "string"},
    "calibration_date": {"type": "string"},
    "calibration_next_due": {"type": "string"},
    "calibration_date_received": {"type": "string"},
    "calibration_procedure_references_types": {"type": "string"},
    "standard_equipment_id": {"type": "string"},
    "standard_equipment_name": {"type": "string"},
    "standard_equipment_serial_number": {"type": "string"},
    "standard_equipment_certificate_number": {"type": "string"},
    "standard_equipment_calibration_date": {"type": "string"},
    "standard_equipment_calibration_due_date": {"type": "string"},
    "result_duc_value": {"type": "number"},
    "result_std_value": {"type": "number"},
    "result_error": {"type": "number"},
    "result_expanded_uncertainty": {"type": "number"},
    "remarks": {"type": "string"},
    "notes": {"type": "string"}
  },
  "required": [
    "certificate_number",
    "issue_date",
    "customer_name",
    "customer_address",
    "duc_id",
    "duc_make_model",
    "duc_range",
    "duc_least_count",
    "calibration_date",
    "calibration_next_due",
    "standard_equipment_id",
    "standard_equipment_name",
    "standard_equipment_certificate_number",
    "standard_equipment_calibration_date",
    "standard_equipment_calibration_due_date",
    "result_duc_value",
    "result_std_value",
    "result_error",
    "result_expanded_uncertainty",
    "remarks",
    "notes"
  ],
  "additionalProperties": False
}


prompt = """

You are given a text that may contain one or more calibration certificates.  

Your task:
- Extract each certificate into a JSON object according to the schema.  
- Output a single JSON array, where each element is one certificate object.  

Rules:
- Follow the schema exactly (no extra keys, no arrays inside certificates).  
- If a field is missing, use "" for strings and null for numbers.  
- Output **only** valid JSON. No explanations, no markdown, no comments.  
- Include the value of all the keys in the schema, don't make it empty or null

Schema:
{
  "type": "object",
  "properties": {
    "certificate_number": {"type": "string"},
    "issue_date": {"type": "string"},
    "customer_name": {"type": "string"},
    "customer_address": {"type": "string"},
    "duc_id": {"type": "string"},
    "duc_serial_number": {"type": "string"},
    "duc_make_model": {"type": "string"},
    "duc_range": {"type": "string"},
    "duc_least_count": {"type": "number"},
    "duc_condition_at_receipt": {"type": "string"},
    "duc_location": {"type": "string"},
    "calibration_done_at": {"type": "string"},
    "calibration_date": {"type": "string"},
    "calibration_next_due": {"type": "string"},
    "calibration_date_received": {"type": "string"},
    "calibration_procedure_references_types": {"type": "string"},
    "standard_equipment_id": {"type": "string"},
    "standard_equipment_name": {"type": "string"},
    "standard_equipment_serial_number": {"type": "string"},
    "standard_equipment_certificate_number": {"type": "string"},
    "standard_equipment_calibration_date": {"type": "string"},
    "standard_equipment_calibration_due_date": {"type": "string"},
    "result_duc_value": {"type": "number"},
    "result_std_value": {"type": "number"},
    "result_error": {"type": "number"},
    "result_expanded_uncertainty": {"type": "number"},
    "remarks": {"type": "string"},
    "notes": {"type": "string"}
  },
  "required": [
    "certificate_number",
    "issue_date",
    "customer_name",
    "customer_address",
    "duc_id",
    "duc_make_model",
    "duc_range",
    "duc_least_count",
    "calibration_date",
    "calibration_next_due",
    "standard_equipment_id",
    "standard_equipment_name",
    "standard_equipment_certificate_number",
    "standard_equipment_calibration_date",
    "standard_equipment_calibration_due_date",
    "result_duc_value",
    "result_std_value",
    "result_error",
    "result_expanded_uncertainty",
    "remarks",
    "notes"
  ],
  "additionalProperties": False
}

Standard Output Example:
[
  {
    "certificate_number": "CC-2024-001",
    "issue_date": "2024-02-10",
    "customer_name": "ABC Industries",
    "customer_address": "45 Industrial Road, Delhi",
    "duc_id": "DUC-12345",
    "duc_serial_number": "SN-789",
    "duc_make_model": "Fluke 87V",
    "duc_range": "0-100V",
    "duc_least_count": 0.01,
    "duc_condition_at_receipt": "Good",
    "duc_location": "Lab-1",
    "calibration_done_at": "In-house",
    "calibration_date": "2024-02-08",
    "calibration_next_due": "2025-02-08",
    "calibration_date_received": "2024-02-07",
    "calibration_procedure_references_types": "ISO/IEC 17025",
    "standard_equipment_id": "STD-567",
    "standard_equipment_name": "Agilent 34461A",
    "standard_equipment_serial_number": "1234",
    "standard_equipment_certificate_number": "STD-CERT-2024-01",
    "standard_equipment_calibration_date": "2023-11-01",
    "standard_equipment_calibration_due_date": "2024-11-01",
    "result_duc_value": 99.98,
    "result_std_value": 100.00,
    "result_error": -0.02,
    "result_expanded_uncertainty": 0.05,
    "remarks": "Within tolerance",
    "notes": "NA"
  },
  {
    "certificate_number": "CC-2024-002",
    "issue_date": "2024-03-05",
    "customer_name": "XYZ Pvt Ltd",
    "customer_address": "Mumbai",
    "duc_id": "DUC-777",
    "duc_serial_number": null,
    "duc_make_model": "Tektronix TDS2002",
    "duc_range": "0-200MHz",
    "duc_least_count": null,
    "duc_condition_at_receipt": "Fair",
    "duc_location": "Site-2",
    "calibration_done_at": "External Lab",
    "calibration_date": "2024-03-01",
    "calibration_next_due": "2025-03-01",
    "calibration_date_received": "2024-02-28",
    "calibration_procedure_references_types": "NABL Guidelines",
    "standard_equipment_id": "STD-890",
    "standard_equipment_name": "Keysight U1234",
    "standard_equipment_serial_number": "4567",
    "standard_equipment_certificate_number": "STD-CERT-2024-02",
    "standard_equipment_calibration_date": "2023-09-01",
    "standard_equipment_calibration_due_date": "2024-09-01",
    "result_duc_value": 200.1,
    "result_std_value": 200.0,
    "result_error": 0.1,
    "result_expanded_uncertainty": 0.2,
    "remarks": "Minor deviation",
    "notes": "Follow-up required"
  }
]

You have to return the list of Json objects only. No other text.

Important: Include the value of all the keys in the schema, don't make it empty or null

"""

import json
import re

allCertificate_number = []

def get_certificate_data(all_cert_text):
    response = client.responses.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        instructions=prompt,
        input=all_cert_text,
        
    )
    raw_text = response.output_text.strip()
    # 🔹 Remove markdown fences like ```json ... ```
    raw_text = re.sub(r"```(json)?", "", raw_text).strip()
    # 🔹 Extract all JSON objects (not assuming single array)
    json_objects = re.findall(r"\{.*?\}", raw_text, re.DOTALL)
    certificates_list = []
    for obj in json_objects:
        try:
            parsed = json.loads(obj)
            certificates_list.append(parsed)
        except Exception as e:
            print("⚠️ Could not parse an object:", e)
            certificates_list.append({"raw_text": obj})

    # # Save as one clean JSON array
    # with open("new2_all_certificatesModelOSS.json", "w", encoding="utf-8") as f:
    #     json.dump(certificates_list, f, indent=4, ensure_ascii=False)

    print(f"✅ Extracted {len(certificates_list)} certificates")
    for certi in certificates_list:
        allCertificate_number.append(certi["certificate_number"])
    return certificates_list


def get_all_certificate_numbers():
    return allCertificate_number


def get_worksheet_from_url(url):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    creds = Credentials.from_service_account_file('../data/credentials.json', scopes=scopes)
    client = gspread.authorize(creds)
    print("-------Authorised-------")
    sheet = client.open_by_url(url)
    return sheet.sheet1

def get_data_from_sheet(url):
    worksheet = get_worksheet_from_url(url)
    values = worksheet.get_all_values()
    if not values:
        return []
    header = values.pop(0)
    res = []
    for row in values:
        tmp = {}
        for i in range(len(header)):
            tmp[header[i]] = row[i]
        res.append(tmp)
    return res

def update(url, data):
    worksheet = get_worksheet_from_url(url)
    worksheet.update(data)
    return {"status": "success"}


def update_sheet_with_certificates(url, all_cert_text):

    certificates = get_certificate_data(all_cert_text)
    worksheet = get_worksheet_from_url(url)
    if not certificates:
        return {"status": "no data to update"}
    
    # Prepare header
    header = list(certificates[0].keys())
    header.append("Verified")
    print("Header is ", header)
    worksheet.append_row(header)
    # Prepare and append each certificate data
    for cert in certificates:
        row = list(cert.values())
        row.append("False")
        print()
        print("row is ", row)
        print()
        worksheet.append_row(row)
    
    return {"status": "success"}



import sqlite3
def push_data(data):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        # Insert data
        for record in data:
            cursor.execute("""
            INSERT INTO calibration_certificates (
                certificate_number, issue_date, customer_name, customer_address,
                duc_id, duc_serial_number, duc_make_model, duc_range, duc_least_count,
                duc_condition_at_receipt, duc_location, calibration_done_at,
                calibration_date, calibration_next_due, calibration_date_received,
                calibration_procedure_references_types, standard_equipment_id,
                standard_equipment_name, standard_equipment_serial_number,
                standard_equipment_certificate_number, standard_equipment_calibration_date,
                standard_equipment_calibration_due_date, result_duc_value, result_std_value,
                result_error, result_expanded_uncertainty, remarks, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                record["certificate_number"], record["issue_date"], record["customer_name"], record["customer_address"],
                record["duc_id"], record["duc_serial_number"], record["duc_make_model"], record["duc_range"], record["duc_least_count"],
                record["duc_condition_at_receipt"], record["duc_location"], record["calibration_done_at"],
                record["calibration_date"], record["calibration_next_due"], record["calibration_date_received"],
                record["calibration_procedure_references_types"], record["standard_equipment_id"],
                record["standard_equipment_name"], record["standard_equipment_serial_number"],
                record["standard_equipment_certificate_number"], record["standard_equipment_calibration_date"],
                record["standard_equipment_calibration_due_date"], record["result_duc_value"], record["result_std_value"],
                record["result_error"], record["result_expanded_uncertainty"], record["remarks"], record["notes"]
            ))

        # Commit and close
        conn.commit()
        conn.close()
        return {"status":"successful"}
    except Exception as e:
        return {"status":"failed"}
    
def update_approval(username, certificate_number):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        UPDATE calibration_certificates
        SET approval = ?
        where certificate_number = ?
        """
        due_date = cursor.execute("SELECT calibration_next_due FROM calibration_certificates WHERE certificate_number = ?", (certificate_number,)).fetchone()[0]
        print(due_date)
        cursor.execute(command,("approved", certificate_number))
        conn.commit()
        conn.close()
        """Add to the calender"""
        due_date = extract_date(due_date)
        path = create_event(username, due_date, certificate_number)
        return {
            "status":"successful",
            "due_date": due_date,
            "path": path
            }
    except Exception as e:
        return {"status":"failed"}