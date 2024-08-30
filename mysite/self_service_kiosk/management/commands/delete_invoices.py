from django.core.management.base import BaseCommand
from ...models import *

class Command(BaseCommand):
    help = 'Delete Invoices'

    def handle(self, *args, **kwargs):
        Invoice.objects.all().delete()

        return
