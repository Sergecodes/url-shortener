from django.urls import path

from . import views

app_name = 'shorten'


urlpatterns = [
   path('ajax/shorten/', views.shorten_url, name='ajax-shorten-url'),
   # Make the path "shorten" unavailable as a hash
   path('shorten/', views.shorten_url, name='shorten-url'),
   path('<str:hash>/preview/', views.preview_hash, name='preview-hash'),
   path('<str:hash>/', views.redirect_hash, name='redirect-hash'),

]
