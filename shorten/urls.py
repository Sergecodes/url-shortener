from django.urls import path

from . import views

app_name = 'shorten'


urlpatterns = [
   path('ajax/shorten/', views.shorten_url, name='ajax-shorten-url'),
   path('ajax/preview/toggle/', views.toggle_preview, name='ajax-toggle-preview'),

   # Make the path "shorten" unavailable as a hash
   path('shorten/', views.shorten_url, name='shorten-url'),
   path('my-urls/', views.my_urls, name='my-urls'),
   path('<str:hash>/preview/', views.preview_hash, name='preview-hash'),
   path('<str:hash>/', views.redirect_hash, name='redirect-hash'),

]
