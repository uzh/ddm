import json
import os
import sys


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DDM_DIR = os.path.join(PROJECT_DIR, 'ddm')
VUE_FRONTEND_DIR = os.path.join(PROJECT_DIR, 'frontend')

sys.path.append(PROJECT_DIR)
sys.path.append(DDM_DIR)

test_config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config.json')))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'ddm',
    'ddm.auth',
    'ddm.logging',
    'ddm.questionnaire',
    'ddm.datadonation',
    'ddm.participation',
    'ddm.projects',
    'ddm.core',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'django_ckeditor_5',
    # 'debug_toolbar',  # Added for debugging purposes
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Added for debugging purposes
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'ddm.core.context_processors.add_ddm_version'
            ],
        },
    },
]

DB_CONFIG = {
    'default': {
        'ENGINE': test_config['DB_ENGINE'],
        'NAME': test_config['DB_NAME'],
    }
}

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ROOT_URLCONF = 'urls'
DATABASES = DB_CONFIG
DEBUG = True
SECRET_KEY = test_config['SECRET_KEY']
SITE_ID = 1
USE_TZ = True
TIME_ZONE = 'Europe/Zurich'
LANGUAGE_CODE = 'en'
USE_I18N = True
LANGUAGES = [
    ('en', 'English'),
    ('de', 'Deutsch')
]

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'test_project', 'static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'test_project', 'media')

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'core/vue/',
        'STATS_FILE': os.path.join(DDM_DIR, 'core', 'static', 'core', 'vue', 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK': r'.*(\.|@)uzh\.ch$',
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LOGIN_REDIRECT_URL = '/projects/'
LOGOUT_REDIRECT_URL = '/login/'

DDM_DEFAULT_HEADER_IMG_LEFT = '/media/project_10/headers/DDLabLogo.png'
DDM_DEFAULT_HEADER_IMG_RIGHT = '/media/project_10/headers/IKMZ_Logo.png'

# INTERNAL_IPS = ["127.0.0.1", ]  # Added for debugging purposes


# ckeditor 5 configuration
CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'authenticated'
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png', 'mp4']
