from django.core.management import BaseCommand

from blogapp.models import Author


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Создаем автора")
        author = Author.objects.get_or_create(name="samir", bio="this is my blog")
        self.stdout.write(f"Автор {author} создан")