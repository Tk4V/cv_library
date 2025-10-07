from .base import *  # noqa

DEBUG = False

# Ensure SECRET_KEY, ALLOWED_HOSTS are provided via env in production.
# Override ALLOWED_HOSTS for production security
if ALLOWED_HOSTS == ['*'] or '*' in ALLOWED_HOSTS:
    # Replace wildcard with specific hosts for security
    ALLOWED_HOSTS = [
        'jellyfish-app-9xfdb.ondigitalocean.app',
        '*.ondigitalocean.app',
        'localhost',  # For local testing
        '127.0.0.1',  # For local testing
    ]

# Static files configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Explicitly disable Silk profiling in production to prevent worker crashes
# (Base settings will handle dev/prod logic, but being explicit here)
SILKY_PYTHON_PROFILER = False
SILKY_META = False
SILKY_AUTHENTICATION = False
SILKY_AUTHORISATION = False
SILKY_PERMISSIONS = lambda user: False

# CSRF settings for production (balanced security)
CSRF_TRUSTED_ORIGINS = [
    'https://jellyfish-app-9xfdb.ondigitalocean.app',
    'https://*.ondigitalocean.app',
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Allow Swagger UI to work
CSRF_COOKIE_SAMESITE = 'Lax'

# Security settings for production (balanced)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow iframes for Swagger
SECURE_SSL_REDIRECT = False  # DigitalOcean handles SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database configuration for production - PostgreSQL with fallback
import os
import dj_database_url

# Debug: Log all environment variables that start with POSTGRES
postgres_vars = {k: v for k, v in os.environ.items() if k.startswith('POSTGRES')}
print(f"DEBUG: Available POSTGRES environment variables: {postgres_vars}")

# Try to get DATABASE_URL first, if not available construct it
DATABASE_URL = env('DATABASE_URL', default='')
if not DATABASE_URL:
    # Construct DATABASE_URL from individual variables
    db_name = env('POSTGRES_DB', default='cvdb')
    db_user = env('POSTGRES_USER', default='cvuser')
    db_password = env('POSTGRES_PASSWORD', default='cvpass')
    db_host = env('POSTGRES_HOST', default='localhost')
    db_port = env('POSTGRES_PORT', default='5432')
    
    # Construct DATABASE_URL
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"
    print(f"DEBUG: Constructed DATABASE_URL: {DATABASE_URL}")

try:
    # Try to parse and use PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    print("DEBUG: Using PostgreSQL database")
except Exception as e:
    print(f"DEBUG: PostgreSQL connection failed: {e}")
    print("DEBUG: Falling back to SQLite")
    # Fallback to SQLite if PostgreSQL fails
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Log database configuration for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Database configured: {DATABASES['default']['ENGINE']}")

# Redis configuration for DigitalOcean App Platform
# DigitalOcean provides Redis connection details via environment variables
REDIS_URL = env('REDIS_URL', default='')
if REDIS_URL:
    # Use the provided Redis URL from DigitalOcean
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = 'django-db'  # Use database instead of Redis for now
    print(f"Using DigitalOcean Redis: {REDIS_URL}")
else:
    # Fallback to individual Redis environment variables
    redis_host = env('REDIS_HOST', default='localhost')
    redis_port = env('REDIS_PORT', default='6379')
    redis_password = env('REDIS_PASSWORD', default='')
    redis_db = env('REDIS_DB', default='0')
    
    if redis_password:
        CELERY_BROKER_URL = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        CELERY_RESULT_BACKEND = 'django-db'  # Use database instead of Redis for now
    else:
        CELERY_BROKER_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"
        CELERY_RESULT_BACKEND = 'django-db'  # Use database instead of Redis for now
    
    print(f"Using constructed Redis: {CELERY_BROKER_URL}")

# Additional Redis configuration for production
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# Ensure Celery variables are available for other parts of the application
# These variables are set above based on environment variables

# Redis connection settings to prevent "Connection closed by server" errors
CELERY_BROKER_POOL_LIMIT = 1  # Reduce pool size
CELERY_BROKER_HEARTBEAT = 60  # Increase heartbeat
CELERY_BROKER_CONNECTION_TIMEOUT = 60  # Increase timeout
CELERY_BROKER_CONNECTION_RETRY_DELAY = 2.0  # Increase retry delay

# Additional Redis settings for stability
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 5
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Result backend settings
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'retry_policy': {
        'timeout': 5.0,
        'max_retries': 3,
    },
    'connection_pool_kwargs': {
        'max_connections': 10,
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {},
    }
}

# OpenAI configuration for production
OPENAI_API_KEY = env('OPENAI_API_KEY', default=None)
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o-mini')
OPENAI_PROJECT = env('OPENAI_PROJECT', default=None)

# Validate OpenAI configuration
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. AI features will not work.")
    logger.warning("OPENAI_API_KEY not configured")
else:
    print(f"OpenAI configured with model: {OPENAI_MODEL}")
    logger.info(f"OpenAI configured with model: {OPENAI_MODEL}")

logger.info(f"Database host: {DATABASES['default'].get('HOST', 'N/A')}")

# Comprehensive debugging for login redirect issues
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'django.contrib.sessions': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'django.contrib.auth': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'main': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

# Session settings for production (balanced)
# Using database sessions with SQLite
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = False  # Allow Swagger UI to work
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True  # Ensure session persistence
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = None  # Use default domain

# Production middleware configuration (Silk disabled to prevent worker crashes)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'main.middleware.RequestLoggingMiddleware',  # Temporarily disabled
    # 'main.middleware.auth_debug.AuthDebugMiddleware',  # Debug auth issues
]

