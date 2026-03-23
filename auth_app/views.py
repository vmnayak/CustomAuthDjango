from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from .tasks import send_password_reset_email, send_activation_email
from .utils import generate_activation_link, generate_reset_password_link
from django.conf import settings
from .models import PasswordResetToken

User = get_user_model()


def user_login(request):
    if request.user.is_authenticated:
        return redirect('fixtures:fixture_dashboard')

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        print(form.data, form.errors) 
        
        if form.is_valid():
            user = form.get_user()
            #  If active, log in the user                        
            login(request, user)
            return redirect('fixtures:fixture_dashboard')

        else:
            #  Handle inactive account error from Django's built-in authentication system
            non_field_errors = form.non_field_errors()
            if non_field_errors:
                messages.error(request, non_field_errors[0])  # Show the first error
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect('fixtures:fixture_dashboard')

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will be inactive until email is verified
            user.save()

            # Generate activation link
            activation_link = generate_activation_link(user, request)

            # Send Activation Email
            try:
                if settings.AUTH_APP["SEND_ACTIVATION_EMAIL"]:
                    if settings.AUTH_APP["USE_CELERY"]:
                        send_activation_email.delay(user.email, activation_link)
                    else:
                        send_activation_email(user.email, activation_link)
                messages.success(request, "Registration successful! Please check your email to activate your account.")
                return redirect('email_verification_pending')
            except Exception as e:
                messages.error(request, f"Error sending email: {str(e)}")
                user.delete()  # Rollback user creation on email failure
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def email_verification_pending(request):
    return render(request, 'email_verification_pending.html')

# Forgot Password View
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            reset_link = generate_reset_password_link(user, request)
            
            # Send email in the background
            # send_password_reset_email.delay(email, reset_link)
            if settings.AUTH_APP["SEND_RESET_EMAIL"]:
                if settings.AUTH_APP["USE_CELERY"]:
                    send_password_reset_email.delay(email, reset_link)
                else:
                    send_password_reset_email(email, reset_link)
                        
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "Email not found.")
    
    return render(request, "password_reset.html")


def reset_password(request, uidb64, token):
    try:
        # Decode UID and get user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        messages.error(request, "Invalid reset link.")
        return redirect("forgot_password")

    # Check if token exists and is valid
    try:
        reset_token = PasswordResetToken.objects.get(user=user, token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")

    if not reset_token.is_valid():
        messages.error(request, "Reset link has expired.")
        reset_token.delete()  # Remove expired token
        return redirect("forgot_password")

    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if new_password1 == new_password2:
            user.set_password(new_password1)
            user.save()

            # Delete the used token
            reset_token.delete()

            messages.success(request, "Password reset successfully. You can now login.")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "password_reset_confirm.html")




def activate_account(request, uidb64, token):
    try:
        # Decode UID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.info(request, "Your account is already activated.")
            return redirect("login")

        # Check if the token exists in the database
        try:
            reset_token = PasswordResetToken.objects.get(user=user, token=token)
        except PasswordResetToken.DoesNotExist:
            messages.error(request, "Invalid or expired activation link.")
            return redirect("login")
        
         # Check if the token is still valid
        if not reset_token.is_valid():
            messages.error(request, "Activation link has expired.")
            reset_token.delete()
            return redirect("login")

        # Activate the user
        user.is_active = True
        user.save()

        # Delete the token so it cannot be reused
        reset_token.delete()

        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect("login")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link.")
        return redirect("login")