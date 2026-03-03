from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Creates Clients and Staff groups"

    def handle(self, *args, **options):
        Group.objects.get_or_create(name="Clients")
        Group.objects.get_or_create(name="Staff")
        self.stdout.write(self.style.SUCCESS("Groups created."))
