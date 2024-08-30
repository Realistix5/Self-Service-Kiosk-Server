import datetime
import csv
import locale

from smtplib import SMTPException

from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .generators import generateInvoicePDF
from ..models import *

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


def generate_invoice_this_year(modeladmin, request, queryset):
    year = datetime.datetime.now().year
    return generateInvoicesAndAddMessages(queryset, request, year)


def generate_invoice_last_year(modeladmin, request, queryset):
    year = datetime.datetime.now().year - 1
    return generateInvoicesAndAddMessages(queryset, request, year)


def send_invoice_emails(modeladmin, request, queryset):
    for invoice in queryset:
        if invoice.email_sent is False:
            try:
                from_email = settings.EMAIL_HOST_USER
                to_email = [invoice.user.email]
                msg = EmailMultiAlternatives(invoice.email_subject, invoice.email_body_text, from_email, to_email)
                msg.attach_alternative(invoice.email_body_html, "text/html")  # Attach html alternative
                msg.attach_file(settings.MEDIA_ROOT + "/" + str(invoice.pdf_path))  # Attach the PDF invoice file
                # Send email
                result = msg.send()
                # If sent update invoice
                if result == 1:
                    invoice.email_sent = True
                    invoice.save()
            except SMTPException:
                pass


def regenerate_invoice(modeladmin, request, queryset):
    success_counter = 0
    gotException = False
    for invoice in queryset:
        try:
            year = invoice.year
            user = invoice.user
            version = invoice.version + 1
            result = generateInvoice(user, year, version)
            if result is True:
                success_counter += 1
            else:
                messages.error(request, str(result))
        except Exception as e:
            gotException = True
    if gotException:
        messages.warning(request, "Doppelte Nutzer und Jahr Paare wurden nur jeweils 1x generiert.")
        messages.warning(request, 'Am Besten "Nur höchste Version"-Filter für Neugenerierungen nutzen.')
    if success_counter != 0:
        if success_counter == 1:
            messages.success(request, f"Abrechnung erfolgreich erstellt.")
        else:
            messages.success(request, f"{success_counter} Abrechnungen erfolgreich erstellt.")
    if success_counter < len(queryset):
        messages.error(request, f"{len(queryset) - success_counter} Abrechnung(en) nicht erstellt.")


def export_order_items_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Bestellungsteile.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Schreibe die Kopfzeile
    writer.writerow(
        ['Bestellung-ID', 'Nutzer', 'Datum', 'Bezahlt', 'Produkt', 'Preis bei Kauf', 'Menge'])

    # Schreibe die Datenzeilen
    for order in queryset:
        order_items = order.orderitem_set.all()  # Hole alle OrderItems für diese Order
        for order_item in order_items:
            writer.writerow([
                order.id,
                order.user.username,
                order.created_at.strftime('%d.%m.%Y'),  # Datum im deutschen Format
                'Ja' if order.paid else 'Nein',  # Übersetze boolesche Werte
                order_item.menu_item.name,
                locale.format_string('%.2f', order_item.price_at_purchase),  # Zahlen im deutschen Format
                order_item.quantity,
            ])

    return response


def export_year_end_statements_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Jahresendabrechnungen.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Schreibe die Kopfzeile
    writer.writerow(['ID', 'Nutzer', 'Jahr', 'Erstellt am', 'Geändert am', 'Guthabenübertrag', 'Rechnungsbetrag'])

    # Schreibe die Datenzeilen
    for statement in queryset:
        writer.writerow([
            statement.id,
            statement.user.username,
            statement.year,
            statement.created_at.strftime('%d.%m.%Y %H:%M:%S'),  # Datum und Uhrzeit im deutschen Format
            statement.changed_at.strftime('%d.%m.%Y %H:%M:%S'),  # Datum und Uhrzeit im deutschen Format
            str(statement.balance_transferred).replace('.', ','),  # Zahlen im deutschen Format
            str(statement.invoice_amount).replace('.', ','),      # Zahlen im deutschen Format
        ])

    return response


# Here come function display names
generate_invoice_this_year.short_description = "Generiere Abrechnung für dieses Jahr"
generate_invoice_last_year.short_description = "Generiere Abrechnung für letztes Jahr"
send_invoice_emails.short_description = "Versende Emails"
regenerate_invoice.short_description = "Erstelle Abrechnungen neu"
export_order_items_csv.short_description = "Exportiere ausgewählte Bestellungen als CSV"
export_year_end_statements_csv.short_description = "Exportiere ausgewählte Jahresendabrechnungen als CSV"


