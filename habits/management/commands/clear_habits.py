from django.core.management.base import BaseCommand

from habits.models import Habit


class Command(BaseCommand):
    help = "Очистка всех привычек из базы данных"

    def handle(self, *args, **options):
        count, _ = Habit.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Удалено {count} привычек"))
