import json
import os

from django.core.management import BaseCommand

from api.models import Ingredient, Tag
from foodgram.settings import BASE_DIR
from users.models import User


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from /static/data/"

    def handle(self, *args, **options):
        # Show this before loading the data into the database
        print("Loading data")
        superuser = User.objects.create(
            username='admin',
            email='admin@admin.ru',
            role='admin',
            first_name='admin',
            last_name='admin'
        )
        superuser.set_password('1q2w3e4r5t6y7u8i9o0p')
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()

        with open(
            os.path.join(BASE_DIR, 'static/data/ingredients.json'),
            'r', encoding='utf-8', newline=''
        ) as jsonfile:
            ingredients = json.load(jsonfile)
            datadict = {}
            for ingredient in ingredients:
                datadict[ingredient['name']] = ingredient['measurement_unit']

            Ingredient.objects.bulk_create([
                Ingredient(
                    name=name, measurement_unit=measurement_unit
                ) for name, measurement_unit in datadict.items()
            ])

        with open(
            os.path.join(BASE_DIR, 'static/data/tags.json'),
            'r', encoding='utf-8', newline=''
        ) as jsonfile:
            tags = json.load(jsonfile)
            Tag.objects.bulk_create([
                Tag(**tag) for tag in tags
            ])

        with open(
            os.path.join(BASE_DIR, 'static/data/users.json'),
            'r', encoding='utf-8', newline=''
        ) as jsonfile:
            users = json.load(jsonfile)
            for user in users:
                password = user.pop('password')
                instance = User.objects.create(**user)
                instance.set_password(password)
                instance.save()

        print("Data upload finished.")
