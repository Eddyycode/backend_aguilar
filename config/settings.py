# config/settings.py
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-cambiar-en-produccion')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=lambda v: [s.strip() for s in v.split(',')])

# Agregar dominios de Vercel
if not DEBUG:
    ALLOWED_HOSTS.extend(['.vercel.app', '.now.sh'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'vehiculos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos
    'corsheaders.middleware.CorsMiddleware',  # IMPORTANTE: Antes de CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - SQLite para desarrollo, PostgreSQL para producción
# Usar DIRECT_URL para migraciones, DATABASE_URL para operaciones normales
DIRECT_URL = config('DIRECT_URL', default=None)
DATABASE_URL = config('DATABASE_URL', default=None)

# Priorizar DIRECT_URL si existe (mejor para migraciones)
db_url_string = DIRECT_URL or DATABASE_URL

if db_url_string:
    # Parsear la URL de la base de datos de Supabase
    from urllib.parse import urlparse
    db_url = urlparse(db_url_string)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_url.path[1:],  # Remover el '/' inicial
            'USER': db_url.username,
            'PASSWORD': db_url.password,
            'HOST': db_url.hostname,
            'PORT': db_url.port or 5432,
            'OPTIONS': {
                'sslmode': 'require',  # Supabase requiere SSL
            }
        },
        # Mantener SQLite disponible para migración de datos
        'sqlite': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # SQLite para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration - Permitir peticiones desde Flutter
# Para desarrollo, permitir todas las origenes
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://10.0.2.2:8000",  # Android emulator
# ]
CORS_ALLOW_CREDENTIALS = True



# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'vehiculos-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Máximo de entradas en caché
        },
        'TIMEOUT': 1800,  # Timeout por defecto: 30 minutos
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'vehiculos': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Configuración de drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Mantenimiento Vehicular',
    'DESCRIPTION': """
    API REST completa para gestión de vehículos, mantenimientos y talleres mecánicos.

    ## Características principales:

    * **Gestión de Vehículos**: CRUD completo con filtros avanzados
    * **Talleres Mecánicos**: Búsqueda por ubicación con geolocalización
    * **Mantenimientos**: Control de preventivos y correctivos con historial
    * **AWS Location Service**: Integración para mapas y geocodificación
    * **Filtros de Fecha**: Todos los endpoints de estadísticas soportan filtros por rango de fechas

    ## Filtros de fecha disponibles:

    Los siguientes endpoints aceptan parámetros `fecha_desde` y `fecha_hasta` (formato: YYYY-MM-DD):

    * `/api/mantenimientos/estadisticas/` - Estadísticas filtradas por fecha
    * `/api/vehiculos/estadisticas/` - Estadísticas de vehículos por fecha de registro
    * `/api/vehiculos/{id}/mantenimientos/` - Mantenimientos de un vehículo
    * `/api/talleres/{id}/mantenimientos/` - Mantenimientos de un taller

    ## Base URL:
    * Desarrollo: `http://127.0.0.1:8000/api/`
    * Producción: (configurar según tu dominio)
    """,
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'Equipo de Desarrollo',
        'email': 'dev@mantenimiento-vehicular.com'
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    'TAGS': [
        {'name': 'vehiculo', 'description': 'Operaciones CRUD para vehículos, estadísticas y actualización de kilometraje'},
        {'name': 'taller', 'description': 'Gestión de talleres mecánicos con búsqueda por ubicación'},
        {'name': 'mantenimiento', 'description': 'Control de mantenimientos preventivos y correctivos'},
        {'name': 'aws-maps', 'description': 'Integración con AWS Location Service para mapas y geocodificación'},
    ],
    # Configuración para mejor visualización en ReDoc
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVERS': [
        {'url': config('API_URL', default='https://tu-proyecto.vercel.app'), 'description': 'Servidor de Producción (Vercel)'},
        {'url': 'http://127.0.0.1:8000', 'description': 'Servidor de Desarrollo Local'},
        {'url': 'http://localhost:8000', 'description': 'Servidor Local Alternativo'},
    ],
    'EXTERNAL_DOCS': {
        'description': 'Documentación adicional del proyecto',
        'url': 'https://github.com/tu-usuario/tu-proyecto'
    },
    # Mejorar la generación de ejemplos
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}