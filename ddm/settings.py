import os
import pytz
from dotenv import load_dotenv
from django.conf import settings

#load_dotenv()

SQ_TIMEZONE = pytz.timezone("Europe/Zurich")

ENCRYPTION_KEY = settings.SECRET_KEY #os.environ['ENCRYPTION_KEY']

# VUE_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'vue_frontend')
# print(VUE_FRONTEND_DIR)
#
# WEBPACK_LOADER = {
#     'DEFAULT': {
#         'CACHE': not settings.DEBUG,
#         'BUNDLE_DIR_NAME': 'vue/',  # must end with slash
#         'STATS_FILE': os.path.join(VUE_FRONTEND_DIR, 'webpack-stats.json'),
#         'POLL_INTERVAL': 0.1,
#         'TIMEOUT': None,
#         'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
#     }
# }
