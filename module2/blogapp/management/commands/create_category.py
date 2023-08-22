from django.core.management import BaseCommand

from blogapp.models import Category


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Создаем категорию")
        category = Category.objects.get_or_create(name="roman")
        self.stdout.write(f"Категория {category} создана")