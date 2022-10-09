from django.shortcuts import render


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
