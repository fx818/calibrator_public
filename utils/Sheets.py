import gspread
from google.oauth2.service_account import Credentials


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

url = "https://docs.google.com/spreadsheets/d/1KhAt3I4Tb0ZtdSpmFlp8DiL6Nr-ps2MIdKGawmB-ZLE/edit?usp=sharing"

def update_sheet_with_certificates(url, certificates):
    worksheet = get_worksheet_from_url(url)
    if not certificates:
        return {"status": "no data to update"}
    tmp = get_data_from_sheet(url)
    if not tmp:
    # Prepare header
        header = list(certificates[0].keys())
        header.append("Verified")
        print("Header is ", header)
        worksheet.append_row(header)

    # Prepare and append each certificate data
    for cert in certificates:
        row = list(cert.values())
        row.append(False)
        print()
        print("row is ", row)
        print()
        worksheet.append_row(row)
    
    return {"status": "success"}

from utility import get_certificate_data
with open("../saves.txt", "r", encoding="cp1252") as f:
    all_cert_text = f.read()
# with open("saves2.txt", "r", encoding="utf-8") as f:
#     all_cert_text = f.read()
print("All cert text length is ", len(all_cert_text))
certificates = get_certificate_data(all_cert_text)
status = update_sheet_with_certificates(url, certificates)
print(status)