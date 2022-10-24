from ipware import get_client_ip

from .constants import BROWSERS


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
	

def get_browser_dict(request):
	browsers_dict = dict(BROWSERS)

	# `family_dict` is used to map browser keys to common user-agent browser names 
	family_dict = browsers_dict.copy()
	family_dict['CHR'] = 'chrome chromium crios'
	family_dict['IEX'] = 'msie'
	family_dict['OPR'] = 'OPR'
	family_dict['UCB'] = 'UCBrowser'
	
	family_values = [value.lower() for value in family_dict.values()]
	browser_family = request.user_agent.browser.family.lower()

	browser_key = ''
	for value in family_values:
		if browser_family in value:
			# Get browser key from value
			for k in family_dict.keys():
				if family_dict[k].lower() == value:
					browser_key = k
					break

	if not browser_key:
		browser_key = 'O'

	print('browser_key', browser_key)
	return {browser_key: browsers_dict[browser_key]}


def get_ip(request):
	client_ip, is_routable = get_client_ip(request)
	print('client_ip', client_ip)
	print('is_routable', is_routable)
	
	if client_ip is None:
		# Unable to get the client's IP address
		pass
	else:
		# We got the client's IP address
		if is_routable:
			pass
		else:
			# The client's IP address is private
			return None

	return client_ip

