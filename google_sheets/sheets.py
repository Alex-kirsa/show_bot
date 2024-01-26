from googleapiclient.discovery import build
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import SPREADSHEET_ID


class GoogleSheets:
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name("config/cred.json", scopes).authorize(httplib2.Http())
    service = build('sheets', 'v4', http=creds_service)
    sheet = service.spreadsheets()

    def rewrite_sheet(self, val: list):
        self.service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range="Лист1!A2:Z1000").execute()

        self.sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Лист1!A2",
            valueInputOption="RAW",
            # insertDataOption="INSERT_ROWS",
            body={'values': val}).execute()

    def read_sheet(self):
        resp = self.sheet.values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=["Лист1"]).execute()
        return [x for x in resp["valueRanges"][0]["values"]][1:]

    def write_receipt(self, val):
        self.sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Оплаты",
            valueInputOption="RAW",
            # insertDataOption="INSERT_ROWS",
            body={'values': val}).execute()

gs = GoogleSheets()