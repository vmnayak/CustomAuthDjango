from django.urls import path
# from .views import user_login, user_logout
from . import views
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path('email-verification-pending/', views.email_verification_pending, name='email_verification_pending'),
]
