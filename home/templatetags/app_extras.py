from django import template
from django.conf import settings

from shorten.utils import format_number

register = template.Library()


register.filter('format_number', format_number)


@register.simple_tag
def get_use_captcha():
	return settings.USE_CAPTCHA


@register.simple_tag
def query_transform(request, **kwargs):
	"""Insert kwargs into url"""
	updated = request.GET.copy()
	for k, v in kwargs.items():
		if v is not None:
			updated[k] = v
		else:
			updated.pop(k, 0)

	return updated.urlencode()

