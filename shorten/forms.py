from captcha.fields import CaptchaField
from django import forms

from .models import URL


class URLForm(forms.ModelForm):
   captcha = CaptchaField()

   class Meta:
      model = URL
      fields = ['captcha', 'url']

