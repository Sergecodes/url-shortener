from decouple import config, Csv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
SECRET_KEY = config('SECRET_KEY')

# DB
USE_PROD_DB = config('USE_PROD_DB', default=False, cast=bool)
DEV_DB_NAME = config('DEV_DB_NAME')
DEV_DB_USER = config('DEV_DB_USER')
DEV_DB_PASSWORD = config('DEV_DB_PASSWORD')
DEV_DB_HOST = config('DEV_DB_HOST')
DEV_DB_PORT = config('DEV_DB_PORT')

# Redis
USE_PROD_REDIS = config('USE_PROD_REDIS', default=False, cast=bool)
DEV_REDIS_URL = config('DEV_REDIS_URL')


AUTH_USER_MODEL = 'users.User'


# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	## Third-party apps
	'django_extensions',

	## My apps
	'users',
	'shorten',
	
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	# 'django_hosts.middleware.HostsRequestMiddleware',  # for django_hosts
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	# 'django_hosts.middleware.HostsResponseMiddleware',  # for django_hosts
]

ROOT_URLCONF = 'urlshortener.urls'

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

WSGI_APPLICATION = 'urlshortener.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if USE_PROD_DB:
	pass
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
			'NAME': DEV_DB_NAME,
			'USER': DEV_DB_USER,
			'PASSWORD': DEV_DB_PASSWORD,
			'HOST': DEV_DB_HOST,
			'PORT': DEV_DB_PORT,
		}
	}


SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Caching (https://github.com/jazzband/django-redis, 
# https://docs.djangoproject.com/en/3.2/topics/cache/)
if USE_PROD_REDIS:
	pass
else:
	CACHES = {
		'default': {
			'BACKEND': 'django_redis.cache.RedisCache',
			'LOCATION': DEV_REDIS_URL,
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

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'