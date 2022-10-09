from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('home.urls', namespace='home')),
    path('', include('shorten.urls', namespace='shorten')),
    path('__reload__/', include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
	# path('users/', include('users.urls', namespace='users')),
]

# if settings.DEBUG:
# 	import debug_toolbar

# 	urlpatterns = [
# 					  path('__debug__/', include(debug_toolbar.urls)),
# 				  ] + urlpatterns
