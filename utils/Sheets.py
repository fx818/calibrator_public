import gspread
from google.oauth2.service_account import Credentials
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


creds_file_path = '../utils/credentials.json'

def get_worksheet_from_url(url):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    creds = Credentials.from_service_account_file(creds_file_path, scopes=scopes)
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
    return res, header

# Not using for now
def delete_data(duc_id, url):
    worksheet = get_worksheet_from_url(url)
    values = worksheet.get_all_values()
    if not values:
        return {"status": "no data to delete"}
    header = values.pop(0)
    for i in range(len(values)):
        row = values[i]
        if row[4] == duc_id:
            worksheet.delete_rows(i + 2)  # +2 because of header and 1-based index
            print("Deleted row with DUC ID:", duc_id)
            return {"status": "success"}
    print("No row found with DUC ID:", duc_id)
    return {"status": "not found"}

def update_data_in_sheet(url, data):
    worksheet = get_worksheet_from_url(url)
    duc_id = data[4]
    values = worksheet.get_all_values()
    if not values:
        print("Sheet is empty")
        return {"status": "Sheet is empty"}
    for i in range(1, len(values)):
        row = values[i]
        if row[4] == duc_id:
            print("Found row with DUC ID:", duc_id)
            worksheet.delete_rows(i + 1)  # +1 because of 1-based index
            print("Deleted row with DUC ID:", duc_id)
            break
    data = [str(d) for d in data]
    worksheet.append_row(data)
    return {"status": "success"}

def update_approval_in_sheet(url, duc_id):
    worksheet = get_worksheet_from_url(url)
    values = worksheet.get_all_values()
    if not values:
        print("Sheet is empty")
        return {"status": "Sheet is empty"}
    header = values[0]
    for i in range(1, len(values)):
        row = values[i]
        if row[4] == duc_id:
            print("Found row with DUC ID:", duc_id)
            row[header.index("Approval")] = "Approved"
            worksheet.delete_rows(i + 1)  # +1 because of 1-based index
            print("Deleted row with DUC ID:", duc_id)
            row = [str(r) for r in row]
            worksheet.append_row(row)
            print("Updated approval for DUC ID:", duc_id)
            return {"status": "success"}
    print("No row found with DUC ID:", duc_id)
    return {"status": "not found"}

def delete_row_with_duc(duc_id):
    url = os.getenv("SHEET_URL", "")
    if not url:
        print("No sheet url found")
        return {"status": "no sheet url found during the deletion"}
    worksheet = get_worksheet_from_url(url)
    values = worksheet.get_all_values()
    if not values:
        print("Sheet is empty")
        return {"status": "Sheet is empty"}
    header = values[0]
    for i in range(1, len(values)):
        row = values[i]
        if row[4] == duc_id:
            print("Found row with DUC ID:", duc_id)
            worksheet.delete_rows(i + 1)  # +1 because of 1-based index
            print("Deleted row with DUC ID:", duc_id)
            return {"status": "success"}
    return {"status": "not found, error dusring deletion from the sheet"}


url = "https://docs.google.com/spreadsheets/d/1KhAt3I4Tb0ZtdSpmFlp8DiL6Nr-ps2MIdKGawmB-ZLE/edit?usp=sharing"

def update_sheet_with_certificates(url, certificates):
    worksheet = get_worksheet_from_url(url)
    if not certificates:
        print("No certificates to update")
        return {"status": "no data to update"}
    tmp, header = get_data_from_sheet(url)
    if not header:
        print("Sheet is empty, adding header")
        # Prepare header
        header = list(certificates[0].keys())
        print("Header is ", header)
        worksheet.append_row(header)

    # Prepare and append each certificate data
    for cert in certificates:
        row = list(cert.values())
        # row.append(False)
        print()
        print("row is ", row)
        print()
        worksheet.append_row(row)
    print("All certificates updated")
    return {"status": "success"}

# from utility import get_certificate_data
# with open("../saves.txt", "r", encoding="cp1252") as f:
    # all_cert_text = f.read()
# with open("saves2.txt", "r", encoding="utf-8") as f:
#     all_cert_text = f.read()
# print("All cert text length is ", len(all_cert_text))
# certificates = get_certificate_data(all_cert_text)
# status = update_sheet_with_certificates(url, certificates)
# print(status)
print(get_worksheet_from_url(url))