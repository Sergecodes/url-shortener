from django.conf import settings
from django.conf.urls.static import static
# from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include('home.urls', namespace='home')),
    path('', include('shorten.urls', namespace='shorten')),
    path('__reload__/', include("django_browser_reload.urls")),
    # path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('qr_code/', include('qr_code.urls', namespace='qr_code')),
	# path('users/', include('users.urls', namespace='users')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

# if settings.DEBUG:
# 	import debug_toolbar

# 	urlpatterns = [
# 					  path('__debug__/', include(debug_toolbar.urls)),
# 				  ] + urlpatterns
