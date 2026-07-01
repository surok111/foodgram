import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='/app/data/ingredients.json',
            help='Path to ingredients JSON file'
        )

    def handle(self, *args, **options):
        file_path = options['path']
        if not os.path.exists(file_path):
            base = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.abspath(
                os.path.join(
                    base, '..', '..', '..', '..', 'data', 'ingredients.json'
                )
            )

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return

        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        created_count = 0
        for item in data:
            _, was_created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            if was_created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} new ingredients'
            )
        )
