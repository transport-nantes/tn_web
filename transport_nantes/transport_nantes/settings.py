"""
Django settings for transport_nantes project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from django.urls import reverse_lazy
from . import settings_local
import sys
import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings_local.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG
ROLE = settings_local.ROLE
ADMIN = [
    ("Dev admins", "dev-admin@mobilitains.fr"),
]

ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS
# This is a list of trusted origins for CSRF protection.
# https://docs.djangoproject.com/en/4.1/ref/settings/#csrf-trusted-origins
# It defaults to an empty list, but you may add your own origins in dev
# using settings_local.py. This allows you to use ngrok or similar.
# Ngrok allows you to open a tunnel and make accessible your local dev branch
# through a browser, notably to make sure it displays well and works on
# your phone before even pushing to beta.
# It avoids too many pushes to beta that may affect the database and require
# a restore.
# see https://ngrok.com/ for usage.
if DEBUG and ROLE == "dev":
    CSRF_TRUSTED_ORIGINS = (
        getattr(settings_local, "CSRF_TRUSTED_ORIGINS", None) or []
    )

# Requirement for Django-debug-toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configure-internal-ips
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
# When running in dev from vagrant, we listen on all interfaces in
# order to port-forward through to the browser.
if DEBUG:
    INTERNAL_IPS = INTERNAL_IPS + ["0.0.0.0"]

# Application definition

INSTALLED_APPS = [
    "surveys.apps.SurveysConfig",
    "asso_tn.apps.AssoTnConfig",
    "mailing_list.apps.MailingListConfig",
    "velopolitain_observatoire.apps.VelopolitainObservatoireConfig",
    "clickcollect.apps.ClickCollectConfig",
    "authentication.apps.AuthenticationConfig",
    "topicblog.apps.TopicBlogConfig",
    "dashboard.apps.DashboardConfig",
    "utm.apps.UtmConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "captcha",
    "geoplan",
    "stripe_app",
    "crispy_forms",
    "django_countries",
    "press",
    "debug_toolbar",
    "photo",
    "mobilito",
    "compressor",
] + settings_local.MORE_INSTALLED_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "asso_tn.middleware.default_context.DefaultContextMiddleware",
    "asso_tn.middleware.sessionCookie.SessionCookieMiddleWare",
    "utm.middleware.utm.UtmMiddleware",
]

if ROLE in ("beta", "production"):
    MIDDLEWARE += [
        "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
    ]

ROOT_URLCONF = "transport_nantes.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "asso_tn.context_processors.role",
                "django.template.context_processors.media",
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = "bootstrap4"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = settings_local.DATABASES

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

password_validation_path = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            password_validation_path + "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": password_validation_path + "MinimumLengthValidator",
    },
    {
        "NAME": password_validation_path + "CommonPasswordValidator",
    },
    {
        "NAME": password_validation_path + "NumericPasswordValidator",
    },
]
PASSWORD_RESET_TIMEOUT_DAYS = 1

if "EMAIL_BACKEND" in settings_local.__dict__:
    EMAIL_BACKEND = settings_local.EMAIL_BACKEND
elif ROLE == "dev":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django_amazon_ses.EmailBackend"

AWS_ACCESS_KEY_ID = settings_local.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings_local.AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = settings_local.AWS_DEFAULT_REGION
AWS_SES_REGION_ENDPOINT_URL = "email.eu-central-1.amazonaws.com"
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
AWS_CONFIGURATION_SET_NAME = getattr(
    settings_local, "AWS_CONFIGURATION_SET_NAME", "placeholder123"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": (
                "[{asctime}] {levelname}[{filename}:{lineno} ({funcName})]"
                " {message}"
            ),
            "style": "{",
        },
        "django.ses.extra": {
            "()": "django.utils.log.ServerFormatter",
            "format": (
                "[{asctime}] {levelname}[{filename}:{lineno} ({funcName})]"
                " {message} Notification : {notification}"
            ),
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "INFO",
            # 'class': 'logging.handlers.TimedRotatingFileHandler',
            "class": "logging.FileHandler",
            "filename": settings_local.LOG_DIR + "tn_web.log",
            "formatter": "django.server",
            # 'when': 'd',
            # 'utc': True,
            # 'backupCount': 10,
        },
        "django_ses_notification": {
            "level": "INFO",
            # 'class': 'logging.handlers.TimedRotatingFileHandler',
            "class": "logging.FileHandler",
            "filename": settings_local.LOG_DIR + "tn_web-ses.log",
            "formatter": "django.ses.extra",
            # 'when': 'd',
            # 'utc': True,
            # 'backupCount': 10,
        },
        "gcp_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": settings_local.LOG_DIR + "gcp.log",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "app": {
            # 'handlers': ['console', 'mail_admins'],
            "handlers": ["django.server", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            # 'handlers': ['console', 'mail_admins'],
            "handlers": ["console", "file", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["django.server", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django_ses": {
            "handlers": ["console", "django_ses_notification", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "gcp": {
            "handlers": ["gcp_handler"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = False
USE_TZ = True
# TODO: stay on same page if authorised to do so.
LOGIN_REDIRECT_URL = "index"
LOGIN_URL = reverse_lazy("authentication:login")
# LOGOUT_REDIRECT_URL = 'index'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = settings_local.STATIC_URL
STATIC_ROOT = settings_local.STATIC_ROOT

# Prefix for uploaded files. Must be different from static_url
MEDIA_URL = settings_local.MEDIA_URL
# Directory where uploaded files are stored
MEDIA_ROOT = settings_local.MEDIA_ROOT

# Define this for nginx contexts.
if "STATIC_ROOT" in dir(settings_local):
    STATIC_ROOT = settings_local.STATIC_ROOT

# FileSystemFinder and AppDirectoriesFinder are enabled by default.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

CAPTCHA_NOISE_FUNCTIONS = ("captcha.helpers.noise_dots",)
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge"
CAPTCHA_LENGTH = 5

STRIPE_PUBLISHABLE_KEY = settings_local.STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY = settings_local.STRIPE_SECRET_KEY
STRIPE_ENDPOINT_SECRET = settings_local.STRIPE_ENDPOINT_SECRET

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Allows the captcha to pass in tests mode
# See doc :
# https://django-simple-captcha.readthedocs.io/en/latest/advanced.html#captcha-test-mode
if "test" in sys.argv and ROLE == "dev":
    CAPTCHA_TEST_MODE = True

CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = "amqp://localhost"

if ROLE in ("beta", "production"):
    ROLLBAR = {
        "access_token": settings_local.ROLLBAR_ACCESS_TOKEN,
        "environment": "dev" if DEBUG else "production",
        "root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    }
    import rollbar

    rollbar.init(**ROLLBAR)

MAPS_API_KEY = settings_local.MAPS_API_KEY
