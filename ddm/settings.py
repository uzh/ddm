import os
import pytz
from dotenv import load_dotenv
from django.conf import settings

#load_dotenv()

SQ_TIMEZONE = pytz.timezone("Europe/Zurich")

ENCRYPTION_KEY = settings.SECRET_KEY #os.environ['ENCRYPTION_KEY']
