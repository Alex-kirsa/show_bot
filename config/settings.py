import os
import dotenv

DEBUG = True

dotenv.load_dotenv()
if DEBUG:
    BOT_TOKEN = os.getenv("DEBUG_TOKEN")
    DATABASE_CONNECT = os.getenv("DEBUG_DATABASE")
else:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_CONNECT = os.getenv("DATABASE_CONNECT")
    