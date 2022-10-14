from ipware import get_client_ip


def get_browser():
	pass


def get_ip(request):
	client_ip, is_routable = get_client_ip(request)
	
	if client_ip is None:
		# Unable to get the client's IP address
		pass
	else:
		# We got the client's IP address
		if is_routable:
			pass
		else:
			# The client's IP address is private
			pass

	return client_ip

