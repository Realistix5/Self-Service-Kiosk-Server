import datetime
import qrcode
from django.db.models import Sum, F
from django.utils.formats import number_format

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether

from django.conf import settings
from ..models import *


def generateRegistrationTokenQRCode(token: RegistrationToken):
    # Daten, die im QR-Code enthalten sein sollen
    data = "register:"+str(token.token)

    # QR-Code-Objekt erstellen
    qr = qrcode.QRCode(
        version=1,  # Version des QR-Codes, bestimmt die Größe
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Fehlerkorrekturlevel
        box_size=10,  # Größe jeder Box im QR-Code-Gitter
        border=4,  # Breite des Randes in Boxen
    )

    # Daten zum QR-Code hinzufügen
    qr.add_data(data)
    qr.make(fit=True)

    # QR-Code-Bild erstellen
    img = qr.make_image(fill='black', back_color='white')

    # QR-Code-Bild speichern
    img.save("qr_codes/password/"+str(token.token)+".png")


def generatePasswordResetTokenQRCode(token: PasswordResetToken):
    # Daten, die im QR-Code enthalten sein sollen
    data = "reset_password:"+str(token.token)

    # QR-Code-Objekt erstellen
    qr = qrcode.QRCode(
        version=1,  # Version des QR-Codes, bestimmt die Größe
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Fehlerkorrekturlevel
        box_size=10,  # Größe jeder Box im QR-Code-Gitter
        border=4,  # Breite des Randes in Boxen
    )

    # Daten zum QR-Code hinzufügen
    qr.add_data(data)
    qr.make(fit=True)

    # QR-Code-Bild erstellen
    img = qr.make_image(fill='black', back_color='white')

    # QR-Code-Bild speichern
    img.save("qr_codes/password/"+str(token.token)+".png")


def generateLoginTokenQRCode(token: LoginToken):
    # Daten, die im QR-Code enthalten sein sollen
    data = "login:"+str(token.token)

    # QR-Code-Objekt erstellen
    qr = qrcode.QRCode(
        version=1,  # Version des QR-Codes, bestimmt die Größe
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Fehlerkorrekturlevel
        box_size=10,  # Größe jeder Box im QR-Code-Gitter
        border=4,  # Breite des Randes in Boxen
    )

    # Daten zum QR-Code hinzufügen
    qr.add_data(data)
    qr.make(fit=True)

    # QR-Code-Bild erstellen
    img = qr.make_image(fill='black', back_color='white')

    # QR-Code-Bild speichern
    img.save("qr_codes/login/"+str(token.token)+".png")


