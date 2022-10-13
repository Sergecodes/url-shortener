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
         'Not required. Your desired shortened url alias (it will be used as the short url). <br>'
         'eg. if you enter "hello", your generated shortened url will be "{}/hello".'.format(BASE_URL),
   )  

   class Meta:
      model = URL
      fields = ['captcha', 'url', 'hash'] if USE_CAPTCHA else ['url', 'hash']
      widgets = {
			'url': forms.URLInput(attrs={
            'placeholder': 'Paste URL here',
         }),
		}
      labels = {'url': ''}

   def clean_url(self):
      url = self.cleaned_data['url']
      # TODO convert url to normalized form... ? check other url-shortener sites
      # eg. https://google.com & google.com & www.google.com are the same.
      return url
