from ..base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pemilu2019',
        'USER': 'root',
        # 'PASSWORD': os.environ['MYSQL_PASSWORD'],
        'PASSWORD': 'mysql123',
        # 'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'HOST': '35.187.254.66',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

