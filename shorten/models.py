import uuid
from django.conf import settings
from django.db import models
from shortuuid import ShortUUID
from shortuuid.django_fields import ShortUUIDField

from .constants import BROWSERS
from .fields import URLField

BASE_URL = settings.BASE_URL
DEFAULT_HASH_LENGTH = settings.DEFAULT_HASH_LENGTH


class URL(models.Model):
   url = URLField(max_length=500, unique=True)
   
   def __str__(self):
      return self.url

   def validate_unique(self, exclude=None):
      # Prevent url uniqueness validation in modelform
      if exclude:
         exclude.append('url')

      return super().validate_unique(exclude)
   

class Browser(models.Model):
   """Store info of browsers that "create"(submit shorten form) the urls"""
   uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
   name = models.CharField(max_length=3, choices=BROWSERS)
   urls = models.ManyToManyField(
      URL, 
      through='ShortURL',
      related_name='browsers',
      related_query_name='browser',
      blank=True,
   )

   def __str__(self):
      return f'{self.get_name_display()}, {self.uuid}'


class ShortURL(models.Model):
   hash = ShortUUIDField(length=DEFAULT_HASH_LENGTH, max_length=32, unique=True)
   num_visits = models.PositiveIntegerField(default=0)
   created_on = models.DateTimeField(auto_now_add=True)
   # No unique constraint on long_url & browser since we can have multiple short urls(aliases)
   # of the same long url and on the same browser.
   long_url = models.ForeignKey(
      URL, 
      on_delete=models.RESTRICT, 
      related_name='short_urls',
      related_query_name='short_url'
   )
   browser = models.ForeignKey(
      Browser, 
      related_name='short_urls',
      related_query_name='short_url',
      on_delete=models.SET_NULL, 
      blank=True,
      null=True
   )

   def save(self, *args, **kwargs):
      # If object is still getting created, try to save it.
      # If there's an error because the auto generated hash is a duplicate,
      # then regenerate till unique one is obtained.
      # Note however that the chances of having a duplicate are extremely slim!

      hash = self.hash
      if not self.pk:
         if not hash:
            hash = ShortUUID().random(length=DEFAULT_HASH_LENGTH)

         while True:
            try:
               ShortURL.objects.get(hash=hash)
            except ShortURL.DoesNotExist:
               # hash was unique, we can go out of loop
               break
            else:
               # hash wasn't unique, try again with new hash
               hash = ShortUUID().random(length=DEFAULT_HASH_LENGTH)

         self.hash = hash

      super().save(*args, **kwargs)

   @property
   def url(self):
      return f'{BASE_URL}/{self.hash}/'

   def __str__(self):
      return self.url


class Visit(models.Model):
   """Handles requests to the short url"""
   ip_address = models.GenericIPAddressField(blank=True, null=True, db_index=True)
   browser_name = models.CharField(max_length=3, choices=BROWSERS)
   short_url = models.ForeignKey(
      ShortURL, 
      on_delete=models.CASCADE, 
      related_name='visits',
      related_query_name='visit'
   )
   date = models.DateTimeField(auto_now_add=True)

   def save(self, *args, **kwargs):
      if not self.pk:
         short_url = self.short_url
         short_url.num_visits = models.F('num_visits') + 1
         short_url.save(update_fields=['num_visits'])

      super().save(*args, **kwargs)

   def __str__(self):
      return f'{self.get_browser_name_display()}, {self.ip_address}'

