from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import PasswordResetToken
from django.utils.crypto import get_random_string

def generate_secure_reset_token(user):
    """Generate a secure password reset token stored in DB"""
    token = get_random_string(50)  # Secure random token
    PasswordResetToken.objects.create(user=user, token=token)
    return token

def generate_activation_link(user, request):
    """Generate activation link for a user"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_secure_reset_token(user)
    return request.build_absolute_uri(f"/auth/activate/{uid}/{token}/")

def generate_reset_password_link(user, request):
    """Generate password reset link"""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_secure_reset_token(user)
    return request.build_absolute_uri(f"/auth/reset-password/{uid}/{token}/")
