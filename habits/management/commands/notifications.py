from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from habits.tasks import send_test_notification

User = get_user_model()


class Command(BaseCommand):
    help = "Быстрая проверка уведомлений"

    def handle(self, *args, **options):
        self.stdout.write("🔔 Testing notifications...")

        # Проверяем пользователей с Telegram
        users_with_telegram = User.objects.filter(telegram_chat_id__isnull=False)
        self.stdout.write(f"Found {users_with_telegram.count()} users with Telegram")

        for user in users_with_telegram:
            self.stdout.write(f"Sending test to {user.username}...")
            result = send_test_notification.delay()
            self.stdout.write(f"Result: {result.result}")
