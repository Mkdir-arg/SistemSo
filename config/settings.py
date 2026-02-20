# settings.py
import os
import sys
import logging
from pathlib import Path
from django.contrib.messages import constants as messages
from dotenv import load_dotenv

# --- Paths y .env (en este orden) ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --- Entorno ---
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "prd")  # dev|qa|prd

# --- Secret Key ---
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY debe estar configurada en .env")

# --- i18n/Timezone ---
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Hosts / CSRF ---
# Tomo del .env si existe; si no, fuerzo dominio de PythonAnywhere para evitar 400.
hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS", "")
hosts = [h.strip() for h in hosts_env.split(",") if h.strip()]
if "mlepera.pythonanywhere.com" not in hosts:
    hosts += ["mlepera.pythonanywhere.com"]
# en desarrollo, también localhost
if DEBUG:
    for h in ("localhost", "127.0.0.1"):
        if h not in hosts:
            hosts.append(h)

# Agregar nombres de servicios Docker para nginx
for h in ("sedronar-http", "sedronar-ws"):
    if h not in hosts:
        hosts.append(h)

ALLOWED_HOSTS = list(dict.fromkeys(hosts))  # sin duplicados

DEFAULT_SCHEME = "https" if ENVIRONMENT == "prd" else "http"

# CSRF_TRUSTED_ORIGINS requiere esquema. Para PA siempre https.
CSRF_TRUSTED_ORIGINS = [
    "https://mlepera.pythonanywhere.com",
    "http://54.172.163.63",
    "http://ec2-54-172-163-63.compute-1.amazonaws.com"
]
if DEBUG:
    CSRF_TRUSTED_ORIGINS += ["http://localhost", "http://127.0.0.1", "http://localhost:9000", "http://127.0.0.1:9000"]

# --- Apps ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    # Libs
    "django_extensions",
    "rest_framework",
    "channels",
    "django_redis",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "silk",  # Performance profiling
    # Apps propias
    "users",
    "core",
    "dashboard",
    "legajos",
    "configuracion",
    "chatbot",
    "conversaciones",
    "portal",
    "tramites",
    "healthcheck",
    "drf_spectacular",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Seguridad primero
    "core.middleware_concurrency.ConcurrencyLimitMiddleware",  # Limitar antes de medir
    "silk.middleware.SilkyMiddleware",  # Performance profiling
    "django.middleware.gzip.GZipMiddleware",
    "core.middleware_concurrency.RequestMetricsMiddleware",    # Métricas en tiempo real
    "core.monitoring.MonitoringMiddleware",  # Sistema de monitoreo avanzado
    "config.middlewares.performance.PerformanceMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "config.middlewares.xss_protection.XSSProtectionMiddleware",
    "config.middlewares.threadlocals.ThreadLocalMiddleware",
    # Nuevos middleware de auditoría
    "core.middleware_auditoria.AuditoriaMiddleware",
    "core.middleware_auditoria.AccesoSensibleMiddleware",
    "core.middleware_auditoria.DescargaArchivoMiddleware",
    "core.middleware_auditoria.SesionUsuarioMiddleware",
    "config.middlewares.query_counter.QueryCountMiddleware",
    # Middleware de redirección para usuarios institución
    "config.middlewares.institucion_redirect.InstitucionRedirectMiddleware",
]

# --- URLs / WSGI / ASGI ---
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "legajos.context_processors.alertas_eventos_criticos",
                "core.context_processors.dispositivos_context",
                "conversaciones.context_processors.user_groups",
            ],
        },
    },
]

# --- Static & Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files optimization
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

if ENVIRONMENT == "prd":
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# --- Auth / Redirects ---
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "login"
ACCOUNT_FORMS = {"login": "users.forms.UserLoginForm"}

# --- Email ---
if ENVIRONMENT == "prd":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- Mensajes ---
MESSAGE_TAGS = {
    messages.DEBUG: "bg-gray-800 text-white",
    messages.INFO: "bg-blue-500 text-white",
    messages.SUCCESS: "bg-green-500 text-white",
    messages.WARNING: "bg-yellow-500 text-white",
    messages.ERROR: "bg-red-500 text-white",
}

# --- DB ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            "isolation_level": "read committed",
            "autocommit": True,
            "connect_timeout": 10,
            "read_timeout": 10,
            "write_timeout": 10,
        },
        "CONN_MAX_AGE": 60,  # Reusar conexiones por 60 segundos
        "CONN_HEALTH_CHECKS": True,  # Verificar salud de conexión antes de reusar
    }
}

if "pytest" in sys.argv or os.environ.get("PYTEST_RUNNING") == "1":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# --- Cache ---
import ssl

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_SSL = os.environ.get("REDIS_SSL", "False") == "True"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{'rediss' if REDIS_SSL else 'redis'}://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 200,
                "ssl_cert_reqs": ssl.CERT_NONE if REDIS_SSL else None,
            },
        },
        "KEY_PREFIX": "sedronar",
        "TIMEOUT": 300,
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{'rediss' if REDIS_SSL else 'redis'}://{REDIS_HOST}:{REDIS_PORT}/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "ssl_cert_reqs": ssl.CERT_NONE if REDIS_SSL else None,
            },
        },
        "KEY_PREFIX": "session",
    }
}

