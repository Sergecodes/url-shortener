from django.conf import settings
from django.db import models
from shortuuid import ShortUUID
from shortuuid.django_fields import ShortUUIDField

from .fields import URLField

BASE_URL = settings.BASE_URL
DEFAULT_HASH_LENGTH = settings.DEFAULT_HASH_LENGTH


class URL(models.Model):
   url = URLField(max_length=500, unique=True)

   def __str__(self):
      return self.url


class ShortURL(models.Model):
   hash = ShortUUIDField(length=DEFAULT_HASH_LENGTH, max_length=32, unique=True)
   num_clicks = models.PositiveIntegerField(default=0)
   long_url = models.OneToOneField(
      URL, 
      on_delete=models.CASCADE,
      related_name='short_url'
   )

   def save(self, *args, **kwargs):
      # If object is still getting created, try to save it.
      # If there's an error because the auto generated hash is a duplicate,
      # then regenerate till unique one is obtained.
      # Note however that the chances of having a duplicate are extremely slim!

      hash = self.hash
      if not self.pk:
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


class Click(models.Model):
   """Handles click requests on the shortened url"""
   ip_address = models.GenericIPAddressField(blank=True, null=True, db_index=True)
   short_url = models.ForeignKey(
      ShortURL, 
      on_delete=models.CASCADE, 
      related_name='clicks',
      related_query_name='click'
   )

   def save(self, *args, **kwargs):
      if not self.pk:
         short_url = self.short_url
         short_url.num_clicks = models.F('num_clicks') + 1
         short_url.save(update_fields=['num_clicks'])

      super().save(*args, **kwargs)

   def __str__(self):
      return self.ip_address