# Here come helper functions
def getMostRecentInvoice(user, year):
    invoices = Invoice.objects.all().filter(user=user, year=year)
    if len(invoices) == 0:
        return None
    most_recent_invoice = invoices[0]
    for invoice in invoices[1:]:
        if most_recent_invoice.version < invoice.version:
            most_recent_invoice = invoice
    return most_recent_invoice


def generateInvoice(user, year, version):
    yearEndStatement = None
    try:
        yearEndStatement = YearEndStatement.objects.get(user=user, year=year)
        Payment.objects.filter(yearEndStatement=yearEndStatement).delete()
    except YearEndStatement.DoesNotExist:
        pass

    # Generate PDF
    try:
        pdf_path, total = generateInvoicePDF(user, year, version)
    except Exception as e:
        return e
    # Save PDF path to the database
    # Generate Email
    email_subject = f'Ihre Abrechnung vom GSV Gundernhausen Kiosk für {year}'
    email_body = f'Hallo {user.last_name},\n\n' \
                 f'Im Anhang findest du die Abrechnung vom GSV Gundernhausen Kiosk für {year}.\n\n' \
                 f'Vielen Dank, dass du Mitglied bei uns bist!'
    email_html = f"""<html>
<head></head>
<body>
    <p>Hallo {user.last_name},</p>
    <p>Im Anhang findest du die Abrechnung vom GSV Gundernhausen Kiosk für {year}.</p>
    <p>Vielen Dank, dass du Mitglied bei uns bist!</p>
</body>
</html>
"""

    def get_pdf_path(filename):
        # Definieren Sie den relativen Pfad zum übergeordneten Ordner
        return os.path.join('..', 'invoices', filename)

    Invoice.objects.create(user=user, year=year, version=version, pdf_path=get_pdf_path(pdf_path),
                           email_subject=email_subject, email_body_text=email_body, email_body_html=email_html)

    if total > 0:
        balance_transferred = 0
        invoice_amount = total
    else:
        balance_transferred = -total
        invoice_amount = 0

    if yearEndStatement is None:
        yearEndStatement = YearEndStatement.objects.create(user=user, year=year,
                                                           balance_transferred=balance_transferred,
                                                           invoice_amount=invoice_amount)
    else:
        yearEndStatement.balance_transferred = balance_transferred
        yearEndStatement.invoice_amount = invoice_amount
        yearEndStatement.save()

    # Wenn der Nutzer übriges Guthaben hat
    if balance_transferred != 0:
        # Guthaben im alten Jahr abziehen
        p = Payment.objects.create(transaction_id=f"Guthabenübertrag für {year+1}", user=user,
                                   amount=-balance_transferred, yearEndStatement=yearEndStatement)
        p.created_at = datetime.datetime(year=year, month=12, day=31, hour=23, minute=59)
        p.save()

        # Guthaben im neuen Jahr hinzufügen
        p = Payment.objects.create(transaction_id=f"Guthabenübertrag aus {year}", user=user,
                                   amount=balance_transferred, yearEndStatement=yearEndStatement)
        p.created_at = datetime.datetime(year=year+1, month=1, day=1)
        p.save()

    elif invoice_amount != 0:
        # Erstelle Zahlung im letzte Jahr
        p = Payment.objects.create(transaction_id="Lastschrift", user=user, amount=invoice_amount,
                                   yearEndStatement=yearEndStatement)
        p.created_at = datetime.datetime(year=year, month=12, day=31, hour=23, minute=59)
        p.save()

    return True


def generateInvoicesAndAddMessages(queryset, request, year):
    success_counter = 0
    for user in queryset:
        most_recent_invoice = getMostRecentInvoice(user, year)
        version = 1
        if most_recent_invoice is not None:
            version = most_recent_invoice.version + 1
        result = generateInvoice(user, year, version)
        if result is True:
            success_counter += 1
        else:
            messages.error(request, str(result))
    if success_counter != 0:
        if success_counter == 1:
            messages.success(request, f"Abrechnung erfolgreich erstellt.")
        else:
            messages.success(request, f"{success_counter} Abrechnungen erfolgreich erstellt.")
    if success_counter < len(queryset):
        messages.error(request, f"{len(queryset) - success_counter} Abrechnung(en) nicht erstellt.")

    return HttpResponseRedirect(reverse('admin:self_service_kiosk_invoice_changelist'))
