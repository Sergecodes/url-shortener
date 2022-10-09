from django.core.validators import URLValidator
from django.db.models import URLField as BaseURLField
from django.forms.fields import URLField as BaseURLFormField


class URLScheme:
   """
   Basically this class permits us to use any schema in a url and exclude undesired ones.
   See https://consideratecode.com/2021/03/08/django-urlvalidator-with-scheme-deny-list/
   """
   def __init__(self, *, exclude=None):
      if exclude is None:
         self.exclude = []

   def __contains__(self, element):
      return element not in self.exclude


class URLFormField(BaseURLFormField):
   # Update default validators for form field too
   default_validators = [URLValidator(schemes=URLScheme())]


class URLField(BaseURLField):
   default_validators = [URLValidator(schemes=URLScheme())]

   def formfield(self, **kwargs):
      # Set the formfield for this model field to our custom URLFormField.
      # see https://stackoverflow.com/questions/41756572/django-urlfield-with-custom-scheme
      return super().formfield(**{
         'form_class': URLFormField,
         **kwargs,
      })
   
