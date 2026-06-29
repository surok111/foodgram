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
        data_path = options['path']
        # Also try relative paths
        if not os.path.exists(data_path):
            base = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base, '..', '..', '..', '..', 'data', 'ingredients.json')
            data_path = os.path.abspath(data_path)

        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'File not found: {data_path}'))
            return

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        created = 0
        for item in data:
            _, was_created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {created} new ingredients'))
