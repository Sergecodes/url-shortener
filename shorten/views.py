import datetime as dt
import pandas as pd
import uuid
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from .constants import BROWSERS
from .forms import URLForm
from .models import URL, Browser, ShortURL, Visit
from .utils import get_browser_dict, get_ip, format_number

USE_CACHE = settings.USE_CACHE
RESULTS_PER_PAGE = settings.RESULTS_PER_PAGE


@require_POST
def shorten_url(request):
	"""This view handles shorten url request"""
	form = URLForm(request.POST)

	if form.is_valid():
		# Note that desired_hash could still be ''
		url, desired_hash = form.cleaned_data['url'], form.cleaned_data['hash']

		# Check if desired hash is available
		if not desired_hash or (desired_hash and not ShortURL.objects.filter(hash=desired_hash).exists()):
			browser_uuid = request.session.get('browser_uuid')
			if not browser_uuid:
				browser_uuid = str(uuid.uuid4())
				request.session['browser_uuid'] = browser_uuid

			with transaction.atomic():
				if USE_CACHE:
					# Cache keys
					browser_key = f'browser_{browser_uuid}'
					long_url_key = f'url_{url}'
					short_url_key1 = f'short_url_url_{url}_browser_{browser_uuid}'

					if not (browser := cache.get(browser_key)):
						browser, __ = Browser.objects.get_or_create(
							uuid=browser_uuid, 
							defaults={'name': list(get_browser_dict(request))[0]}
						)
						cache.set(browser_key, browser)

					if not (long_url := cache.get(long_url_key)):
						long_url, __ = URL.objects.get_or_create(url=url)
						cache.set(long_url_key, long_url)

					if not (short_url := cache.get(short_url_key1)):
						short_url, __ = ShortURL.objects.get_or_create(
							long_url=long_url, 
							browser=browser,
							defaults={'hash': desired_hash or ''}
						)
						cache.set(short_url_key1, short_url)

						# Store short url in cache using hash
						short_url_key2 = f'short_url_{short_url.hash}'
						cache.set(short_url_key2, short_url)
				else:
					browser, __ = Browser.objects.get_or_create(
						uuid=browser_uuid, 
						defaults={'name': list(get_browser_dict(request))[0]}
					)
					long_url, __ = URL.objects.get_or_create(url=url)
					short_url, __ = ShortURL.objects.get_or_create(
						long_url=long_url, 
						browser=browser,
						defaults={'hash': desired_hash or ''}
					)
				
				# TODO: Update response to include qrcode 
				result = short_url.__dict__.copy()
				result.pop('_state')
				long_url_dict = short_url.long_url.__dict__.copy()
				long_url_dict.pop('_state')
				result.update({
					'url': short_url.url,
					'num_visits_ft': format_number(short_url.num_visits),
					'long_url': long_url_dict,
					'qr_url': ''
				})
				
				return JsonResponse(result, status=201)
		else:
			# Hash has already been used
			return JsonResponse({'code': 'HASH_UNAVAILABLE'}, status=409)
	else: 
		return JsonResponse({'data': form.errors.as_json()}, status=400)


def redirect_url(request, hash):
	if USE_CACHE:
		# Use short_url_key2
		key = f'short_url_{hash}'
		if not (short_url := cache.get(key)):
			short_url = get_object_or_404(ShortURL, hash=hash)

			# Add in cache
			short_url_key1 = f'short_url_url_{short_url.long_url.url}_browser_{short_url.browser.uuid}'
			short_url_key2 = f'short_url_{hash}'
			cache.set_many({short_url_key1: short_url, short_url_key2: short_url})
	else:
		short_url = get_object_or_404(ShortURL, hash=hash)

	with transaction.atomic():
		# Add visits & update cache
		short_url.num_visits = F('num_visits') + 1
		short_url.save(update_fields=['num_visits'])
		Visit.objects.create(
			short_url=short_url, 
			browser_name=list(get_browser_dict(request))[0], 
			ip_address=get_ip(request)
		)

		if USE_CACHE:
			## Update cache
			# Do this so as to get numeric val of num_visits without doing a refresh_from_db()
			# else it will be a "CombinedExpression" instance
			short_url.num_visits += 1  
			short_url_key1 = f'short_url_url_{short_url.long_url.url}_browser_{short_url.browser.uuid}'
			short_url_key2 = f'short_url_{hash}'
			cache.set_many({short_url_key1: short_url, short_url_key2: short_url})

	# If previewing is available, redirect to preview page. else redirect to long url page
	if request.session.get('preview_urls'):
		return redirect('shorten:preview-url', hash=hash)

	return redirect(short_url.long_url.url)


