import environ
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# django-environ
env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
env.read_env(env_file)

DEBUG = env.bool('DEBUG', True)
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# DB
DEV_DB_NAME = env('DEV_DB_NAME', default=None)
DEV_DB_USER = env('DEV_DB_USER', default=None)
DEV_DB_PASSWORD = env('DEV_DB_PASSWORD', default=None)
DEV_DB_HOST = env('DEV_DB_HOST', default=None)
DEV_DB_PORT = env.int('DEV_DB_PORT', default=None)

# Redis
USE_CACHE = env.bool('USE_CACHE', False)
REDIS_URL = env('REDIS_URL', default=None)

# Misc
BASE_URL = env('BASE_URL')
DEFAULT_HASH_LENGTH = env.int('DEFAULT_HASH_LENGTH', 6)
USE_CAPTCHA = env.bool('USE_CAPTCHA', True)
RESULTS_PER_PAGE = env.int('RESULTS_PER_PAGE', 10)

AUTH_USER_MODEL = 'users.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Added, needed in development only
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Added

    ## Third-party apps
    'django_extensions',
    'captcha',
    'tailwind',
    'fontawesomefree',
    'django_user_agents',
    'qr_code',
    'django_hosts',

    ## My apps
    'users',
    'home',
    'shorten',
    'theme',  # For django-tailwind

]

if DEBUG:
    INSTALLED_APPS.append('django_browser_reload')

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',  # for django_hosts
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # for whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',  # for django_hosts
]

if DEBUG:
    # For django_browser_reload
    MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')

ROOT_URLCONF = 'urlshortener.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', ],
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

WSGI_APPLICATION = 'urlshortener.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# DATABASES = {
# 	'default': {
# 		'ENGINE': 'django.db.backends.postgresql',
# 		'NAME': DEV_DB_NAME,
# 		'USER': DEV_DB_USER,
# 		'PASSWORD': DEV_DB_PASSWORD,
# 		'HOST': DEV_DB_HOST,
# 		'PORT': DEV_DB_PORT,
# 	}
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SESSION_COOKIE_AGE = 9.461 * (10 ** 7)  # 3yrs. (default is 1209600 - 2weeks)

if USE_CACHE:
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

    # Caching (https://github.com/jazzband/django-redis,
    # https://docs.djangoproject.com/en/3.2/topics/cache/)
    CACHES = {
        'default': {
            'TIMEOUT': 43200,  # Default is 300(seconds)
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# CACHES = {
# 	'default': {
# 		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
# 		'LOCATION': 'cache_table',
# 	}
# }
# python manage.py createcachetable --dry-run

# CACHES = {
# 	'default': {
# 		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
# 		'TIMEOUT': 300,  # The default(300s = 5mins)
# 		# 'TIMEOUT': 60 * 60 * 24,  # 86400(s)=24h
# 	}
# }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## THIRD-PARTY APP SETTINGS
# geoip2
GEOIP_PATH = BASE_DIR / 'geoip_db'

# django-tailwind
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ALLOWED_HOSTS

# django-hosts
ROOT_HOSTCONF = 'urlshortener.hosts'
DEFAULT_HOST = 'www'

# django-qr-code
if USE_CACHE:
    QR_CODE_CACHE_ALIAS = 'default'
