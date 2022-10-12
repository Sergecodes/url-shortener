from captcha.fields import CaptchaField
from django import forms

from .models import URL


class URLForm(forms.ModelForm):
   captcha = CaptchaField()

   class Meta:
      model = URL
      fields = ['captcha', 'url']
      widgets = {
			'url': forms.URLInput(attrs={
            'placeholder': 'Paste URL here',
         }),
		}
      labels = {
         'url': ''
      }
