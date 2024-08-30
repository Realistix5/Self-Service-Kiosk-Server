import datetime
import os

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

from .custom_storage import SecurePDFStorage


# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=30, verbose_name="Name")
    order_number = models.IntegerField(default=100, verbose_name="Ordnungsnummer")
    event_category = models.BooleanField(default=False, verbose_name="Event Kategorie")

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __str__(self):
        return self.category_name


class MenuItem(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategorie")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Preis")
    picture = models.ImageField(upload_to='produkte/', null=True, blank=True, verbose_name="Bild")
    order_number = models.IntegerField(default=100, verbose_name="Ordnungsnummer")
    hidden = models.BooleanField(default=False, verbose_name="Versteckt")

    class Meta:
        verbose_name = "Menüpunkt"
        verbose_name_plural = "Menüpunkte"

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")
    paid = models.BooleanField(default=False, verbose_name="Bezahlt")

    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"

    def __str__(self):
        return f"Bestellung Nr. {self.id}"

    def get_total_price(self):
        """
        Summarizes the prices of all :class:`~self_service_kiosk.models.MenuItem`.

        :return: A Decimal with the total price of the :class:`~self_service_kiosk.models.Order`.
        """
        total_price = sum(item.get_price() for item in self.orderitem_set.all())
        return total_price

    get_total_price.short_description = "Gesamtpreis"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Bestellung")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Menüpunkt")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Menge")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preis beim Kauf")

    class Meta:
        verbose_name = "Bestellungsteil"
        verbose_name_plural = "Bestellungsteile"
        unique_together = [['order', 'menu_item']]

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def get_price(self):
        """
        Multiplicates :attr:`~self_service_kiosk.models.OrderItem.quantity` with :attr:`~self_service_kiosk.models.OrderItem.price_at_purchase`.

        :return: The price of the :class:`~self_service_kiosk.models.OrderItem`.
        """
        if self.price_at_purchase is not None:
            return self.price_at_purchase * self.quantity
        else:
            return None  # Oder einen anderen geeigneten Standardwert zurückgeben

    get_price.short_description = 'Zwischenpreis'

    def save(self, *args, **kwargs):
        """
        Overrides the normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model` to set :attr:`~self_service_kiosk.models.OrderItem.price_at_purchase` according the :attr:`~self_service_kiosk.models.MenuItem.price` of relating :class:`~self_service_kiosk.models.MenuItem`.

        :param args: Gets passed to normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model`.
        :param kwargs: Gets passed to normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model`.
        :return: 0 on success.
        """
        if self.price_at_purchase is None:  # Wenn der Preis beim Kauf noch nicht gesetzt ist
            self.price_at_purchase = self.menu_item.price  # Setze den Preis beim Kauf auf den aktuellen Preis des MenuItems
        super().save(*args, **kwargs)


class TokenBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")
    valid_until = models.DateTimeField(verbose_name="Gültig bis")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overrides the normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model` to set :attr:`~self_service_kiosk.models.TokenBase.valid_until`.

        :param args: Gets passed to normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model`.
        :param kwargs: Gets passed to normal :func:`~django.db.models.Model.save` method of :class:`~django.db.models.Model`.
        :return: 0 on success.
        """
        if not self.id:
            self.set_valid_until()
        super().save(*args, **kwargs)

    def set_valid_until(self):
        """
        To be overridden by subclasses to set the appropriate validity period.
        :return: NotImplementedError("Subclasses must define `set_valid_until`.")
        """
        raise NotImplementedError("Subclasses must define `set_valid_until`.")

    def is_valid(self):
        """
        Checks if the token is still valid.
        :return: True if the token is still valid, False otherwise.
        """
        return self.valid_until > timezone.now()


class RegistrationToken(TokenBase):
    class Meta:
        verbose_name = "Registrierungs-Token"
        verbose_name_plural = "Registrierungs-Tokens"

    def set_valid_until(self):
        """
        Sets the :attr:`~self_service_kiosk.models.TokenBase.valid_until` to one day after creation.
        :return: 0 on success.
        """
        self.valid_until = timezone.now() + timezone.timedelta(days=1)


class PasswordResetToken(TokenBase):
    class Meta:
        verbose_name = "Passwort-Reset-Token"
        verbose_name_plural = "Passwort-Reset-Tokens"

    def set_valid_until(self):
        """
        Sets the :attr:`~self_service_kiosk.models.TokenBase.valid_until` to one day after creation.
        :return: 0 on success.
        """
        self.valid_until = timezone.now() + timezone.timedelta(days=1)


class LoginToken(TokenBase):
    class Meta:
        verbose_name = "Login-Token"
        verbose_name_plural = "Login-Tokens"

    def set_valid_until(self):
        """
        Sets the :attr:`~self_service_kiosk.models.TokenBase.valid_until` to one year after creation.
        :return: 0 on success.
        """
        self.valid_until = timezone.now() + timezone.timedelta(days=365)


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    gender = models.CharField(max_length=10, verbose_name="Geschlecht")
    street = models.CharField(max_length=255, verbose_name="Straße")
    city = models.CharField(max_length=100, verbose_name="Stadt")
    plz = models.IntegerField(verbose_name="PLZ")

    class Meta:
        verbose_name = "Nutzer Info"
        verbose_name_plural = "Nutzer Infos"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    year = models.IntegerField(verbose_name="Jahr")
    version = models.IntegerField(verbose_name="Versions-Nummer")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")
    pdf_path = models.FileField(storage=SecurePDFStorage(), upload_to='', null=True, blank=True, verbose_name="PDF Pfad")
    email_sent = models.BooleanField(default=False, verbose_name="E-Mail gesendet")
    email_subject = models.CharField(max_length=200, verbose_name="E-Mail Betreff")
    email_body_text = models.TextField(verbose_name="E-Mail Text")
    email_body_html = models.TextField(verbose_name="E-Mail Text-HTML")

    def __str__(self):
        return f"Abrechnung für {self.user.last_name} von {self.year}"

    class Meta:
        verbose_name = "Abrechnung"
        verbose_name_plural = "Abrechnungen"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'year', 'version'], name='unique_user_year_version_combination'
            )
        ]


class YearEndStatement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    year = models.IntegerField(verbose_name="Jahr")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Geändert")
    changed_at = models.DateTimeField(auto_now=True, verbose_name="Geändert")
    balance_transferred = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Guthabenübertrag")
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Rechnungsbetrag")

    class Meta:
        verbose_name = "Jahresendabrechnung"
        verbose_name_plural = "Jahresendabrechnungen"


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=30, verbose_name="TransaktionsID", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nutzer")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Betrag")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Bestellung")
    yearEndStatement = models.ForeignKey(YearEndStatement, on_delete=models.CASCADE, null=True,
                                         blank=True, verbose_name="Jahresendabrechnung", default=None)

    class Meta:
        verbose_name = "Zahlung"
        verbose_name_plural = "Zahlungen"
