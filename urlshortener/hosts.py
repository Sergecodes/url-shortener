from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns('',
   host('www', settings.ROOT_URLCONF, name='www'),
   host('sup3r-s3cr3t-p4ge', 'shorten.admin_urls', name='admin'),
)
