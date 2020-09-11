from dotenv import load_dotenv
import os

load_dotenv()

SPREAD_ID = os.getenv("SPREAD_ID")
CRED_PATH = os.getenv("CRED_PATH")

MONGO_URL = os.getenv("MONGO_URL")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")

MAINGUN_API = os.getenv("MAINGUN_API")
MAILGUN_BASEURL = os.getenv("MAILGUN_BASEURL")
MAINGUN_DOMAIN = os.getenv("MAINGUN_DOMAIN")
MAILGUN_TO = os.getenv("MAILGUN_TO")
