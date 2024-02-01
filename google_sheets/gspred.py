import gspread
from icecream import ic

from config.settings import CREDENTIALS_PATH, SPREADSHEET_ID

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/"+SPREADSHEET_ID

class GoogleSheets:
    def __init__(self):
        self._gc = gspread.service_account(filename=CREDENTIALS_PATH)
        self._sh = self._gc.open_by_key(SPREADSHEET_ID)
        self.wks = self._sh.get_worksheet(0)

    def count_column_values(self):
        return self.wks.row_count-1
    

gs = GoogleSheets()