def preview_url(request, hash):
	if USE_CACHE:
		# Use short_url_key2
		key = f'short_url_{hash}'
		if not (short_url := cache.get(key)):
			short_url = get_object_or_404(ShortURL, hash=hash)

			# Add in cache
			short_url_key1 = f'short_url_url_{short_url.long_url.url}_browser_{short_url.browser.uuid}'
			short_url_key2 = f'short_url_{hash}'
			cache.set_many({short_url_key1: short_url, short_url_key2: short_url})
	else:
		short_url = get_object_or_404(ShortURL, hash=hash)

	template = 'shorten/preview.html'
	context = {'short_url': short_url}
	return render(request, template, context)


@require_POST
def delete_url(request):
	hash = request.POST.get('hash')
	browser_uuid = request.session.get('browser_uuid')
	short_url = get_object_or_404(ShortURL, hash=hash, browser__uuid=browser_uuid)
	short_url.delete()

	if next_url := request.POST.get('next'):
		return redirect(next_url)

	return redirect('shorten:my-urls')


def my_urls(request):
	template = 'shorten/my_urls.html'
	if browser_uuid := request.session.get('browser_uuid'):
		result = ShortURL.objects.filter(browser__uuid=browser_uuid).order_by('-created_on')
	else:
		result = ShortURL.objects.none()

	## paginate results
	paginator = Paginator(result, RESULTS_PER_PAGE)
	page_number = request.GET.get('page')
	# if page_number is None, the first page is returned
	page_obj = paginator.get_page(page_number) 
	
	context = {
		'page_obj': page_obj,
		# if more than one page is present, then the results are paginated
		'is_paginated': paginator.num_pages > 1,
		'preview_urls': request.session.get('preview_urls', False)
	}

	return render(request, template, context)


def stats(request, hash):
	"""
	To get stats of number of visits of a url. 
	It's considered that the frontend uses the library charts.js
	""" 
	if USE_CACHE:
		# Use short_url_key2
		key = f'short_url_{hash}'
		if not (short_url := cache.get(key)):
			short_url = get_object_or_404(ShortURL, hash=hash)

			# Add in cache
			short_url_key1 = f'short_url_url_{short_url.long_url.url}_browser_{short_url.browser.uuid}'
			short_url_key2 = f'short_url_{hash}'
			cache.set_many({short_url_key1: short_url, short_url_key2: short_url})
	else:
		short_url = get_object_or_404(ShortURL, hash=hash)

	template = 'shorten/stats.html'
	all_visits = short_url.visits.all()
	context = {'short_url': short_url}

	## Visits per past n months
	past_num_months = -6
	today = dt.datetime.today().date()
	start_date, end_date = (today + relativedelta(months=past_num_months)).replace(day=1), today

	dates = pd.date_range(start_date, end_date, freq='MS').to_pydatetime().tolist() # MS = month-start
	visits_per_month = {date.strftime('%b-%Y'): date for date in dates}
	visits = all_visits.filter(date__date__range=[start_date, end_date])

	for date_str, date in visits_per_month.items():
		visits_per_month[date_str] = visits.filter(
			date__month=date.month, 
			date__year=date.year
		).count()

	context['past_num_months'] = abs(past_num_months)
	context['visits_per_month'] = visits_per_month

	## Visits per past n days
	past_num_days = -15
	start_date, end_date = today + dt.timedelta(days=past_num_days), today

	dates = pd.date_range(start_date, end_date, freq='D').to_pydatetime().tolist() 
	visits_per_day = {date.strftime('%b %d'): date for date in dates}
	visits = all_visits.filter(date__date__range=[start_date, end_date])

	for date_str, date in visits_per_day.items():
		visits_per_day[date_str] = visits.filter(date__date=date).count()

	context['past_num_days'] = abs(past_num_days)
	context['visits_per_day'] = visits_per_day

	## Visits per browser
	visits = all_visits \
		.order_by('browser_name') \
		.values('browser_name') \
		.annotate(count=Count('browser_name'))
	visits_per_browser = {dict(BROWSERS)[v['browser_name']]: v['count'] for v in visits}

	context['visits_per_browser'] = visits_per_browser

	## Visits per city & country
	visits_per_city, visits_per_country = {}, {}
	g = GeoIP2()
	other_cities, other_countries = 0, 0
	for visit in all_visits:
		if ip := visit.ip_address:
			city_info = g.city(ip)
			city, country = city_info['city'], city_info['country_name']

			if city:
				visits_per_city[city] = visits_per_city.get(city, 0) + 1
			else:
				other_cities += 1
			
			if country:
				visits_per_country[country] = visits_per_country.get(country, 0) + 1
			else:
				other_countries += 1
		else:
			other_cities += 1
			other_countries += 1

	visits_per_city['Others'] = other_cities
	visits_per_country['Others'] = other_countries

	context['visits_per_city'] = visits_per_city 
	context['visits_per_country'] = visits_per_country

	return render(request, template, context)


@require_POST
def toggle_preview(request):
	preview = True if request.POST.get('preview', False) == 'true' else False

	if preview:
		request.session['preview_urls'] = True
	else:
		request.session.pop('preview_urls', None)

	return JsonResponse({'new_preview': preview})

