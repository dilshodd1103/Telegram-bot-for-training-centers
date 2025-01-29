from dotenv import load_dotenv
import os

load_dotenv()

ADMINS = os.getenv('ADMINS', '')
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')

if not ADMINS or not BOT_TOKEN or not API_ID or not API_HASH:
    raise ValueError("Missing essential environment variables!")

try:
    ADMINS = [int(admin) for admin in ADMINS.split(',')]
except ValueError:
    raise ValueError("ADMINS must contain only integer IDs.")

print("Environment variables loaded successfully!")
