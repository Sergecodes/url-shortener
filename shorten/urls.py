from django.urls import path

from . import views

app_name = 'shorten'


urlpatterns = [
   path('ajax/shorten/', views.shorten_url, name='ajax-shorten-url'),
   path('ajax/preview/toggle/', views.toggle_preview, name='ajax-toggle-preview'),

   # Make the path "shorten" unavailable as a hash
   path('shorten/', views.shorten_url, name='shorten-url'),
   path('my-urls/', views.my_urls, name='my-urls'),
   path('delete/', views.delete_url, name='delete-url'),
   path('<str:hash>/stats/', views.stats, name='stats'),
   path('<str:hash>/preview/', views.preview_url, name='preview-url'),
   path('<str:hash>/', views.redirect_url, name='redirect-url'),

]
