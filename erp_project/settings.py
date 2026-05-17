from pathlib import Path
import os
import oracledb

# Load .env file if it exists
_env_path = Path(__file__).resolve().parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Enable python-oracledb thick mode for Oracle 12c compatibility
# Requires Oracle Instant Client. Set ORACLE_CLIENT_DIR to your Instant Client path.
# If you want thin mode (no Instant Client), comment out the line below.
ORACLE_CLIENT_DIR = os.environ.get('ORACLE_CLIENT_DIR', None)
if ORACLE_CLIENT_DIR:
    oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#q2tdm7+pa9psv#^=*d(91gts%p_zrye%ckdefy@pen)o8tnbm'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'rest_framework',
    # ERP modules
    'core',
    'accounts',
    'hr',
    'inventory',
    'finance',
    'sales',
    'purchasing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.OracleAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'erp_project.urls'

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

WSGI_APPLICATION = 'erp_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'erp_project.oracle_compat',
        'NAME': os.environ.get('ORACLE_DB_NAME', 'ORCL'),        # Service name or SID (e.g. ORCL, XEPDB1)
        'USER': os.environ.get('ORACLE_DB_USER', 'erp_user'),    # Oracle schema/user
        'PASSWORD': os.environ.get('ORACLE_DB_PASSWORD', ''),    # Password
        'HOST': os.environ.get('ORACLE_DB_HOST', 'localhost'),   # Oracle server host/IP
        'PORT': os.environ.get('ORACLE_DB_PORT', '1521'),        # Default Oracle port
        'OPTIONS': {},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Oracle works best with AutoField (uses Oracle SEQUENCES under the hood)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # kept for /admin/ only
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

SESSION_COOKIE_AGE = 600          # 10 minutes
SESSION_SAVE_EVERY_REQUEST = True  # reset timer on every request
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False      # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Settings
CSRF_COOKIE_HTTPONLY = False       # Must be False so JS can read it for forms
CSRF_COOKIE_SECURE = False         # Set to True in production with HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['http://localhost:9001', 'http://127.0.0.1:9001']

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'accounts.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
