from datetime import timedelta
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY')

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

# Comma-separated environment variables keep deployment-specific addresses out
# of source code. Never use '*' here: it makes Host-header attacks possible.
ALLOWED_HOSTS = [host.strip() for host in config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'axes',
    'core',
    'accounts',
    'households',
    'evacuation_centers',
    'announcements',
    'maps',
    'reports',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.security.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        # PostgreSQL verifies encrypted connections in production when the
        # deployment supplies sslmode=verify-full (and a CA certificate, if
        # required by the provider). "prefer" keeps local development simple.
        'OPTIONS': {'sslmode': config('DB_SSLMODE', default='prefer')},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173').split(',')
    if origin.strip()
]
# Authentication is sent in an Authorization header, not a cross-site cookie.
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = ['accept', 'authorization', 'content-type', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with']
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config('CSRF_TRUSTED_ORIGINS', default='http://localhost:5173').split(',')
    if origin.strip()
]

# Browser and transport protections. SSL redirect/HSTS are deliberately
# disabled for local HTTP development but enabled by default in production.
SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
if config('DJANGO_BEHIND_HTTPS_PROXY', default=False, cast=bool):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31_536_000 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_SSL_REDIRECT
SECURE_HSTS_PRELOAD = SECURE_SSL_REDIRECT
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SAMESITE = 'Strict'

# Reject unexpectedly large request bodies before they consume server memory.
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # must be first
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        # django-axes is the stricter credential-stuffing defence; this is an
        # additional per-IP burst limit that also protects the login endpoint.
        'login': '10/minute',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',
    'UPDATE_LAST_LOGIN': True,
}

# django-axes: lock an account/IP after 3 failed login attempts, 1-minute cooldown.
# Field personnel (Kagawad/Tanod) may need urgent access during an active
# disaster, so we do NOT rely on cooldown alone — an admin can unlock early
# via `python manage.py axes_reset` or the Django admin's "Access attempts" panel.
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 3
# django-axes 8.x reads AXES_COOLOFF_TIME (not AXES_COOLDOWN_TIME).
# A nested list uses the username/IP combination as the lockout key; a flat
# list creates separate username-only and IP-only lockout keys.
AXES_COOLOFF_TIME = timedelta(minutes=1)
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False

# Do not leak passwords, access tokens, or API keys in Django error emails.
DEFAULT_EXCEPTION_REPORTER_FILTER = 'django.views.debug.SafeExceptionReporterFilter'

# SMS gateway (Semaphore — semaphore.co). SMS_DRY_RUN defaults to True so the
# app is safe to run with no credentials at all — nothing gets sent, nothing
# gets spent, until this is explicitly set to False in .env once real
# credentials exist. Switching to live sending is then just an env var
# change, not a code change.
SMS_DRY_RUN = config('SMS_DRY_RUN', default=True, cast=bool)
SEMAPHORE_API_KEY = config('SEMAPHORE_API_KEY', default='')
