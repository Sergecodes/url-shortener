from django.core.cache import cache
from django.test import TestCase

from .models import ShortURL, Visit, URL


class ShortURLTestCase(TestCase):
	def setUp(self):
		self.hash = 'hash1'
		self.short_url = ShortURL.objects.create(
			hash=self.hash,
			long_url=URL.objects.create(url='www.google.com')
		)

	def test_desired_alias_already_taken(self):
		"""Check that if alias is already taken, new one is generated"""
		obj = ShortURL.objects.create(
			hash=self.hash, 
			long_url=URL.objects.create(url='www.github.com')
		)
		self.assertNotEqual(self.hash, obj.hash)

	def test_url_visits_increment(self):
		Visit.objects.create(browser_name='CHR', short_url=self.short_url)
		Visit.objects.create(browser_name='CHR', short_url=self.short_url)

		self.short_url.refresh_from_db()
		self.assertEqual(self.short_url.num_visits, 2)


class CacheTestCase(TestCase):
	def setUp(self):
		pass

	def test_keys_stored_success(self):
		"""Verify that key is stored in cache"""
		key, value = 'key1', 'value1'
		cache.set(key, value)

		cache_val = cache.get(key)
		self.assertEqual(value, cache_val)

