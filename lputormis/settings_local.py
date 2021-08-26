from dotenv import load_dotenv
import dj_database_url
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

load_dotenv()

NAME_DB = os.getenv('NAME_ORA')

if os.environ.get('DATABASE_URL', ''):
    DATABASES = {
        "default": dj_database_url.parse(os.environ["DATABASE_URL"]),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('NAME_PSQL'),
            'USER': os.getenv('USER_PSQL'),
            'PASSWORD': os.getenv('PASSWORD_PSQL'),
            'HOST': os.getenv('HOST_PSQL'),
            'PORT': os.getenv('PORT_PSQL')
        }
    }


DATABASES[NAME_DB] = {
    'ENGINE': 'django.db.backends.oracle',
    'NAME': os.getenv('NAME_ORA'),
    'USER': os.getenv('USER_ORA'),
    'PASSWORD': os.getenv('PASSWORD_ORA'),
    'HOST': os.getenv('HOST_ORA'),
    'PORT': os.getenv('PORT_ORA'),

}


EXCHANGE_SERVICE = {
    "name": "Сервис выгрузки в ИСМЛП талонов на молочное питание",
    "srv_rid": 37,
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

TIME_ZONE = 'Europe/Moscow'

# CELERY SETTINGS
CELERY_BROKER_URL = os.getenv('BROKER_URL')
CELERY_TIMEZONE = 'Europe/Moscow'

#WSDL
WSDL = os.getenv('WSDL')