import os
import dotenv

DEBUG = False

dotenv.load_dotenv()
if DEBUG:
    BOT_TOKEN = os.getenv("DEBUG_BOT_TOKEN")
    DATABASE_CONNECT = os.getenv("DEBUG_DATABASE")
    CREDENTIALS_PATH = os.getenv("DEBUG_CREDENTIALS_PATH")
    SPREADSHEET_ID = os.getenv("DEBUG_SPREADSHEET_ID")
else:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_CONNECT = os.getenv("DATABASE_CONNECT")
    CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    
