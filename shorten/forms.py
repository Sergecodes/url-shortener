from captcha.fields import CaptchaField
from django import forms
from django.conf import settings

from .models import URL

BASE_URL = settings.BASE_URL
USE_CAPTCHA = settings.USE_CAPTCHA


class URLForm(forms.ModelForm):
   captcha = CaptchaField() if USE_CAPTCHA else None
   hash = forms.CharField(
      label='Desired alias', 
      max_length=24,  # Well let's just say 24
      required=False,
      help_text= 
         'Not required. Your desired shortened url alias(it will be used as the short url). <br>'
         'eg. if you enter "hello", your generated shortened url will be "{}/hello".'.format(BASE_URL),
   )  

   class Meta:
      model = URL
      fields = ['captcha', 'url', 'hash'] if USE_CAPTCHA else ['url', 'hash']
      widgets = {
			'url': forms.URLInput(attrs={
            'placeholder': 'Paste URL here',
            'value': 'https://'
         }),
		}
      labels = {'url': ''}
      help_texts = {
         'url': 'The protocol/scheme(eg. http, https, ftp) should be included.'
      }

