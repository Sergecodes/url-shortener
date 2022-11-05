### Uses AZURE ###
from .settings import *


# Configure the domain name using the environment variable
# that Azure automatically creates for us.
SITE_HOSTNAME = env('WEBSITE_HOSTNAME')

BASE_URL = env('BASE_URL', default=SITE_HOSTNAME)
ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS', default=[])]
hostname = env('DBHOST')  # DBHOST is only the server name, not the full URL

# DB
DBNAME = env('DBNAME')
DBUSER = env('DBUSER')
DBPASS = env('DBPASS')

if SITE_HOSTNAME:
	ALLOWED_HOSTS = [SITE_HOSTNAME]
	CSRF_TRUSTED_ORIGINS = ['https://'+ SITE_HOSTNAME]

# WhiteNoise configuration
try:
	INSTALLED_APPS.remove('whitenoise.runserver_nostatic')
except ValueError:
	pass

# Add whitenoise directly after security middleware
sec_middleware_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
MIDDLEWARE.insert(sec_middleware_idx + 1, 'django.contrib.sessions.middleware.SessionMiddleware')

# Static files config
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  


# Configure Postgres database; the full username for PostgreSQL flexible server is
# username (not @sever-name).
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': DBNAME,
		'HOST': hostname + ".postgres.database.azure.com",
		'USER': DBUSER,
		'PASSWORD': DBPASS 
	}
}

