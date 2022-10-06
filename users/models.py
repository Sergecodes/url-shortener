from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
   first_name, last_name = None, None

