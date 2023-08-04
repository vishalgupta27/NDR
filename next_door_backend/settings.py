"""
Django settings for next_door_backend project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-31v7ylh*irc+og!6)pi89*z41!i#)iz-(9^l^=xc#l=9&wq5(p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django_crontab',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.staticfiles'
    # https://stackoverflow.com/questions/2878490/how-to-delete-old-image-when-update-imagefield,
    'django_cleanup.apps.CleanupConfig',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'accounts',
    'products',
    'payments',
    'chat',
    'login_portal',
    'fcm_django',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'next_door_backend.urls'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

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
            ],
        },
    },
]

WSGI_APPLICATION = 'next_door_backend.wsgi.application'

CRONJOBS = [
    ('*/2 * * * *', 'products.cron.TestCronJob')
]

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ndr',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

FIREBASE_CREDENTIALS = {
  "type": "service_account",
  "project_id": "next-door-renal",
  "private_key_id": "72f71c88a3618766909f9f261477af7c7d5dc842",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCOW0mg7j6GiySc\nm3vcc8DbkGqkG51EYdLRPZBGx92aYgs/6lptqyrKWlJk1k1k43U8S+dZERTK3boq\nz8vZBncd8MWlvwKcaMfFuBe/fo+ibK/NOjpJHA9rJxLOAyRteoRbcrI5YEqP8clI\nuQ7ilU1r+oRtVKDcvBSoTvgDpBe02d6gCthGlQ2JgIWIT9FL5ye4i0kpFkvOubeg\nwVu4wV1vjE3XVOKbRI7rbiA2c0fEJ89emMZCNLX1CBXid9jC7eSyqQcX46R0g7kc\nm9bphZvGolLTsjDsNnezOXvo8Uql0sT+WrcDDY3TLSuEGL6WuAEgwovu/rdqxsT0\nGnHGQCNnAgMBAAECggEABf1eUDimBdg17qb2I7T1IOfnLMeCqv1otugduXSwZM4K\nRiKwsluY3dHGFLsVn5CYfrR84/j9hHmm2yVKIPQOMALQ9iPe0sDv4uhXi3WiSoXD\nMeHo0Omu1mXa+zMTpc2ZYxWk3Rgpmvvj6bzrnOoGS2xLhSQh7pe1UM2dzt1pJ/FQ\nwuC4+DOaar5Rp5Bm+m3qolaTCEplEwH1rhq24PZgRrABfahxDPzqTWfqwn961Uwy\nxeQ321ox8dnJNqZh7JCwdL08iEuUpyJdHAS1Z9VjU9kJuo2w243hvjjzG1VMgJ46\nbtNgtosLtOmKGzKwQzzcDFWC2phSEDXU0eZ32wO0cQKBgQDF/FF/wuZq7Gev/bRz\nRIYgUvUC2PzIZXCa68/Er5Lj5X4oLmpP9Yw/5wEeU8Pi7lk7RE+zJfhuN1eWush2\nXQJegYg3THKSKTX2X1deJQw0a8IIIyZShZAu0o6l46xsE2jsHYjGDbQ1N4BwwSgB\nWvrVCA8vhaDgZT32NCszNcPG1wKBgQC4EgRHq9/IImPbQwYUkDtI0uJSHaYszYAx\nosHferLK87mOLg1GV146p/BnXXDWQdIZjG4j6Em20Sn4CSHwcdbRxLjmrR6i6lVN\n6fxYCcv3yeBI3u0f4A8eBfhfEbfRWasPmdz8Pto6ZLEjOnELaNjD0l7ceKsot0gw\nlEYpxTZF8QKBgAM901PFLCKaBkSSYc71U0DaOtq2FMVvK73NmJQ+z6fdjQg5YlI2\n0foF3TXS50Ui4+EdiDSFraCYVV3JZxjRAwXrFwDYxpNwC0siWnrXHnEJRp79fFYj\ni63Ikr9Sj/MhCjm7bg7YEJhCdV7jOrVy+OJeBGmhxXWHEtGiHwbynWb3AoGAIQQC\nRoS6l+ArPwnPjmKsb4x70bTFuKWHh9+knJwac7KxpqH1+Zb0LNswkKm+8n9N2w1I\nOCKTDjqIJ5gjwUf5+xgo/h8xLpGPiXEdtQDU1/Yax5dMuvnqXD0/5nV8Hg3SU/MK\nIyh25iBncWUrH5vHvZ//KdZvBNeTGDuQNi/MY1ECgYAXBs3kToB+JN8yQ08dtS/v\nMYRJp6g84towUlg2jeWJxKm5/QWgryBiEfeHkCANrgHBCsuNIMFPhamm5XSU9Mfc\n5LjvM5eb0OZSxZXK6f4TEDgcvcXueEnqwy29CQi7UdzghczWACpMO7d2r0yAnKgE\npYy+7uQwtWk6D9a7/fzhcg==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-g36xf@next-door-renal.iam.gserviceaccount.com",
  "client_id": "109397714675176080302",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-g36xf%40next-door-renal.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
MAILER_EMAIL_BACKEND = EMAIL_BACKEND
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'ccslilhyptuysdku'
EMAIL_HOST_USER = 'anand.augurstech@gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static/"),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    "EXCEPTION_HANDLER": "accounts.utils.custom_exception_handler",  #
    "DATE_INPUT_FORMATS": ["%d-%m-%Y"],

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    # 'USER_ID_FIELD': 'id',
    'USER_ID_FIELD': 'account_id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'anand.augurstech@gmail.com'
EMAIL_HOST_PASSWORD = 'ccslilhyptuysdku'
EMAIL_USE_TLS = True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.privateemail.com'
# EMAIL_PORT = '465'
# EMAIL_HOST_USER = 'support@nextdoorrental.ca'
# EMAIL_HOST_PASSWORD = '1D4h7k9!#%'
# EMAIL_USE_TLS = True


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

APP_SCHEME = "ndr:/"

# Django FCM Token Send Firebase Notifications
FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "AAAAX3RjOd4:APA91bFJfTNa0N5VLJtS7ZSh6MXFjvbyaI7Hl8adhCkVFmnCYpetILz6GmwZ7RvZC7xbo7d8FDwDZ53D4uYGT5xkcif119MS2RXOx4FjdW2RqKi9P_ibCvq0BTRNCXUGfZuAp2XjezdH"
}

# Stripe Keys
# STRIPE_PUBLISHABLE_KEY = 'pk_live_51LhCxIGV1VIVQNOZGjKa6mL3DPnvOwRsOAYGNDnNEVCFpGbA1YgnhGncYamThqCe0OaGhv8rszk7hGuKGWD8MScg00nUFglIDo'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51LhCxIGV1VIVQNOZVNC5h1Aw0Dk4N2TUPv7zvR3DhviWyjsGzo4yMsIdshjw32o5Dvv532Wsj1uEaltlvgZd2GNp00D74MIqoe'
# STRIPE_SECRET_KEY = ''
STRIPE_SECRET_KEY = 'sk_test_51LhCxIGV1VIVQNOZ4Nnzf9q6UEKDtNjRPEClzX32CKO34nes74VHxm7a9AO4k7wumKuQSma8cL3ZvgGNuv4P1XF100iI81kAIt'
STRIPE_CONNECT_CLIENT_ID = "ca_MdqRokN7luLTBkDg98GiXZhhxGs0NuNT"
# This is your Stripe CLI webhook secret for testing your endpoint locally.
WEBHOOK_ENDPOINT_SECRET = 'whsec_05ac0be16091894dbd56542b1686faf12b6b338516595b12a4cd4bab836c9d78'

# Xero Accounting Keys
XERO_CLIENT_ID = "9F801E1DE2FE42A88330D5DBE80F0692"
XERO_CLIENT_SECRET = "XsrSRBuNuqUJKqb1-56hZIW6hc29NIO7GxafbsLzF6diAQtF"
