import sqlite3
import json
from typing import List, Optional

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


# conn.commit()
# conn.close()

def push_data(data, email):
    if not email: 
        raise ValueError("You are not logged in or some error in fetching mail, see push_db node")
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        # Insert data
        for record in data:
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
    

def update_approval(certificate_number, email):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        UPDATE calibration_data
        SET approval = ?
        where certificate_number = ? and email = ?
        """
        cursor.execute(command,("approved", certificate_number, email))
        conn.commit()
        conn.close()
        return {"status":"successful"}
    except Exception as e:
        return {"status":"failed"}


def get_calibrated_data_from_db(email: str) -> Optional[List]:
    command = """
        SELECT * FROM calibration_data WHERE email = ? AND approval = ?
    """
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    cursor.execute(command, (email, "approved"))
    result = cursor.fetchall()
    conn.close()
    return result

def delete_calibrated_data_from_db(pk: str, email: str) -> Optional[List]:
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    get_data = cursor.execute("SELECT * FROM calibration_data WHERE duc_id = ? AND email = ? AND approval = ?", (pk, email, "approved"))
    result = get_data.fetchall()[0]
    command = """
        DELETE FROM calibration_data WHERE duc_id = ? AND email = ? AND approval = ?
    """
    cursor.execute(command, (pk, email, "approved"))
    conn.commit()
    conn.close()
    return result


def create_user_table():
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        table_name = "user"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            attempts NUMBER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        return {"status": "table created"}
    except Exception as e:
        return {"status": "failed to create table"}
    

def add_user(username: str):
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
        INSERT INTO user (username, attempts) VALUES (?, 0)
        """
        cursor.execute(command, (username,))
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
        if exists:
            print(f"Record with duc_id {pk} already exists so we delete it so that new one can be added.")
            cursor.execute("DELETE FROM deleted_calibration_data WHERE duc_id = ?", (pk,))
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
        print("Failed to push the data")
        return {"status":"failed"}
  

# data = get_user_activity("fx818anuraghehe")
# print(data)
# print(add_user("testuser"))
# data = get_user_activity("testuser")
# print(data)