def generateInvoicePDF(user, year, version):
    userInfo = UserInfo.objects.get(user=user)
    orders = Order.objects.filter(user=user, created_at__year=year)
    payments = Payment.objects.filter(user=user, order=None, created_at__year=year)

    hasPayments = True
    if len(payments) == 0:
        hasPayments = False

    filename = f"Abrechnung_{year}_{user.username}_{version}.pdf"
    doc = SimpleDocTemplate(f"invoices/{filename}", pagesize=letter, title=f"Abrechnung für {year}")

    # Daten für die Bestellungenstabelle
    data_orders = [['#', 'ID', 'Datum', 'Betrag', 'Rechnungskauf']]  # Kopfzeile
    counter = 0
    for order in orders:
        counter += 1
        paid_status = '✘' if order.paid else '✔'
        data_orders.append(
            [str(counter), str(order.id), order.created_at.strftime("%d.%m.%Y"),
             number_format(order.get_total_price())+" €", paid_status])
    total_orders = sum(order.get_total_price() for order in orders)
    unpaid_total = sum(order.get_total_price() for order in orders if not order.paid)

    # Daten für die Guthabenzahlungentabelle
    if hasPayments:
        data_payments = [['#', 'ID', 'Datum', 'Betrag']]  # Kopfzeile
        counter = 0
        for payment in payments:
            counter += 1
            data_payments.append(
                [str(counter), str(payment.transaction_id), payment.created_at.strftime("%d.%m.%Y"),
                 number_format(str(payment.amount)+" €")])
        total_balance = sum(payment.amount for payment in payments)
    else:
        total_balance = 0

    # Daten für die Produkttabelle
    order_items = OrderItem.objects.filter(order__in=orders)
    product_totals = order_items.values('menu_item__name').annotate(
        total_quantity=Sum('quantity'),
        total_price=Sum(F('quantity') * F('price_at_purchase'))
    ).order_by('menu_item__name')

    data_products = [['Produktname', 'Anzahl', 'Gesamtpreis']]  # Kopfzeile
    counter = 0
    for item in product_totals:
        counter += 1
        data_products.append(
            [item['menu_item__name'], str(item['total_quantity']), f"{number_format(item['total_price'])} €"])

    # Daten für offenen Betrag
    needsToPay = False
    total_price = unpaid_total - total_balance
    if total_price < 0:
        total_label = 'Restliches Guthaben:'
        total = -total_price
    else:
        total_label = 'Offener Betrag:'
        total = total_price
        needsToPay = True
    total_text = f"{total_label} {number_format(total)} €"

    # Header erstellen
    header = [
        Paragraph(user.last_name, getSampleStyleSheet()['Normal']),
        Paragraph(userInfo.street, getSampleStyleSheet()['Normal']),
        Paragraph(f"{userInfo.plz} {userInfo.city}", getSampleStyleSheet()['Normal']),
        Paragraph("", getSampleStyleSheet()['Normal']),
        Spacer(1, 12 * 3),
        Paragraph(f"Abrechnung für {year}", getSampleStyleSheet()['Title']),
        Spacer(1, 12 * 3),
    ]

    # Tabellen-Breite
    table_width = 6.4 * inch

    # Erste Tabelle (Bestellungen) erstellen
    # Berechne Spaltenbreiten
    min_col_widths = [max([len(str(row[i])) for row in data_orders]) * inch / 10 for i in range(len(data_orders[0]))]
    space = table_width - sum(min_col_widths)
    col_widths = [x + (space / len(min_col_widths)) for x in min_col_widths]

    table_orders = Table(data_orders, colWidths=col_widths)
    table_orders.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))

    # Zweite Tabelle (Guthabenzahlungen) erstellen
    # Berechne Spaltenbreiten
    if hasPayments:
        min_col_widths = [max([len(str(row[i])) for row in data_payments]) * inch / 10 for i in range(len(data_payments[0]))]
        space = table_width - sum(min_col_widths)
        col_widths = [x + (space / len(min_col_widths)) for x in min_col_widths]
        table_payments = Table(data_payments, colWidths=col_widths)
        table_payments.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ]))

    # Dritte Tabelle (Produkte) erstellen
    # Berechne Spaltenbreiten
    min_col_widths = [max([len(str(row[i])) for row in data_products]) * inch / 10 for i in
                      range(len(data_products[0]))]
    space = table_width - sum(min_col_widths)
    col_widths = [x + (space / len(min_col_widths)) for x in min_col_widths]
    table_products = Table(data_products, colWidths=col_widths)
    table_products.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))

    # Bestellungen
    order_info = [
        Paragraph("Bestellungen", getSampleStyleSheet()['Heading1']),
        table_orders,
        Paragraph(f"Gesamtbetrag Bestellungen: {number_format(total_orders)} €", getSampleStyleSheet()['Heading3']),
        Paragraph(f"Rechnungsbetrag Bestellungen: {number_format(unpaid_total)} €", getSampleStyleSheet()['Heading3']),
        Spacer(1, 24),
    ]

    # Einzahlungen
    balance_info = [
        Paragraph("Einzahlungen", getSampleStyleSheet()['Heading1'])
    ]
    if hasPayments:
        balance_info.append(table_payments)
        balance_info.append(Paragraph(f"Gesamtbetrag Einzahlungen: {number_format(total_balance)} €", getSampleStyleSheet()['Heading3']))
    else:
        # Hier info einbauen, falls keine guthabenzahlungen gab
        balance_info.append(Paragraph("Es wurden keine Einzahlungen getätigt."))

    balance_info.append(Spacer(1, 24))

    # Offener Betrag
    open_amount = [Paragraph(total_text, getSampleStyleSheet()['Heading1']),
                   Spacer(1, 24)]

    if needsToPay:
        text = f"Dementsprechend werden innerhalb der nächsten Tage {number_format(total)}" \
               f" € von Ihrem Girokonto abgebucht."
        open_amount.append(Paragraph(text, getSampleStyleSheet()['Normal']))
        open_amount.append(Spacer(1, 24))

    open_amount.append(
        Paragraph("Vielen Dank, dass sie Mitglied beim GSV Gundernhausen sind!", getSampleStyleSheet()['Normal']))

    # Bestellte Produkte
    products_info = [Paragraph("Bestellte Produkte",getSampleStyleSheet()['Heading1']),
                     table_products,
                     Spacer(1, 24)]

    story: list
    story = header
    story += order_info
    story += [KeepTogether(balance_info),
              KeepTogether(open_amount)]
    story.append(PageBreak())
    story.append(KeepTogether(products_info))

    doc.build(story)

    return f"{filename}", total_price
