from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Insert data into MyModel'

    def handle(self, *args, **kwargs):
        categories = [
            Category(category_name="Alkoholfreie Getränke"),
            Category(category_name="Alkoholische Getränke"),
            Category(category_name="Snacks"),
            Category(category_name="Eis"),
            Category(category_name="Equipment"),
            Category(category_name="Gastspiele"),
        ]
        counter = 1
        for i in categories:
            i.order_number = counter
            counter += 1

        menuItems = [
            MenuItem(name="Coca Cola", category=categories[0], price=1.5, picture="produkte/coca cola.JPEG"),
            MenuItem(name="Coca Cola Zero", category=categories[0], price=1.5, picture="produkte/coca cola zero.JPEG"),
            MenuItem(name="Fanta", category=categories[0], price=1.5, picture="produkte/fanta.JPEG"),
            MenuItem(name="Sprite", category=categories[0], price=1.5, picture="produkte/sprite.JPEG"),
            MenuItem(name="Wasser klein", category=categories[0], price=1.5, picture="produkte/wasser klein.JPEG"),
            MenuItem(name="Wasser groß", category=categories[0], price=2.2, picture="produkte/wasser gross.JPEG"),
            MenuItem(name="Red Bull", category=categories[0], price=2.2, picture="produkte/red bull.JPEG"),
            MenuItem(name="28 Black", category=categories[0], price=2.2),
            MenuItem(name="Tee", category=categories[0], price=1.2, picture="produkte/tee.JPEG"),
            MenuItem(name="Kaffee Crema", category=categories[0], price=1.2, picture="produkte/kaffee crema.JPEG"),
            MenuItem(name="Cappuccino", category=categories[0], price=2.2, picture="produkte/cappuccino.JPEG"),
            MenuItem(name="Caffè Latte", category=categories[0], price=2.2, picture="produkte/caffe latte.JPEG"),
            MenuItem(name="Espresso", category=categories[0], price=1.2, picture="produkte/espresso.JPEG"),

            MenuItem(name="Helles Naturtrüb", category=categories[1], price=2.2, picture="produkte/naturtrübes helles.JPEG"),
            MenuItem(name="Radler", category=categories[1], price=2.2, picture="produkte/radler.JPEG"),
            MenuItem(name="Pilsner Alkoholfrei", category=categories[1], price=2.2, picture="produkte/pilsner alkoholfrei.JPEG"),
            MenuItem(name="Weißbier Hefe-Hell", category=categories[1], price=2.8, picture="produkte/weissbier hefe-hell.JPEG"),
            MenuItem(name="Weißbier Kristall", category=categories[1], price=2.8, picture="produkte/weissbier kristall.JPEG"),
            MenuItem(name="Weißbier Alkoholfrei", category=categories[1], price=2.8, picture="produkte/weissbier alkoholfrei.JPEG"),
            MenuItem(name="Bembel With Care", category=categories[1], price=2.8, picture="produkte/bembel.JPEG"),
            MenuItem(name="Scavy & Ray Prosecco", category=categories[1], price=4.0, picture="produkte/prosecco.JPEG"),
            MenuItem(name="Aperol Spritz", category=categories[1], price=4.0, picture="produkte/aperol.JPEG"),
            MenuItem(name="Schorlefranz Weinschorle", category=categories[1], price=4.0, picture="produkte/weinschorle.JPEG"),
            MenuItem(name="Rotwein", category=categories[1], price=4.0, picture="produkte/rotwein.JPEG"),
            MenuItem(name="Weißwein", category=categories[1], price=4.0, picture="produkte/weisswein.JPEG"),

            MenuItem(name="Tüte Chips", category=categories[2], price=1.5, picture="produkte/chips.JPEG"),
            MenuItem(name="Dose Nüsse", category=categories[2], price=1.5, picture="produkte/nuesse.JPEG"),
            MenuItem(name="Tüte Kekse", category=categories[2], price=1.5, picture="produkte/kekse.JPEG"),
            MenuItem(name="Schokoriegel", category=categories[2], price=1, picture="produkte/schokoriegel.JPEG"),

            MenuItem(name="Kleines Eis", category=categories[3], price=1, picture="produkte/eis klein.JPEG"),
            MenuItem(name="Großes Eis", category=categories[3], price=1.5, picture="produkte/eis gross.JPEG"),

            MenuItem(name="HTV Spielball", category=categories[4], price=12, picture="produkte/htv spielball.JPEG"),
            MenuItem(name="Wilson US Open 4er", category=categories[4], price=9, picture="produkte/wilson 4er.JPEG"),
            MenuItem(name="Wilson US Open 3er", category=categories[4], price=7.5),
            MenuItem(name="Methodikbälle rot", category=categories[4], price=5),
            MenuItem(name="Methodikbälle orange", category=categories[4], price=5),
            MenuItem(name="Methodikbälle grün", category=categories[4], price=5, picture="produkte/methodikbaelle gruen.JPEG"),
            MenuItem(name="Griffband", category=categories[4], price=1.5, picture="produkte/griffband.JPEG"),
            MenuItem(name="Dämpfer", category=categories[4], price=1, picture="produkte/daempfer.JPEG"),
            MenuItem(name="Finisher", category=categories[4], price=0.5, picture="produkte/finisher.JPEG"),
            MenuItem(name="Schweißband", category=categories[4], price=3, picture="produkte/schweissband.JPEG"),
            MenuItem(name="Stirnband", category=categories[4], price=3, picture="produkte/stirnband.JPEG"),
            MenuItem(name="Kappe", category=categories[4], price=7.5),
            MenuItem(name="Handgelenkbandage", category=categories[4], price=4.5, picture="produkte/handgelenkbandage.JPEG"),
            MenuItem(name="Ball-Clip", category=categories[4], price=3, picture="produkte/ballclip.JPEG"),
            MenuItem(name="GSV Tennis Handtuch", category=categories[4], price=12, picture="produkte/handtuch.JPEG"),

            MenuItem(name="Erwachsene", category=categories[5], price=10, picture="produkte/erwachsene.JPEG"),
            MenuItem(name="Kinder und Jugendl. bis 18 J.", category=categories[5], price=5, picture="produkte/kinder.JPEG"),
        ]
        counter = 1
        for i in menuItems:
            i.order_number = counter
            counter += 1

        Category.objects.bulk_create(categories)

        MenuItem.objects.bulk_create(menuItems)

        return
