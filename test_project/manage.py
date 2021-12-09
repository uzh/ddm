#!/usr/bin/env python

import django
import json
import sys

from django.conf import settings
from django.core.management import execute_from_command_line

# Import local test settings.
test_config = json.load(open('test_config.json'))

sys.path.append('..')

settings.configure(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'sekizai',
        'ddm.apps.DdmConfig'
    ],
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
    ],
    TEMPLATES=[
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
                    'sekizai.context_processors.sekizai',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                ],
            },
        },
    ],
    ALLOWED_HOSTS=['localhost', '127.0.0.1'],
    ROOT_URLCONF='urls',
    DATABASES={
        'default': {
            'ENGINE': test_config['DB_ENGINE'],
            'NAME': test_config['DB_NAME'],
            'USER': test_config['DB_USER'],
            'PASSWORD': test_config['DB_PASSWORD'],
            'HOST': test_config['DB_HOST'],
            'PORT': test_config['DB_PORT'],
        }
    },
    DEBUG=True,
    SECRET_KEY=test_config['SECRET_KEY'],
    SITE_ID=1,
    STATIC_URL='/static/'
)

django.setup()

execute_from_command_line(sys.argv)
