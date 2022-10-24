from django.contrib import admin

from .models import ShortURL, Browser, Visit, URL


admin.site.register(ShortURL)
admin.site.register(Browser)
admin.site.register(Visit)
admin.site.register(URL)
