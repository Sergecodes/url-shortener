from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
	# path('users/', include('users.urls', namespace='users')),
]

# if settings.DEBUG:
# 	import debug_toolbar

# 	urlpatterns = [
# 					  path('__debug__/', include(debug_toolbar.urls)),
# 				  ] + urlpatterns
