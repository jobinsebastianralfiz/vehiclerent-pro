import os
from pathlib import Path

import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key-change-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# Railway sets RAILWAY_PUBLIC_DOMAIN
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if RAILWAY_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
if RAILWAY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_DOMAIN}")

INSTALLED_APPS = [
    "core",
    "vehicles",
    "customers",
    "allocations",
    "enquiries",
    "dashboard",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.AdminLoginRequiredMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
                "core.context_processors.whatsapp_config",
                "core.context_processors.admin_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database — Railway provides DATABASE_URL for PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Auth
AUTH_USER_MODEL = "core.AdminUser"
AUTHENTICATION_BACKENDS = ["core.backends.EmailBackend"]
LOGIN_URL = "/manage/login/"
LOGIN_REDIRECT_URL = "/manage/"
LOGOUT_REDIRECT_URL = "/manage/login/"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Static files — served by WhiteNoise
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files — Railway volume mount at /data/media
MEDIA_URL = "/media/"
RAILWAY_VOLUME_MOUNT = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "")
if RAILWAY_VOLUME_MOUNT:
    MEDIA_ROOT = os.path.join(RAILWAY_VOLUME_MOUNT, "media")
else:
    MEDIA_ROOT = BASE_DIR / "media"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Email
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("SMTP_HOST", default="")
EMAIL_PORT = config("SMTP_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("SMTP_USER", default="")
EMAIL_HOST_PASSWORD = config("SMTP_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config("FROM_EMAIL", default="noreply@example.com")
NOTIFICATION_EMAIL = config("NOTIFICATION_EMAIL", default="admin@example.com")

# WhatsApp
WHATSAPP_NUMBER = config("WHATSAPP_NUMBER", default="")
WHATSAPP_DEFAULT_MESSAGE = config(
    "WHATSAPP_DEFAULT_MESSAGE",
    default="Hi, I'm interested in renting a vehicle from your fleet.",
)

# Business info (fallback — primary source is SiteConfig in DB)
BUSINESS_NAME = config("BUSINESS_NAME", default="VehicleRent Pro")
BUSINESS_PHONE = config("BUSINESS_PHONE", default="")
BUSINESS_EMAIL = config("BUSINESS_EMAIL", default="")
BUSINESS_ADDRESS = config("BUSINESS_ADDRESS", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security (production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
