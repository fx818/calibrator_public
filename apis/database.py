import sqlite3
import json
from typing import Any, Dict, List, Optional
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.Sheets import delete_row_with_duc
from gmail_work.gmail import create_event
from utils.date_extraction import extract_date
from config import load_tokens, load_new_settings
from mail_scheduler.tests import schedule_email_via_api

from dateutil.parser import parse
from datetime import datetime, timezone
from datetime import timedelta


def parse_flexible_date(date_string: str) -> datetime | None:
    """
    Parses a date string in various formats into a datetime object.

    Args:
        date_string: The date string to parse (e.g., "13may2025", "13/05/2025").

    Returns:
        A datetime object if parsing is successful, otherwise None.
    """
    try:
        # The parse() function does all the hard work of figuring out the format.
        parsed_date = parse(date_string)
        return parsed_date
    except (ValueError, TypeError):
        # Handle cases where the string is completely unparseable.
        print(f"Error: Could not understand the date format for '{date_string}'")
        return None




# Your JSON data (replace with loading from file if needed)
# data = [
#     {
#         "certificate_number": "25000008034",
#         "issue_date": "24 May2025",
#         "customer_name": "Prag Polymers",
#         "customer_address": "A-40 & A-41, Talkatora Industrial Area, Lucknow-226011",
#         "duc_id": "GTM-13",
#         "duc_serial_number": "",
#         "duc_make_model": "Gera Research",
#         "duc_range": "0 to110°C",
#         "duc_least_count": 0.1,
#         "duc_condition_at_receipt": "No Damage",
#         "duc_location": "Design Room",
#         "calibration_done_at": "Laboratory",
#         "calibration_date": "15 May2025",
#         "calibration_next_due": "14 May2026",
#         "calibration_date_received": "15 May2025",
#         "calibration_procedure_references_types": "VCS/WI/56, IS6274:1971 (Reaffirmed2017)",
#         "standard_equipment_id": "VCS/RTD/01 & VCS/THM/01",
#         "standard_equipment_name": "RTD (4 Wire) With Digital Thermometer",
#         "standard_equipment_serial_number": "",
#         "standard_equipment_certificate_number": "2401888",
#         "standard_equipment_calibration_date": "08 June2024",
#         "standard_equipment_calibration_due_date": "07 June2025",
#         "result_duc_value": "null",
#         "result_std_value": "null",
#         "result_error": "null",
#         "result_expanded_uncertainty": "null",
#         "remarks": "None",
#         "notes": "1. The reported expanded uncertainty is stated as the standard uncertainty in measurement multiplied by the coverage factor (k=2), which for a normal distribution corresponds a coverage probability of approximately95%. 2. This certificate is referes only to the particular item submitted for calibration. 3. Results reported are valid at the time of and under stated conditions of measurement 4. This certificate shall not be reproduced except in full without permission of Head of Laboratory. 5. This certificate is for industrial and scientific purpose and can not be used in legal matters."
#     },
#     {
#         "certificate_number": "25000008035",
#         "issue_date": "24 May2025",
#         "customer_name": "Prag Polymers",
#         "customer_address": "A-40 & A-41, Talkatora Industrial Area, Lucknow-226011",
#         "duc_id": "GTM-14",
#         "duc_serial_number": "",
#         "duc_make_model": "Gera Research",
#         "duc_range": "0 to110°C",
#         "duc_least_count": 0.1,
#         "duc_condition_at_receipt": "No Damage",
#         "duc_location": "Design Room",
#         "calibration_done_at": "Laboratory",
#         "calibration_date": "15 May2025",
#         "calibration_next_due": "14 May2026",
#         "calibration_date_received": "15 May2025",
#         "calibration_procedure_references_types": "VCS/WI/56, IS6274:1971 (Reaffirmed2017)",
#         "standard_equipment_id": "VCS/RTD/01 & VCS/THM/01",
#         "standard_equipment_name": "RTD (4 Wire) With Digital Thermometer",
#         "standard_equipment_serial_number": "",
#         "standard_equipment_certificate_number": "2401888",
#         "standard_equipment_calibration_date": "08 June2024",
#         "standard_equipment_calibration_due_date": "07 June2025",
#         "result_duc_value": "null",
#         "result_std_value": "null",
#         "result_error": "null",
#         "result_expanded_uncertainty": "null",
#         "remarks": "None",
#         "notes": "1. The reported expanded uncertainty is stated as the standard uncertainty in measurement multiplied by the coverage factor (k=2), which for a normal distribution corresponds a coverage probability of approximately95%. 2. This certificate is referes only to the particular item submitted for calibration. 3. Results reported are valid at the time of and under stated conditions of measurement 4. This certificate shall not be reproduced except in full without permission of Head of Laboratory. 5. This certificate is for industrial and scientific purpose and can not be used in legal matters."
#     },
#     {
#         "certificate_number": "25000008036",
#         "issue_date": "24 May2025",
#         "customer_name": "Prag Polymers",
#         "customer_address": "A-40 & A-41, Talkatora Industrial Area, Lucknow-226011",
#         "duc_id": "GTM-15",
#         "duc_serial_number": "",
#         "duc_make_model": "Gera Research",
#         "duc_range": "0 to110°C",
#         "duc_least_count": 0.1,
#         "duc_condition_at_receipt": "No Damage",
#         "duc_location": "Design Room",
#         "calibration_done_at": "Laboratory",
#         "calibration_date": "15 May2025",
#         "calibration_next_due": "14 May2026",
#         "calibration_date_received": "15 May2025",
#         "calibration_procedure_references_types": "VCS/WI/56, IS6274:1971 (Reaffirmed2017)",
#         "standard_equipment_id": "VCS/RTD/01 & VCS/THM/01",
#         "standard_equipment_name": "RTD (4 Wire) With Digital Thermometer",
#         "standard_equipment_serial_number": "",
#         "standard_equipment_certificate_number": "2401888",
#         "standard_equipment_calibration_date": "08 June2024",
#         "standard_equipment_calibration_due_date": "07 June2025",
#         "result_duc_value": "null",
#         "result_std_value": "null",
#         "result_error": "null",
#         "result_expanded_uncertainty": "null",
#         "remarks": "None",
#         "notes": "1. The reported expanded uncertainty is stated as the standard uncertainty in measurement multiplied by the coverage factor (k=2), which for a normal distribution corresponds a coverage probability of approximately95%. 2. This certificate is referes only to the particular item submitted for calibration. 3. Results reported are valid at the time of and under stated conditions of measurement 4. This certificate shall not be reproduced except in full without permission of Head of Laboratory. 5. This certificate is for industrial and scientific purpose and can not be used in legal matters."
#     },
#     {
#         "certificate_number": "25000008037",
#         "issue_date": "24 May2025",
#         "customer_name": "Prag Polymers",
#         "customer_address": "A-40 & A-41, Talkatora Industrial Area, Lucknow-226011",
#         "duc_id": "GTM-16",
#         "duc_serial_number": "",
#         "duc_make_model": "Gera Research",
#         "duc_range": "0 to110°C",
#         "duc_least_count": 0.1,
#         "duc_condition_at_receipt": "No Damage",
#         "duc_location": "Design Room",
#         "calibration_done_at": "Laboratory",
#         "calibration_date": "15 May2025",
#         "calibration_next_due": "14 May2026",
#         "calibration_date_received": "15 May2025",
#         "calibration_procedure_references_types": "VCS/WI/56, IS6274:1971 (Reaffirmed2017)",
#         "standard_equipment_id": "VCS/RTD/01 & VCS/THM/01",
#         "standard_equipment_name": "RTD (4 Wire) With Digital Thermometer",
#         "standard_equipment_serial_number": "",
#         "standard_equipment_certificate_number": "2401888",
#         "standard_equipment_calibration_date": "08 June2024",
#         "standard_equipment_calibration_due_date": "07 June2025",
#         "result_duc_value": "null",
#         "result_std_value": "null",
#         "result_error": "null",
#         "result_expanded_uncertainty": "null",
#         "remarks": "None",
#         "notes": "1. The reported expanded uncertainty is stated as the standard uncertainty in measurement multiplied by the coverage factor (k=2), which for a normal distribution corresponds a coverage probability of approximately95%. 2. This certificate is referes only to the particular item submitted for calibration. 3. Results reported are valid at the time of and under stated conditions of measurement 4. This certificate shall not be reproduced except in full without permission of Head of Laboratory. 5. This certificate is for industrial and scientific purpose and can not be used in legal matters."
#     }
# ]

