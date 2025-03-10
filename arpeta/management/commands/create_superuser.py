from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username="manzola").exists():
            User.objects.create_superuser("manzola", "manuel.anzola31@gmail.com", "mia2712")
            self.stdout.write(self.style.SUCCESS("Superusuario creado con éxito"))