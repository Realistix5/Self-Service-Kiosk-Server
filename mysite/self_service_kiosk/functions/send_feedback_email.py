from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from email.mime.image import MIMEImage
from ..models import *
from .generators import *
import os


def sendFeedbackEmail(feedback_text: str, feedback_sender: str):

    subject = 'Neues Feedback vom Self-Service-Kiosk'
    from_email = settings.EMAIL_HOST_USER
    to_email = ["christopher.b.trautmann@stud.h-da.de"]
    text_content = f'Feedback-Text: {feedback_text}\n' \
                   f'Feedback-Sender: {feedback_sender}'

    # Erstellen der E-Mail
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)

    # E-Mail senden
    msg.send()

    return True