# Connect to SQLite DB
# conn = sqlite3.connect("calibration.db")
# cursor = conn.cursor()
# cursor.execute("delete from calibration_data")
# result = cursor.fetchall()
# cursor.execute("select * from calibration_certificates")
# result2 = cursor.fetchall()
# print(len(result))
# print(len(result2))
# conn.commit()
# conn.close()
# # Create table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS deleted_calibration_data (
#     id INTEGER,
#     certificate_number TEXT NOT NULL,
#     issue_date TEXT,
#     customer_name TEXT,
#     customer_address TEXT,
#     duc_id TEXT PRIMARY KEY,
#     duc_serial_number TEXT,
#     duc_make_model TEXT,
#     duc_range TEXT,
#     duc_least_count REAL,
#     duc_condition_at_receipt TEXT,
#     duc_location TEXT,
#     calibration_done_at TEXT,
#     calibration_date TEXT,
#     calibration_next_due TEXT,
#     calibration_date_received TEXT,
#     calibration_procedure_references_types TEXT,
#     standard_equipment_id TEXT,
#     standard_equipment_name TEXT,
#     standard_equipment_serial_number TEXT,
#     standard_equipment_certificate_number TEXT,
#     standard_equipment_calibration_date TEXT,
#     standard_equipment_calibration_due_date TEXT,
#     result_duc_value REAL,
#     result_std_value REAL,
#     result_error REAL,
#     result_expanded_uncertainty REAL,
#     remarks TEXT,
#     notes TEXT,
#     approval TEXT,
#     email TEXT NOT NULL
# );
# """)

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS deleted_warranty_claims (
#     warranty_claim_no TEXT PRIMARY KEY,
#     warranty_rejection_advice_no TEXT NOT NULL,
#     supplementary_claim_reference TEXT,
#     claim_date TEXT,
#     po_contract_no TEXT,
#     po_contract_date TEXT,

#     depot_lodging_claim TEXT,
#     consignee_code TEXT,
#     consignee_reporting_rejection TEXT,
#     sub_consignee TEXT,
#     complaint_no TEXT,
#     complaint_date TEXT,

#     supplier_name TEXT,
#     supplier_address TEXT,
#     ireps_code TEXT,
#     challan_no TEXT,
#     challan_date TEXT,
#     ic_no TEXT,
#     ic_date TEXT,

#     pl_item_code TEXT,
#     inspection_by TEXT,
#     vendor_approving_agency TEXT,
#     description TEXT,
#     make_brand TEXT,
#     batch_product_slno TEXT,
#     warranty_period TEXT,
#     coach_no TEXT,

#     qty_rejected REAL,
#     qty_rejected_words TEXT,
#     reason_of_rejection TEXT,
#     remarks TEXT,
#     pu_remarks TEXT,

#     rate_per_unit REAL,
#     claim_amount REAL,
#     head_allocation TEXT,

#     recovery_advice TEXT,
#     remarks_for_inspection_agency TEXT,
#     paying_authority TEXT,
#     shop_depot_official TEXT,
#     controlling_officer_name TEXT,
#     controlling_officer_email TEXT,

#     warranty_voucher_date TEXT,
#     drop_remarks TEXT,
#     signatories TEXT,
#     approval TEXT,
#     email TEXT NOT NULL
# );

# """)

# conn.commit()
# conn.close()

def push_data(record, email):
    if not email: 
        raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        # Insert data
        pk = record.get("duc_id")
        # Check if record with same primary key exists
        cursor.execute("SELECT 1 FROM calibration_data WHERE duc_id = ?", (pk,))
        exists = cursor.fetchone() is not None
        if exists:
            print(f"Record with duc_id {pk} already exists so we delete it so that new one can be added.")
            cursor.execute("DELETE FROM calibration_data WHERE duc_id = ?", (pk,))
        values = [
            str(record.get("certificate_number")),
            str(record.get("issue_date")),
            str(record.get("customer_name")),
            str(record.get("customer_address")),
            str(record.get("duc_id")),
            str(record.get("duc_serial_number")),
            str(record.get("duc_make_model")),
            str(record.get("duc_range")),
            record.get("duc_least_count"),  # keep as is (float/int)
            str(record.get("duc_condition_at_receipt")),
            str(record.get("duc_location")),
            str(record.get("calibration_done_at")),
            str(record.get("calibration_date")),
            str(record.get("calibration_next_due")),
            str(record.get("calibration_date_received")),
            str(record.get("calibration_procedure_references_types")),
            str(record.get("standard_equipment_id")),
            str(record.get("standard_equipment_name")),
            str(record.get("standard_equipment_serial_number")),
            str(record.get("standard_equipment_certificate_number")),
            str(record.get("standard_equipment_calibration_date")),
            str(record.get("standard_equipment_calibration_due_date")),
            str(record.get("result_duc_value")),
            str(record.get("result_std_value")),
            str(record.get("result_error")),
            str(record.get("result_expanded_uncertainty")),
            str(record.get("remarks")),
            str(record.get("notes")),
            "Pending",
            str(email)
        ]
        cursor.execute("""
        INSERT INTO calibration_data (
            certificate_number, issue_date, customer_name, customer_address,
            duc_id, duc_serial_number, duc_make_model, duc_range, duc_least_count, duc_condition_at_receipt, duc_location, calibration_done_at, calibration_date, calibration_next_due, calibration_date_received, calibration_procedure_references_types, standard_equipment_id,standard_equipment_name, standard_equipment_serial_number,standard_equipment_certificate_number, standard_equipment_calibration_date,standard_equipment_calibration_due_date, result_duc_value, result_std_value,result_error, result_expanded_uncertainty, remarks, notes, approval, email
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(values))

        # Commit and close
        conn.commit()
        conn.close()
        print("pushed the data in the db")
        return {"status":"successful"}
    except Exception as e:
        print("Failed to push the data")
        return {"status":"failed"}
    
def push_data_warranty(record, email):
    # Write the logic here
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if not email: 
            raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
        # Also check for already existing record with same primary key 
        pk = record.get("warranty_claim_no", "")
        cursor.execute("Select 1 from warranty_claims where email = ? AND warranty_claim_no = ?", (email, pk))
        res = cursor.fetchall()
        if res:
            cursor.execute("DELETE from warranty_claims where email = ? and warranty_claim_no = ?", (email, pk))
            print("Deleting some data from the warranty claim table to insert the new data")
        # Insert data
        values = [
            str(record.get("warranty_claim_no","")),
            str(record.get("warranty_rejection_advice_no","")),
            str(record.get("supplementary_claim_reference","")),
            str(record.get("claim_date","")),
            str(record.get("po_contract_no","")),
            str(record.get("po_contract_date","")),
            str(record.get("depot_lodging_claim","")),
            str(record.get("consignee_code","")),
            str(record.get("consignee_reporting_rejection","")),
            str(record.get("sub_consignee","")),
            str(record.get("complaint_no","")),
            str(record.get("complaint_date","")),
            str(record.get("supplier_name","")),
            str(record.get("supplier_address","")),
            str(record.get("ireps_code","")),
            str(record.get("challan_no","")),
            str(record.get("challan_date","")),
            str(record.get("ic_no","")),
            str(record.get("ic_date","")),
            str(record.get("pl_item_code","")),
            str(record.get("inspection_by","")),
            str(record.get("vendor_approving_agency","")),
            str(record.get("description","")),
            str(record.get("make_brand","")),
            str(record.get("batch_product_slno","")),
            str(record.get("warranty_period","")),
            str(record.get("coach_no","")),
            record.get("qty_rejected",0),  # keep as is (float/int)    
            str(record.get("qty_rejected_words","")),
            str(record.get("reason_of_rejection","")),
            str(record.get("remarks","")),
            str(record.get("pu_remarks","")),
            record.get("rate_per_unit",0),  # keep as is (float/int)
            record.get("claim_amount",0),  # keep as is (float/int)
            str(record.get("head_allocation","")),
            str(record.get("recovery_advice","")),
            str(record.get("remarks_for_inspection_agency","")),
            str(record.get("paying_authority","")),
            str(record.get("shop_depot_official","")),
            str(record.get("controlling_officer_name","")),
            str(record.get("controlling_officer_email","")),
            str(record.get("warranty_voucher_date","")),
            str(record.get("drop_remarks","")),
            str(record.get("signatories","")),
            "Pending",
            str(email)
            ]
        cursor.execute("""
            INSERT INTO warranty_claims (warranty_claim_no, warranty_rejection_advice_no, supplementary_claim_reference, claim_date, po_contract_no, po_contract_date, depot_lodging_claim, consignee_code, consignee_reporting_rejection, sub_consignee, complaint_no, complaint_date, supplier_name, supplier_address, ireps_code, challan_no, challan_date, ic_no, ic_date, pl_item_code, inspection_by, vendor_approving_agency, description, make_brand, batch_product_slno, warranty_period, coach_no, qty_rejected, qty_rejected_words, reason_of_rejection, remarks, pu_remarks, rate_per_unit, claim_amount, head_allocation, recovery_advice, remarks_for_inspection_agency, paying_authority, shop_depot_official, controlling_officer_name, controlling_officer_email, warranty_voucher_date, drop_remarks, signatories, approval, email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(values))
        conn.commit()
        conn.close()
        print("pushed the warranty data in the db")
        return {"status":"Data pushed successfully"}
    except Exception as e:
        conn.commit()
        conn.close()
        print("Some error while pushing the warranty data in the db", e)
        return {"status": "Some error while pushing the warranty data in the db"}
    
def deleted_push_data_warranty(record, email):
    # Write the logic here
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if not email: 
            raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
        # Also check for already existing record with same primary key 
        pk = record[0]
        cursor.execute("Select 1 from deleted_warranty_claims where email = ? AND warranty_claim_no = ?", (email, pk))
        res = cursor.fetchall()
        if res:
            cursor.execute("DELETE from deleted_warranty_claims where email = ? and warranty_claim_no = ?", (email, pk))
            print("Deleting some data from the warranty claim table to insert the new data")
        # Insert data
        # values = [
        #     str(record.get("warranty_claim_no","")),
        #     str(record.get("warranty_rejection_advice_no","")),
        #     str(record.get("supplementary_claim_reference","")),
        #     str(record.get("claim_date","")),
        #     str(record.get("po_contract_no","")),
        #     str(record.get("po_contract_date","")),
        #     str(record.get("depot_lodging_claim","")),
        #     str(record.get("consignee_code","")),
        #     str(record.get("consignee_reporting_rejection","")),
        #     str(record.get("sub_consignee","")),
        #     str(record.get("complaint_no","")),
        #     str(record.get("complaint_date","")),
        #     str(record.get("supplier_name","")),
        #     str(record.get("supplier_address","")),
        #     str(record.get("ireps_code","")),
        #     str(record.get("challan_no","")),
        #     str(record.get("challan_date","")),
        #     str(record.get("ic_no","")),
        #     str(record.get("ic_date","")),
        #     str(record.get("pl_item_code","")),
        #     str(record.get("inspection_by","")),
        #     str(record.get("vendor_approving_agency","")),
        #     str(record.get("description","")),
        #     str(record.get("make_brand","")),
        #     str(record.get("batch_product_slno","")),
        #     str(record.get("warranty_period","")),
        #     str(record.get("coach_no","")),
        #     record.get("qty_rejected",0),  # keep as is (float/int)    
        #     str(record.get("qty_rejected_words","")),
        #     str(record.get("reason_of_rejection","")),
        #     str(record.get("remarks","")),
        #     str(record.get("pu_remarks","")),
        #     record.get("rate_per_unit",0),  # keep as is (float/int)
        #     record.get("claim_amount",0),  # keep as is (float/int)
        #     str(record.get("head_allocation","")),
        #     str(record.get("recovery_advice","")),
        #     str(record.get("remarks_for_inspection_agency","")),
        #     str(record.get("paying_authority","")),
        #     str(record.get("shop_depot_official","")),
        #     str(record.get("controlling_officer_name","")),
        #     str(record.get("controlling_officer_email","")),
        #     str(record.get("warranty_voucher_date","")),
        #     str(record.get("drop_remarks","")),
        #     str(record.get("signatories","")),
        #     "Pending",
        #     str(email)
        #     ]
        cursor.execute("""
            INSERT INTO deleted_warranty_claims (warranty_claim_no, warranty_rejection_advice_no, supplementary_claim_reference, claim_date, po_contract_no, po_contract_date, depot_lodging_claim, consignee_code, consignee_reporting_rejection, sub_consignee, complaint_no, complaint_date, supplier_name, supplier_address, ireps_code, challan_no, challan_date, ic_no, ic_date, pl_item_code, inspection_by, vendor_approving_agency, description, make_brand, batch_product_slno, warranty_period, coach_no, qty_rejected, qty_rejected_words, reason_of_rejection, remarks, pu_remarks, rate_per_unit, claim_amount, head_allocation, recovery_advice, remarks_for_inspection_agency, paying_authority, shop_depot_official, controlling_officer_name, controlling_officer_email, warranty_voucher_date, drop_remarks, signatories, approval, email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, record)
        conn.commit()
        conn.close()
        print("pushed the warranty data in the db")
        return {"status":"Data pushed successfully"}
    except Exception as e:
        conn.commit()
        conn.close()
        print("Some error while pushing the warranty data in the db", e)
        return {"status": "Some error while pushing the warranty data in the db"}

def update_approval(pk, email, intent):
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if intent == "calibration_certificate":
            command = """
            UPDATE calibration_data
            SET approval = ?
            where duc_id = ? and email = ?
            """
            cursor.execute(command,("approved", pk, email))
            # calendar event creation
            due_date = cursor.execute("SELECT calibration_next_due FROM calibration_data WHERE duc_id = ?", (pk,)).fetchone()[0]
            calibration_date = cursor.execute("SELECT calibration_data from calibration_data where duc_id = ?", (pk)).fetchone()[0]
            print(due_date)
            due_date = extract_date(due_date)
            create_event(email, due_date, pk)
            conn.commit()
            conn.close()
            # schedule_email_via_api()
            print()
            print()
            print()
            print("lets get the tokens first")
            tokens = load_tokens(email)
            print("The tokens are ", tokens)
            # Lets get all the mail to which we have to send to
            settings = load_new_settings(email)
            
            print(settings)
            allemails = settings.get("scheduled_emails")
            for name, reciever in allemails.items():
                print(name, reciever)
                from datetime import datetime, timedelta, timezone
                # time_to_send = datetime.now(timezone.utc) + timedelta(minutes=2)
                print(calibration_date)
                start_date = parse_flexible_date(calibration_date)
                if start_date:
                    # Set the time and add the UTC timezone
                    start_date = start_date.replace(
                        hour=18,
                        minute=30,
                        tzinfo=timezone.utc
                    )
                    # Now you can add a duration to it
                    time_to_send = start_date + timedelta(days=327)

                    print(f"\nFinal scheduled time in UTC: {time_to_send}")
                    schedule_email_via_api(token_data=tokens, receiver=reciever, subject=f"Callibration Email schdule - {pk}", body=f"This is in regards to the certificate no {pk}. This certificate is now due. Please co-ordinate within due time", send_at=time_to_send)



                # print(extract_date(claim_date), type(extract_date(claim_date)))
                print("Scheduler confirmed")
                print()
                print()
                print()
        elif intent == "Warranty_claim":
            command = """
            UPDATE warranty_claims
            SET approval = ?
            where warranty_claim_no = ? and email = ?
            """
            cursor.execute(command, ("approved", pk, email))
            claim_date = cursor.execute("SELECT claim_date from warranty_claims where warranty_claim_no = ?", (pk)).fetchone()[0]
            conn.commit()
            conn.close()
            print()
            print()
            print()
            print("lets get the tokens first")
            tokens = load_tokens(email)
            print("The tokens are ", tokens)
            # Lets get all the email where we have to send mail
            # Lets get all the mail to which we have to send to
            settings = load_new_settings(email)
            print(settings)
            allemails = settings.get("scheduled_emails")
            for name, reciever in allemails.items():
                print(name, reciever)
                from datetime import datetime, timedelta, timezone
                # time_to_send = datetime.now(timezone.utc) + timedelta(minutes=2)
                print(claim_date)
                start_date = parse_flexible_date(claim_date)
                if start_date:
                    # Set the time and add the UTC timezone
                    start_date = start_date.replace(
                        hour=18,
                        minute=30,
                        tzinfo=timezone.utc
                    )
                    # Now you can add a duration to it
                    time_to_send = start_date + timedelta(days=327)

                    print(f"\nFinal scheduled time in UTC: {time_to_send}")
                    schedule_email_via_api(token_data=tokens, receiver=reciever, subject=f"Warranty Email schdule - {pk}", body=f"This is in regards to the warranty claim no {pk}. This certificate is now due. Please co-ordinate within due time", send_at=time_to_send)



                # print(extract_date(claim_date), type(extract_date(claim_date)))
                print("Scheduler confirmed")
                print()
                print()
                
        return {"status":"successful"}

    except Exception as e:
        conn.commit()
        conn.close()
        return {"status":"failed to update approval", "error": str(e)}


def get_calibrated_data_from_db(email: str, role: str) -> Optional[List[Dict[str, Any]]]:
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if role == "calibration_manager":
            command = """
                SELECT * FROM calibration_data WHERE email = ? AND approval = ?
            """
            cursor.execute(command, (email, "approved"))
            result = cursor.fetchall()
            # Get column names and convert to dict format
            column_names = [description[0] for description in cursor.description]
            result_dicts = [dict(zip(column_names, row)) for row in result]
            print()
            print(result_dicts)
            print()
            conn.close()
            return result_dicts
        elif role == "warranty_claim_manager":
            command = """
                SELECT * FROM warranty_claims WHERE email = ? AND approval = ?
            """
            cursor.execute(command, (email, "approved"))
            result = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            result_dicts = [dict(zip(column_names, row)) for row in result]
            print()
            print(result_dicts)
            print()
            conn.close()
            return result_dicts
    except Exception as e:
        conn.close()
        return []

def get_pending_data_from_db(email: str, role: str) -> Optional[List[Dict[str, Any]]]:
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if role == "calibration_manager":
            command = """
                SELECT * FROM calibration_data WHERE email = ? AND approval = ?
            """
            cursor.execute(command, (email, "pending"))
            result = cursor.fetchall()
            # Get column names and convert to dict format
            column_names = [description[0] for description in cursor.description]
            result_dicts = [dict(zip(column_names, row)) for row in result]
            print()
            print(result_dicts)
            print()
            conn.close()
            return result_dicts
        elif role == "warranty_claim_manager":
            command = """
                SELECT * FROM warranty_claims WHERE email = ? AND approval = ?
            """
            cursor.execute(command, (email, "pending"))
            result = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            result_dicts = [dict(zip(column_names, row)) for row in result]
            print()
            print(result_dicts)
            print()
            conn.close()
            return result_dicts
    except Exception as e:
        conn.close()
        return []


def update_callibration_pending_data(email, standard_equipment_name, duc_id, duc_range, customer_address, calibration_done_at, certificate_number, calibration_date_received, calibration_next_due, approval):
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        query = """
        UPDATE calibration_data
        SET
            standard_equipment_name = ?,
            certificate_number = ?,
            duc_range = ?,
            customer_address = ?,
            calibration_done_at = ?,
            calibration_date_received = ?,
            calibration_next_due = ?,
            approval = ?
            WHERE email = ? and duc_id = ?
        """
        values = (
            standard_equipment_name,
            certificate_number,
            duc_range,
            customer_address,
            calibration_done_at,
            calibration_date_received,
            calibration_next_due,
            approval,
            email,
            duc_id
        )
        cursor.execute(query, values)
        conn.commit()
        # Schedule the mail here too
        print("Values updated succesfully with certificate number", certificate_number)
        print()
        print()
        print()
        print("lets get the tokens first")
        tokens = load_tokens(email)
        print("The tokens are ", tokens)
        # Lets get all the mail to which we have to send to
        settings = load_new_settings(email)
        print(settings)
        allemails = settings.get("scheduled_emails")
        for name, reciever in allemails.items():
            print(name, reciever)
            from datetime import datetime, timedelta, timezone
            # time_to_send = datetime.now(timezone.utc) + timedelta(minutes=2)
            print(calibration_date_received)
            start_date = parse_flexible_date(calibration_date_received)
            if start_date:
                # Set the time and add the UTC timezone
                start_date = start_date.replace(
                    hour=18,
                    minute=30,
                    tzinfo=timezone.utc
                )
                # Now you can add a duration to it
                time_to_send = start_date + timedelta(days=327)

                print(f"\nFinal scheduled time in UTC: {time_to_send}")
                schedule_email_via_api(token_data=tokens, receiver=reciever, subject=f"Callibration Email schdule - {duc_id}", body=f"This is in regards to the certificate no {duc_id}. This certificate is now due. Please co-ordinate within due time", send_at=time_to_send)



            # print(extract_date(claim_date), type(extract_date(claim_date)))
            print("Scheduler confirmed")
        print()
        print()
        print()
        print()
        print()
        print()
        return {"status": "success", "error":"None"}
    except Exception as e:
        print("Some error occurred as ",e)
        conn.close()
        return {"error": e, "status":"failed"}


def update_warranty_pending_data(email,warranty_claim_no, claim_date, supplier_name, supplier_address, ic_no, inspection_by, description, qty_rejected, reason_of_rejection, signatories, approval):
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        query = """
        UPDATE warranty_claims
        SET
            description = ?,
            ic_no = ?,
            supplier_name = ?,
            supplier_address = ?,
            claim_date = ?,
            inspection_by = ?,
            approval = ?,
            qty_rejected = ?,
            reason_of_rejection = ?,
            signatories = ?
            WHERE email = ? and warranty_claim_no = ?
        """
        values = (
            description,
            ic_no,
            supplier_name,
            supplier_address,
            claim_date,
            inspection_by,
            approval,
            qty_rejected,
            reason_of_rejection,
            signatories,
            email,
            warranty_claim_no
        )

        cursor.execute(query, values)
        conn.commit()
        print("Values updated succesfully with warranty_claim number", warranty_claim_no)
        print()
        print()
        print()
        print("lets get the tokens first")
        tokens = load_tokens(email)
        print("The tokens are ", tokens)
        # Lets get all the mail to which we have to send to
        settings = load_new_settings(email)
        print(settings)
        allemails = settings.get("scheduled_emails")
        for name, reciever in allemails.items():
            print(name, reciever)
            from datetime import datetime, timedelta, timezone
            # time_to_send = datetime.now(timezone.utc) + timedelta(minutes=2)
            print(claim_date)
            start_date = parse_flexible_date(claim_date)
            if start_date:
                # Set the time and add the UTC timezone
                start_date = start_date.replace(
                    hour=18,
                    minute=30,
                    tzinfo=timezone.utc
                )
                # Now you can add a duration to it
                time_to_send = start_date + timedelta(days=327)

                print(f"\nFinal scheduled time in UTC: {time_to_send}")
                schedule_email_via_api(token_data=tokens, receiver=reciever, subject=f"Warranty Email schdule - {warranty_claim_no}", body=f"This is in regards to the warranty claim no {warranty_claim_no}. This certificate is now due. Please co-ordinate within due time", send_at=time_to_send)



            # print(extract_date(claim_date), type(extract_date(claim_date)))
            print("Scheduler confirmed")
        print()
        print()
        print()
        return {"status": "success", "error":"None"}
    
    
    except Exception as e:
        print("Some error occurred as ",e)
        conn.close()
        return {"error": e, "status":"failed"}

def get_record_from_db(email, role, pk):
    if role == "calibration_manager":
        conn = sqlite3.connect("calibration.db")
        try:
            cursor = conn.cursor()
            command = """
                SELECT * FROM calibration_data WHERE email = ? and duc_id = ?
            """
            cursor.execute(command, (email, pk))
            result = cursor.fetchone()
            return {"result": result}
        except Exception as e:
            print("error fetching data")
            conn.close()
            return {"status":"error", "error":f"Error {e}"}
    
    elif role == "warranty_claim_manager":
        conn = sqlite3.connect("calibration.db")
        try:
            cursor = conn.cursor()
            command = """
                SELECT * FROM warranty_claims WHERE email = ? and warranty_claim_no = ?
            """
            cursor.execute(command, (email,pk))
            result = cursor.fetchone()
            return {"result": result}
        except Exception as e:
            print("error fetching data")
            conn.close()
            return {"status":"error", "error":f"Error {e}"}
    return {"status":"Role issues", "error":f"Error {e}"}
    

def delete_calibrated_data_from_db(pk: str, email: str, role: str):
    
    if role == "calibration_manager":
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        get_data = cursor.execute("SELECT * FROM calibration_data WHERE duc_id = ? AND email = ? AND approval = ?", (pk, email, "approved"))
        try:
            result = get_data.fetchall()[0]
            command = """
                DELETE FROM calibration_data WHERE duc_id = ? AND email = ? AND approval = ?
            """
            cursor.execute(command, (pk, email, "approved"))
            conn.commit()
            conn.close()
        except Exception as e:
            print("No such record found to delete", e)
            return {"status": "No such record found"}, None
    elif role == "warranty_claim_manager":
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        get_data = cursor.execute("SELECT * FROM warranty_claims WHERE warranty_claim_no = ? AND email = ? AND approval = ?", (pk, email, "approved"))
        try:
            result = get_data.fetchall()[0]
            command = """
                DELETE FROM warranty_claims WHERE warranty_claim_no = ? AND email = ? AND approval = ?
            """
            cursor.execute(command, (pk, email, "approved"))
            conn.commit()
            conn.close()
        except Exception as e:
            print("No such record found to delete", e)
            return {"status":"No such record found"}, None
    else:
        result = []

    status = delete_row_with_duc(pk, role)
    print(status)
    return result, role


def create_user_table():
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        table_name = "user"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        return {"status": "table created"}
    except Exception as e:
        return {"status": "failed to create table"}
    

def add_user(username: str, role: str):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        SELECT * FROM user WHERE username = ?
        """
        cursor.execute(command, (username,))
        record = cursor.fetchall()
        if record:
            return {"status": "already", "exist":True}
        command = """
        INSERT INTO user (username, role) VALUES (?, ?)
        """
        cursor.execute(command, (username, role))
        conn.commit()
        conn.close()
        return {"status":"created", "exist":False}
    except Exception as e:
        return {"status": "failed", "exist":False}

def get_user_activity(username):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        SELECT * FROM user
        where username = ?
        ORDER BY timestamp DESC
        LIMIT 5
        """
        cursor.execute(command,(username,))
        records = cursor.fetchall()
        conn.close()
        return {"status":"successful", "data": records}
    except Exception as e:
        return {"status":"failed", "data": []} 

def increment_attempts(username: str):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        Update user set attempts = attempts + 1 where username = ?
        """
        cursor.execute(command,(username,))
        conn.commit()
        conn.close()
        return {"status":"successful"}
    except Exception as e:
        return {"status":"failed"} 

def reset_attempt(username: str):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        UPDATE user SET attempts = ? WHERE username = ?
        """
        cursor.execute(command,(0, username))
        conn.commit()
        conn.close()
        print(f"Setting attempts for user {username} to 0")
        return {"status":"successful"}
    except Exception as e:
        print("username is in heeree is ", username)
        return {"status":"failed"} 


def deleted_push_data(record, email):
    if not email: 
        raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
    try:
        print("the record is ", record)
        record = record[1:]
        if not record:
            print("No record data found to push to deleted_db")
            return {"status":"failed"}
        
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        # Insert data
        pk = record[5]
        # Check if record with same primary key exists
        cursor.execute("SELECT 1 FROM deleted_calibration_data WHERE duc_id = ?", (pk,))
        exists = cursor.fetchone() is not None
        print(exists)
        if exists:
            print(f"Record with duc_id {pk} already exists so we delete it so that new one can be added.")
            cursor.execute("DELETE FROM deleted_calibration_data WHERE duc_id = ?", (pk,))
            conn.commit()
        print("Now starting the cursor execution")
        cursor.execute("""
        INSERT INTO deleted_calibration_data (
            certificate_number, issue_date, customer_name, customer_address,
            duc_id, duc_serial_number, duc_make_model, duc_range, duc_least_count, duc_condition_at_receipt, duc_location, calibration_done_at, calibration_date, calibration_next_due, calibration_date_received, calibration_procedure_references_types, standard_equipment_id,standard_equipment_name, standard_equipment_serial_number,standard_equipment_certificate_number, standard_equipment_calibration_date,standard_equipment_calibration_due_date, result_duc_value, result_std_value,result_error, result_expanded_uncertainty, remarks, notes, approval, email
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, record)
        print("Inserted dude.................")
        # Commit and close
        conn.commit()
        conn.close()
        print("pushed the data in the deleted db")
        return {"status":"successful"}
    except Exception as e:
        print("Failed to push the data", e)
        return {"status":"failed"}
  

def create_config_table():
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        table_name = "config"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            email TEXT PRIMARY KEY,
            calibration_sheet text,
            warranty_sheet text,
            calibration_dept_email text,
            store_dept_email text,
            vendor_email text,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        return {"status": "table created"}
    except Exception as e:
        return {"status": "failed to create table"} 
    
def create_new_config_table():
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        table_name = "configs"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            email TEXT PRIMARY KEY,
            sheet text,
            scheduled_emails text, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        return {"status": "table created"}
    except Exception as e:
        return {"status": "failed to create table"}

def add_new_config(email: str, sheet: str, scheduled_emails: dict):
    conn = sqlite3.connect("calibration.db")
    try:
        cursor = conn.cursor()
        command = """
        SELECT * FROM configs WHERE email = ?
        """
        cursor.execute(command, (email,))
        record = cursor.fetchall()
        scheduled_emails = json.dumps(scheduled_emails) 
        if record:
            command = """
                UPDATE configs SET 
                sheet = ?,
                scheduled_emails = ?,
                timestamp = CURRENT_TIMESTAMP
            WHERE email = ?
            """
            cursor.execute(command, (sheet, scheduled_emails, email))
            conn.commit()
            conn.close()
            return {"status":"updated", "exist":True}
        command = """
        INSERT INTO configs (email, sheet, scheduled_emails) VALUES (?, ?, ?)
        """
        cursor.execute(command, (email, sheet, scheduled_emails))
        conn.commit()
        conn.close()
        return {"status":"created", "exist":False}
    except Exception as e:
        conn.close()
        print("Some error while adding config data", e)
        return {"status": "failed", "exist":False}
                

def add_config(email, calibration_sheet, warranty_sheet, calibration_dept_email, store_dept_email, vendor_email):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        SELECT * FROM config WHERE email = ?
        """
        cursor.execute(command, (email,))
        record = cursor.fetchall()
        if record:
            command = """
                UPDATE config SET 
                calibration_sheet = ?,
                warranty_sheet = ?,
                calibration_dept_email = ?,
                store_dept_email = ?,
                vendor_email = ?,
                timestamp = CURRENT_TIMESTAMP
            WHERE email = ?
            """
            cursor.execute(command, (calibration_sheet, warranty_sheet, calibration_dept_email, store_dept_email, vendor_email, email))
            conn.commit()
            conn.close()
            return {"status":"updated", "exist":True}
        command = """
        INSERT INTO config (email, calibration_sheet, warranty_sheet, calibration_dept_email, store_dept_email, vendor_email) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(command, (email, calibration_sheet, warranty_sheet, calibration_dept_email, store_dept_email, vendor_email))
        conn.commit()
        conn.close()
        return {"status":"created", "exist":False}
    except Exception as e:
        print("Some error while adding config data", e)
        return {"status": "failed", "exist":False}


def get_deleted_data_from_db(email: str, role: str):
    if not email: 
        raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
    conn = sqlite3.connect("calibration.db")
    if role == "calibration_manager":
        try:
            cursor = conn.cursor()
            cursor.execute("Select * from deleted_calibration_data where email = ?", (email,))
            rows = cursor.fetchall()

            # Get column names from the cursor description
            columns = [description[0] for description in cursor.description]

            # Create a list of dictionaries using a list comprehension
            result = [dict(zip(columns, row)) for row in rows]

            return {"data": result}
        except Exception as e:
            conn.close()
            return {"error": e}
        finally:
            conn.close()
    elif role == "warranty_claim_manager":
        try:
            cursor = conn.cursor()
            cursor.execute("Select * from deleted_warranty_claims where email = ?", (email,))
            rows = cursor.fetchall()

            # Get column names from the cursor description
            columns = [description[0] for description in cursor.description]

            # Create a list of dictionaries using a list comprehension
            result = [dict(zip(columns, row)) for row in rows]

            return {"data": result}
        except Exception as e:
            conn.close()
            return {"error": e}
        finally:
            conn.close()
        
    return {}





# create_new_config_table()
# email = "anuragfx818@gmail.com"
# scheduled_emails = {
#     "store": "store@gmail.com",
#     "vendor": "vendor@gmail.com"
# }
# sheet = "sheetid12345"
# data = add_new_config(email, sheet, scheduled_emails)
# print(data)
# data = get_user_activity("fx818anuraghehe")
# print(data)
# print(add_user("testuser"))
# data = get_user_activity("testuser")
# print(data)
# conn = sqlite3.connect("calibration.db")
# cursor = conn.cursor()
# cursor.execute("delete from calibration_data")
# conn.commit()
# conn.close()
# data = get_calibrated_data_from_db("testingbyme818@gmail.com", "warranty_claim_manager")
# print(data)
# data = get_record_from_db("220104076@hbtu.ac.in", "warranty_claim_manager", "866A-25-02659")
# print(data.get("result"))