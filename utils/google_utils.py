import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
import json

JSON_PARAMS = ["type", "project_id", "private_key_id", "private_key", "client_email", "client_id", "auth_uri",
               "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url"]


def create_gspread_client() -> gspread.Client:
    """
    Create the client to be able to access google drive (sheets)
    """
    # Scope of what we can do in google drive
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    # Write the credentials file if we don't have it
    if not os.path.exists('client_secret.json'):
        json_creds = dict()
        for param in JSON_PARAMS:
            json_creds[param] = os.getenv(param).replace('\"', '').replace('\\n', '\n')
        with open('../client_secret.json', 'w') as f:
            json.dump(json_creds, f)
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
    return gspread.authorize(creds)


def get_next_row(sheet: gspread.Worksheet) -> int:
    """Get the next empty row index
    :param sheet: (gspread.Worksheet) the sheet
    :return idx: the index"""

    for idx, row in reversed(list(enumerate(sheet.get_all_values()))):
        print(row)
        if row[0] == "":
            continue
        else:
            break
    return idx + 2