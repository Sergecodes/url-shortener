import uuid
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from .forms import URLForm
from .models import URL, Browser, ShortURL, Visit
from .utils import get_browser_dict, get_ip

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
				browser, __ = Browser.objects.get_or_create(
					uuid=browser_uuid, 
					defaults={'name': list(get_browser_dict(request))[0]}
				)
				long_url, __ = URL.objects.get_or_create(url=url)
				short_url, __ = ShortURL.objects.get_or_create(long_url=long_url, browser=browser)
				return JsonResponse({'hash': short_url.hash}, status=201)
		else:
			# Hash has already been used
			return JsonResponse({'code': 'HASH_UNAVAILABLE'}, status=409)
	else: 
		return JsonResponse({'data': form.errors.as_json()}, status=400)


def redirect_hash(request, hash):
	short_url = get_object_or_404(ShortURL, hash=hash)

	with transaction.atomic():
		# Add visits
		short_url.num_visits = F('num_visits') + 1
		short_url.save(update_fields=['num_visits'])
		Visit.objects.create(
			short_url=short_url, 
			browser_name=list(get_browser_dict(request))[0], 
			ip_address=get_ip(request)
		)

	# If previewing is available, redirect to preview page. else redirect to long url page
	if request.session.get('PREVIEW_HASH'):
		return redirect('shorten:preview-hash', {'hash': hash})

	return redirect(short_url.long_url.url)


def preview_hash(request, hash):
	template = 'shorten/preview.html'
	short_url = get_object_or_404(ShortURL, hash=hash)
	context = {'hash': hash, 'long_url': short_url.long_url.url}
	return render(request, template, context)


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
		'is_paginated': paginator.num_pages > 1
	}

	return render(request, template, context)


@require_POST
def toggle_preview(request):
	ok = request.POST.get('ok', False)

	if ok:
		request.session['preview_hash'] = '1'
	else:
		request.session.pop('preview_hash', None)

	return JsonResponse({'new_ok': ok})



# In a view or a middleware where the `request` object is available

#  from ipware import get_client_ip
#  client_ip, is_routable = get_client_ip(request)
#  if client_ip is None:
#     # Unable to get the client's IP address
#  else:
#      # We got the client's IP address
#      if is_routable:
#          # The client's IP address is publicly routable on the Internet
#      else:
#          # The client's IP address is private

#  # Order of precedence is (Public, Private, Loopback, None)

