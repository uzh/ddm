import os
import pytz
from dotenv import load_dotenv

load_dotenv()

SQ_TIMEZONE = pytz.timezone("Europe/Zurich")

ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']
