from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from email.mime.image import MIMEImage
from ..models import *
from .generators import *
import os


host = "192.168.8.144"


def sendRegistrationEmail(registration_token: RegistrationToken):
    email_address = registration_token.user.email

    subject = 'Registrierung beim GSV Gundernhausen Tennis Kiosk'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]
    text_content = 'Wilkommen beim GSV Gunderhausen Tennis Kiosk! Hier der Link um ihre Registrierung abzuschließen:' +\
                   f"\nhttps://{host}/set_password/"+str(registration_token.token) + "\n"\
                   "Verwende alternativ gerne den angehängten QR Code."
    html_content = \
        '<p>Wilkommen beim GSV Gunderhausen Tennis Kiosk!</p>' \
        '<p>Hier der Link um ihre Registrierung abzuschließen:\n' + \
        f'{host}/set_password/'+str(registration_token.token) + "</p>\n" +\
        '<p>Oder verwende diesen QR-Code:</p>\n' +\
        '<img src="cid:image1">'

    # Erstellen der E-Mail
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    # Bild einbetten
    generateRegistrationTokenQRCode(registration_token)
    img_path = "qr_codes/password/" + str(registration_token.token)+".png"
    with open(img_path, 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        image.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_path))
        msg.attach(image)

    # E-Mail senden
    msg.send()

    # Datei löschen
    os.remove(img_path)

    return True


def sendForgotPasswordEmail(token: PasswordResetToken):
    email_address = token.user.email

    subject = 'Neues Passwort beim GSV Gundernhausen Tennis Kiosk'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]
    text_content = f'Hallo {token.user.last_name},\n hier der Link um dein Passwort zurückzusetzen:' + \
                   f"\nhttps://{host}/set_password/" + str(token.token) + \
                   "\nVerwende alternativ gerne den angehängten QR Code."
    html_content = \
        f'<p>Hallo {token.user.last_name},</p>\n' \
        '<p>hier der Link um dein Passwort zurückzusetzen: ' + \
        f'\nhttps://{host}/set_password/' + str(token.token) + "</p>\n" + \
        '<p>Oder verwende diesen QR-Code:</p>\n' + \
        '<img src="cid:image1">'

    # Erstellen der E-Mail
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    # Bild einbetten
    generatePasswordResetTokenQRCode(token)
    img_path = "qr_codes/password/" + str(token.token)+".png"
    with open(img_path, 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        image.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_path))
        msg.attach(image)

    # E-Mail senden
    msg.send()

    # Datei löschen
    os.remove(img_path)

    return True


def sendNewPasswordSetEmail(token: LoginToken):
    email_address = token.user.email

    subject = 'Neuer QR-Code für die Anmeldung beim GSV Gundernhausen Tennis Kiosk'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email_address]
    text_content = f'Hallo {token.user.last_name},\n anbei ein QR-Code mit dem du dich das nächste Jahr oder bis zu' \
                   f'deinem nächsten Passwortwechsel beim GSV Gundernhausen Tennis Kiosk anmelden kannst.'
    html_content = \
        f'<p>Hallo {token.user.last_name},</p>\n' \
        f'</p>hier dein neuer QR-Code mit dem du dich das nächste Jahr oder bis zu' \
        f'deinem nächsten Passwortwechsel beim GSV Gundernhausen Tennis Kiosk anmelden kannst:</p>' \
        '<img src="cid:image1">'

    # Erstellen der E-Mail
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    # Bild einbetten
    generateLoginTokenQRCode(token)
    img_path = "qr_codes/login/" + str(token.token) + ".png"
    with open(img_path, 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        image.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_path))
        msg.attach(image)

    # E-Mail senden
    msg.send()

    # Datei löschen
    os.remove(img_path)

    return True
