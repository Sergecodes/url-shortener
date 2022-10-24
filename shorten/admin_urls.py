from django.contrib import admin
from django.urls import path, include


urlpatterns = [
   path('', admin.site.urls),
   path('__reload__/', include("django_browser_reload.urls")),
]

