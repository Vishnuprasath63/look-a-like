"""
Django settings for lookalike project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_list_env(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-x7!k3m$r@q9z#f2&w5^t8n+p1j6c4v0y')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['*'] if DEBUG else get_list_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')

# CSRF checks require full origins including scheme.
CSRF_TRUSTED_ORIGINS = get_list_env('CSRF_TRUSTED_ORIGINS')
if not CSRF_TRUSTED_ORIGINS:
    if DEBUG:
        CSRF_TRUSTED_ORIGINS = [
            'http://localhost',
            'http://127.0.0.1',
        ]
    else:
        CSRF_TRUSTED_ORIGINS = [
            f'https://{host}' for host in ALLOWED_HOSTS
            if host not in {'localhost', '127.0.0.1', '*'}
        ]

# Trust HTTPS information from reverse proxies on hosted platforms.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'matcher',
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

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = ['https://.up.railway.app', 'http://.up.railway.app'] if not DEBUG else []

ROOT_URLCONF = 'lookalike.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'lookalike.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Add WhiteNoise for serving static files in production
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Auth redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/upload/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
