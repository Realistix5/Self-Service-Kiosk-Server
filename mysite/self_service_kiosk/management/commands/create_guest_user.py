from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Erstelle Gast-Nutzer'

    def handle(self, *args, **kwargs):
        user = User.objects.create_user(username="guest_user", password="123")

        return
