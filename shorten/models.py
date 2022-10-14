import uuid
from django.conf import settings
from django.db import models
from shortuuid import ShortUUID
from shortuuid.django_fields import ShortUUIDField

from .fields import URLField

BASE_URL = settings.BASE_URL
DEFAULT_HASH_LENGTH = settings.DEFAULT_HASH_LENGTH
BROWSERS = (
   ('SAF', 'Safari'),
   ('CHR', 'Chrome'),
   ('OPE', 'Opera'),
   ('FOX', 'Firefox'),
   ('EDG', 'Edge'),
   ('IEX', 'Internet Explorer'),
   ('UCB', 'UC Browser'),
   ('O', 'Other'),
)


class URL(models.Model):
   url = URLField(max_length=500, unique=True)

   def __str__(self):
      return self.url


class ShortURL(models.Model):
   browser = models.ForeignKey(
      'Browser', 
      on_delete=models.SET_NULL, 
      related_name='shortened_urls',
      related_query_name='shortened_url',
      null=True, 
      blank=True
   )
   hash = ShortUUIDField(length=DEFAULT_HASH_LENGTH, max_length=32, unique=True)
   num_visits = models.PositiveIntegerField(default=0)
   long_url = models.OneToOneField(
      URL, 
      on_delete=models.CASCADE,
      related_name='short_url'
   )
   created_on = models.DateTimeField(auto_now_add=True)

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


class Browser(models.Model):
   """Store info of browsers that "create"(submit shorten form) the urls"""
   uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
   name = models.CharField(max_length=3, choices=BROWSERS)

   def __str__(self):
      return f'{self.get_name_display()}, {self.uuid}'


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
      return f'{self.get_browser_display()}, {self.ip_address}'

