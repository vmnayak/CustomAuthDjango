from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        if '@' in username:
            user = CustomUser.objects.filter(email=username).first()
        elif username.isdigit():
            user = CustomUser.objects.filter(phone=username).first()
        else:
            user = CustomUser.objects.filter(username=username).first()

        if user and user.check_password(password):
            return user
        return None
