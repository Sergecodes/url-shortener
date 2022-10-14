import uuid
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from .forms import URLForm
from .models import URL, Browser, ShortURL, Visit
from .utils import get_browser, get_ip


@require_POST
def shorten_url(request):
	"""This view handles shorten url request"""
	print(request.body)
	form = URLForm(request.POST)

	if form.is_valid():
		url, desired_hash = form.cleaned_data['url'], form.cleaned_data['hash']

		# Check if desired hash is available
		if not ShortURL.objects.exists(hash=desired_hash):
			with transaction.atomic():
				browser_uuid = request.session.get('browser_uuid', str(uuid.uuid4()))
				request.session['browser_uuid'] = browser_uuid
				browser = Browser.objects.get_or_create(
					uuid=browser_uuid, 
					defaults={'name': get_browser()}
				)
					
				long_url = URL.objects.get_or_create(url=url)
				short_url = ShortURL.objects.create(
					long_url=long_url, 
					hash=desired_hash, 
					browser=browser
				)
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
			browser_name=get_browser(), 
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


def my_links(request):
	template = 'shorten/my_links.html'
	context = {}
	return render(request, template, context)


@require_POST
def toggle_preview(request):
	ok = request.POST.get('ok', False)

	if ok:
		request.session['PREVIEW_HASH'] = '1'
	else:
		request.session.pop('PREVIEW_HASH', None)

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

