from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None):
        if not username and not email and not phone:
            raise ValueError("User must have a username, email, or phone number.")

        user = self.model(
            username=username if username else None,
            email=self.normalize_email(email) if email else None,
            phone=phone if phone else None
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password):
        user = self.create_user(username, email, phone, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = []
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username or self.email or self.phone



class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(hours=1)  # Expires in 1 hour