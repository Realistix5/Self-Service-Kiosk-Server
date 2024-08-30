# your_app/management/commands/update_user_info.py

import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import UserInfo
from ...functions.member_api import get_user_info  # Stellen Sie sicher, dass der Importpfad korrekt ist
from datetime import datetime


class Command(BaseCommand):
    help = 'Update email addresses and user info for users with numeric usernames'

    def handle(self, *args, **kwargs):
        numeric_users = User.objects.filter(username__regex=r'^\d+$')

        for user in numeric_users:
            name, email, gender, street, plz, city = get_user_info(user.username)

            if name == "not authorized":
                self.stdout.write(self.style.ERROR(f"{datetime.now()}: Authorization failed for user {user.username}"))
                continue
            elif name is None:
                self.stdout.write(self.style.WARNING(f"{datetime.now()}: User info not found for user {user.username}"))
                continue

            # Update user email
            user.email = email
            user.save()

            # Update or create UserInfo
            UserInfo.objects.update_or_create(
                user=user,
                defaults={
                    'gender': gender,
                    'street': street,
                    'city': city,
                    'plz': plz
                }
            )

            self.stdout.write(self.style.SUCCESS(f"{datetime.now()}: Updated info for user {user.username}"))
