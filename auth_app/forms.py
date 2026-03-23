from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username / Email / Phone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username, email or phone'}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
    )


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
        help_text="Required. Letters, digits, and @/./+/-/_ only."
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        help_text="Enter a valid email address."
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
        help_text="Enter your phone number without the country code."
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        help_text="Enter the same password again for verification."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if not username and not email and not phone:
            raise forms.ValidationError("At least one of username, email, or phone is required.")

        return cleaned_data
