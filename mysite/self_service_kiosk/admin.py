import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Max

from .functions.admin_functions import generate_invoice_this_year, generate_invoice_last_year, regenerate_invoice, \
    send_invoice_emails, export_order_items_csv, export_year_end_statements_csv
from .models import *


class UserProfileInline(admin.StackedInline):
    model = UserInfo
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    actions = [generate_invoice_this_year, generate_invoice_last_year]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'order_number', 'event_category']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'picture', 'order_number', 'hidden']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def get_price(self, instance):
        return str(instance.get_price()).replace(".", ",")

    get_price.short_description = "Zwischenpreis"

    readonly_fields = ['price_at_purchase', 'get_price']

    fields = ["menu_item", 'price_at_purchase', "quantity", 'get_price']


class OrderYearFilter(admin.SimpleListFilter):
    title = 'Jahr'
    parameter_name = 'created_at__year'

    def lookups(self, request, model_admin):
        years = Order.objects.dates('created_at', 'year')
        return [(year.year, year.year) for year in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_at__year=self.value())
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "get_total_price"]
    actions = [export_order_items_csv]
    list_filter = (OrderYearFilter,)
    fieldsets = [
        (None, {"fields": ["user", "created_at", "paid", "get_total_price"]}),
    ]

    inlines = [OrderItemInline]
    list_display = ["__str__", "user", "created_at", "paid", "get_total_price"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["transaction_id", "created_at", "user", "order", "amount"]


class MaxVersionFilter(admin.SimpleListFilter):
    title = 'Version Filter'
    parameter_name = 'max_version'

    def lookups(self, request, model_admin):
        return (
            ('max_only', 'Nur höchste Versionen'),
            ('all', 'Alle'),
        )

    def queryset(self, request, queryset):
        if self.value() != 'all':
            max_versions = Invoice.objects.values('user', 'year').annotate(max_version=Max('version'))
            max_version_ids = [
                queryset.filter(user=item['user'], year=item['year'], version=item['max_version']).values_list('id', flat=True)
                for item in max_versions
            ]
            max_version_ids = [item for sublist in max_version_ids for item in sublist]
            return queryset.filter(id__in=max_version_ids)
        return queryset

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            if lookup in ['max_only', 'all']:
                yield {
                    'selected': self.value() == lookup,
                    'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                    'display': title,
                }


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    actions = [send_invoice_emails, regenerate_invoice]
    list_display = ["id", "user", "year", "email_sent", "version", "created_at"]
    list_filter = ["year", "email_sent", MaxVersionFilter]
    fields = ['user', 'year', 'version', 'created_at', 'pdf_path', 'email_sent',
              'email_subject', 'email_body_text', 'email_body_html']
    readonly_fields = ['created_at']

    def get_default_filters(self, request):
        default_filters = super().get_default_filters(request)
        default_filters['max_version'] = 'yes'
        return default_filters


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAmountFilter(admin.SimpleListFilter):
    title = 'mit Rechnungsbetrag'
    parameter_name = 'invoice_amount'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'mit Rechnungsbetrag')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(invoice_amount__gt=0)
        return queryset


@admin.register(YearEndStatement)
class YearEndStatementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'year', 'changed_at', 'balance_transferred', 'invoice_amount')
    list_filter = ['year', InvoiceAmountFilter]
    inlines = [PaymentInline]
    fields = ['user', 'year', 'created_at', 'changed_at', 'balance_transferred', 'invoice_amount']
    readonly_fields = ['created_at', 'changed_at']
    actions = [export_year_end_statements_csv]