# --- Sessions ---
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_AGE = 86400  # 24 horas

# --- Channels ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, int(REDIS_PORT))],
            "capacity": 1500,
            "expiry": 60,
        },
    },
}

# --- Health Check ---
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,     # in MB
}

# --- TTLs ---
DEFAULT_CACHE_TIMEOUT = 600  # Aumentado a 10 minutos
DASHBOARD_CACHE_TIMEOUT = 600
CIUDADANO_CACHE_TIMEOUT = 600

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# --- Integraciones ---
DOMINIO = os.environ.get("DOMINIO", "localhost:8001")
RENAPER_API_USERNAME = os.getenv("RENAPER_API_USERNAME")
RENAPER_API_PASSWORD = os.getenv("RENAPER_API_PASSWORD")
RENAPER_API_URL = os.getenv("RENAPER_API_URL")
RENAPER_TEST_MODE = os.getenv("RENAPER_TEST_MODE", "False") == "True"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_KEY", ""))
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_TIMEOUT_SECONDS = int(os.getenv("SUPABASE_TIMEOUT_SECONDS", "12"))

# --- Logging ---
LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "info_only": {"()": "django.utils.log.CallbackFilter", "callback": lambda r: r.levelno == logging.INFO},
        "error_only": {"()": "django.utils.log.CallbackFilter", "callback": lambda r: r.levelno == logging.ERROR},
        "warning_only": {"()": "django.utils.log.CallbackFilter", "callback": lambda r: r.levelno == logging.WARNING},
        "critical_only": {"()": "django.utils.log.CallbackFilter", "callback": lambda r: r.levelno == logging.CRITICAL},
        "data_only": {"()": "django.utils.log.CallbackFilter", "callback": lambda r: hasattr(r, "data")},
    },
    "formatters": {
        "verbose": {"format": "[{asctime}] {module} {levelname} {name}: {message}", "style": "{"},
        "simple": {"format": "[{asctime}] {levelname} {message}", "style": "{"},
        "json_data": {"()": "core.utils.JSONDataFormatter"},
    },
    "handlers": {
        "info_file": {"level": "INFO", "filters": ["info_only"], "class": "core.utils.DailyFileHandler", "filename": str(LOG_DIR / "info.log"), "formatter": "verbose"},
        "error_file": {"level": "ERROR", "filters": ["error_only"], "class": "core.utils.DailyFileHandler", "filename": str(LOG_DIR / "error.log"), "formatter": "verbose"},
        "warning_file": {"level": "WARNING", "filters": ["warning_only"], "class": "core.utils.DailyFileHandler", "filename": str(LOG_DIR / "warning.log"), "formatter": "verbose"},
        "critical_file": {"level": "CRITICAL", "filters": ["critical_only"], "class": "core.utils.DailyFileHandler", "filename": str(LOG_DIR / "critical.log"), "formatter": "verbose"},
        "data_file": {"level": "INFO", "filters": ["data_only"], "class": "core.utils.DailyFileHandler", "filename": str(LOG_DIR / "data.log"), "formatter": "json_data"},
    },
    "root": {"handlers": ["info_file", "error_file", "warning_file", "critical_file", "data_file"], "level": "DEBUG" if DEBUG else "INFO"},
    "loggers": {"django": {"handlers": [], "level": "DEBUG" if DEBUG else "INFO", "propagate": True}, "django.request": {"handlers": ["error_file"], "level": "ERROR", "propagate": False}},
}

# --- Password validators ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Debug tools ---
if DEBUG:
    INTERNAL_IPS = ["127.0.0.1", "::1"]

# --- Compresión Gzip ---
USE_GZIP = True
GZIP_CONTENT_TYPES = (
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/x-javascript',
    'text/xml',
    'text/plain',
    'text/html',
    'application/json',
)

# --- Silk Configuration ---
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_MAX_REQUEST_BODY_SIZE = 1024  # 1KB
SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # 1KB
SILKY_INTERCEPT_PERCENT = 100 if DEBUG else 10  # 100% en dev, 10% en prod

# --- Seguridad por entorno ---
if ENVIRONMENT == "prd":
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"  # Cambiado temporalmente
    SECURE_HSTS_SECONDS = 0  # Deshabilitado hasta configurar SSL
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_SSL_REDIRECT = False  # Deshabilitado hasta configurar SSL
    SESSION_COOKIE_SECURE = False  # Deshabilitado hasta configurar SSL
    CSRF_COOKIE_SECURE = False  # Deshabilitado hasta configurar SSL
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
# DRF Spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'SEDRONAR API',
    'DESCRIPTION': 'Sistema de Gestión SEDRONAR - Documentación de APIs',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}
