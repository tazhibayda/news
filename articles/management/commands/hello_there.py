from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Hello"

    def handle(self, *args, **options):
        print("Hello there")
