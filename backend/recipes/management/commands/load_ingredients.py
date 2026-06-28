import json
import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON or CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='data/ingredients.json')
        parser.add_argument('--format', type=str, default='json', choices=['json', 'csv'])

    def handle(self, *args, **options):
        file_path = options['file']
        fmt = options['format']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        if fmt == 'json':
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
            ingredients = [
                Ingredient(name=item['name'], measurement_unit=item['measurement_unit'])
                for item in data
            ]
        else:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.reader(f)
                ingredients = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader if len(row) >= 2
                ]

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(ingredients)} ingredients'))
