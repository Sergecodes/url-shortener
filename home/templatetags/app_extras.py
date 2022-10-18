from django import template

register = template.Library()


@register.filter
def format_number(num):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0

	return '{}{}'.format(
		'{:f}'.format(num).rstrip('0').rstrip('.'), 
		['', 'K', 'M', 'B', 'T'][magnitude]
	)

 
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

