import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "DAT250 SecureApp")
APP_ENV = os.getenv("APP_ENV", "lab")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dat250:dat250@db:5432/dat250_secureapp")
SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET is not set. Define it in the .env file.")
MAILHOG_HOST = os.getenv("MAILHOG_HOST", "mailhog")
MAILHOG_PORT = int(os.getenv("MAILHOG_PORT", "1025"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:18181")
