from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from habits.models import Habit
from habits.tasks import send_habit_reminder, send_test_notification

User = get_user_model()


class Command(BaseCommand):
    help = "Отправка тестового уведомления"

    def add_arguments(self, parser):
        parser.add_argument("--habit", type=int, help="Send reminder for specific habit ID")
        parser.add_argument("--user", type=str, help="Send to specific username")

    def handle(self, *args, **options):
        if options["habit"]:
            # Отправка напоминания для конкретной привычки
            habit_id = options["habit"]
            self.stdout.write(f"Sending reminder for habit {habit_id}...")
            result = send_habit_reminder.delay(habit_id)
            self.stdout.write(self.style.SUCCESS(f"Result: {result.result}"))

        elif options["user"]:
            # Отправка тестового уведомления конкретному пользователю
            username = options["user"]
            user = User.objects.filter(username=username).first()
            if user and user.telegram_chat_id:
                from habits.tasks import send_telegram_message

                message = f"🧪 Тестовое уведомление для {username}"
                success = send_telegram_message(user.telegram_chat_id, message)
                self.stdout.write(self.style.SUCCESS(f"Notification sent: {success}"))
            else:
                self.stdout.write(self.style.ERROR("User not found or no Telegram chat_id"))

        else:
            # Обычное тестовое уведомление
            self.stdout.write("Sending test notification...")
            result = send_test_notification.delay()
            self.stdout.write(self.style.SUCCESS(f"Result: {result.result}"))
