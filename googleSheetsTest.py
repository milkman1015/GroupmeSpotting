import os

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1R8jyl4dru3OwQVcHkFE38DpxmvooNg0_F6Z7KrBv0oI"


def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheets = service.spreadsheets()

        for row in range(2, 9):
            num1 = int(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Sheet1!A{row}").execute().get("values")[0][0])
            num2 = int(sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=f"Sheet1!B{row}").execute().get("values")[0][0])
            calc_result = num1 + num2
            print(f"proccessing {num1} + {num2}")

            sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Sheet1!C{row}", valueInputOption="USER_ENTERED", body={"values": [[f"{calc_result}"]]}).execute()
            sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Sheet1!D{row}", valueInputOption="USER_ENTERED", body={"values": [["Done"]]}).execute()
    except HttpError as error:
        print(error)


if __name__ == "__main__":
    main()

