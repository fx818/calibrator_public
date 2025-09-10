import sqlite3
import json

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
conn = sqlite3.connect("calibration.db")
cursor = conn.cursor()
cursor.execute("select * from user")
result = cursor.fetchall()
print(result)
conn.commit()
conn.close()
# # Create table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS calibration_certificates (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     certificate_number TEXT NOT NULL,
#     issue_date TEXT,
#     customer_name TEXT,
#     customer_address TEXT,
#     duc_id TEXT,
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
#     approval TEXT
# );
# """)



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
                result_error, result_expanded_uncertainty, remarks, notes, approval
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                record["certificate_number"], record["issue_date"], record["customer_name"], record["customer_address"],
                record["duc_id"], record["duc_serial_number"], record["duc_make_model"], record["duc_range"], record["duc_least_count"],
                record["duc_condition_at_receipt"], record["duc_location"], record["calibration_done_at"],
                record["calibration_date"], record["calibration_next_due"], record["calibration_date_received"],
                record["calibration_procedure_references_types"], record["standard_equipment_id"],
                record["standard_equipment_name"], record["standard_equipment_serial_number"],
                record["standard_equipment_certificate_number"], record["standard_equipment_calibration_date"],
                record["standard_equipment_calibration_due_date"], record["result_duc_value"], record["result_std_value"],
                record["result_error"], record["result_expanded_uncertainty"], record["remarks"], record["notes"],"Pending"
            ))

        # Commit and close
        conn.commit()
        conn.close()
        return {"status":"successful"}
    except Exception as e:
        return {"status":"failed"}
    
def update_approval(certificate_number):
    try:
        conn = sqlite3.connect("calibration.db")
        cursor = conn.cursor()
        command = """
        UPDATE calibration_certificates
        SET approval = ?
        where certificate_number = ?
        """
        cursor.execute(command,("approved", certificate_number))
        conn.commit()
        conn.close()
        return {"status":"successful"}
    except Exception as e:
        return {"status":"failed"}


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
# data = get_user_activity("fx818anuraghehe")
# print(data)
# print(add_user("testuser"))
# data = get_user_activity("testuser")
# print(data)