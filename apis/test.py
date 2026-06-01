import sqlite3
from typing import List, Dict, Any, Optional
def get_pending_data_from_db(email: str, role: str) -> Optional[List[Dict[str, Any]]]:
    conn = sqlite3.connect("calibration.db")
    cursor = conn.cursor()
    try:
        if role == "calibration_manager":
            command = """
                SELECT * FROM calibration_data WHERE email = ? AND approval = ?
            """
            cursor.execute(command, (email, "Pending"))
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

data = get_pending_data_from_db("testingbyme818@gmail.com", "calibration_manager")
print(data)