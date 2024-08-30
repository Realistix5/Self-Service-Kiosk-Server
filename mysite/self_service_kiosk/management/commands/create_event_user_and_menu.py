from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Erstelle Event-Nutzer und Menü'

    def handle(self, *args, **kwargs):
        User.objects.create_user(username="event_user", password="event_user_pw")
        category = Category.objects.create(category_name="Event Artikel", event_category=True)
        MenuItem.objects.create(name="Event Produkt", price=2.00, category=category)

        return
