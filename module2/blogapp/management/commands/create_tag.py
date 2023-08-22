from django.core.management import BaseCommand

from blogapp.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Создаем автора")
        tag = Tag.objects.get_or_create(name="interesting")
        self.stdout.write(f"Тег {tag} создан")