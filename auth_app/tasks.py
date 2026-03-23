from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_password_reset_email(email, reset_link):
    email_subject = "Reset Your Password"
    email_body = render_to_string('password_reset_email.html', {'reset_link': reset_link})

    send_mail(
        email_subject, 
        '',  # Plain text left empty
        settings.DEFAULT_FROM_EMAIL, 
        [email],
        html_message=email_body,
    )


@shared_task
def send_activation_email(email, activation_link):
    """Send activation email in the background."""
    email_subject = "Activate Your Account"
    email_body = render_to_string("activation_email.html", {"activation_link": activation_link})

    send_mail(email_subject, '', settings.DEFAULT_FROM_EMAIL, [email], html_message=email_body,)