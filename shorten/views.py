from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST, require_GET

from .forms import URLForm
from .models import URL, ShortURL


@require_POST
def shorten_url(request):
	"""This view handles shorten url request"""
	print(request.POST)
	form = URLForm(request.POST)
	if form.is_valid():
		url, desired_hash = form.cleaned_data['url'], form.cleaned_data['hash']

		# Check if desired hash is available
		if not ShortURL.objects.exists(hash=desired_hash):
			long_url = URL.objects.get_or_create({'url': url}, url=url)
			# device_id
			short_url = ShortURL.objects.create(long_url=long_url, hash=desired_hash)
			return JsonResponse({'hash': short_url.hash}, status=201)
		else:
			# Hash has already been used
			return JsonResponse({'code': 'HASH_UNAVAILABLE'}, status=409)
	else: 
		return JsonResponse({'data': form.errors.as_json()}, status=400)


def redirect_hash(request, hash):
	short_url = get_object_or_404(ShortURL, hash=hash)
	# if previewing is available, redirect to preview page. else redirect to long url page
	if request.COOKIES.get('PREVIEW_HASH'):
		return redirect('shorten:preview-hash', {'hash': hash})

	return redirect(short_url.long_url.url)


def preview_hash(request, hash):
	template = 'shorten/preview.html'
	context = {}

	return render(request, template, context)


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

